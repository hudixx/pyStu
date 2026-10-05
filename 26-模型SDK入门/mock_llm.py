"""本机假模型：实现 OpenAI 兼容的 POST /v1/chat/completions。

阶段六示例和练习都打这里，不访问公网、不花 token。
换真模型时：同一套 AsyncOpenAI，只改环境变量 OPENAI_BASE_URL / OPENAI_API_KEY。

对照 Java：这就是一个写死业务规则的假支付网关，专门给你联调用。
底层用的是标准库 http.server，不是 FastAPI。一个请求一个线程（ThreadingHTTPServer）。

特殊用户文案（写在最后一条 user 消息里）：
- 含 TRIGGER:429      → 一直 429，用来看 SDK 怎么报错
- 含 TRIGGER:429-ONCE → 第一次 429，第二次成功（看重试）
- 含 TRIGGER:SLOW     → 先睡 2 秒再回，用来看超时
- 含 TRIGGER:BADJSON  → 返回不是 JSON 的字符串，用来看 pydantic 失败
"""

from __future__ import annotations

import json  # 解析请求体、拼响应。对照 Jackson 的 readTree / writeValueAsString，这里是标准库。
import threading  # 把 serve_forever 丢到后台线程，调用方才能继续跑客户端。
import time  # sleep：故意拖慢，或流式时每吐一个字停一下。
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer  # 标准库的迷你 HTTP 服务器。


