"""第 34 课示例：内存里的 Top-K。生产以后可以换成 pgvector，查询形状一样。

本课不上数据库。阶段十才学 SQLAlchemy，现在装 Postgres 会挡住 RAG。
业务上的用户表、订单表以后仍是普通 SQL。向量只存「这块文字的坐标」。
"""

from __future__ import annotations

import importlib.util  # 按文件路径加载模块。本课要用它，因为 32_切块 这种名字不能出现在 import 语句里。
import sys  # sys.modules：解释器已经加载的模块表。对照 ClassLoader 里「已定义的类」登记处。
from dataclasses import dataclass
from pathlib import Path

# 本文件在「34-检索/」。parent 是本目录，parent.parent 是仓库根。后面用仓库根去拼 32、33 课的路径。
_ROOT = Path(__file__).resolve().parent.parent


def _load(file_name: str, folder: str):
    """文件名以数字开头，不能写 import 32_切块。对照第 20 课的 importlib。

    import 后面必须是合法标识符，不能以数字开头，所以那行会直接语法错误。
    这里改成「知道文件在哪，就执行那个文件」，名字另起一个 lesson_ 开头的。
    没有写返回类型：返回的是执行完的模块对象，上面有 Chunk、embed 这些属性。对照反射拿到一个 Class。
    """
    path = _ROOT / folder / file_name  # Path 用 / 拼接。对照 Paths.get(root, folder, fileName)，分隔符它自己处理。
    # 模块名不能以数字开头。把「32_切块.py」换成「lesson_32_切块_py」。replace 换的是所有点，不只是扩展名。
    module_name = "lesson_" + file_name.replace(".", "_")
    # 造一份「从哪加载」的说明书，此时还没执行文件。对照拿到 Class 的字节码，还没跑静态初始化。
    spec = importlib.util.spec_from_file_location(module_name, path)
    # spec 或它的 loader 缺失时，后面无法执行。assert 失败抛 AssertionError。对照 Objects.requireNonNull。
    # python -O 会丢掉 assert。教学代码这样写可以，业务代码里不要用 assert 做必经的校验。
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)  # 空模块对象，文件还没跑。
    # 先登记再执行。32 课的 @dataclass 在创建类时会按模块名回 sys.modules 找自己。
    # 不先放进去，查到的是 None，加载会失败。对照：静态初始化回头 Class.forName 自己时，类必须已经登记。
    sys.modules[module_name] = module
    spec.loader.exec_module(module)  # 真正执行那个 .py 的顶层。它的 if __name__ 不会进，因为名字不是 "__main__"。
    return module


# 这两行在 import 本文件时就执行，不是等 main()。对照类加载时的静态初始化。
_chunks = _load("32_切块.py", "32-文档切块")
_vectors = _load("33_向量.py", "33-向量与相似度")
# 从模块对象上取出函数和类，后面当成本文件的名字用。对照 import static。
Chunk = _chunks.Chunk
chunk_markdown = _chunks.chunk_markdown
cosine = _vectors.cosine
embed = _vectors.embed


@dataclass
class Hit:
    """一次命中：哪一块、向量分、关键词分。对照一条查询结果 DTO，三个字段。"""

    chunk: Chunk  # 命中的那一块。类型是 32 课的 Chunk，字段是 source 和 text。
    vector_score: float  # 余弦相似度。越大越像。本课大约在 0～1。
    keyword_score: float  # 编号是否原样出现。本课只有 0.0 或 1.0。


def build_index(chunks: list[Chunk]) -> list[tuple[Chunk, list[float]]]:
    """每块算一次向量。对照：入库时算，不是用户每问一次都把全文重算。

    返回的每一项是 (块, 该块的向量)。元组把这两样捆在一起，没有再定义一个类。
    """
    # 列表推导：对 chunks 里每块做 embed，收成一个新列表。对照 stream.map(...).toList()。
    # 方括号就是「我要一个 list」。换成圆括号会变成生成器，这里需要能反复遍历的列表。
    return [(chunk, embed(chunk.text)) for chunk in chunks]


