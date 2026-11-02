"""验收第 2 课：同一份文档，切块前两题都过不了，按句号切开之后两题都过。

整段又含「7」又含「400」。退款题不许带电话，电话题不许带天数，所以整段两题都失败。
切开之后，每题只拿含自己关键词的那一块。
这是黄金集：题是固定的，通过数能比。不调用模型。
"""

from __future__ import annotations

# 全大写是约定，不是真的常量。这一整段同时含天数和电话，用来证明「不切就会两题都失败」。
DOC = "退款需要 7 天。客服电话是 400-100-1000。"


def pieces(text: str, split: bool) -> list[str]:
    """不切就一整段。切就按句号拆开，丢掉拆完后的空串。

    逻辑：
    - split 是 False：返回只有一个元素的列表，元素就是原文。整段又有 7 又有 400。
    - split 是 True：按中文句号切开。句号本身不留在每一块里。切完若多出一个空串，丢掉。
    参数名 split 是布尔开关，不是字符串的 split 方法。下面 text.split 才是那个方法。
    """

    if not split:
        # not 把布尔反过来。False 时走进这里。对照 if (!split)。
        return [text]  # 方括号包一个元素，就是只有这一段的列表。对照 List.of(text)。
    # split 之后最后若是句号，会多出一个空串。空串不含关键词，但留着只会碍事。
    # text.split("。") 按这个分隔符切开，分隔符自己不留在结果里。对照 String.split("。")。
    # 原文以句号结尾时，最后会多一项 ""。
    # 方括号里是列表推导：对每一块，if part 为真才留下。空串是假值，所以被丢掉。
    # 对照 stream.filter(part -> !part.isEmpty()).toList()。
    return [part for part in text.split("。") if part]


def retrieve(chunks: list[str], word: str) -> str:
    """把含这个词的块拼起来。一块都没有就是空串。

    逻辑：先筛出包含 word 的块，再按原来的顺序用空串粘成一段。没有命中时 join 空列表，得到 ""。
    """

    hits = [chunk for chunk in chunks if word in chunk]
    # word in chunk 是「这个词是不是这块的子串」，不是等于。对照 chunk.contains(word)。
    return "".join(hits)  # 用空串拼接。对照 String.join("", hits)。


def passes(word: str, must: str, ban: str, citation: str) -> bool:
    """引用里要有必须出现的字，且不能有禁止的字。空引用两头都不算过。

    逻辑：must 必须是引用的子串，并且 ban 不是引用的子串。两个条件都要成立。
    word 是这道题用来检索的词，真正的筛选已经在 retrieve 里做过。这里不再看 word，只看引用正文。
    空串里既没有 must，也没有 ban。must in "" 是 False，所以空引用不会通过。
    """

    return must in citation and ban not in citation
    # and 短路：左边已经是假，右边不再看。对照 &&。
    # not in 是「不是子串」。对照 !citation.contains(ban)。


def score(split: bool) -> int:
    """两道固定题。通过几道就返回几。

    逻辑：
    1. 按 split 决定切不切，得到块列表。
    2. 两道题写死在 exams 里。每题是 (检索词, 必须出现, 禁止出现)。
    3. 用检索词取出引用，再交给 passes。过一题就把计数加 1。
    4. 返回 0、1 或 2。不调用模型，所以没有随机。
    """

    chunks = pieces(DOC, split)
    exams = (
        ("退", "7", "400"),  # 退款题：要有 7，不能有 400。
        ("电话", "400", "7"),  # 电话题：要有 400，不能有 7。
    )
    # 外层圆括号是一个元组，里面两个小元组各是一道题。对照一张固定的试题表，不能中途改。
    # 元组拆包一次把三个字符串交给三个名字。对照从一个三字段记录里取值。
    passed = 0
    for word, must, ban in exams:
        citation = retrieve(chunks, word)  # 不切时，整段同时含两个词，两题拿到的是同一整段。
        if passes(word, must, ban, citation):
            passed += 1  # 整数不可变。+= 是把新的数贴回这个名字。对照 passed = passed + 1。
    return passed


def main() -> None:
    """同一份文档打两次分：不切应是 0/2，按句号切开应是 2/2。

    f"{score(False)}/2" 把函数结果嵌进字符串。False 不加引号，它是布尔值，不是文字。
    """

    print("切块前", f"{score(False)}/2")
    print("切块后", f"{score(True)}/2")


if __name__ == "__main__":
    main()

# 这个脚本想说明的事：
# 黄金集是固定的题。整段资料又含天数又含电话时，两道互相禁止的题都会失败。
# 按句号切开之后，每题只拿到含自己关键词的那一块，禁止的字不在里面，两题才都过。
# 这里不调用模型。通过数能反复比，不靠「感觉切完更好」。
