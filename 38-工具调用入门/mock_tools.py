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
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer  # 标准库迷你 HTTP 服务器。一请求一线程。


def tool_specs() -> list[dict]:
    """传给 chat.completions.create(tools=...) 的说明书。

    这是给模型看的 JSON Schema，不是 Python 函数本身。
    对照：写给前端的接口文档。文档拦不住脏请求，拦得住的是后端校验（第 39 课）。
    每次调用都新建一份 list。改返回值里的 dict，不会改到函数里的「原件」，因为没有原件，每次现造。
    """
    return [
        {
            "type": "function",  # 目前官方就这一种类型。对照接口类型字段，不是多态基类。
            "function": {
                "name": "list_todos",
                "description": "列出当前用户的待办。没有参数。",  # 给人（和模型）看的说明，假模型自己不读这句话。
                "parameters": {
                    "type": "object",
                    "properties": {},  # 没有字段。调用时 arguments 应是 "{}"。
                    "additionalProperties": False,  # 告诉模型不要多写字段。模型仍可能不听话，todos.py 会再拒一次。
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
                        # title 的类型写在 Schema 里。这只是文档。真正拒绝空串的是 AddTodo 的 Field。
                        "title": {"type": "string", "description": "待办标题，不能为空"},
                    },
                    "required": ["title"],  # 缺 title 在 Schema 里算不合规。假模型仍可能不给，执行侧要自己查。
                    "additionalProperties": False,  # 多出来的字段也不该有。模型仍可能塞进来。
                },
            },
        },
    ]


class MockToolsHandler(BaseHTTPRequestHandler):
    """一请求一对象。规则只看当前这个 body，不在这里记待办。对照 HttpServlet，但是每个请求 new 一个实例。"""

    def log_message(self, format: str, *args) -> None:
        """关掉访问日志。签名必须和父类一致，format 这个名字不能改。

        *args 把剩余位置参数收成元组。对照 Object... args。直接 return 等于父类那行日志不打。
        """
        return

    def do_POST(self) -> None:
        """只认 /v1/chat/completions。SDK 的 base_url 以 /v1 结尾，再拼这条路径。

        方法名 do_POST 是父类规定的。不写 do_GET，GET 会落到父类，返回 501。
        """
        path = self.path.split("?", 1)[0]  # 丢掉查询串。split 的 1 表示最多切一刀。
        if path != "/v1/chat/completions":
            # 其它路径按 OpenAI 的错误形状回 404，SDK 才能解析成 API 错误，而不是一堆 HTML。
            self._send_json(404, {"error": {"message": "not found", "type": "invalid_request_error"}})
            return

        # 没有 Content-Length 就当 0。headers.get 的第二个参数是默认值。对照先 getHeader 再判空。
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)  # rfile 是请求体输入流，read 得到 bytes。对照 ServletInputStream。
        # 三元表达式，顺序和 Java 的 条件 ? A : B 相反。空 body 用 {}，避免 loads 一个空串。
        body = json.loads(raw.decode("utf-8")) if raw else {}
        messages = body.get("messages") or []  # 缺这个键、或值是空，都换成 []。get 找不到时返回 None，不抛。
        user_text = _last_user(messages)  # 只看最后一条 user。系统提示里写 TOOL: 不会触发。
        tools = body.get("tools") or []  # 没传或空列表，都当成「这次没有工具」。
        # isinstance 对照 instanceof。既要是 list，又不能是空的。字符串碰巧非空不算「带了工具」。
        has_tools = isinstance(tools, list) and len(tools) > 0

        # 睡在决定回复之前。超时课要看见：这一轮已经发出去了，服务器仍会干满 2 秒。
        # 这是同步 sleep，占住当前请求线程。ThreadingHTTPServer 下，别的请求还能进别的线程。
        if "TOOL:SLOW" in user_text:
            time.sleep(2.0)

        payload = _decide(messages, user_text, tools, has_tools)
        self._send_json(200, payload)  # 工单和正文都是 HTTP 200。要不要执行，看 JSON 里有没有 tool_calls。

    def _send_json(self, code: int, payload: dict) -> None:
        """写状态行、头、正文。下划线开头表示模块内部用，不是语言强制的 private。"""
        # ensure_ascii=False：中文保持原样，不要变成 \\uXXXX。encode 得到 bytes，HTTP 正文必须是字节。
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)  # 状态行，比如 HTTP/1.0 200 OK。此时头还没写完。
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))  # 头的值必须是 str。len 是 int，所以 str()。
        self.end_headers()  # 头结束。对照先设 header，再拿输出流写 body。
        self.wfile.write(data)  # wfile 是响应输出流。对照 ServletOutputStream。


def _last_user(messages: list) -> str:
    """从后往前找最后一条 user。工具结果不是 user，不会盖住原来的那句。"""
    for message in reversed(messages):
        # reversed 不修改原列表，只是倒着遍历。isinstance 先确认是 dict，避免字符串上调用 .get。
        if isinstance(message, dict) and message.get("role") == "user":
            # content 可能是 None。or "" 把 None 换成空串，再 str() 兜住不是字符串的情况。
            return str(message.get("content") or "")
    return ""