def keyword_score(question: str, text: str) -> float:
    """问题里的连续数字/字母（如 SKU-8891、400）是否原样出现。没有就 0。

    返回 float 而不是 bool，是为了和向量分放进同一种「分」里排序。1.0 表示命中，0.0 表示没有。
    """
    token = _long_token(question)
    if token and token in text:
        # token 非空，并且整段编号是 text 的子串。in 对 str 是 contains，不是等于。
        return 1.0
    return 0.0


def search(question: str, index: list[tuple[Chunk, list[float]]], k: int = 2) -> list[Hit]:
    """向量分和关键词分都算，按「向量为主、关键词兜底」排序，取前 k 个。

    k=2 是默认值。调用时写 search(q, index, k=1) 就只留第 1 名。
    """
    qv = embed(question)  # 问题也变成同一套 32 维。必须和入库用同一个 embed，否则余弦没有意义。
    hits: list[Hit] = []
    for chunk, vec in index:
        # 元组拆包。vec 是入库时算好的，这里不再 embed(chunk.text)。
        hits.append(
            Hit(
                chunk=chunk,  # 关键字参数，顺序可以不跟字段声明一致，但写出来更清楚。对照 new Hit(chunk, ...) 的具名参数。
                vector_score=cosine(qv, vec),
                keyword_score=keyword_score(question, chunk.text),
            )
        )
    # 订单号这种要精确匹配：关键词命中时把它顶上去。普通问句关键词分都是 0，主要看向量。
    # lambda h: ... 是匿名函数，只在排序时用。对照 Comparator.comparing(...).thenComparing(...)。
    # 返回元组：先比 keyword_score，相同再比 vector_score。Python 比元组是从左到右逐个比。
    # reverse=True：从大到小。list.sort 原地排序，不返回新列表（返回的是 None，所以不能链式调用）。
    hits.sort(key=lambda h: (h.keyword_score, h.vector_score), reverse=True)
    return hits[:k]  # 切片出前 k 个，是一个新列表。不足 k 个就全返回。对照 subList(0, k)，但越界不会抛。


def _long_token(question: str) -> str:
    """抽出问题里最长的一段「像编号」的字符。没有长度>=4 的就返回空串。

    连续的中文也会被收进来：汉字的 isalnum() 是 True（Unicode 里它算字母）。
    「退款几天」这种整句长度够 4，会变成 token；正文里没有这整句时，关键词分就是 0，退回向量。
    SKU-8891 这种才是本函数真正想托底的编号。
    """
    buf = ""  # 当前这一段还没被标点或空格打断的字符。
    best = ""  # 到目前为止最长的那一段。
    for ch in question:
        # 遍历 str 得到的是一个一个字符，每个 ch 仍是长度为 1 的 str。对照对 codePoint 循环，不是 char 拆字节。
        if ch.isalnum() or ch in "-_":
            # isalnum：字母或数字。ch in "-_"：这个字符是不是 "-" 或 "_"。对照 "-_".contains(ch)。
            buf += ch  # 字符串不可变，+= 会新建一个。编号很短，这里可以接受。对照 StringBuilder 更合适，但没必要。
            if len(buf) > len(best):
                best = buf
        else:
            buf = ""  # 空格、标点把编号切断，下一段从头开始。best 保留已经见过的最长段。
    return best if len(best) >= 4 else ""  # 短于 4 的（比如单独一个「7」）不当编号，避免误伤普通问句。


def main() -> None:
    # 手册不在本目录，在 32 课目录。read_text 读成 str。文件不存在会抛 FileNotFoundError。
    handbook = (_ROOT / "32-文档切块" / "手册.md").read_text(encoding="utf-8")
    index = build_index(chunk_markdown(handbook))  # 先切块，再每块算一次向量。
    for question in ("退款几天", "客服电话多少", "SKU-8891 是什么"):
        # 圆括号里三个字符串是一个元组。for 直接遍历它。对照 List.of(...) 再 for。
        print("问:", question)
        for hit in search(question, index, k=1):
            # :.3f 表示这个 float 打印时保留 3 位小数。:.0f 是不要小数。这是格式说明，不是把值改成 int。
            print(
                f"  [{hit.chunk.source}] 向量={hit.vector_score:.3f} 关键词={hit.keyword_score:.0f}"
            )
            print(" ", hit.chunk.text)


if __name__ == "__main__":
    main()
