"""选修 B4 第 3 课参考答案。题 1 过了。题 2 写在下面。

运行 03_练习.py 看到：

会好的那笔
第1次 暂时失败
第2次 完成
死信 0
一直失败的那笔
第1次 暂时失败
第2次 暂时失败
死信 1 C-2

C-1 第 1 次失败、第 2 次完成。C-2 两次都失败，进了 dead，没有再回到 jobs。
用的是 rpop，不是 brpop。

两笔共用了一个客户端。题目写了各用一个新的。这次第一笔没进死信，个数没有叠上，所以最后仍是 1 C-2。
新的 FakeStrictRedis() 是另一块空内存，不是连到同一份数据的第二个连接。
第一笔如果也进了死信：共用客户端时 llen 是 2，lindex 0 仍是后 lpush 的 C-2；新客户端的 dead 从 0 开始，llen 是 1。
真 Redis 上两个客户端连同一台，看的是同一份列表，新开一个不会把死信清掉。
if 条件的右括号前面多了一个空格。本课 ruff 没报。

题 2：
- 次数用完还放回 jobs，这笔会永远被拿出来、再失败、再放回。后面的任务排不上，循环也不会停。
  放进 dead 是等人来看。再试不会把一笔坏消息修好。
- rpop 发现列表是空的，立刻返回 None。brpop 会停在那里等下一笔。
  这个练习里没有另一个人往队列里放，用 brpop 进程就停住了。
"""

from __future__ import annotations

import json

import fakeredis

MAX_ATTEMPTS = 2


def run_job(job: dict[str, object]) -> None:
    attempt = int(job["attempt"])
    if job["id"] == "C-1" and attempt < MAX_ATTEMPTS:
        raise RuntimeError("失败")
    if job["id"] == "C-2":
        raise RuntimeError("失败")


def enqueue(cache: fakeredis.FakeStrictRedis, job_id: str) -> None:
    job = {"id": job_id, "attempt": 1}
    cache.lpush("jobs", json.dumps(job, ensure_ascii=False))


def drain(cache: fakeredis.FakeStrictRedis) -> None:
    while True:
        raw = cache.rpop("jobs")
        if raw is None:
            return
        job = json.loads(raw)
        attempt = int(job["attempt"])
        try:
            run_job(job)
        except RuntimeError:
            print(f"第{attempt}次 暂时失败")
            if attempt >= MAX_ATTEMPTS:
                cache.lpush("dead", json.dumps(job, ensure_ascii=False))
            else:
                job["attempt"] = attempt + 1
                cache.lpush("jobs", json.dumps(job, ensure_ascii=False))
        else:
            print(f"第{attempt}次 完成")


def main() -> None:
    first = fakeredis.FakeStrictRedis(decode_responses=True)
    print("会好的那笔")
    enqueue(first, "C-1")
    drain(first)
    print("死信", first.llen("dead"))

    second = fakeredis.FakeStrictRedis(decode_responses=True)
    print("一直失败的那笔")
    enqueue(second, "C-2")
    drain(second)
    saved = json.loads(second.lindex("dead", 0))
    print("死信", second.llen("dead"), saved["id"])


if __name__ == "__main__":
    main()
