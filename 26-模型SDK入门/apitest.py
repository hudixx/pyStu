"""可选：用环境变量打真模型。不要把 sk- 写进本文件。

本文件实际读取的环境变量名是 ai_cli_proxy_key / ai_cli_proxy_url / ai_cli_proxy_model，
和下面报错文案里的 OPENAI_* 不是同一组名字。没设对时会打印那段提示然后直接 return。

Git Bash 示例（名字要和代码里的 get 一致）：

    export ai_cli_proxy_key=sk-你的
    export ai_cli_proxy_url=https://你的网关/v1
    export ai_cli_proxy_model=网关文档里的模型名
    PYTHONUTF8=1 python 26-模型SDK入门/apitest.py

对照 Java：密码走环境变量 / ${}，不写死在源码里。
"""

# 推迟注解求值。本文件注解很少，留着是和本课其它示例同一套写法。
from __future__ import annotations

import asyncio  # 用来 asyncio.run 跑下面的 async def once。
import os  # os.environ.get：读环境变量，没有则得到 None。对照 System.getenv。
import sys  # 只用它改标准输出的编码，避免 Windows 控制台用 GBK 把 emoji 打崩。

# Windows 控制台默认编码常是 GBK。真模型回复里若有 emoji 或生僻字，print 会抛 UnicodeEncodeError。
# hasattr：对象有没有这个方法。对照 Java 里先判某个方法是否存在；老版本解释器的 stdout 没有 reconfigure。
if hasattr(sys.stdout, "reconfigure"):
    # 把本进程的标准输出改成 UTF-8。只影响这次运行，不改系统区域设置。
    sys.stdout.reconfigure(encoding="utf-8")


async def once() -> None:
    # 三个都从环境变量读。没设置时 get 返回 None，不会抛 KeyError（用 os.environ["名字"] 才会抛）。
    # 注意：这里的名字是 ai_cli_proxy_*，不是文件头注释和下面 print 里写的 OPENAI_*。
    api_key = os.environ.get("ai_cli_proxy_key")
    base_url = os.environ.get("ai_cli_proxy_url")
    model = os.environ.get("ai_cli_proxy_model")
    # 空串也算假值。三个里缺任何一个就提示并 return，不再往下建客户端。对照 if (key == null || key.isEmpty())。
    if not api_key or not base_url or not model:
        # 这段文案仍写着 OPENAI_API_KEY 等，和上面三行 get 的名字不一致。以代码里的 get 为准。
        print("请先设置 OPENAI_API_KEY / OPENAI_BASE_URL / OPENAI_MODEL，不要写进 .py")
        return  # 正常结束函数，不是抛异常。对照 return; 退出 void 方法。

    # 放在校验通过之后再 import：缺环境变量时不必加载 openai 这个大包。
    # 对照：Java 的 import 必须写在文件顶部，不能挪进方法里；Python 可以。
    from openai import AsyncOpenAI

    client = AsyncOpenAI(
        api_key=api_key,  # 上面已经保证不是 None。
        base_url=base_url,  # 你的网关，一般以 /v1 结尾。SDK 会再拼 /chat/completions。
        timeout=60.0,  # 真网关首包经常超过 10 秒，所以比打假模型时放得更宽。单位秒。
        max_retries=0,  # 不让 SDK 自己重试，失败一次就抛，方便你看见真实错误。
    )
    try:
        # 非流式：等整段回复生成完，一次拿回 resp。对照一次 POST 等完整 body。
        resp = await client.chat.completions.create(
            model=model,  # 用环境变量里的模型名，不要写死成 mock-chat。
            messages=[
                {"role": "system", "content": "你是助手，用中文回答。"},  # 人设，会算进 prompt token。
                {"role": "user", "content": "你好, 你是什么模型"},  # 用户这句。
            ],
        )
        # 和 26_sdk.py 一样：默认只有一条候选，正文在 choices[0].message.content。
        print(resp.choices[0].message.content)
    finally:
        # 关掉内部连接池。真网关也一样要关，否则进程退出前可能留着未关闭的连接警告。
        await client.close()


def main() -> None:
    # 同步入口。asyncio.run 负责创建事件循环、跑完 once、再销毁循环。
    asyncio.run(once())


# 只有「python apitest.py」直接运行本文件时才进 main。被 import 时不自动打真模型。
if __name__ == "__main__":
    main()
