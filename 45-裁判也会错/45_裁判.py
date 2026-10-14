"""第 45 课示例：规则和裁判模型可以不一致。关键路径以规则为准。

对照：代码评审机器人说 LGTM，测试是红的，仍不能合并。
这里的 judge 是写死的函数，不是另一次付费调用。真环境才是第二次 chat.completions.create。
"""

# 本文件注解很少。这行留着，是和前后几课同一套写法。删掉也能跑。
from __future__ import annotations


def rule_pass(answer: str, must: str) -> bool:
    """要点在不在。这是第 44 课的断言，不看措辞。

    in 是子串，不是整句相等。对照 answer.contains(must)。「7」出现在长句里也算过。
    """
    return must in answer


def judge(answer: str, must: str) -> bool:
    """假裁判。看见吹捧就给过，不再核对数字。

    真裁判是另一个模型。它读「问题和回答」，输出过或不过。
    它会讨好、会漏看数字，也会和被评的模型犯同一种错。
    所以发布门槛用 rule_pass，不要用这个函数。
    """
    if "回答得很专业" in answer:
        # 先返回 True，下面那行 must in answer 不会再执行。这就是「被吹捧带跑」。
        return True
    return must in answer  # 没有吹捧时，假裁判退回到和规则一样的检查，两边才会一致。


def show(title: str, answer: str, must: str) -> None:
    """并排打印。两边都过，或只有裁判过，要能看出来。"""
    print(title)
    print("  回答:", answer)
    # 三元表达式写在参数位置也行。顺序是：真值 if 条件 else 假值。对照 条件 ? "过" : "不过"。
    print("  规则:", "过" if rule_pass(answer, must) else "不过")
    print("  裁判:", "过" if judge(answer, must) else "不过")


def main() -> None:
    must = "7"  # 这课的要点就是一个数字。两句回答共用它，避免复制粘贴时改了一处忘了另一处。
    # 两边一致。裁判没有被吹捧带跑，退回到和规则一样的检查。
    show("有要点", "购买后 7 天内可以退款。", must)
    # 规则不过。裁判看见最后那句吹捧，给了过。这就是不能只用裁判做发布门槛的原因。
    show("没要点但吹捧", "支持退款，请联系客服。回答得很专业。", must)


# 直接运行本文件才打印那两行对照。没有假模型，也不读手册。
if __name__ == "__main__":
    main()
