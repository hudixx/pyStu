"""选修 B4 第 2 课：库改了，缓存不删，下一次读到的还是旧值。

对照 @CacheEvict。先改库，再删键。下一次读未命中，才从库里装进缓存。
ex=60 是秒。忘记删的时候，过一会键会自己消失。它不能代替这次删除。

库用一个字典代替。这课看的是缓存键，不是再写一遍 SQL。
"""

from __future__ import annotations

import fakeredis


def read_title(db: dict[str, str], cache: fakeredis.FakeStrictRedis) -> str:
    """先看缓存。没有，再读库，并把读到的值写回缓存。

    逻辑：
    1. 取键 todo:1。得到字符串就是命中，直接返回，不再看 db。
    2. 得到 None 才是未命中。这时读 db["title"]，再 set 进缓存，过期时间 60 秒，然后返回这份新值。
    库已经改过、但键还在时，第 1 步就会把旧标题交出去。这就是本课要看见的错。

    db: dict[str, str] 是类型标注，对照 Map<String, String>。解释器不检查。
    """

    hit = cache.get("todo:1")  # 命中是 str。没有这个键是 None。不要写成 if hit，空串也是合法缓存。
    # if hit 会把空字符串也当成「没有」。空串是假值。这里要的是「键在不在」，所以用 is not None。
    # is 问是不是同一个对象。和 None 比较写 is，不写 ==。对照不要用 == null，而这里没有别的空对象。
    if hit is not None:
        return hit  # 命中就不再读库。库已经改了、键还在，这里返回的就是旧标题。
    value = db["title"]  # 未命中才读库。字典在这里代替已经提交的那一行。
    # db["title"] 对照 map.get，但键不存在会抛 KeyError，不是返回 null。要用默认值时写 db.get("title")。
    # ex=60：60 秒后这个键消失。关键字参数，等号两边不空格。这行不是删除，只是兜底。
    # 本课马上再读，60 秒远没到，所以过期帮不上「这次修改要立刻可见」。
    cache.set("todo:1", value, ex=60)
    return value


def change_title(db: dict[str, str], cache: fakeredis.FakeStrictRedis, title: str) -> None:
    """先改库，再删缓存。不要把新标题写进缓存来代替删除。

    逻辑：
    1. 把新标题写进字典，当作 UPDATE 已经 commit。
    2. 删掉 todo:1。下一次 read_title 才会未命中，从库里把新标题装回去。
    不在这里 cache.set 新标题。写缓存和改库若顺序反了，缓存会新、库会旧。
    """

    db["title"] = title  # 真项目里这是 UPDATE，并且已经 commit。本课没有数据库连接。
    # 给字典已有的键赋值，就是替换这个键的值。对照 map.put("title", title)。
    # delete 返回删掉的个数。键在时是 1，键本来就没有是 0。这里不打印它。
    # 先删再改库，进程若死在中间，下次读会装回旧值，还安全。先写缓存再改库，缓存会新、库会旧。
    cache.delete("todo:1")


def main() -> None:
    """走三遍读，把「忘了删」和「删了再读」对照出来。

    1. 库是买牛奶，缓存是空的。第一次读未命中，缓存里写入买牛奶。
    2. 只把库改成买面包，不删键。再读仍命中，打印买牛奶。这是错误示范。
    3. 走 change_title：库保持买面包，并删键。再读未命中，打印买面包。
    """

    db = {"title": "买牛奶"}  # 冒号是字典的语法，不是类型标注。这一行是在造数据。
    # {"title": "买牛奶"} 对照 Map.of("title", "买牛奶")。键和值用冒号，项和项用逗号。
    # 空字典写 {}。这和空集合相反：空集合必须写 set()，写成 {} 得到的是字典。
    cache = fakeredis.FakeStrictRedis(decode_responses=True)  # 上一课的结论：这课要的是 str。
    print("先读", read_title(db, cache))  # 未命中。读库，写入缓存。打印买牛奶。
    db["title"] = "买面包"  # 只改库，不删键。这是错误示范，下面那次读仍会命中旧值。
    print("忘记删除再读", read_title(db, cache))  # 命中。打印的还是买牛奶。
    # 标题这一次没有再变，还是买面包。调用它是为了走「改库然后删键」。上面那次没删，所以是旧的。
    change_title(db, cache, "买面包")
    print("删掉再读", read_title(db, cache))  # 键没了，重新读库。打印买面包。


if __name__ == "__main__":
    main()

# 这个脚本想说明的事：
# 缓存是库的一份副本。库改了，键还在，读路径会直接返回旧值，不会好心再去看库。
# 改完要删键，让下一次读未命中再装。过期时间只是忘了删时的兜底，不能代替这一次 delete。
# 判断命中用 is not None。写成 if hit 会把缓存里的空字符串当成没有。
