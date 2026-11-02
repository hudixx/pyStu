"""验收第 2 课：同一份文档，切块前两题都过不了，按句号切开之后两题都过。

整段又含「7」又含「400」。退款题不许带电话，电话题不许带天数，所以整段两题都失败。
切开之后，每题只拿含自己关键词的那一块。
这是黄金集：题是固定的，通过数能比。不调用模型。
"""

from __future__ import annotations

DOC = "退款需要 7 天。客服电话是 400-100-1000。"


def pieces(text: str, split: bool) -> list[str]:
    """不切就一整段。切就按句号拆开，丢掉拆完后的空串。"""

    if not split:
        return [text]
    # split 之后最后若是句号，会多出一个空串。空串不含关键词，但留着只会碍事。
    return [part for part in text.split("。") if part]


def retrieve(chunks: list[str], word: str) -> str:
    """把含这个词的块拼起来。一块都没有就是空串。"""

    hits = [chunk for chunk in chunks if word in chunk]
    return "".join(hits)


def passes(word: str, must: str, ban: str, citation: str) -> bool:
    """引用里要有必须出现的字，且不能有禁止的字。空引用两头都不算过。"""

    return must in citation and ban not in citation


def score(split: bool) -> int:
    """两道固定题。通过几道就返回几。"""

    chunks = pieces(DOC, split)
    exams = (
        ("退", "7", "400"),  # 退款题：要有 7，不能有 400。
        ("电话", "400", "7"),  # 电话题：要有 400，不能有 7。
    )
    passed = 0
    for word, must, ban in exams:
        citation = retrieve(chunks, word)
        if passes(word, must, ban, citation):
            passed += 1
    return passed


def main() -> None:
    print("切块前", f"{score(False)}/2")
    print("切块后", f"{score(True)}/2")


if __name__ == "__main__":
    main()
