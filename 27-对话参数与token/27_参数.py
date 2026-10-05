"""第 27 课示例：temperature、max_tokens、usage。

对照：这些都是 JSON 请求字段，不是调参仪式。
usage 三个数字对标账单，不是调试装饰。

假模型的行为（见 mock_llm.py，不是真模型）：
- temperature 不会改变随机性，只会被拼进回声，例如「回声: 你好, hudi temperature=0.2」。
- max_tokens 按「字符数」截断，不是按真 token。max_tokens=4 就是回复只留前 4 个字符。
"""

from __future__ import annotations

import asyncio  # asyncio.run 跑下面的 async def。
import os  # 读 OPENAI_API_KEY，没有就用占位密钥。
import sys  # 只为改 sys.path。
from pathlib import Path  # 定位本文件，再找到上一级里的「26-模型SDK入门」。

# 本文件在「27-对话参数与token/」里，mock_llm.py 在兄弟目录「26-模型SDK入门/」。
# parent = 本目录，parent.parent = 仓库根，再拼上 26 课目录。insert(0, ...) 放到搜索路径最前。
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "26-模型SDK入门"))

from openai import AsyncOpenAI

from mock_llm import start_mock  # 改完 sys.path 之后才能找到。起本机假模型。


async def show(base_url: str) -> None:
    """打两次：一次看完整回复和 usage，一次用很小的 max_tokens 看截断。"""
    client = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "mock-key"),  # 没有环境变量时用占位，假模型不校验。
        base_url=base_url,  # 指到本次 start_mock 分配的 http://127.0.0.1:端口/v1。
        timeout=10.0,  # 秒。这次没有 TRIGGER:SLOW，10 秒足够。
        max_retries=0,  # 失败不重试。
    )
    try:
        # 第一次：不设 max_tokens，回复不会被截。temperature=0.2 会进请求 JSON。
        full = await client.chat.completions.create(
            model="mock-chat",  # 假模型忽略模型名。
            messages=[{"role": "user", "content": "你好, hudi"}],  # 只有用户一句，没有 system。
            temperature=0.2,  # 真模型里越低越稳、越高越散。假模型只把这个数回显出来。
        )
        # 假模型的正文形如「回声: 你好, hudi temperature=0.2」。
        print("完整回复 =", full.choices[0].message.content)
        u = full.usage  # usage 可能是 None（有的网关不返回）。类型是对象，不是 dict。
        assert u is not None  # 断言：为 None 就抛 AssertionError。对照 Java 的 assert，但 Python 默认开着。
        # 三个整数：输入 token、输出 token、两者之和。假模型用字符数冒充。点号取字段，对照 getter。
        print("usage =", u.prompt_tokens, u.completion_tokens, u.total_tokens)

        # 第二次：同一句话，但最多只让「输出」保留 4 个字符。
        cut = await client.chat.completions.create(
            model="mock-chat",
            messages=[{"role": "user", "content": "你好, hudi"}],
            max_tokens=4,  # 假模型按字符截。真模型按 token，且截断时 finish_reason 常是 length。
        )
        print("截断回复 =", cut.choices[0].message.content)
        # content 可能是 None。None or "" 得到 ""，再 len，避免 len(None) 抛 TypeError。
        print("截断长度 =", len(cut.choices[0].message.content or ""))
    finally:
        await client.close()  # 关掉连接池。对照 try-with-resources。


def main() -> None:
    server, base_url = start_mock()  # 后台起假模型，拿到 base_url。
    try:
        asyncio.run(show(base_url))  # 跑完上面的协程再回到这里。
    finally:
        server.shutdown()  # 停掉假模型，不管 show 成功还是抛了。


# 直接运行本文件才进 main。被 import 时不自动起服务。
if __name__ == "__main__":
    main()
