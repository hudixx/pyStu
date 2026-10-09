"""第 32 课示例：按标题切文档，太长再滑窗。

对照：不是把整本手册塞进一次 prompt（第 27 课：输入 token 又贵又慢）。
一块 = 以后检索能指回的最小出处。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Chunk:
    """一块正文，外加它从哪一节来。source 用来做引用，不是给模型随便编的。"""

    source: str
    text: str


def chunk_markdown(text: str, max_chars: int = 80, overlap: int = 20) -> list[Chunk]:
    """先按 ## 标题切开，一节仍超长再按字符滑窗。

    max_chars：一块最多多少字。太长又回到「整篇粘贴」。
    overlap：相邻窗重叠多少字，避免一句话被切在边界上两边都看不懂。
    """
    sections = _split_headings(text)
    chunks: list[Chunk] = []
    for source, body in sections:
        body = body.strip()
        if not body:
            continue
        if len(body) <= max_chars:
            chunks.append(Chunk(source, body))
            continue
        # 超长才滑窗。start 每次前进 max_chars - overlap，所以相邻块有重叠。
        step = max(max_chars - overlap, 1)
        start = 0
        while start < len(body):
            piece = body[start : start + max_chars].strip()
            if piece:
                chunks.append(Chunk(source, piece))
            if start + max_chars >= len(body):
                break
            start += step
    return chunks


def _split_headings(text: str) -> list[tuple[str, str]]:
    """按以 ## 开头的行分节。返回 (标题, 该节正文)。没有标题的前言标题记为「全文」。"""
    sections: list[tuple[str, str]] = []
    title = "全文"
    buf: list[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            sections.append((title, "\n".join(buf)))
            title = line[3:].strip()  # 去掉「## 」
            buf = []
            continue
        if line.startswith("# "):
            continue  # 文档大标题不单独成块
        buf.append(line)
    sections.append((title, "\n".join(buf)))
    return sections


def main() -> None:
    handbook = Path(__file__).with_name("手册.md").read_text(encoding="utf-8")
    print("=== 按标题切（每节都短，不会滑窗）===")
    for i, chunk in enumerate(chunk_markdown(handbook), start=1):
        print(f"{i}. [{chunk.source}] {chunk.text}")

    long = "退款规则。" * 30  # 人为拉长，才能看见重叠
    print("=== 超长一节，max_chars=20，overlap=5 ===")
    for chunk in chunk_markdown("## 退款\n" + long, max_chars=20, overlap=5):
        print(repr(chunk.text))


if __name__ == "__main__":
    main()
