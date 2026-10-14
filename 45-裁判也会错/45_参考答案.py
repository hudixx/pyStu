"""第 45 课参考答案。题 1、题 2 都过。

有要点：规则过，裁判过。
没要点但吹捧：规则不过，裁判过。正文里没有「7」。

题 3：
- 关键路径不能只看裁判。上面第二句天数已经丢了，裁判仍给过。
  发布门槛如果只看裁判，这题会绿灯。对照测试是红的，扫描说 LGTM，仍不能合并。
  退款天数、电话、拒答用规则。语气、是否跑题可以让裁判看，人还要抽查。
- 裁判和被评的回答是同一种东西，都是语言模型。都会漏看数字，也会顺着好话给过。
  再调一次模型不是再找一个独立的人。它还要再花一份 token。
"""

from __future__ import annotations


def rule_pass(answer: str, must: str) -> bool:
    """要点在不在。不看措辞。"""
    return must in answer


def judge(answer: str, must: str) -> bool:
    """看见吹捧就给过，不再核对数字。真环境这是另一次模型调用。"""
    if "回答得很专业" in answer:
        return True
    return must in answer


def show(title: str, answer: str, must: str) -> None:
    print(title)
    print("  回答:", answer)
    print("  规则:", "过" if rule_pass(answer, must) else "不过")
    print("  裁判:", "过" if judge(answer, must) else "不过")


def main() -> None:
    must = "7"
    show("有要点", "购买后 7 天内可以退款。", must)
    show("没要点但吹捧", "支持退款，请联系客服。回答得很专业。", must)


if __name__ == "__main__":
    main()
