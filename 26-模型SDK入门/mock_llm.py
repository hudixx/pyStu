"""本机假模型：实现 OpenAI 兼容的 POST /v1/chat/completions。

阶段六示例和练习都打这里，不访问公网、不花 token。
换真模型时：同一套 AsyncOpenAI，只改环境变量 OPENAI_BASE_URL / OPENAI_API_KEY。

对照 Java：这就是一个写死业务规则的假支付网关，专门给你联调用。

特殊用户文案（写在最后一条 user 消息里）：
- 含 TRIGGER:429      → 一直 429，用来看 SDK 怎么报错
- 含 TRIGGER:429-ONCE → 第一次 429，第二次成功（看重试）
- 含 TRIGGER:SLOW     → 先睡 2 秒再回，用来看超时
- 含 TRIGGER:BADJSON  → 返回不是 JSON 的字符串，用来看 pydantic 失败
"""

from __future__ import annotations

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class MockLLMHandler(BaseHTTPRequestHandler):
    """每个请求 new 一个实例。对照 HttpServlet。"""

    # 类变量：跨请求计数。仅给 TRIGGER:429-ONCE 用。
    _once_hits = 0

    def log_message(self, format: str, *args) -> None:
        """关掉默认访问日志，演示时太吵。签名必须和父类一致。"""
        return

    def do_POST(self) -> None:
        """只认 /v1/chat/completions。官方 SDK 的 base_url=.../v1 会拼这个路径。"""
        path = self.path.split("?", 1)[0]
        if path != "/v1/chat/completions":
            self._send_json(404, {"error": {"message": "not found", "type": "invalid_request_error"}})
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        body = json.loads(raw.decode("utf-8")) if raw else {}

        messages = body.get("messages") or []
        user_text = _last_user(messages)
        stream = bool(body.get("stream"))
        max_tokens = body.get("max_tokens")
        temperature = body.get("temperature")
        want_json = _wants_json(body)

        # —— 故障注入：练习 30 用 ——
        if "TRIGGER:429-ONCE" in user_text:
            MockLLMHandler._once_hits += 1
            if MockLLMHandler._once_hits % 2 == 1:
                self._send_json(429, _rate_limit_body())
                return
        elif "TRIGGER:429" in user_text:
            self._send_json(429, _rate_limit_body())
            return

        if "TRIGGER:SLOW" in user_text:
            time.sleep(2.0)  # 故意堵住；客户端 timeout 设小就会失败

        reply = _make_reply(user_text, want_json, temperature)
        if "TRIGGER:BADJSON" in user_text:
            # 看起来像 JSON，其实缺引号，json.loads / pydantic 都会炸。
            reply = "{name: hudi, score: 70"
        if isinstance(max_tokens, int) and max_tokens > 0:
            reply = reply[:max_tokens]  # 假 token：1 个字符算 1 个，够用来看截断

        prompt_tokens = sum(len(str(m.get("content", ""))) for m in messages)
        completion_tokens = len(reply)

        if stream:
            self._send_sse(reply, prompt_tokens, completion_tokens)
            return
        self._send_json(200, _completion_body(reply, prompt_tokens, completion_tokens))

    def _send_json(self, code: int, payload: dict) -> None:
        """普通 JSON 响应。对照 16 课 _send。"""
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_sse(self, reply: str, prompt_tokens: int, completion_tokens: int) -> None:
        """按 OpenAI 流式协议一块一块推。SDK 的 stream=True 靠这个解析。"""
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        # 第一块带 role，后面只带 content。对照 choices[0].delta。
        first = True
        for ch in reply:
            delta: dict = {"content": ch}
            if first:
                delta["role"] = "assistant"
                first = False
            chunk = {
                "id": "chatcmpl-mock",
                "object": "chat.completion.chunk",
                "choices": [{"index": 0, "delta": delta, "finish_reason": None}],
            }
            self.wfile.write(f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n".encode("utf-8"))
            self.wfile.flush()  # 立刻推出去，客户端才能边收边打
            time.sleep(0.02)
        done = {
            "id": "chatcmpl-mock",
            "object": "chat.completion.chunk",
            "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
        }
        self.wfile.write(f"data: {json.dumps(done)}\n\n".encode("utf-8"))
        self.wfile.write(b"data: [DONE]\n\n")
        self.wfile.flush()


def _last_user(messages: list) -> str:
    """从后往前找最后一条 role=user 的 content。没有就空串。"""
    for m in reversed(messages):
        if m.get("role") == "user":
            return str(m.get("content", ""))
    return ""


def _wants_json(body: dict) -> bool:
    """response_format.type == json_object 时，假模型返回一段合法 JSON。"""
    fmt = body.get("response_format") or {}
    return fmt.get("type") == "json_object"


def _make_reply(user_text: str, want_json: bool, temperature: object) -> str:
    """确定性回复，方便练习断言。真模型不会这么听话。"""
    if want_json or "TRIGGER:BADJSON" in user_text:
        return '{"name": "hudi", "score": 70}'
    extra = ""
    if temperature is not None:
        extra = f" temperature={temperature}"
    return f"回声: {user_text}{extra}"


def _completion_body(reply: str, prompt_tokens: int, completion_tokens: int) -> dict:
    """非流式的 chat.completion 形状。SDK 用 choices[0].message.content 取值。"""
    return {
        "id": "chatcmpl-mock",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": reply},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
    }


def _rate_limit_body() -> dict:
    """429 的常见 JSON。SDK 会抬成 RateLimitError。"""
    return {
        "error": {
            "message": "Rate limit exceeded (mock)",
            "type": "rate_limit_error",
            "code": "rate_limit_exceeded",
        }
    }


def start_mock() -> tuple[ThreadingHTTPServer, str]:
    """端口 0 = OS 分配。返回 (server, base_url)。

    base_url 形如 http://127.0.0.1:xxxxx/v1 ，直接传给 AsyncOpenAI(base_url=...)。
    """
    server = ThreadingHTTPServer(("127.0.0.1", 0), MockLLMHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    return server, f"http://{host}:{port}/v1"
