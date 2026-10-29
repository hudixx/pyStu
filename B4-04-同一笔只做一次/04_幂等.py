"""选修 B4 第 4 课：同一笔消息可能送来两次，副作用只能做一次。

对照幂等表。消息号做主键，第二次插入会被唯一约束拒绝。
这里用 SET 的 nx=True：键不存在才写入，而且是一条命令。成功返回 True，键已经在返回 None。
先查「做过没有」再追加，两个进程可以同时查到没有，于是做两次。nx 不会。

fakeredis 的键随这个进程结束就没了。下单、付钱不能只记在 Redis 里，要记在数据库的唯一键上。
上一课的死信不会自己回到队列。真要重新放回 jobs，处理函数仍得认出「已经做过」。
"""

from __future__ import annotations

import fakeredis


def apply_once(
    cache: fakeredis.FakeStrictRedis,
    message_id: str,
    title: str,
    orders: list[str],
) -> str:
    """第一次把标题放进 orders。同一个消息号再来，列表长度不变。

    逻辑：
    1. 用消息号做键，尝试 SET，并且带 nx=True。这条命令是「没有才写入」，检查和写入分不开。
    2. 返回 None：键已经在，说明这笔做过了。不 append，返回「已经做过」。
    3. 返回 True：这次写成了。这时才把标题放进 orders，返回「完成」。
    orders 是调用方传来的那个列表，不是拷贝。append 会改到调用方手里的那一份。对照方法参数是同一个 ArrayList。
    """

    # nx=True：只有键不存在时才设置。返回 True 表示这次写成了。键已经在，返回 None，不是 False。
    # 键名带上消息号。两笔不同的单是两个键，互不影响。
    # f"done:{message_id}" 把变量嵌进字符串。对照 "done:" + messageId。message_id 是 A-1 时，键是 done:A-1。
    first = cache.set(f"done:{message_id}", "1", nx=True)
    if first is None:
        # is None 只认「没写成」。不要写成 if not first：以后如果返回值变成 0 或空串，也会被当成没写成。
        return "已经做过"  # 不要再 append。已经做过不是失败，是第二次投递。
    orders.append(title)  # 副作用只放在写键成功之后。写键之前就追加，第二次拦不住。
    # append 对照 list.add。加在末尾。列表是可变对象，这里改的就是 main 里那个 orders。
    return "完成"


def main() -> None:
    """同一份订单列表上打三笔：A-1 两次，A-2 一次。

    预期打印：完成、已经做过、完成，然后列表是 ['买牛奶', '买面包']。
    A-1 的第二次没有再 append。A-2 是另一个消息号，所以还能加。
    """

    cache = fakeredis.FakeStrictRedis(decode_responses=True)  # get/set 的结果用 str，不用 bytes。
    # 冒号是类型标注，等号两边有空格。这是这次进程里的订单行，不是 Redis。
    # list[str] 对照 List<String>。= [] 才是造出一个空列表。只有标注、没有等号，不会造出列表。
    orders: list[str] = []
    print(apply_once(cache, "A-1", "买牛奶", orders))  # 第一次。完成。
    print(apply_once(cache, "A-1", "买牛奶", orders))  # 同一个号。已经做过。列表不加。
    print(apply_once(cache, "A-2", "买面包", orders))  # 另一个号。完成。
    print(orders)  # 默认打印，方括号和单引号。不要自己用空格去拼。
    # print 一个列表，走的是它的字符串形式，类似 ["买牛奶", "买面包"]。对照自己写循环拼接，这里不用。


if __name__ == "__main__":
    main()

# 这个脚本想说明的事：
# 同一笔消息可能到两次。能不能只做一次，不靠「先 get 看做过没有，再 append」。
# 那两步之间另一个执行也会看到「没有」，于是做两次。SET nx 把「没有才写入」收成一条命令。
# 写成了才产生副作用。返回 None 是「键已经在」，不是 False，也不是失败。
# 演示用的键在进程结束就没了。真正的下单、付钱要记在数据库的唯一键上，Redis 只是这里的替身。
