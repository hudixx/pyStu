"""选修 B4 第 2 课参考答案。题 1 过了。题 2 写在下面。

运行 02_练习.py 看到：

买牛奶
None
买豆浆

read_title 先看 todo:1，没有才读库。change_title 先改字典，再 delete。
改完立刻 get，是 None。下一次读才重新装上买豆浆。没有把新标题 set 进缓存。

cache.set("todo:1", hit, 60) 这个 60 能生效，是因为 set 的第三个参数正好叫 ex，单位是秒。
下一个参数是 px，单位是毫秒。位置一旦变了，60 就会落到别的意思上。写成 ex=60。
函数和函数之间少了一行空行。本课 ruff 没报。

题 2：
- 改完要删键，不是把新标题写进缓存。甲可能已经读到旧标题。乙改完库并删了键之后，
  甲再把旧标题 set 回去，缓存又旧了。删键不会把旧值写回去。下一次谁读，都再问库。
- ex=60 是 60 秒后键自己消失。这次读就在改完的下一行，60 秒远没到，键还在，读到的仍是旧标题。
  它是忘记删除时的兜底，不是这次更新要立刻可见的办法。
"""

from __future__ import annotations

import fakeredis


def read_title(db: dict[str, str], cache: fakeredis.FakeStrictRedis) -> str:
    hit = cache.get("todo:1")
    if hit is not None:
        return hit
    value = db["title"]
    cache.set("todo:1", value, ex=60)
    return value


def change_title(db: dict[str, str], cache: fakeredis.FakeStrictRedis, title: str) -> None:
    db["title"] = title
    cache.delete("todo:1")


def main() -> None:
    cache = fakeredis.FakeStrictRedis(decode_responses=True)
    db = {"title": "买牛奶"}
    print(read_title(db, cache))
    change_title(db, cache, "买豆浆")
    print(cache.get("todo:1"))
    print(read_title(db, cache))


if __name__ == "__main__":
    main()
