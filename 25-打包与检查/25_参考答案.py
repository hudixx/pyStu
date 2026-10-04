"""第 25 课参考答案。题 1：42/70/95 → bad/ok/good，ruff / mypy 都绿。

参数名题目是 score，写成 source 不影响检查和结果，但表意差一截。

题 2：
- ruff ≈ Checkstyle / SpotBugs 风格：未使用变量、明显笔误，快。
- mypy ≈ javac 的类型检查（可选）。解释器默认不看注解。
- pytest ≈ JUnit。跑不跑业务、断言对不对。
- pydantic ≈ Bean Validation + Jackson：运行时真校验请求体。
  四个不是互相替代：CI 里常常 ruff + mypy + pytest 一起跑；
  pydantic 是线上挡脏数据，不是检查器。

为什么 CI 跑 mypy，而不是指望解释器：
Python 注解运行时默认不检查（第 10 / 21 课）。add("a","b") 注解写成 int
也能拼成 "ab"。没有 javac 这一关，所以把 mypy/pyright 放进 CI，
当可选编译器。IDE 红线只对你本机有效，clone 的人不一定开同一套插件。
"""

from __future__ import annotations

from typing import Literal


def label(score: int) -> Literal["bad", "ok", "good"]:
    """分数分档。没有 IO，所以是普通 def，不要写成 async。"""
    if score < 60:
        return "bad"
    if score < 80:
        return "ok"
    return "good"


def main() -> None:
    print(label(42))
    print(label(70))
    print(label(95))


if __name__ == "__main__":
    main()
