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
    """第一次把标题放进 orders。同一个消息号再来，列表长度不变。"""

    # nx=True：只有键不存在时才设置。返回 True 表示这次写成了。键已经在，返回 None，不是 False。
    # 键名带上消息号。两笔不同的单是两个键，互不影响。
    first = cache.set(f"done:{message_id}", "1", nx=True)
    if first is None:
        return "已经做过"  # 不要再 append。已经做过不是失败，是第二次投递。
    orders.append(title)  # 副作用只放在写键成功之后。写键之前就追加，第二次拦不住。
    return "完成"


def main() -> None:
    cache = fakeredis.FakeStrictRedis(decode_responses=True)
    # 冒号是类型标注，等号两边有空格。这是这次进程里的订单行，不是 Redis。
    orders: list[str] = []
    print(apply_once(cache, "A-1", "买牛奶", orders))  # 第一次。完成。
    print(apply_once(cache, "A-1", "买牛奶", orders))  # 同一个号。已经做过。列表不加。
    print(apply_once(cache, "A-2", "买面包", orders))  # 另一个号。完成。
    print(orders)  # 默认打印，方括号和单引号。不要自己用空格去拼。


if __name__ == "__main__":
    main()
