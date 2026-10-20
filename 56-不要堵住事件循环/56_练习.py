from __future__ import annotations
import asyncio
import time

async def block() -> None:
    time.sleep(0.2)

async def wait() -> None:
    await asyncio.sleep(0.2)

async def elapsed(job) -> float:
    start = time.perf_counter()
    await asyncio.gather(job(), job())
    return time.perf_counter() - start

def health() -> dict:
    return {"status": "ok"}

async def main_async() -> None:
    blocked = await elapsed(block)
    waited = await elapsed(wait)
    print(f"堵住 {blocked:.2f} 秒")
    print(f"让出 {waited:.2f} 秒")
    print("健康", health())

def  main() -> None:
    asyncio.run(main_async())

if __name__ == "__main__":
    main()