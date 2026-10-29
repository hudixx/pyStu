"""选修 B4 第 2 课：库改了，缓存不删，下一次读到的还是旧值。

对照 @CacheEvict。先改库，再删键。下一次读未命中，才从库里装进缓存。
ex=60 是秒。忘记删的时候，过一会键会自己消失。它不能代替这次删除。

库用一个字典代替。这课看的是缓存键，不是再写一遍 SQL。
"""

from __future__ import annotations

import fakeredis


def read_title(db: dict[str, str], cache: fakeredis.FakeStrictRedis) -> str:
    """先看缓存。没有，再读库，并把读到的值写回缓存。"""

    hit = cache.get("todo:1")  # 命中是 str。没有这个键是 None。不要写成 if hit，空串也是合法缓存。
    if hit is not None:
        return hit  # 命中就不再读库。库已经改了、键还在，这里返回的就是旧标题。
    value = db["title"]  # 未命中才读库。字典在这里代替已经提交的那一行。
    # ex=60：60 秒后这个键消失。关键字参数，等号两边不空格。这行不是删除，只是兜底。
    cache.set("todo:1", value, ex=60)
    return value


def change_title(db: dict[str, str], cache: fakeredis.FakeStrictRedis, title: str) -> None:
    """先改库，再删缓存。不要把新标题写进缓存来代替删除。"""

    db["title"] = title  # 真项目里这是 UPDATE，并且已经 commit。本课没有数据库连接。
    # delete 返回删掉的个数。键在时是 1，键本来就没有是 0。这里不打印它。
    # 先删再改库，进程若死在中间，下次读会装回旧值，还安全。先写缓存再改库，缓存会新、库会旧。
    cache.delete("todo:1")


def main() -> None:
    db = {"title": "买牛奶"}  # 冒号是字典的语法，不是类型标注。这一行是在造数据。
    cache = fakeredis.FakeStrictRedis(decode_responses=True)  # 上一课的结论：这课要的是 str。
    print("先读", read_title(db, cache))  # 未命中。读库，写入缓存。打印买牛奶。
    db["title"] = "买面包"  # 只改库，不删键。这是错误示范，下面那次读仍会命中旧值。
    print("忘记删除再读", read_title(db, cache))  # 命中。打印的还是买牛奶。
    # 标题这一次没有再变，还是买面包。调用它是为了走「改库然后删键」。上面那次没删，所以是旧的。
    change_title(db, cache, "买面包")
    print("删掉再读", read_title(db, cache))  # 键没了，重新读库。打印买面包。


if __name__ == "__main__":
    main()
