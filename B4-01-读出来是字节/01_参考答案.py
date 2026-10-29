"""选修 B4 第 1 课参考答案。题 1 过了。题 2 写在下面。

运行 01_练习.py 看到：

不解码 b'400-100-1000'
解码 400-100-1000
没有这个键 None

两个客户端都 set 了 phone。empty 没有 set。输出和题目一致。

set("phone","400-100-1000") 逗号后面少了一个空格。本课 ruff 没报，不影响这三行。
import 和函数之间少了一行空行。演示文件空了两行。

题 2：
- 默认带 b，是因为取回来的类型是 bytes，不是 str 前面多了一个字母。
  Redis 里存的是字节。redis-py 默认不解码，Python 打印 bytes 就会带 b 和引号。
- decode_responses=True 改的是这个客户端。get 的时候用 UTF-8 把字节变成 str。
  服务器里的存法不变。这两个 FakeStrictRedis 各有一份内存，所以各 set 了一次。
  换成真 Redis 时，同一个键只写一次。一个客户端解码、一个不解码，拿到的仍是两种类型。
- 没有这个键是 None。"" 是键在、值是空字符串。b"" 是空的字节。三件不是一回事。
  GET 对没有的键给空结果，不抛「找不到」。对照缓存未命中是 null。
"""

from __future__ import annotations

import fakeredis


def main() -> None:
    raw = fakeredis.FakeStrictRedis(decode_responses=False)
    raw.set("phone", "400-100-1000")
    print("不解码", raw.get("phone"))

    text = fakeredis.FakeStrictRedis(decode_responses=True)
    text.set("phone", "400-100-1000")
    print("解码", text.get("phone"))
    print("没有这个键", text.get("empty"))


if __name__ == "__main__":
    main()
