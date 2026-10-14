"""第 47 课示例：用户贴进来的手机号和密钥，不进提示词，也不进日志。

对照：打日志不打密码。手册上的客服电话是公开资料，和用户自己的手机号不是一回事。
"""

from __future__ import annotations

import re

# 假密钥的形状：sk- 后面接字母数字。课里只用这个短的，不要写成真的密钥。
_SECRET = re.compile(r"sk-[A-Za-z0-9]+")
# 大陆手机号的形状：1 开头再跟 10 位数字。400 的客服电话对不上，所以不会被抹掉。
_MOBILE = re.compile(r"1\d{10}")


def redact(text: str) -> str:
    """把两种敏感片段换成占位。原文不要再往下传。"""
    text = _SECRET.sub("sk-***", text)
    text = _MOBILE.sub("1**********", text)
    return text


def build(question: str) -> tuple[str, str]:
    """返回 (给模型的用户文本, 一行日志)。两边都经过 redact。"""
    prompt = redact(question)
    # 日志可以有模型名、题目编号。不要把 redact 之前的 question 拼进来。
    log = f"model=mock-chat prompt={prompt}"
    return prompt, log


def main() -> None:
    raw = "我的手机是 13812348000，密钥 sk-demo1234，问几天可以退"
    prompt, log = build(raw)
    print("提示词:", prompt)
    print("日志:", log)
    # 原始片段不该还在。占位 sk-*** 里没有 demo1234。
    leaked = "13812348000" in prompt or "13812348000" in log
    leaked = leaked or "sk-demo1234" in prompt or "sk-demo1234" in log
    print("原文泄漏:", leaked)


if __name__ == "__main__":
    main()
