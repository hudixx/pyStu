"""选修 B4 第 4 课参考答案。题 1 过了。题 2 写在下面。选修 B4 到这里结束。

运行 04_练习.py 看到：

完成
已经做过
完成
['买牛奶', '买豆浆']

A-1 做了两次，列表里只有一条买牛奶。A-2 是另一个号，加上了买豆浆。
用的是 set 的 nx=True。没有先 get 再追加。

文件开头是 from __future__ import print_function。这是 Python 2 里把 print 变成函数的开关。
Python 3 里 print 本来就是函数。这门课用的是 from __future__ import annotations。这行不影响这四行输出。

if not flag 这次没有问题。这一行的 set 只返回 True 或 None，不返回 False、0 或空字符串。
None 在 if 里是假，所以和 flag is None 结果一样。
换方法才会变：setnx 失败返回 False，不是 None。那时 is None 对不上，if not flag 仍然对。
再加上 get=True 之后，返回的是旧值，不是成没写成。第一次成功也是 None，两种判断都会错。
if 里已经 return，下面的 else 可以不写。

题 2：
- 先 get 再追加，中间可以插进另一次执行。两边都看见「没有」，于是各加一行。
  nx=True 把「没有才写入」收成一条命令，只有一个能写成。写成了才 append。
- fakeredis 的键随进程结束就没了。真 Redis 也会重启、内存满了丢键。
  键写成了、订单还没写进库，进程若在这中间死掉，下次再来会看到键已在，于是跳过，订单丢了。
  下单、付钱要把消息号写成数据库的唯一键，和订单放在同一个事务里。Redis 只能挡一层很快的重复请求。
"""

from __future__ import annotations

import fakeredis


def apply_once(
    cache: fakeredis.FakeStrictRedis,
    message_id: str,
    title: str,
    orders: list[str],
) -> str:
    first = cache.set(f"done:{message_id}", "1", nx=True)
    if first is None:
        return "已经做过"
    orders.append(title)
    return "完成"


def main() -> None:
    orders: list[str] = []
    cache = fakeredis.FakeStrictRedis(decode_responses=True)
    print(apply_once(cache, "A-1", "买牛奶", orders))
    print(apply_once(cache, "A-1", "买牛奶", orders))
    print(apply_once(cache, "A-2", "买豆浆", orders))
    print(orders)


if __name__ == "__main__":
    main()
