"""第 32 课示例：按标题切文档，太长再滑窗。

对照：不是把整本手册塞进一次 prompt（第 27 课：输入 token 又贵又慢）。
一块 = 以后检索能指回的最小出处。
"""

# 推迟注解求值。后面的 list[Chunk] 在 import 时不会被立刻执行。
# 对照 Java：泛型本来就不在运行时当代码跑。这行删掉，本文件也能跑。
from __future__ import annotations

# dataclass：按下面的字段自动生成构造方法、__eq__、__repr__。对照 Lombok @Data，或 Java 16 的 record。
from dataclasses import dataclass
# Path：面向对象的路径。对照 java.nio.file.Path。这里用来找同目录的「手册.md」。
from pathlib import Path


@dataclass
class Chunk:
    """一块正文，外加它从哪一节来。source 用来做引用，不是给模型随便编的。

    类体里只有字段、没有方法。生成的构造器按字段顺序：Chunk(source, text)。
    对照：record Chunk(String source, String text)。读字段用 chunk.source，不是 getSource()。
    """

    source: str  # 出处，比如「退款」。命中后告诉用户这句话来自哪一节。
    text: str  # 这一块的正文，也是以后拿去算向量的那段字。


def chunk_markdown(text: str, max_chars: int = 80, overlap: int = 20) -> list[Chunk]:
    """先按 ## 标题切开，一节仍超长再按字符滑窗。

    max_chars：一块最多多少字。太长又回到「整篇粘贴」。
    overlap：相邻窗重叠多少字，避免一句话被切在边界上两边都看不懂。

    等号后面的 80、20 是默认值，调用时可以不传。对照 Java 靠重载少写参数，Python 用默认参数。
    默认值在 def 执行时算一次。这里是 int，不可变，没有「可变默认参数」那个坑。
    -> list[Chunk] 对照 List<Chunk>。解释器默认不检查这个标注。
    """
    sections = _split_headings(text)  # 得到 [(标题, 该节正文), ...]。
    chunks: list[Chunk] = []  # 冒号后面是类型标注，运行时就是普通 list。对照 new ArrayList<Chunk>()。
    # 元组拆包：每一项两个值，一次赋给两个变量。对照自己写 Pair 再 getLeft / getRight。
    for source, body in sections:
        body = body.strip()  # 去掉首尾空白和换行。对照 trim()，Python 3 的 strip 也去掉 \\n。
        if not body:
            # 空串是假值。只有标题、没有正文的节，不单独成块。
            continue
        if len(body) <= max_chars:
            # 一节不超长：整节就是一块。append 对照 List.add。Chunk(source, body) 是位置参数构造。
            chunks.append(Chunk(source, body))
            continue  # 这一节处理完了。不要再往下滑窗。
        # 超长才滑窗。每次前进 max_chars - overlap，相邻两块就重叠 overlap 个字符。
        # max(..., 1)：万一 overlap >= max_chars，步长至少是 1，避免 start 不前进、死循环。对照 Math.max。
        step = max(max_chars - overlap, 1)
        start = 0  # 当前窗口在 body 里的起始下标。
        while start < len(body):
            # 切片 [start : start + max_chars]：含起点、不含终点。对照 substring(start, end)。
            # 右端超出字符串长度时，Python 截到末尾，不抛异常。Java 的 substring 越界会抛。
            piece = body[start : start + max_chars].strip()
            if piece:
                # 同一节切出来的多块，出处都还是这个标题。strip 后变空的窗（比如全是空格）丢掉。
                chunks.append(Chunk(source, piece))
            if start + max_chars >= len(body):
                # 这一窗已经盖住正文结尾，再滑就是重复的尾巴。
                break
            start += step
    return chunks


def _split_headings(text: str) -> list[tuple[str, str]]:
    """按以 ## 开头的行分节。返回 (标题, 该节正文)。没有标题的前言标题记为「全文」。

    下划线开头表示「给本模块自己用」，不是语言强制的 private。别的文件仍能调用它。
    tuple[str, str] 对照 Pair<String, String>。
    """
    sections: list[tuple[str, str]] = []
    title = "全文"  # 还没遇到 ## 时，攒下来的行算前言，出处先记成「全文」。
    buf: list[str] = []  # 当前这一节的各行。最后再 join，避免在循环里反复用 + 拼字符串。
    for line in text.splitlines():
        # splitlines()：按行拆开，行尾的换行不留在 line 里。对照 BufferedReader.readLine()。
        if line.startswith("## "):
            # 新的二级标题。先把「上一节」收进结果，此时 title 还是上一节的名字。
            # "\\n".join(buf)：用换行把各行粘回去。buf 为空时得到空串。
            sections.append((title, "\n".join(buf)))
            title = line[3:].strip()  # 切片 [3:] 丢掉开头三个字符「## 」。对照 substring(3).trim()。
            buf = []  # 换成新列表。不能 buf.clear()：旧列表已经放进上面的元组里，清掉会把上一节正文清掉。
            continue
        if line.startswith("# "):
            continue  # 一级大标题不进正文，也不单独成块。
        buf.append(line)
    # 最后一节没有「下一个 ##」来触发收尾，循环完还在 buf 里，所以这里再收一次。
    sections.append((title, "\n".join(buf)))
    return sections


def main() -> None:
    # __file__ 是本 .py 的路径。with_name 只换文件名，目录不变。对照同目录下另开一个 Path。
    # read_text 一次读成 str。encoding 写明 utf-8，避免 Windows 默认用 GBK 把中文读坏。
    handbook = Path(__file__).with_name("手册.md").read_text(encoding="utf-8")
    print("=== 按标题切（每节都短，不会滑窗）===")
    # enumerate(..., start=1)：同时给序号和元素，序号从 1 起。对照 int i = 1; i++，但不用自己管下标。
    for i, chunk in enumerate(chunk_markdown(handbook), start=1):
        # f-string 里 {chunk.source} 会换成字段的字符串。对照 " [" + chunk.source + "] "。
        print(f"{i}. [{chunk.source}] {chunk.text}")

    long = "退款规则。" * 30  # 字符串乘整数：同一段重复 30 次。人为拉长，下面才能看见窗在滑动。
    print("=== 超长一节，max_chars=20，overlap=5 ===")
    # 关键字参数覆盖默认的 80 和 20。只传需要改的，另一个仍用定义时的默认值也可以，这里两个都改了。
    for chunk in chunk_markdown("## 退款\n" + long, max_chars=20, overlap=5):
        # repr 打出带引号的字面形式，重叠的那几个字在边界上看得更清楚。对照给字符串两侧加引号再打印。
        print(repr(chunk.text))


# 直接 python 本文件时，__name__ 是 "__main__"，才会跑 main。
# 第 34 课用 importlib 加载本文件时，__name__ 是别的名字，下面不执行，避免一 import 就打印。
if __name__ == "__main__":
    main()
