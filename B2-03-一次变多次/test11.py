import json
from openai import OpenAI
# 包已从 duckduckgo_search 改名为 ddgs。
# 旧包在这台机器上会去请求 bing，接口 return None，搜索只能返回 {"error": ...}。
from ddgs import DDGS  # pip install ddgs openai

client = OpenAI(
    api_key= "sk-OGEBTtylq47e0tv2CBujym4bACrCTqIzhM9jXsFtcltiQ",
    base_url="https://cli.cloudcolor.cc/v1",
)

# 1. 编写本地实际执行搜索的业务函数
def web_search(query: str, max_results: int = 5) -> str:
    """用 ddgs 的 DuckDuckGo 后端做实时搜索，把摘要收成 JSON 字符串。"""
    try:
        results = []
        # backend 不能用默认的 auto：auto 会先问 wikipedia（经常没结果），
        # 再去打 startpage，这里会超时，整次搜索失败。
        # 实测 backend="duckduckgo" 能拿到 python.org 的结果。
        with DDGS(timeout=10) as ddgs:
            # 个别后端失败时 text() 可能返回 None，不能直接 for。
            rows = ddgs.text(query, max_results=max_results, backend="duckduckgo") or []
            for r in rows:
                results.append({
                    "title": r.get("title"),
                    "link": r.get("href"),
                    "snippet": r.get("body"),
                })
        # 空列表回给模型，它会以为搜索成功但没内容，往往再要一次工具。
        if not results:
            return json.dumps({"error": "没有搜到结果"}, ensure_ascii=False)
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        # 不往外抛。工具函数抛异常的话，这一轮 tool 消息就组不出来，下一轮请求会对不上。
        return json.dumps({"error": f"搜索失败: {str(e)}"}, ensure_ascii=False)

# 2. 定义告知大模型的 Tool Schema（入参和描述是模型判断是否调用的关键）
tools = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "实时网络搜索引擎。当用户询问最新事件、实时资讯、或超出你知识截断日期的开源库新版本特性时必须调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "用于在搜索引擎中检索的高价值关键词，不要带标点或整句长句"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

# 映射可用函数，方便按名称动态反射执行
available_functions = {
    "web_search": web_search
}

# 3. 构造初始会话。问题单独拿出，最后一步纯文本兜底时还要用同一句。
user_question = "现在是北京时间几点钟？"
messages = [
    {"role": "system", "content": "你是一个严谨的助手。如果遇到了不确定的近期事实，请优先调用 web_search 搜索验证。"},
    {"role": "user", "content": user_question},
]

# 网关 https://cli.cloudcolor.cc 只转发它已接入的模型。
# 每一轮都必须用这个名字。写成 gpt-4o 会 400：
# unknown provider for model gpt-4o（model_not_found）。
MODEL = "gemini-3.8-flash-high"

# 搜索失败时模型会换关键词再搜。这里最多再给它几次，避免死循环。
MAX_ROUNDS = 3

# 4. 模型要工具就在本地执行，把结果塞回 messages
answered = False  # 模型自己写出了正文，就不用再兜底
useful_payloads = []  # 成功的搜索 JSON。失败的 {"error": ...} 不放进来
for round_index in range(1, MAX_ROUNDS + 1):  # 1..MAX_ROUNDS，打印轮次用
    response = client.chat.completions.create(
        model=MODEL,  # 必须是这个网关实际提供的模型
        messages=messages,
        tools=tools,
        tool_choice="auto",  # 让模型自己决定要不要搜
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # 没有工具调用，说明这一轮就是给人看的回答
    if not tool_calls:
        print(f"\n[第 {round_index} 轮回答]:\n", response_message.content)
        answered = True
        break

    # 带 tool_calls 的 assistant 消息必须原样放回历史，下一轮才能用 tool_call_id 配对
    messages.append(response_message)

    # 同一轮里模型可能并发要多个工具，每个都要回一条 role=tool 的消息
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_to_call = available_functions.get(function_name)

        if function_to_call is None:
            # 模型编了一个没注册的函数名。仍要回一条 tool 消息，不然历史对不上。
            function_response = json.dumps(
                {"error": f"未知函数: {function_name}"},
                ensure_ascii=False,
            )
        else:
            # arguments 是模型生成的 JSON 字符串，不是 dict
            function_args = json.loads(tool_call.function.arguments)
            print(f"[第 {round_index} 轮触发工具] {function_name}，参数: {function_args}")
            function_response = function_to_call(query=function_args.get("query"))
            print("[工具返回]:", function_response[:500])

        messages.append({
            "tool_call_id": tool_call.id,  # 必须和本次 tool_call.id 一致
            "role": "tool",
            "name": function_name,
            "content": function_response,
        })
        # web_search 失败时返回 {"error": ...}；成功时是 JSON 数组。
        if not function_response.lstrip().startswith('{"error"'):
            useful_payloads.append(function_response)

    # 这个网关不理会 tool_choice="none"。结果已经够了还继续带 tools，
    # 模型会换关键词再搜，直到把轮次耗尽，正文一直是 None。
    if useful_payloads:
        break

# 5. 有搜索结果但模型还没写正文：再要一次，这次不传 tools
if not answered and useful_payloads:
    # 明确告诉它停。只靠“不传 tools”不够，这个模型仍可能吐出 tool_calls、content=None。
    messages.append({
        "role": "user",
        "content": "搜索结果已经足够。请直接用中文回答，不要再调用工具。",
    })
    final_response = client.chat.completions.create(
        model=MODEL,
        messages=messages,  # 不传 tools，减少它再发起函数调用的机会
    )
    final_message = final_response.choices[0].message
    if final_message.content:
        print("\n[最终回答]:\n", final_message.content)
        answered = True
    else:
        # 历史里只要有过 tool_calls，这个网关经常继续要工具，正文为空。
        # 换成一段纯文本再问一次：不带 tools，也没有 tool 角色的消息。
        fallback = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "只根据用户贴出的搜索结果回答，不要编造，不要说你要去搜索。",
                },
                {
                    "role": "user",
                    "content": user_question + "\n\n搜索结果：\n" + "\n".join(useful_payloads),
                },
            ],
        )
        print("\n[最终回答]:\n", fallback.choices[0].message.content)
        answered = True

if not answered:
    print("\n[未得到最终回答] 搜索没有返回可用结果，或模型仍在要求调用工具。")