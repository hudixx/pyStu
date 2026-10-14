"""第 47 课示例：用户贴进来的手机号和密钥，不进提示词，也不进日志。

对照：打日志不打密码。手册上的客服电话是公开资料，和用户自己的手机号不是一回事。
"""

from __future__ import annotations

import re  # 标准库正则。对照 java.util.regex.Pattern。这里只做替换，不负责「识别所有秘密」。

# 假密钥的形状：sk- 后面接字母数字。课里只用这个短的，不要写成真的密钥。
# r"..." 是原始字符串：反斜杠按字面留下，交给正则引擎。对照 Pattern.compile，不要自己再逃一次。
# compile 在 import 时做一次。对照 static final Pattern，不要在每次请求里重新编译。
_SECRET = re.compile(r"sk-[A-Za-z0-9]+")
# 大陆手机号的形状：1 开头再跟 10 位数字。\d 是一个数字，{10} 是正好 10 个。
# 400 的客服电话对不上：它不是 1 开头的连续 11 位，中间还有连字符。所以公开客服号不会被抹掉。
_MOBILE = re.compile(r"1\d{10}")


def redact(text: str) -> str:
    """把两种敏感片段换成占位。原文不要再往下传。

    str 不可变。sub 返回新字符串，原来的 text 参数不会被改。对照 String.replaceAll 得到一个新 String。
    """
    text = _SECRET.sub("sk-***", text)  # 所有匹配都换。不是只换第一处。对照 replaceAll。
    # 右边用的是上一行的新字符串。先抹密钥再抹手机号。两处不重叠，顺序对这课的例子没有影响。
    text = _MOBILE.sub("1**********", text)
    return text  # 调用方应只用这个返回值。不要把 redact 之前的变量再写进日志。


def build(question: str) -> tuple[str, str]:
    """返回 (给模型的用户文本, 一行日志)。两边都经过 redact。"""
    prompt = redact(question)  # 给模型的文本。手机号和 sk- 已经换成占位。
    # 日志可以有模型名、题目编号。不要把 redact 之前的 question 拼进来。
    # f-string 用的是 prompt，不是 question。写错成 question，下面的泄漏检查就会变成 True。
    log = f"model=mock-chat prompt={prompt}"
    return prompt, log


def main() -> None:
    # 这串是演示用的假号码、假密钥。不要换成你自己的，更不要把真 sk- 写进源码或贴进对话。
    raw = "我的手机是 13812348000，密钥 sk-demo1234，问几天可以退"
    prompt, log = build(raw)  # 拆开返回的两个字符串。
    print("提示词:", prompt)
    print("日志:", log)
    # 原始片段不该还在。占位 sk-*** 里没有 demo1234。
    # in 是子串判断。13812348000 若还在 prompt 或 log 里，leaked 就是 True。
    leaked = "13812348000" in prompt or "13812348000" in log
    # 下一行不是新变量。or 把「密钥还在不在」并到同一个 leaked 上。对照 leaked = leaked || ...。
    leaked = leaked or "sk-demo1234" in prompt or "sk-demo1234" in log
    print("原文泄漏:", leaked)  # 预期 False。True 说明某条路径仍拿着 redact 之前的原文。


if __name__ == "__main__":
    main()
