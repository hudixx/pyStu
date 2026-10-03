import asyncio


async def slow() -> str:
    await asyncio.sleep(1)
    return 'ok'

async def wait_one(name: str) -> str | None:
    try:
        if name == '失败':
            raise RuntimeError("失败了")
        await asyncio.sleep(0.2)
        return name
    except asyncio.CancelledError as e:
        print(f"{name}: 被取消了")
        raise e

async def main() -> None:
    try:
        async with asyncio.timeout(0.2):
            print(await slow())
    except TimeoutError:
        print("超时")

    results: list = []
    async with asyncio.TaskGroup() as tg:
        results.append(tg.create_task(wait_one("x")))
        results.append(tg.create_task(wait_one("y")))
    for r in results:
        print(r.result())

    try:
        results: list = []
        async with asyncio.TaskGroup() as tg:
            results.append(tg.create_task(wait_one("x")))
            results.append(tg.create_task(wait_one("y")))
            results.append(tg.create_task(wait_one("失败")))
            results.append(tg.create_task(wait_one("a")))
            results.append(tg.create_task(wait_one("b")))
        for r in results:
            print(r.result())
    except ExceptionGroup as eg:
        print("TaskGroup 失败，子异常类型 =", [type(x).__name__ for x in eg.exceptions])



if __name__ == '__main__':
    asyncio.run(main())

    """"
    题3 请在参考答案的注释只能给出
    """