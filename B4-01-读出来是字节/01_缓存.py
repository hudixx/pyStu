"""选修 B4 第 1 课：Redis 取出来默认是字节，不是字符串。

对照 StringRedisTemplate。Java 那边把字节解码成 String，redis-py 默认不解码。
decode_responses=True 只在客户端用 UTF-8 把字节变成 str。服务器里存的仍是字节。
没有这个键时返回 None，不是空字符串，也不抛异常。

本课用 fakeredis。命令和 redis.Redis 一样。数据在这个进程里，不连接真服务器，也不写密码。
"""

from __future__ import annotations

import fakeredis  # 进程内的 Redis。对照测试里的嵌入式 Redis，不是生产上的 Lettuce 客户端。


def main() -> None:
    # 生产要连真服务器时才用 redis.Redis(host=..., port=6379)。本课不创建那个对象，避免真的去连。
    # decode_responses=False 是默认值。写出来是为了和下面那个客户端对照。
    # 等号两边不空格，这是关键字参数。
    raw = fakeredis.FakeStrictRedis(decode_responses=False)
    raw.set("buyer", "hudi")  # 传入 str。客户端按 UTF-8 写成字节再交给服务器。
    # print 几个参数之间用一个空格隔开。bytes 打印出来带 b 和引号，所以是 b'hudi'，不是 hudi。
    print("不解码", raw.get("buyer"))
    # 键不存在。对照缓存未命中。Java 的 get 往往也是 null，不是空串，更不是抛「找不到键」。
    print("没有这个键", raw.get("missing"))

    # True：每次 get 把 UTF-8 字节解码成 str。键、命令都没变，变的是客户端要不要解码。
    text = fakeredis.FakeStrictRedis(decode_responses=True)
    text.set("buyer", "hudi")
    print("解码", text.get("buyer"))  # 这一行没有 b。类型是 str。


if __name__ == "__main__":
    main()
