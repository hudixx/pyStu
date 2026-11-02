"""验收第 2 课参考答案。题 1 过了。题 2 写在下面。

运行 02_练习.py 看到：

切块前 0/2
切块后 2/2

文档是「买牛奶在一楼。买面包在二楼。」
不切开时，两题拿到的都是整段，既有要的楼，也有不许出现的楼。
按句号切开之后，牛奶只拿到一楼那块，面包只拿到二楼那块。

def 和 score 之间多了一个空格。word:str 冒号后面少了一个空格。
本课 ruff 没报，不影响这两行。

题 2：
- 整段里找得到「牛奶」，也找得到「一楼」。黄金集仍是 0/2，因为同一段里还有「二楼」。
  题要的是引用只带该带的事实。找到字，不等于引用干净。
- 切块变好，只说明拿回来的那一块对了。这一课没有调用模型。
  模型仍可能不看引用，自己编一句。回答变没变好，要另用回答的黄金集，不是这一份检索分数。
"""

from __future__ import annotations

DOC = "买牛奶在一楼。买面包在二楼。"


def pieces(text: str, split: bool) -> list[str]:
    if split:
        return [part for part in text.split("。") if part]
    return [text]


def retrieve(chunks: list[str], word: str) -> str:
    hits = [chunk for chunk in chunks if word in chunk]
    return "".join(hits)


def passes(word: str, must: str, ban: str, citation: str) -> bool:
    return must in citation and ban not in citation


def score(split: bool) -> int:
    chunks = pieces(DOC, split)
    exams = (
        ("牛奶", "一楼", "二楼"),
        ("面包", "二楼", "一楼"),
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
