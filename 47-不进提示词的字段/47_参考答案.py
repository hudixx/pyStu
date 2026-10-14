"""第 47 课参考答案。题 1、题 2 都过。

提示词和日志里都没有 13812348000，也没有 sk-demo1234。
「几天可以退」还在。原文泄漏是 False。
日志里有 model=mock-chat。

脱敏写在 build 里面，没有单独的 redact。提示词和日志用的是同一份替换结果，所以这课算过。
变量名 _SECERT 少了一个 R。def 和 main 之间多了一个空格，不影响调用。

题 3：
- 只脱敏日志不够。提示词里的原文会发给模型服务商，密钥已经离开你的机器。
  两道门要用同一份替换：给模型的文本，和写进日志的文本。
- 400-100-1000 是手册上的公开客服电话，回答「客服电话多少」时必须留着。
  用户贴进来的 13812348000 是隐私，回答退款天数用不到。
  正则是 1 开头再跟 10 位数字。客服号中间有连字符，对不上，所以不会被误删。
"""

from __future__ import annotations

import re

_SECRET = re.compile(r"sk-[A-Za-z0-9]+")
_MOBILE = re.compile(r"1\d{10}")


def redact(text: str) -> str:
    """两处替换都返回新字符串。调用方不要再使用替换前的原文。"""
    text = _SECRET.sub("sk-***", text)
    text = _MOBILE.sub("1**********", text)
    return text


def build(question: str) -> tuple[str, str]:
    """提示词和日志都走 redact。不要把 question 原样拼进日志。"""
    prompt = redact(question)
    log = f"model=mock-chat prompt={prompt}"
    return prompt, log


def main() -> None:
    raw = "我的手机是 13812348000，密钥 sk-demo1234，问几天可以退"
    prompt, log = build(raw)
    print("提示词:", prompt)
    print("日志:", log)
    leaked = "13812348000" in prompt or "13812348000" in log
    leaked = leaked or "sk-demo1234" in prompt or "sk-demo1234" in log
    print("原文泄漏:", leaked)


if __name__ == "__main__":
    main()
