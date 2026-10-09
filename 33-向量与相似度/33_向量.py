"""第 33 课示例：把一段文字变成向量，用余弦相似度比较。

这不是真 embedding 模型。真环境换成 client.embeddings.create，得到的仍是 list[float]。
本课向量是确定性的，方便断言，不花钱。

Python 内置 hash() 每次启动会变（为了防止用哈希做攻击，解释器启动时加了随机盐），不能用来做向量。
这里用 md5：同一段字节，永远得到同一串十六进制。对照 MessageDigest.getInstance("MD5")，只为分桶，不是加密。
"""

from __future__ import annotations

import hashlib  # 标准库的摘要。本课只用 md5，把一段二字组稳定地映射到某个下标。
import math  # sqrt：算向量长度。对照 Math.sqrt。

# 前 10 维留给手册里的关键词，后面的维用字二元组。换文档要改这张表，这是假模型的局限。
# dict[str, int] 对照 Map<String, Integer>。这里的 int 是「这个词占第几维」，不是出现次数。
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
_DIM = 32  # 向量总维数。下标 0～9 是上面的关键词，10～31 是二字组的哈希桶。


def embed(text: str) -> list[float]:
    """文本 → 32 维向量。相同文本永远得到相同向量。

    真 embedding 也是这个形状：一段文字进去，一串 float 出来。本课只是用规则把这串数造出来。
    """
    vec = [0.0] * _DIM  # 32 个 0.0。[0.0] * 32 是「把这个列表重复 32 次再拼平」。float 不可变，这样乘是安全的。
    for word, index in _ANCHORS.items():
        # .items() 一次给出键和值。对照 map.entrySet() 里的 getKey / getValue。
        if word in text:
            # in 对字符串是「是否包含子串」，不是「是否等于」。对照 text.contains(word)。
            vec[index] += 1.0  # 命中就在对应那一维加 1。列表下标赋值，对照数组 vec[index] += 1。
    compact = "".join(text.split())  # split 不带参数：按任意空白切开。再 join 成空串，等于删掉所有空白。
    for i in range(len(compact) - 1):
        # range(n) 是 0, 1, ..., n-1。这里到倒数第二字为止，因为每次取 i 和 i+1。对照 for (int i = 0; i < len - 1; i++)。
        gram = compact[i : i + 2]  # 连续两个字，叫二元组。比如「退款几天」会得到「退款」「款几」「几天」。
        # encode 得到 bytes。md5 吃字节，不吃 str。hexdigest() 是 32 位十六进制字符串。
        # int(十六进制, 16) 把它变成整数。对照 Integer.parseInt(hex, 16)，但 Python 的 int 不会溢出。
        # % (_DIM - 10) 落到 0～21，再 + 10，就只占用下标 10～31，不冲掉前面的关键词维。
        bucket = int(hashlib.md5(gram.encode("utf-8")).hexdigest(), 16) % (_DIM - 10) + 10
        vec[bucket] += 0.3  # 权重比关键词的 1.0 小。关键词对得上时，余弦分会被那几维拉得更近。
    return vec


def cosine(left: list[float], right: list[float]) -> float:
    """余弦相似度，范围大约 -1 到 1。1 表示方向相同。对照：不是 SQL 的 LIKE。

    公式：点积 / （左向量长度 × 右向量长度）。只比方向，不比长短。
    两段字完全一样时，结果是 1。正交（完全不像）接近 0。本课的向量分量都是非负的，所以不会出现负分。
    """
    # zip：两个列表并排走，每次拿出一对 (a, b)。短的那个结束就停。对照把两个数组按下标对齐。
    # 生成器表达式交给 sum，不先建成一个中间列表。对照用一个循环累加 a * b。
    dot = sum(a * b for a, b in zip(left, right))
    norm_l = math.sqrt(sum(a * a for a in left))  # 左向量的欧氏长度。对照 Math.sqrt(平方和)。
    norm_r = math.sqrt(sum(b * b for b in right))
    if norm_l == 0 or norm_r == 0:
        # 全 0 的向量长度为 0，再除就会 ZeroDivisionError。规定这种相似度是 0。
        return 0.0
    return dot / (norm_l * norm_r)


def main() -> None:
    refund = embed("购买后 7 天内可以退款")  # 手册里「退款」那类句子。含「退款」「7」「天」，前几维会亮。
    ask = embed("退款几天")  # 问题。也含「退款」「天」，所以和上面方向接近。
    price = embed("月度会员 99 元")  # 价格句。亮的是「会员」「99」，和「退款几天」几乎不共享关键词维。
    # round(x, 3)：保留 3 位小数，返回的仍是 float，不是字符串。对照自己用 Decimal 设 scale，这里只为了打印好看。
    print("退款问题 vs 退款段落 =", round(cosine(ask, refund), 3))
    print("退款问题 vs 价格段落 =", round(cosine(ask, price), 3))
    print("同一段 vs 自己 =", round(cosine(refund, refund), 3))  # 自己比自己，应当是 1.0。


# 直接运行本文件才打印那三行。被第 34 课加载时不自动打印。
if __name__ == "__main__":
    main()