class MockLLMHandler(BaseHTTPRequestHandler):
    """每个请求 new 一个实例。对照 HttpServlet：类是单例，但这里是「一请求一对象」。

    因此想跨请求记次数，不能放在 self 上（下个请求是另一个对象），要放类变量，对照 static 字段。
    """

    # 类变量：所有请求共享这一份整数。只给 TRIGGER:429-ONCE 计数。
    # 演示没加锁。两个请求同时进来时 += 可能丢更新；本课是单客户端串行调用，够用。
    _once_hits = 0

    def log_message(self, format: str, *args) -> None:
        """关掉默认访问日志，演示时太吵。

        父类每个请求都会调这个方法往 stderr 打一行。签名必须和父类一致（名字、参数），
        否则不算覆盖。format 这个参数名和内置函数重名，但必须沿用父类的名字，不能改成 fmt。
        *args：剩余位置参数收成元组。对照 Java 的 Object... args。直接 return 等于什么都不打。
        """
        return

    def do_POST(self) -> None:
        """只认 /v1/chat/completions。官方 SDK 的 base_url=.../v1 会再拼上 /chat/completions。

        方法名 do_POST 是父类规定的：收到 POST 就调它。对照 servlet 的 doPost。
        不写 do_GET，所以 GET 会落到父类，返回 501。
        """
        # self.path 可能带查询串，比如 /v1/chat/completions?foo=1。split 一次，只留 ? 左边。
        # split("?", 1) 的 1 表示最多切一刀。对照 String.split("\\?", 2) 的限制次数。
        path = self.path.split("?", 1)[0]
        if path != "/v1/chat/completions":
            # 其它路径按 OpenAI 的错误形状回 404，让 SDK 能解析成 API 错误而不是一堆 HTML。
            self._send_json(404, {"error": {"message": "not found", "type": "invalid_request_error"}})
            return  # 这个请求到此结束。对照 return; 退出 doPost。

        # Content-Length 没有就当 0。headers.get 的第二个参数是默认值，对照 request.getHeader 后自己判空。
        length = int(self.headers.get("Content-Length", "0"))
        # rfile 是「已经按 HTTP 解好头」的请求体输入流。对照 ServletInputStream。read(n) 正好读 n 个字节。
        raw = self.rfile.read(length)
        # 有 body 才解析。raw 是 bytes，decode 成 str 再 json.loads 成 dict。空 body 用 {}。
        # 「值 if 条件 else 另一值」是三元表达式，顺序和 Java 的 条件 ? 值 : 另一值 相反。
        body = json.loads(raw.decode("utf-8")) if raw else {}

        # dict.get：没有这个键就返回 None，不抛异常。对照 Map.get。or []：None 或空列表都换成 []。
        messages = body.get("messages") or []
        user_text = _last_user(messages)  # 只看最后一条 user，系统提示里的 TRIGGER 不会触发。
        stream = bool(body.get("stream"))  # 缺省或 false 都当非流式。bool(None) 是 False。
        max_tokens = body.get("max_tokens")  # 可能是 None、int，或客户端乱传的别的类型。
        temperature = body.get("temperature")  # 假模型只是把它拼进回声，并不真的随机。
        want_json = _wants_json(body)  # 客户端是否要 response_format=json_object。

        # —— 故障注入：练习 30 用。先判 429-ONCE，再判 429，避免「ONCE」被更短的「429」提前截走。 ——
        if "TRIGGER:429-ONCE" in user_text:
            # 类名.字段：改的是共享的那一份，不是某一个请求对象上的副本。对照 MockLLMHandler.staticField++。
            MockLLMHandler._once_hits += 1
            # % 2 == 1：第 1、3、5… 次返回 429，第 2、4… 次放行。所以「第一次失败，第二次成功」。
            if MockLLMHandler._once_hits % 2 == 1:
                self._send_json(429, _rate_limit_body())
                return
        elif "TRIGGER:429" in user_text:
            # 每次都 429。SDK 的 max_retries 用完后会抛 RateLimitError。
            self._send_json(429, _rate_limit_body())
            return

        if "TRIGGER:SLOW" in user_text:
            # 故意堵住当前这个请求线程 2 秒。客户端 timeout 小于 2 秒就会先断开。
            # 这是同步 sleep，会占住本线程；ThreadingHTTPServer 下别的请求仍能进别的线程。
            time.sleep(2.0)

        reply = _make_reply(user_text, want_json, temperature)
        if "TRIGGER:BADJSON" in user_text:
            # 看起来像 JSON，其实缺引号、缺右花括号。json.loads 和 pydantic 都会失败。
            # 这行放在 _make_reply 之后，专门覆盖掉上面生成的合法 JSON。
            reply = "{name: hudi, score: 70"
        # isinstance：是不是 int。对照 instanceof。浮点 4.0 或字符串 "4" 不会进这个分支。
        if isinstance(max_tokens, int) and max_tokens > 0:
            # 切片 [ : n ]：取前 n 个字符，不够 n 个就全给。假 token：1 个字符算 1 个，只为了看见截断。
            reply = reply[:max_tokens]

        # 生成器表达式：对 messages 里每条的 content 长度求和。没有 content 时 get 给空串。
        # 对照 messages.stream().mapToInt(m -> text(m).length()).sum()。
        prompt_tokens = sum(len(str(m.get("content", ""))) for m in messages)
        completion_tokens = len(reply)  # 回复字符串的字符数，同样是假 token。

        if stream:
            # stream=true 时不回一个 JSON 对象，而回 text/event-stream，一块一块推。
            self._send_sse(reply, prompt_tokens, completion_tokens)
            return
        # 非流式：一个 200 JSON，形状要让 SDK 的 choices[0].message.content 取得出来。
        self._send_json(200, _completion_body(reply, prompt_tokens, completion_tokens))

    def _send_json(self, code: int, payload: dict) -> None:
        """普通 JSON 响应。对照 16 课自己写的 _send。下划线开头表示「模块内部用」，不是语言强制的 private。"""
        # ensure_ascii=False：中文保持原样，不要变成 \\uXXXX。encode 得到 bytes，HTTP 正文必须是字节。
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)  # 写状态行，比如 HTTP/1.0 200 OK。此时还没写完头。
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))  # 头的值必须是 str，len 是 int，所以 str()。
        self.end_headers()  # 头结束，后面的 write 才是正文。对照 response 先设 header 再 getWriter。
        self.wfile.write(data)  # wfile 是响应输出流。对照 ServletOutputStream。

    def _send_sse(self, reply: str, prompt_tokens: int, completion_tokens: int) -> None:
        """按 OpenAI 流式协议一块一块推。SDK 的 stream=True 靠这个解析。

        SSE 的一条消息是「data: 内容」加一个空行（\\n\\n）。这里的内容是一小段 JSON。
        """
        self.send_response(200)
        # text/event-stream 才是 SSE。SDK 认的是 data: 行，不是普通 JSON 数组。
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")  # 告诉中间代理不要缓存这股流。
        self.end_headers()
        # 第一块带 role，后面只带 content。对照客户端读到的 choices[0].delta。
        first = True
        for ch in reply:
            # 一个字一块。delta 的类型标成 dict，是给阅读和 mypy 的，运行时仍是普通字典。
            delta: dict = {"content": ch}
            if first:
                delta["role"] = "assistant"  # 只在第一块声明「这是助手在说」。
                first = False
            chunk = {
                "id": "chatcmpl-mock",  # 假的完成 id，字段对齐官方 chunk，SDK 不拿它做业务。
                "object": "chat.completion.chunk",  # 流式块的类型名。非流式是 chat.completion。
                "choices": [{"index": 0, "delta": delta, "finish_reason": None}],
            }
            # f"..." 是格式化字符串。对照 Java 的 "data: " + json。末尾两个换行才是一条 SSE 的结束。
            self.wfile.write(f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n".encode("utf-8"))
            self.wfile.flush()  # 立刻从缓冲区推给客户端。不 flush，客户端要等缓冲区满或连接结束才看得到。
            time.sleep(0.02)  # 每字停 20 毫秒，演示时才能看出「边收边打」，而不是一瞬间全出来。
        # 结束块：delta 为空，finish_reason=stop，并带上 usage。官方协议里 usage 常在最后一块。
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
        # [DONE] 是协议规定的纯文本哨兵，不是 JSON。b"..." 表示这是 bytes 字面量，不用再 encode。
        self.wfile.write(b"data: [DONE]\n\n")
        self.wfile.flush()


def _last_user(messages: list) -> str:
    """从后往前找最后一条 role=user 的 content。没有就空串。

    reversed(messages) 不修改原列表，只是倒着遍历。对照从 list.size()-1 往 0 扫。
    """
    for m in reversed(messages):
        # m 预期是 dict。get 找不到 role 时返回 None，不会 KeyError。
        if m.get("role") == "user":
            return str(m.get("content", ""))  # content 可能不是字符串，str() 兜一下。
    return ""


def _wants_json(body: dict) -> bool:
    """response_format.type == json_object 时，假模型返回一段合法 JSON。"""
    # 没有 response_format 时 get 得到 None，or {} 换成空 dict，后面的 .get 才不会在 None 上报错。
    fmt = body.get("response_format") or {}
    return fmt.get("type") == "json_object"


def _make_reply(user_text: str, want_json: bool, temperature: object) -> str:
    """确定性回复，方便练习断言。真模型不会这么听话。

    temperature 标成 object：调用方可能传入 None、float 或别的。对照 Object，表示「这里不限定具体类型」。
    """
    # 要 JSON，或这句是来测脏 JSON 的：先给一段合法 JSON。脏 JSON 分支会在 do_POST 里把它覆盖掉。
    if want_json or "TRIGGER:BADJSON" in user_text:
        return '{"name": "hudi", "score": 70}'
    extra = ""
    if temperature is not None:
        # f-string 里 {temperature} 会调用它的字符串形式。0.2 就会变成 " temperature=0.2"。
        extra = f" temperature={temperature}"
    # 默认就是回声，把用户原文原样接在后面。所以练习里可以用「回复里包含某句话」做断言。
    return f"回声: {user_text}{extra}"


def _completion_body(reply: str, prompt_tokens: int, completion_tokens: int) -> dict:
    """非流式的 chat.completion 形状。SDK 用 choices[0].message.content 取值。"""
    return {
        "id": "chatcmpl-mock",
        "object": "chat.completion",  # 非流式对象名。和上面 chunk 那个不一样。
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": reply},  # 整段回复一次给完。
                "finish_reason": "stop",  # stop=正常说完。被 max_tokens 截断时真模型会给 length；这里没区分。
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,  # 输入侧估算。
            "completion_tokens": completion_tokens,  # 输出侧估算。
            "total_tokens": prompt_tokens + completion_tokens,  # 账单通常按 total 计。
        },
    }


