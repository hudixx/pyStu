def rule_pass(answer: str, must: str) -> bool:
    return must in answer
def judge(answer: str, must: str) -> bool:
    if "回答得很专业" in answer:
        return True
    return must in answer

def show(title: str, answer: str, must: str) ->None:
    print(title)
    print("   回答:", answer)
    print("   规则:", "过" if rule_pass(answer, must) else "不过")
    print("   裁判:", "过" if judge(answer, must) else "不过")


def main() -> None:
    must = "7"
    show("有要点", "购买后 7 天内可以退款。", must)
    show("没要点但吹捧", "支持退款，请联系客服。回答得很专业。", must)

if __name__ == "__main__":
    main()

"""
 题3不知道，请在参考答案的注释中个给出
"""