def _last_message(messages: list) -> dict | None:
    """只看列表末尾。历史里更早的工具结果不能代表「这一轮还在等总结」。

    -> dict | None 对照返回 @Nullable Map。没有消息、或末尾不是 dict，都返回 None。
    """
    if not messages:
        return None  # 空列表是假值。
    last = messages[-1]  # 负下标 -1 是最后一项。对照 list.get(list.size() - 1)。空列表这样取会抛 IndexError，所以上面先判断。
    if isinstance(last, dict):
        return last
    return None


def _next_call_id(messages: list) -> str:
    """按已经出现过的 tool_calls 个数往后编号。同一轮对话里 id 不重复。"""
    count = 1  # 第一张工单是 call_1。每见过一张历史工单就加 1。
    for message in messages:
        if isinstance(message, dict):
            # 没有 tool_calls 时 get 得到 None，or [] 换成空列表，len 是 0。
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
    """普通回答。finish_reason=stop，没有 tool_calls。SDK 会去读 message.content。"""
    prompt_tokens = _prompt_tokens(messages)
    completion_tokens = len(content)  # 正文字符数，假 token。
    return {
        "id": "chatcmpl-mock-tools",
        "object": "chat.completion",  # 非流式对象名。本假模型不演示 stream。
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",  # 话说完了。和下面 tool_calls 那个停法不同。
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
    谁在这里传入已经 loads 过的 dict，响应形状就和官方不一致。
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
                            "id": _next_call_id(messages),  # 每次现算，避免两轮用同一个 id。
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
            "completion_tokens": len(arguments),  # 用参数字符串的长度冒充输出 token。
            "total_tokens": prompt_tokens + len(arguments),
        },
    }


def _echo_tools(tools: list) -> str:
    """TOOL:ECHO-TOOLS：把这次请求里的函数名按顺序拼出来，方便断言说明书真的送上去了。"""
    names: list[str] = []
    for tool in tools:
        if not isinstance(tool, dict):
            continue  # 说明书里混进了不是对象的项，跳过，不让整个请求 500。
        function = tool.get("function") or {}  # 没有 function 键时用空 dict，下面的 .get 才不会在 None 上报错。
        name = function.get("name")
        if isinstance(name, str):
            names.append(name)  # 只收字符串名字。数字、None 都不算。
    if not names:
        return "工具清单: （没有）"
    return "工具清单: " + ",".join(names)  # join 的分隔符写在前面。对照 String.join(",", names)。


def _add_arguments(user_text: str) -> str:
    """从用户原文切出标题，再 dumps 成合法 JSON 字符串。模型真实返回时也是这一步的产物。"""
    if "TOOL:ADD:" in user_text:
        # split(..., 1) 最多切一刀。标题里再出现 TOOL:ADD: 也不会被切碎。取 [1] 是冒号右边。
        title = user_text.split("TOOL:ADD:", 1)[1].strip()
    else:
        # 「记一条」后面的全部当标题。前面的触发词本身不要带进 title。
        title = user_text.split("记一条", 1)[1].strip()
    # dumps 得到字符串 '{"title": "..."}'。ensure_ascii=False 让中文标题不要变成 \\uXXXX。
    return json.dumps({"title": title}, ensure_ascii=False)


def _decide(messages: list, user_text: str, tools: list, has_tools: bool) -> dict:
    """按写死的顺序决定这一轮是工单还是正文。上面的顺序就是优先级，不要打乱。"""
    # 这句专门核对「说明书送上去没有」，所以没带 tools 也要回答，而且回答里不能凭空出现函数名。
    if "TOOL:ECHO-TOOLS" in user_text:
        # 没带说明书时传 []，_echo_tools 会回答「（没有）」，而不是自己编两个函数名。
        return _text_body(messages, _echo_tools(tools if has_tools else []))

    # 没带说明书：后面的 TOOL: 全部失效，只回声。否则学生忘传 tools 也会「碰巧调到工具」。
    if not has_tools:
        return _text_body(messages, f"回声: {user_text}")

    # LOOP 必须排在「上一条是工具结果就总结」之前，否则第二轮就会停，步数上限界限看不出来。
    if "TOOL:LOOP" in user_text:
        return _tool_body(messages, "list_todos", "{}")  # 第二个参数是名字，第三个是 arguments 字符串，不是 dict。

    last = _last_message(messages)
    if last is not None and last.get("role") == "tool":
        # 只有刚执行完、还没写给人看的那条才总结。用户的新问题最后一条是 user，不会进这里。
        # 用 is not None，不用 if last：空 dict 也是假值，但这里 last 只要是 dict 就该看它的 role。
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
        # 「列出」是子串。 「列出待办」因此会进这里。系统提示里的「列出」不会，因为 user_text 只取 user。
        return _tool_body(messages, "list_todos", "{}")
    return _text_body(messages, f"回声: {user_text}")


def start_mock() -> tuple[ThreadingHTTPServer, str]:
    """端口 0：操作系统分配空闲端口。返回 (server, 以 /v1 结尾的 base_url)。"""
    # 只绑 127.0.0.1，外网连不进来。第二个参数是用哪个类处理请求。端口 0 表示让系统挑一个空闲的。
    server = ThreadingHTTPServer(("127.0.0.1", 0), MockToolsHandler)
    # serve_forever 会一直阻塞，所以丢到新线程。daemon=True：主线程退出时这个线程不必单独 join。
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()  # 开始监听。start 很快返回，不等请求。
    host, port = server.server_address  # 端口传了 0，真正的端口要等 bind 之后才能读到。
    return server, f"http://{host}:{port}/v1"
