from __future__ import annotations

DOC = "买牛奶在一楼。买面包在二楼。"

def pieces(text: str, split: bool) -> list[str]:
    if split:
        return [part for part in text.split("。") if part]
    else:
        return [text]

def retrieve(chunks: list[str], word: str) -> str:
    hits = [chunk for chunk in chunks if word in chunk]
    return "".join(hits)

def passes(word:str, must: str, ban: str, citation: str) -> bool:
    return must in citation and ban not in citation

def  score(split: bool) -> int:
    chunks = pieces(DOC, split)
    exams = (
        ("牛奶", "一楼", "二楼"),
        ("面包", "二楼", "一楼")
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

#  题2不知道，请在参考答案的注释中个给出
