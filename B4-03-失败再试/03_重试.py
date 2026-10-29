"""选修 B4 第 3 课：失败可以再试，但有次数。用完就放进死信，不再回到原队列。

对照消息队列的重试和死信。本课不装 Celery，也不启动工人进程。
队列就是 Redis 的 list。lpush 从左边放，rpop 从右边拿，先放进去的先被拿走。
rpop 在空列表上立刻返回 None。brpop 会一直等。这里没有另一个进程往里放，用 brpop 会停住。

同一笔消息可能做了两次。下一次课处理这件事。这一课先把「别无限重试」写对。
"""

from __future__ import annotations

import json  # 任务要放进字符串里。Redis 的 list 存的是字符串，不是 Python 字典。

import fakeredis

MAX_ATTEMPTS = 2  # 含第一次。第 2 次还失败，就不再放回 jobs。


def run_job(job: dict[str, object]) -> None:
    """A-1 只有第 1 次失败。A-2 每次都失败。"""

    attempt = int(job["attempt"])  # JSON 的数字读出来是 int。若是 str，和 2 比会抛 TypeError。
    if job["id"] == "A-1" and attempt < MAX_ATTEMPTS:
        raise RuntimeError("暂时失败")  # 第 1 次进来。第 2 次 attempt 是 2，这个条件不成立。
    if job["id"] == "A-2":
        raise RuntimeError("暂时失败")  # 不看次数。用来演示死信。


def enqueue(cache: fakeredis.FakeStrictRedis, job_id: str) -> None:
    """放一笔新任务。次数从 1 开始。"""

    job = {"id": job_id, "attempt": 1}
    # ensure_ascii=False：以后值里有中文时，不要存成 \\uXXXX。本课的 id 是英文，开了也一样。
    # lpush 的返回值是列表现在的长度。这里不用。
    cache.lpush("jobs", json.dumps(job, ensure_ascii=False))


def drain(cache: fakeredis.FakeStrictRedis) -> None:
    """处理完现在队列里的任务就停。不等人家再塞新的。"""

    while True:
        raw = cache.rpop("jobs")  # 空了是 None。不要换成 brpop，那个会卡住。
        if raw is None:
            return
        job = json.loads(raw)  # decode_responses=True，所以 raw 是 str，不是 bytes。
        attempt = int(job["attempt"])
        try:
            run_job(job)
        except RuntimeError:
            print(f"第{attempt}次 暂时失败")
            if attempt >= MAX_ATTEMPTS:
                # 放进另一个 list。不要再 lpush 回 jobs，不然这笔会永远被拿出来、再失败、再放回。
                cache.lpush("dead", json.dumps(job, ensure_ascii=False))
            else:
                # 下次拿出来就是第 2 次。改的是这份字典，然后下面重新序列化。
                job["attempt"] = attempt + 1
                cache.lpush("jobs", json.dumps(job, ensure_ascii=False))
        else:
            # 没有抛异常才走到这里。失败的那次已经在 except 里打印过了。
            print(f"第{attempt}次 完成")


def main() -> None:
    # 两笔各用一个新的客户端。死信个数就不会叠在一起。
    first = fakeredis.FakeStrictRedis(decode_responses=True)
    print("会好的那笔")
    enqueue(first, "A-1")
    drain(first)
    print("死信", first.llen("dead"))  # 0。llen 对没有的键也是 0，不是 None。

    second = fakeredis.FakeStrictRedis(decode_responses=True)
    print("一直失败的那笔")
    enqueue(second, "A-2")
    drain(second)
    # lindex 0 是列表左边第一个。死信只有一笔，就是刚才 lpush 进去的那份 JSON。
    saved = json.loads(second.lindex("dead", 0))
    print("死信", second.llen("dead"), saved["id"])


if __name__ == "__main__":
    main()
