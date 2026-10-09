"""第 35 课示例：有命中才回答，并带上出处；没有就说不知道。

本课不打聊天模型。答案先用命中的原文，避免假模型把资料回声一遍。
真环境把「原文」换成一次 chat：system 写「只根据资料回答」，资料放进 user。
没命中时仍然不要调用模型。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent  # 仓库根。本文件在「35-引用与拒答/」下。


def _load(folder: str, file_name: str):
    """按路径加载 32、34 课。参数顺序是 (目录, 文件名)，和第 34 课那个 _load 相反，调用时别抄错。

    原因和第 34 课相同：文件名以数字开头，写不成 import 语句。
    """
    path = _ROOT / folder / file_name
    module_name = "lesson_" + file_name.replace(".", "_")  # 「35 自己的加载名」，避免和数字开头的文件名冲突。
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader  # 路径不对、loader 造不出来就立刻失败，不要继续往下。
    module = importlib.util.module_from_spec(spec)
    # 先登记。被加载的文件里有 @dataclass，创建类时会回 sys.modules 找自己的模块。
    sys.modules[module_name] = module
    spec.loader.exec_module(module)  # 执行该文件顶层。它的 main 不会跑。
    return module


# import 本文件时就加载这两课。34 课自己还会再去加载 32 和 33，所以向量函数不用在这里再拿一次。
_chunks = _load("32-文档切块", "32_切块.py")
_search = _load("34-检索", "34_检索.py")

# 向量分低于这个值，且关键词也没命中，就当没检索到。
# 假向量上「退款几天」大约 0.7，「公司地址」接近 0。换真 embedding 要重调这个数。
# 全大写是本模块的常量约定，不是语言强制。对照 public static final，但别人仍能改它。
_MIN_VECTOR = 0.45


def answer(question: str, index: list) -> tuple[str, list[str]]:
    """返回 (回答, 出处列表)。出处为空表示拒答。

    index 的标注只写了 list，没写里面是什么。运行时不检查。实际放进去的是 34 课 build_index 的结果。
    返回元组而不是一个类：两个值捆在一起。调用方用 text, sources = answer(...) 拆开。
    """
    hits = _search.search(question, index, k=1)  # 只要第 1 名。可能是空列表：索引本身是空的时候。
    if not hits:
        # 空列表是假值。没有候选，就不要编答案。第二个值是空列表，不是 None。
        return "不知道", []
    top = hits[0]  # k=1 时最多一个。上面已经排除了空，这里下标 0 是安全的。
    # 关键词分到 1 分（编号原样出现），或者向量分过门槛，才算「这份资料和问题有关」。
    # or 会短路：左边已经是 True 时，右边的向量分不再看。对照 || 。
    relevant = top.keyword_score >= 1 or top.vector_score >= _MIN_VECTOR
    if not relevant:
        # 有一块「最像」，但还是不够像。比如问公司地址，手册里没有，最近的一块分也很低。
        # 这种要拒答。若把这块交给模型，模型会用无关的段落编一句。
        return "不知道", []
    # 先把资料原句交出去，并写明来自哪一节。模型改写时也必须保留这个来源。
    # f-string 的两个花括号会换成字段。对照 String.format("%s（来源：%s）", text, source)。
    text = f"{top.chunk.text}（来源：{top.chunk.source}）"
    return text, [top.chunk.source]  # 方括号：一个只含这一节名字的新列表。对照 List.of(source)。


def main() -> None:
    handbook = (_ROOT / "32-文档切块" / "手册.md").read_text(encoding="utf-8")
    # 切块函数在 32 课模块上，建索引的函数在 34 课模块上。索引只建一次，三问共用。
    index = _search.build_index(_chunks.chunk_markdown(handbook))
    for question in ("退款几天", "SKU-8891 是什么", "公司地址在哪"):
        # 拆开返回的元组。sources 是 list[str]，拒答时是 []。
        text, sources = answer(question, index)
        print("问:", question)
        print("  答:", text)
        print("  出处:", sources)  # 打印列表会带方括号，比如 ['退款'] 或 []。


if __name__ == "__main__":
    main()
