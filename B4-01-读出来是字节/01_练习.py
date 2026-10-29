from __future__ import annotations

import fakeredis

def main() -> None:
    raw = fakeredis.FakeStrictRedis(decode_responses=False)
    raw.set("phone","400-100-1000")
    print("不解码", raw.get("phone"))

    text = fakeredis.FakeStrictRedis(decode_responses=True)
    text.set("phone","400-100-1000")
    print("解码", text.get("phone"))
    print("没有这个键", text.get("empty"))

if __name__ == "__main__":
    main()

#  题2不知道，请在参考答案的注释中个给出