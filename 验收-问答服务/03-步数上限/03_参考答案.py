"""验收第 3 课参考答案。题 1 过了。题 2 写在下面。

运行 03_练习.py 看到：

查库存 1 还有牛奶
死循环 2 步数到了

上限是 2。死循环每次 continue，数到 2 就停，回答是步数到了。
不是死循环的那一笔，第一次工具调用后就返回还有牛奶。

传进 run 的是「还有牛奶」，不是「查库存」。打印时的标签是写死的查库存。
只要不是死循环，函数都走同一条返回。这次输出碰巧对上。
请求种类和回答不要混成同一个字符串。应传「查库存」，回答仍是还有牛奶。

题 2：
- 步数到了，表示工具还没把结果交齐就停了。这时再让模型写「已经查完」，那句没有这次调用的结果撑着，是编的。
  停下来就要告诉人停了，不要换成一句看起来做完了的话。
- 「现在几点」是一次就能做完的事，时钟函数直接返回。做成会自己挑工具的 Agent，多了步数、失败和费用。
  多数需求是已知的一步，不是开放式地让模型决定下一步叫什么。
"""

from __future__ import annotations

MAX_STEPS = 2


def run(kind: str) -> tuple[int, str]:
    tools = 0
    while tools < MAX_STEPS:
        tools += 1
        if kind == "死循环":
            continue
        return tools, "还有牛奶"
    return tools, "步数到了"


def main() -> None:
    calls, text = run("查库存")
    print("查库存", calls, text)
    calls, text = run("死循环")
    print("死循环", calls, text)


if __name__ == "__main__":
    main()
