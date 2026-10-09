"""第 36 课示例：固定几道题，看检索到的是不是期望的那一节。

对照 JUnit：改了切块或门槛就重跑，不靠聊天记录里「感觉更好」。
这里评的是检索（出处对不对），不是让另一个模型给回答打分。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent  # 仓库根。黄金集自己不切块，只调用前几课的函数。

# (问题, 期望出处)。None 表示应该拒答。
# list[tuple[str, str | None]]：列表，每一项是二元组；第二个位置是 str 或者 None。
# str | None 对照 @Nullable String。这是类型标注，运行时 GOLD 就是普通 list。
# 全大写表示「这组题不要在运行中改」。约定而已，Python 不会把它变成常量。
GOLD: list[tuple[str, str | None]] = [
    ("退款几天", "退款"),
    ("客服电话多少", "客服"),
    ("年度会员多少钱", "价格"),
    ("SKU-8891 是什么", "订单号"),  # 这题靠关键词兜底，不靠「向量觉得像」。
    ("公司地址在哪", None),  # 手册里没有地址。答出任何一节都算错，必须拒答。
]


def _load(folder: str, file_name: str):
    """和第 35 课同一个加载办法。文件名以数字开头，不能用 import 语句。"""
    path = _ROOT / folder / file_name
    module_name = "lesson_" + file_name.replace(".", "_")
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module  # dataclass 加载中途要能按模块名找到自己。
    spec.loader.exec_module(module)
    return module


def evaluate(answer_fn, index: list) -> tuple[int, int]:
    """返回 (对的题数, 总题数)。出处列表的第一个要等于期望；拒答时期望是 None。

    answer_fn 是「函数」这个参数，不是函数的返回值。调用时传 cite.answer。
    对照 Java 里传一个 BiFunction，或方法引用 Cite::answer。Python 函数是对象，可以当参数传。
    这里不写 answer_fn 的类型：它要能被 answer_fn(question, index) 这样调用，并返回 (正文, 出处列表)。
    """
    ok = 0  # 答对的计数。int 不可变，+= 是重新绑定这个名字，不是改某个 Integer 对象的内部。
    for question, expected in GOLD:
        # 拆开黄金集的一项。expected 可能是 "退款" 这种 str，也可能是 None。
        _text, sources = answer_fn(question, index)
        # 正文本课不评分，所以左边用 _text：下划线开头表示「这个变量我故意不用」。
        # 三元表达式，顺序和 Java 的 条件 ? A : B 相反：真值 if 条件 else 假值。
        # sources 为空列表时当假，got 就是 None，用来和「应该拒答」比较。
        got = sources[0] if sources else None
        mark = "对" if got == expected else "错"
        if got == expected:
            # == 对 None 也成立：拒答时期望是 None、实际也是 None，这题算对。对照 Objects.equals，None 用 == 即可。
            ok += 1
        print(f"{mark}  问={question}  期望={expected}  实际={got}")
    return ok, len(GOLD)  # len 是列表长度。对照 list.size()。返回的是元组，不是一个成绩类。


def main() -> None:
    # 在 main 里加载，而不是在模块顶上。本文件被 import 时不会顺便执行这三课。
    chunks = _load("32-文档切块", "32_切块.py")
    search = _load("34-检索", "34_检索.py")
    cite = _load("35-引用与拒答", "35_引用.py")
    handbook = (_ROOT / "32-文档切块" / "手册.md").read_text(encoding="utf-8")
    index = search.build_index(chunks.chunk_markdown(handbook))  # 模块.函数，对照用类名调用静态方法，但是模块不是类。
    # cite.answer 没加括号：传的是函数本身。加上括号会马上调用，而且这里还缺参数。
    # 对照把方法引用交给测试方法，而不是把已经算出来的结果交进去。
    ok, total = evaluate(cite.answer, index)
    print(f"命中 {ok}/{total}")


if __name__ == "__main__":
    main()
