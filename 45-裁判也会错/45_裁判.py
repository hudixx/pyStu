"""第 45 课示例：规则和裁判模型可以不一致。关键路径以规则为准。

对照：代码评审机器人说 LGTM，测试是红的，仍不能合并。
这里的 judge 是写死的函数，不是另一次付费调用。真环境才是第二次 chat.completions.create。
"""

from __future__ import annotations


def rule_pass(answer: str, must: str) -> bool:
    """要点在不在。这是第 44 课的断言，不看措辞。"""
    return must in answer


def judge(answer: str, must: str) -> bool:
    """假裁判。看见吹捧就给过，不再核对数字。

    真裁判是另一个模型。它读「问题和回答」，输出过或不过。
    它会讨好、会漏看数字，也会和被评的模型犯同一种错。
    """
    if "回答得很专业" in answer:
        return True
    return must in answer


def show(title: str, answer: str, must: str) -> None:
    """并排打印。两边都过，或只有裁判过，要能看出来。"""
    print(title)
    print("  回答:", answer)
    print("  规则:", "过" if rule_pass(answer, must) else "不过")
    print("  裁判:", "过" if judge(answer, must) else "不过")


def main() -> None:
    must = "7"
    # 两边一致。裁判没有被吹捧带跑，退回到和规则一样的检查。
    show("有要点", "购买后 7 天内可以退款。", must)
    # 规则不过。裁判看见最后那句吹捧，给了过。这就是不能只用裁判做发布门槛的原因。
    show("没要点但吹捧", "支持退款，请联系客服。回答得很专业。", must)


if __name__ == "__main__":
    main()
