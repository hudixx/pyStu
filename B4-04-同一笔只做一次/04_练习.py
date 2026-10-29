from __future__ import print_function

import fakeredis


def apply_once(
        cache: fakeredis.FakeStrictRedis,
        message_id: str,
        title: str,
        orders: list[str],
) -> str:
    flag = cache.set(f"done:{message_id}", "1", nx=True)
    if flag is None:
        return "已经做过"
    else:
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

#  题2不知道，请在参考答案的注释中个给出