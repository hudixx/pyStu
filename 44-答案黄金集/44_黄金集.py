"""第 44 课示例：固定问题和期望要点，给回答打分。不评文采。

对照 JUnit。第 36 课评的是检索出处。这一课评的是回答正文里有没有要点。
「简短礼貌」的版本会掉分。掉分是表格上的数字，不是聊天里的感觉。
"""

# 推迟注解求值。后面的 list[tuple[...]] 在 import 时不会被执行。
from __future__ import annotations

import importlib.util  # 按文件路径加载。32_切块 这种名字以数字开头，写不成 import 语句。
import sys  # sys.modules：已经加载的模块表。dataclass 创建类时要能按名字找到自己。
from pathlib import Path  # 定位仓库根和手册文件。对照 java.nio.file.Path。

# 本文件在「44-答案黄金集/」。parent 是本目录，parent.parent 是仓库根。
_ROOT = Path(__file__).resolve().parent.parent

# (问题, 要点, 是否必须拒答)。
# 要点是 None 且必须拒答：正文里要有「不知道」，不能编出一个城市。
# 全大写是约定，不是语言强制的常量。别人仍能改这个列表。
# list[tuple[str, str | None, bool]] 对照 List<三元组>，中间那个 String 可以是 null。
GOLD: list[tuple[str, str | None, bool]] = [
    ("退款几天", "7", False),  # 正文里要出现「7」。不要求整句一模一样。
    ("客服电话多少", "400-100-1000", False),  # 电话要原样出现。只说「请拨打客服」不算过。
    ("公司地址在哪", None, True),  # 手册里没有地址。必须拒答，要点栏空着。
]


def _load(folder: str, file_name: str):
    """文件名以数字开头，import 语句写不出来。

    返回执行完的模块对象。对照用 ClassLoader 从指定路径加载，再拿上面的函数。
    """
    path = _ROOT / folder / file_name  # Path 用 / 拼接，分隔符它自己处理。
    # gold44_ 前缀和别的课的 lesson_、route_ 分开，避免同一个进程里模块名撞车。
    module_name = "gold44_" + file_name.replace(".", "_")
    spec = importlib.util.spec_from_file_location(module_name, path)  # 从哪加载，此时还没执行文件。
    assert spec and spec.loader  # 路径不对就立刻失败。python -O 会丢掉 assert，教学代码里这样写可以。
    module = importlib.util.module_from_spec(spec)  # 空模块对象。
    sys.modules[module_name] = module  # 先登记，dataclass 执行时才找得到自己。
    spec.loader.exec_module(module)  # 跑该文件顶层。它的 main 不会跑，因为名字不是 "__main__"。
    return module


def passes(text: str, must: str | None, abstain: bool) -> bool:
    """一条规则。拒答看有没有「不知道」，以及有没有编城市。其余看要点是不是子串。

    -> bool 对照返回 boolean。解释器默认不检查这个标注。
    """
    if abstain:
        # in 对字符串是「是否包含子串」，不是等于。对照 text.contains("不知道")。
        # 编了北京仍含「不知道」也不算过。两个条件都要。and 会短路，对照 &&。
        return "不知道" in text and "北京" not in text
    # must 在非拒答的题里不会是 None。这里收窄，是给类型检查看的。
    # assert 失败抛 AssertionError。对照 Objects.requireNonNull，但 -O 运行时这行会被丢掉。
    assert must is not None
    return must in text  # 「7」出现在长句里也算过。不看前后是不是礼貌用语。


def evaluate(answer_fn, index: list) -> tuple[int, int]:
    """返回 (对的题数, 总题数)。answer_fn 是函数本身，调用时传进去，不要先加括号。

    对照把方法引用交给测试，或传一个 BiFunction。加上括号会马上调用，而且这里还缺参数。
    返回元组。调用方用 ok, total = evaluate(...) 拆开。对照一次只能 return 一个对象，这里自带 Pair。
    """
    ok = 0  # int 不可变。+= 是重新绑定这个名字，不是改某个 Integer 内部。
    for question, must, abstain in GOLD:
        # 一项有三个值，一次拆给三个变量。对照自己写一个三字段的记录再取值。
        text, _sources = answer_fn(question, index)
        # 本课评正文，不评出处。左边写成 _sources：下划线表示「这个值我故意不用」。
        good = passes(text, must, abstain)  # True 或 False。不要和字符串「对」混在一个类型里。
        if good:
            ok += 1
        mark = "对" if good else "错"  # 三元表达式，顺序和 Java 的 条件 ? A : B 相反。
        print(f"  {mark}  问={question}  答={text}")  # f-string。对照 String.format。
    return ok, len(GOLD)  # len 是列表长度。对照 list.size()。


def brief(question: str, index: list) -> tuple[str, list[str]]:
    """「感觉更礼貌」的一版。不写数字，地址题还编了一个城市。index 不用，签名要和第 35 课对齐。

    返回 (正文, 出处列表)，形状和 cite.answer 一样，才能传给同一个 evaluate。
    对照两个实现同一个接口，测试方法只认这个方法签名。
    """
    del index  # 明确丢掉。不写这行也会跑，但读代码的人会以为漏了。
    # del 删的是这个局部名字，不是调用方手里的索引。对照「这个参数未使用」，这里用删名字来标明。
    if "地址" in question:
        # 编了一个城市，还带了假出处「编造」。拒答题会因为含「北京」、不含「不知道」而失败。
        return "我们在北京市海淀区，欢迎来访。", ["编造"]
    if "电话" in question:
        # 没有 400-100-1000。礼貌，但要点不在。
        return "请拨打客服电话，我们会尽快回复。", ["客服"]
    if "退" in question:
        # 「退款几天」含「退」，会进这里。没有数字 7。
        return "支持退款，请尽快联系客服办理。", ["退款"]
    return "不知道", []  # 三条都没碰上时的兜底。黄金集里的三题走不到这里。


def main() -> None:
    chunks = _load("32-文档切块", "32_切块.py")
    search = _load("34-检索", "34_检索.py")
    cite = _load("35-引用与拒答", "35_引用.py")
    # 手册不在本目录。read_text 读成 str。encoding 写明 utf-8，避免 Windows 用 GBK 读坏中文。
    handbook = (_ROOT / "32-文档切块" / "手册.md").read_text(encoding="utf-8")
    # 先切块再算向量。索引只建一次，两版回答共用。对照测试夹具只准备一份。
    index = search.build_index(chunks.chunk_markdown(handbook))

    print("引用版")
    # cite.answer 不加括号：传函数。evaluate 里面才会 answer_fn(question, index)。
    ok, total = evaluate(cite.answer, index)
    print(f"  通过 {ok}/{total}")

    print("简短版")
    # brief 也是函数，签名对齐，所以能放进同一个 evaluate。这就是「同一套断言，两套实现」。
    ok_brief, total_brief = evaluate(brief, index)
    print(f"  通过 {ok_brief}/{total_brief}")


# 直接 python 本文件才跑 main。被 import 时不自动打分。
if __name__ == "__main__":
    main()
