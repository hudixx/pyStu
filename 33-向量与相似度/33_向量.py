"""第 33 课示例：把一段文字变成向量，用余弦相似度比较。

这不是真 embedding 模型。真环境换成 client.embeddings.create，得到的仍是 list[float]。
本课向量是确定性的，方便断言，不花钱。

Python 内置 hash() 每次启动会变，不能用来做向量。这里用 md5。
"""

from __future__ import annotations

import hashlib
import math

# 前 10 维留给手册里的关键词，后面的维用字二元组。换文档要改这张表，这是假模型的局限。
_ANCHORS: dict[str, int] = {
    "退款": 0,
    "7": 1,
    "天": 2,
    "客服": 3,
    "电话": 4,
    "400": 5,
    "会员": 6,
    "99": 7,
    "899": 8,
    "价格": 9,
}
_DIM = 32


def embed(text: str) -> list[float]:
    """文本 → 32 维向量。相同文本永远得到相同向量。"""
    vec = [0.0] * _DIM
    for word, index in _ANCHORS.items():
        if word in text:
            vec[index] += 1.0
    compact = "".join(text.split())  # 去掉空白，避免空格把词拆开
    for i in range(len(compact) - 1):
        gram = compact[i : i + 2]
        # md5 稳定。int(..., 16) 把十六进制变成整数，再映射到 10..31。
        bucket = int(hashlib.md5(gram.encode("utf-8")).hexdigest(), 16) % (_DIM - 10) + 10
        vec[bucket] += 0.3
    return vec


def cosine(left: list[float], right: list[float]) -> float:
    """余弦相似度，范围大约 -1 到 1。1 表示方向相同。对照：不是 SQL 的 LIKE。"""
    dot = sum(a * b for a, b in zip(left, right))
    norm_l = math.sqrt(sum(a * a for a in left))
    norm_r = math.sqrt(sum(b * b for b in right))
    if norm_l == 0 or norm_r == 0:
        return 0.0
    return dot / (norm_l * norm_r)


def main() -> None:
    refund = embed("购买后 7 天内可以退款")
    ask = embed("退款几天")
    price = embed("月度会员 99 元")
    print("退款问题 vs 退款段落 =", round(cosine(ask, refund), 3))
    print("退款问题 vs 价格段落 =", round(cosine(ask, price), 3))
    print("同一段 vs 自己 =", round(cosine(refund, refund), 3))


if __name__ == "__main__":
    main()