def _rate_limit_body() -> dict:
    """429 的常见 JSON。SDK 看到 HTTP 429 加这种 body，会抛 RateLimitError。"""
    return {
        "error": {
            "message": "Rate limit exceeded (mock)",
            "type": "rate_limit_error",
            "code": "rate_limit_exceeded",
        }
    }


def start_mock() -> tuple[ThreadingHTTPServer, str]:
    """端口 0 = 让操作系统分配一个空闲端口。返回 (server, base_url)。

    base_url 形如 http://127.0.0.1:xxxxx/v1 ，直接传给 AsyncOpenAI(base_url=...)。
    -> tuple[...] 只是标注返回类型，运行时返回的就是一个普通元组。
    """
    # 绑定 127.0.0.1（只有本机能连）和端口 0。第二个参数是「用哪个 Handler 类处理请求」。
    server = ThreadingHTTPServer(("127.0.0.1", 0), MockLLMHandler)
    # serve_forever 会一直阻塞，所以丢到新线程。daemon=True：主线程退出时这个线程不必单独 join。
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()  # 开始监听。start 很快返回，不等请求来。
    # 端口传了 0，真正的端口要等 bind 之后从 server_address 读出来。(host, port) 再拆成两个变量。
    host, port = server.server_address
    return server, f"http://{host}:{port}/v1"
