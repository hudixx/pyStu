from __future__ import annotations

import fakeredis
import json

MAX_ATTEMPTS = 2

def run_job(job: dict[str, object]) -> None:
    attempt = int(job["attempt"])

    if (job["id"] == "C-1" and attempt < MAX_ATTEMPTS ) or (job["id"] == "C-2"):
        raise RuntimeError("失败")

def enqueue(cache: fakeredis.FakeStrictRedis, job_id: str) -> None:
    job = {"id": job_id, "attempt": 1}
    cache.lpush("jobs", json.dumps(job, ensure_ascii=False))

def drain(cache: fakeredis.FakeStrictRedis) -> None:
    while True:
        job = cache.rpop("jobs")
        if job is None:
            return
        job = json.loads(job)
        attempt = int(job["attempt"])
        try:
            run_job(job)
        except RuntimeError:
            print(f"第{attempt}次 暂时失败")
            if attempt < MAX_ATTEMPTS:
                job["attempt"] = attempt + 1
                cache.lpush("jobs", json.dumps(job, ensure_ascii=False))
            else:
                cache.lpush("dead", json.dumps(job, ensure_ascii=False))

        else:
            print(f"第{attempt}次 完成")

def main() -> None:
    cache = fakeredis.FakeStrictRedis(decode_responses=True)
    print("会好的那笔")
    enqueue(cache, "C-1")
    drain(cache)
    print("死信", cache.llen("dead"))
    enqueue(cache, "C-2")
    print("一直失败的那笔")
    drain(cache)
    print("死信", cache.llen("dead"), json.loads(cache.lindex("dead", 0))["id"])

if __name__ == "__main__":
    main()
#  题2不知道，请在参考答案的注释中个给出