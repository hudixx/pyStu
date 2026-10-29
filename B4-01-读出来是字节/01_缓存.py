"""选修 B4 第 1 课：Redis 取出来默认是字节，不是字符串。

对照 StringRedisTemplate。Java 那边把字节解码成 String，redis-py 默认不解码。
decode_responses=True 只在客户端用 UTF-8 把字节变成 str。服务器里存的仍是字节。
没有这个键时返回 None，不是空字符串，也不抛异常。

本课用 fakeredis。命令和 redis.Redis 一样。数据在这个进程里，不连接真服务器，也不写密码。
"""

# 推迟注解求值。本文件注解很少，留着是和前后几课同一套写法。
from __future__ import annotations

import fakeredis  # 进程内的 Redis。对照测试里的嵌入式 Redis，不是生产上的 Lettuce 客户端。


def main() -> None:
    """造两个客户端，对同一个键 set 再 get，看出「解码」只发生在客户端。

    步骤：
    1. 不解码的客户端写入 "hudi"，取出来应是字节 b'hudi'。
    2. 再取一个不存在的键，应是 None，不是 ""，也不抛异常。
    3. 解码的客户端再写一次、再取一次，取出来应是普通字符串 hudi，打印时没有 b。
    两个客户端各有自己的那份内存数据，不是连到同一台 Redis。所以 text 要自己再 set 一次。
    """

    # 生产要连真服务器时才用 redis.Redis(host=..., port=6379)。本课不创建那个对象，避免真的去连。
    # decode_responses=False 是默认值。写出来是为了和下面那个客户端对照。
    # 等号两边不空格，这是关键字参数。对照 new 的时候给一个命名参数。有空格也能跑，是这门课的写法约定。
    raw = fakeredis.FakeStrictRedis(decode_responses=False)
    # set(键, 值)。传入的是 str。客户端先按 UTF-8 编成字节，再交给「服务器」。对照 redis.set。
    raw.set("buyer", "hudi")  # 传入 str。客户端按 UTF-8 写成字节再交给服务器。
    # get 按键取值。键不存在时返回 None。对照缓存 get，未命中是 null。
    # print 几个参数之间用一个空格隔开。bytes 打印出来带 b 和引号，所以是 b'hudi'，不是 hudi。
    # b'hudi' 是字节字面量的样子。类型是 bytes，不是 str。对它当字符串用（比如和 "hudi" 用 + 拼）会抛 TypeError。
    print("不解码", raw.get("buyer"))
    # 键不存在。对照缓存未命中。Java 的 get 往往也是 null，不是空串，更不是抛「找不到键」。
    # None 是唯一的空对象。不要写成 if raw.get("missing") == ""，那是另一种情况：键在，值是空串。
    print("没有这个键", raw.get("missing"))

    # True：每次 get 把 UTF-8 字节解码成 str。键、命令都没变，变的是客户端要不要解码。
    # 这是另一个 FakeStrictRedis，内存是空的。上面 raw 里的 "buyer" 这里看不见。
    text = fakeredis.FakeStrictRedis(decode_responses=True)
    text.set("buyer", "hudi")
    print("解码", text.get("buyer"))  # 这一行没有 b。类型是 str。可以和别的 str 拼接、比较。


# 直接 python 本文件时 __name__ 才是 "__main__"，于是调用 main。被 import 时不自动连缓存。
# 对照类里的 main 不会因为别人引用了这个文件就自动跑。
if __name__ == "__main__":
    main()

# 这个脚本想说明的事：
# Redis 里存的是字节。redis-py 默认 get 回 bytes，打印出来带 b。Java 的 StringRedisTemplate 已经帮你解码了。
# decode_responses=True 只改变这个客户端的 get 结果，不改变服务器里的存法。
# 没有这个键得到 None。None、空字符串 ""、字节 b"" 是三件不同的东西，后面写 if hit 时不能混用。
