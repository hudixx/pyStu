"""本机假模型：专门给阶段八返回 tool_calls。不访问公网。

阶段六的 mock_llm.py 继续只做回声和 TRIGGER，不要往那边加工具。
两套假模型分开，26–31 课的断言才不会被工具形状弄坏。

对照：一个写死规则的调度员。它只填写「该叫哪个函数、参数 JSON 长什么样」，
不维护待办列表，也不执行函数。执行在 todos.py，循环在 agent_loop.py。

start_mock() 用端口 0，不占用 8001。8001 仍留给 mock_llm.py 的常驻入口。

用户文案写在最后一条 role=user 里（系统提示里的同名文字不会触发）：
- 列出待办、或含 TOOL:LIST     → 要求调用 list_todos，参数 "{}"
- 记一条 标题、或 TOOL:ADD:标题 → 要求调用 add_todo
- TOOL:BADJSON                  → arguments 故意不是 JSON
- TOOL:EMPTY                    → {"title": ""}
- TOOL:UNKNOWN                  → 工具名 drop_database（你的白名单里没有）
- TOOL:LOOP                     → 即使已经有工具结果，仍继续要求 list_todos
- TOOL:SLOW                     → 先睡 2 秒，再要求 list_todos
- TOOL:ECHO-TOOLS               → 不调工具，正文列出本次请求里的工具名
- 其它                          → 回声，没有 tool_calls
- 请求没带非空 tools            → 一律回声。说明书都没给，就不能假装要调工具
  例外：TOOL:ECHO-TOOLS 会回答「工具清单: （没有）」，用来证明名字不是假模型自己编的
- 最后一条已经是 role=tool 且不是 LOOP → 正文「已根据工具结果回答: ...」
  用户又发了新的一句时，最后一条是 user，按这句重新派工单，不拿旧的工具结果充数
"""

from __future__ import annotations

import json  # 拼响应、把标题收成合法 JSON 字符串。对照 Jackson。
import threading  # serve_forever 放后台，示例才能继续当客户端。
import time  # TOOL:SLOW 故意堵住这个请求线程。
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def tool_specs() -> list[dict]:
    """传给 chat.completions.create(tools=...) 的说明书。

    这是给模型看的 JSON Schema，不是 Python 函数本身。
    对照：写给前端的接口文档。文档拦不住脏请求，拦得住的是后端校验（第 39 课）。
    """
    return [
        {
            "type": "function",  # 目前官方就这一种类型。对照接口类型字段，不是多态基类。
            "function": {
                "name": "list_todos",
                "description": "列出当前用户的待办。没有参数。",
                "parameters": {
                    "type": "object",
                    "properties": {},  # 没有字段。调用时 arguments 应是 "{}"。
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "add_todo",
                "description": "新增一条待办。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "待办标题，不能为空"},
                    },
                    "required": ["title"],
                    "additionalProperties": False,  # 多出来的字段也不该有。模型仍可能塞进来。
                },
            },
        },
    ]


class MockToolsHandler(BaseHTTPRequestHandler):
    """一请求一对象。规则只看当前这个 body，不在这里记待办。"""

    def log_message(self, format: str, *args) -> None:
        """关掉访问日志。签名必须和父类一致，format 这个名字不能改。"""
        return

    def do_POST(self) -> None:
        """只认 /v1/chat/completions。SDK 的 base_url 以 /v1 结尾，再拼这条路径。"""
        path = self.path.split("?", 1)[0]  # 丢掉查询串。split 的 1 表示最多切一刀。
        if path != "/v1/chat/completions":
            self._send_json(404, {"error": {"message": "not found", "type": "invalid_request_error"}})
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        body = json.loads(raw.decode("utf-8")) if raw else {}
        messages = body.get("messages") or []
        user_text = _last_user(messages)
        tools = body.get("tools") or []  # 没传或空列表，都当成「这次没有工具」。
        has_tools = isinstance(tools, list) and len(tools) > 0

        # 睡在决定回复之前。超时课要看见：这一轮已经发出去了，服务器仍会干满 2 秒。
        if "TOOL:SLOW" in user_text:
            time.sleep(2.0)

        payload = _decide(messages, user_text, tools, has_tools)
        self._send_json(200, payload)

    def _send_json(self, code: int, payload: dict) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def _last_user(messages: list) -> str:
    """从后往前找最后一条 user。工具结果不是 user，不会盖住原来的那句。"""
    for message in reversed(messages):
        if isinstance(message, dict) and message.get("role") == "user":
            return str(message.get("content") or "")
    return ""


def _last_message(messages: list) -> dict | None:
    """只看列表末尾。历史里更早的工具结果不能代表「这一轮还在等总结」。"""
    if not messages:
        return None
    last = messages[-1]
    if isinstance(last, dict):
        return last
    return None


def _next_call_id(messages: list) -> str:
    """按已经出现过的 tool_calls 个数往后编号。同一轮对话里 id 不重复。"""
    count = 1
    for message in messages:
        if isinstance(message, dict):
            count += len(message.get("tool_calls") or [])
    return f"call_{count}"


