from __future__ import annotations

import fakeredis

def read_title(db: dict[str, str], cache: fakeredis.FakeStrictRedis) -> str:
    hit = cache.get("todo:1")
    if hit is not None:
        return hit
    hit = db["title"]
    cache.set("todo:1", hit, ex=60)
    return hit

def change_title(db: dict[str, str], cache: fakeredis.FakeStrictRedis, title: str) -> None:
    db["title"] = title
    cache.delete("todo:1")

def main() -> None:
    cache = fakeredis.FakeStrictRedis(decode_responses=True)
    db = {"title": "买牛奶"}
    text = read_title(db, cache)
    print(text)
    change_title(db, cache, "买豆浆")
    print(cache.get("todo:1"))
    text = read_title(db, cache)
    print(text)

if __name__ == "__main__":
    main()

#  题2不知道，请在参考答案的注释中个给出