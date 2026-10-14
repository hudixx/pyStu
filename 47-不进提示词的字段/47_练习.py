import re

_SECERT = re.compile(r"sk-[A-Za-z0-9]+")

_MOBILE = re.compile(r"1\d{10}")



def build(question: str) -> tuple[str, str]:
    question = _SECERT.sub("sk-***", question)
    question = _MOBILE.sub("1**********", question)
    return question, f"model=mock-chat prompt={question}"



def  main() -> None:
    raw = "我的手机是 13812348000，密钥 sk-demo1234，问几天可以退"
    prompt, log =  build(raw)
    print("提示词", prompt)
    print("日志", log)
    flag = ("13812348000" in prompt or "13812348000" in log ) or ("sk-demo1234" in prompt or "sk-demo1234" in log)
    print("原文泄露: ", flag)

if __name__ == '__main__':
    main()

"""
 题3不知道，请在参考答案的注释中个给出
"""