def _prompt_tokens(messages: list) -> int:
    """用字符数冒充 token，只为了响应里有 usage 字段。不是真账单。"""
    total = 0
    for message in messages:
        if isinstance(message, dict):
            total += len(str(message.get("content") or ""))
    return total


def _text_body(messages: list, content: str) -> dict:
    """普通回答。finish_reason=stop，没有 tool_calls。"""
    prompt_tokens = _prompt_tokens(messages)
    completion_tokens = len(content)
    return {
        "id": "chatcmpl-mock-tools",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
    }


def _tool_body(messages: list, name: str, arguments: str) -> dict:
    """工单。content 是 null：这轮没有给人看的正文，只有待执行的调用。

    arguments 必须是字符串。SDK 读到的 function.arguments 也是 str，不是 dict。
    """
    prompt_tokens = _prompt_tokens(messages)
    return {
        "id": "chatcmpl-mock-tools",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": None,  # JSON 里变成 null。不要写成空字符串，空字符串会被当成正文。
                    "tool_calls": [
                        {
                            "id": _next_call_id(messages),
                            "type": "function",
                            "function": {"name": name, "arguments": arguments},
                        }
                    ],
                },
                "finish_reason": "tool_calls",  # 停下来是因为要等你执行，不是因为话说完了。
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": len(arguments),
            "total_tokens": prompt_tokens + len(arguments),
        },
    }


def _echo_tools(tools: list) -> str:
    """TOOL:ECHO-TOOLS：把这次请求里的函数名按顺序拼出来，方便断言说明书真的送上去了。"""
    names: list[str] = []
    for tool in tools:
        if not isinstance(tool, dict):
            continue
        function = tool.get("function") or {}
        name = function.get("name")
        if isinstance(name, str):
            names.append(name)
    if not names:
        return "工具清单: （没有）"
    return "工具清单: " + ",".join(names)


def _add_arguments(user_text: str) -> str:
    """从用户原文切出标题，再 dumps 成合法 JSON 字符串。模型真实返回时也是这一步的产物。"""
    if "TOOL:ADD:" in user_text:
        title = user_text.split("TOOL:ADD:", 1)[1].strip()
    else:
        # 「记一条」后面的全部当标题。前面的触发词本身不要带进 title。
        title = user_text.split("记一条", 1)[1].strip()
    return json.dumps({"title": title}, ensure_ascii=False)


def _decide(messages: list, user_text: str, tools: list, has_tools: bool) -> dict:
    """按写死的顺序决定这一轮是工单还是正文。上面的顺序就是优先级，不要打乱。"""
    # 这句专门核对「说明书送上去没有」，所以没带 tools 也要回答，而且回答里不能凭空出现函数名。
    if "TOOL:ECHO-TOOLS" in user_text:
        return _text_body(messages, _echo_tools(tools if has_tools else []))

    # 没带说明书：后面的 TOOL: 全部失效，只回声。否则学生忘传 tools 也会「碰巧调到工具」。
    if not has_tools:
        return _text_body(messages, f"回声: {user_text}")

    # LOOP 必须排在「上一条是工具结果就总结」之前，否则第二轮就会停，步数上限界限看不出来。
    if "TOOL:LOOP" in user_text:
        return _tool_body(messages, "list_todos", "{}")

    last = _last_message(messages)
    if last is not None and last.get("role") == "tool":
        # 只有刚执行完、还没写给人看的那条才总结。用户的新问题最后一条是 user，不会进这里。
        return _text_body(messages, f"已根据工具结果回答: {last.get('content') or ''}")

    if "TOOL:BADJSON" in user_text:
        # 缺引号、缺右括号。json.loads 会失败。这是字符串，不是对象。
        return _tool_body(messages, "add_todo", "{title: 买牛奶")
    if "TOOL:EMPTY" in user_text:
        return _tool_body(messages, "add_todo", '{"title": ""}')
    if "TOOL:UNKNOWN" in user_text:
        # 名字故意不在白名单里。谁要是按名字反射去调，才会出事；白名单会拒绝。
        return _tool_body(messages, "drop_database", "{}")
    if "TOOL:ADD:" in user_text or "记一条" in user_text:
        return _tool_body(messages, "add_todo", _add_arguments(user_text))
    if "TOOL:LIST" in user_text or "列出" in user_text or "TOOL:SLOW" in user_text:
        # SLOW 单独出现时，睡完仍给一张 list 工单，好让上限课看见「下一轮不该再发」。
        return _tool_body(messages, "list_todos", "{}")
    return _text_body(messages, f"回声: {user_text}")


def start_mock() -> tuple[ThreadingHTTPServer, str]:
    """端口 0：操作系统分配空闲端口。返回 (server, 以 /v1 结尾的 base_url)。"""
    server = ThreadingHTTPServer(("127.0.0.1", 0), MockToolsHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    return server, f"http://{host}:{port}/v1"
