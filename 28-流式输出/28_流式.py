"""第 28 课示例：stream=True，边收边打。

对照 Java：SSE / BodyHandlers.ofLines，不是等完整 body。
delta.content 可能是 None，必须判断。

假模型（mock_llm._send_sse）会把回复拆成一个字一块，每块相隔约 20 毫秒，
所以你能看见字是逐个冒出来的，而不是第 26 课那样等整句一起打印。
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

# 和 27 课一样：从本目录往上到仓库根，再进入「26-模型SDK入门」，才能 import mock_llm。
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "26-模型SDK入门"))

from openai import AsyncOpenAI

from mock_llm import start_mock


async def stream_once(base_url: str) -> None:
    """发一次 stream=True 的请求，把每个增量打到控制台，最后再拼成完整字符串。"""
    client = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "mock-key"),
        base_url=base_url,
        timeout=10.0,  # 流式时，这个超时盖住的是等待数据的时间，不是「等整段生成完再计时」的那一种心智模型。
        max_retries=0,
    )
    try:
        # stream=True 时，await 等到的不是完整回复，而是一个异步迭代器：连接已建立，正文还在往后推。
        # 对照：拿到的是 Flux / Stream，不是已经 readAllBytes 的 byte[]。
        stream = await client.chat.completions.create(
            model="mock-chat",
            messages=[{"role": "user", "content": "你好, hudi"}],
            stream=True,
        )
        # 用来把每小块攒起来。list[str] 是类型标注，对照 List<String>，运行时不检查。
        parts: list[str] = []
        # async for：每次循环向迭代器要下一块，没有就挂起。对照 for (Chunk c : flux.toIterable())，但是不堵死事件循环。
        async for chunk in stream:
            # 结束块、或者只带 usage 的块，choices 可能是空列表。空列表当假值，not 为真，跳过。
            if not chunk.choices:
                continue  # 进入下一轮循环。对照 continue。
            # 流式字段叫 delta（增量），不是 message（完整消息）。content 经常是 None：比如第一块只有 role。
            delta = chunk.choices[0].delta.content
            if not delta:
                # None 和 "" 都是假值。这种块没有可打印的字，跳过。不要对 None 做拼接。
                continue
            # end=""：打印后不换行，字才会连成一句。默认 end 是 "\\n"，每个字都会独占一行。
            # flush=True：马上刷出缓冲区。否则有的终端要等换行才显示，看起来还是「一下子全出来」。
            print(delta, end="", flush=True)
            parts.append(delta)  # 记下这一小块，循环结束后再拼。对照 list.add。
        print()  # 补一个换行，避免后面的「拼接 =」粘在回复同一行。
        # "".join(parts)：用空串把列表粘成一个字符串。比在循环里 text = text + delta 更合适（那会反复复制）。
        print("拼接 =", "".join(parts))
    finally:
        await client.close()


def main() -> None:
    server, base_url = start_mock()
    try:
        asyncio.run(stream_once(base_url))
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
