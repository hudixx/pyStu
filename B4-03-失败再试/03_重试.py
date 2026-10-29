"""选修 B4 第 3 课：失败可以再试，但有次数。用完就放进死信，不再回到原队列。

对照消息队列的重试和死信。本课不装 Celery，也不启动工人进程。
队列就是 Redis 的 list。lpush 从左边放，rpop 从右边拿，先放进去的先被拿走。
rpop 在空列表上立刻返回 None。brpop 会一直等。这里没有另一个进程往里放，用 brpop 会停住。

同一笔消息可能做了两次。下一次课处理这件事。这一课先把「别无限重试」写对。
"""

from __future__ import annotations

import json  # 任务要放进字符串里。Redis 的 list 存的是字符串，不是 Python 字典。

import fakeredis

# 全大写是「请别改」的约定，不是真的常量。别人仍能给 MAX_ATTEMPTS 重新赋值。
MAX_ATTEMPTS = 2  # 含第一次。第 2 次还失败，就不再放回 jobs。


def run_job(job: dict[str, object]) -> None:
    """按任务号决定这次算不算失败。成功时什么都不返回。

    逻辑：
    - A-1：第 1 次抛 RuntimeError，第 2 次（attempt 已经是 2）不再抛，当作做好了。
    - A-2：每次都抛，用来把它送进死信。
    - 别的 id：不抛，也算成功。本课没有这样的数据。
    job 标成 dict[str, object]：键是字符串，值先不限定。对照 Map<String, Object>。
    """

    attempt = int(job["attempt"])  # JSON 的数字读出来是 int。若是 str，和 2 比会抛 TypeError。
    # int(...) 是内置函数，把值收成整数。对照 Integer.parseInt，但这里传入的本来就是 int 时，结果还是 int。
    # job["attempt"] 键不存在会抛 KeyError。对照 map.get 得到 null 再拆箱，这里是直接抛。
    if job["id"] == "A-1" and attempt < MAX_ATTEMPTS:
        # and 短路：左边已经是假，右边不再看。对照 &&。
        raise RuntimeError("暂时失败")  # 第 1 次进来。第 2 次 attempt 是 2，这个条件不成立。
        # raise 对照 throw。RuntimeError 是普通运行错误。调用方用 except 接住，任务本身不负责重试。
    if job["id"] == "A-2":
        raise RuntimeError("暂时失败")  # 不看次数。用来演示死信。


def enqueue(cache: fakeredis.FakeStrictRedis, job_id: str) -> None:
    """放一笔新任务。次数从 1 开始。

    逻辑：造一个只有 id 和 attempt 的字典，dumps 成 JSON 字符串，从左边推进 jobs 这个 list。
    Redis 的 list 不能直接存字典，所以要先变成文本。
    """

    job = {"id": job_id, "attempt": 1}  # 花括号加冒号是字典。对照 Map.of("id", jobId, "attempt", 1)。
    # ensure_ascii=False：以后值里有中文时，不要存成 \\uXXXX。本课的 id 是英文，开了也一样。
    # dumps 把字典变成 str。对照 writeValueAsString。loads 是反方向，把 str 变回字典。
    # lpush 的返回值是列表现在的长度。这里不用。
    # lpush 从左边放。和下面的 rpop（从右边拿）配在一起，先放进去的先被拿走。对照队列的入队和出队。
    cache.lpush("jobs", json.dumps(job, ensure_ascii=False))


def drain(cache: fakeredis.FakeStrictRedis) -> None:
    """处理完现在队列里的任务就停。不等人家再塞新的。

    逻辑，循环直到右边拿不到东西：
    1. rpop。得到 None 就 return，函数结束。
    2. 把 JSON 变回字典，读出这次是第几次。
    3. 调用 run_job。没抛异常就打印「完成」。
    4. 抛了 RuntimeError：次数用尽就推进 dead，否则 attempt 加 1 再推进 jobs，下一轮还能拿到。
    只抓 RuntimeError。别的异常（比如 JSON 坏了）会让这个循环停掉，不会被当成「再试一次」。
    """

    while True:
        # while True 是无限循环。出口是下面的 return，不是一个布尔条件。对照 for (;;) 加 return。
        raw = cache.rpop("jobs")  # 空了是 None。不要换成 brpop，那个会卡住。
        # rpop 从右边弹出一项，列表里就少了这一项。对照 queue.poll()，没有就返回 null，不等待。
        if raw is None:
            return  # 结束整个 drain，不是 continue。队列空了就停。
        job = json.loads(raw)  # decode_responses=True，所以 raw 是 str，不是 bytes。
        # loads 对照 readValue。传入 bytes 会失败，所以上一课要把客户端设成解码。
        attempt = int(job["attempt"])
        try:
            run_job(job)
        except RuntimeError:
            # 只接这一类。对照 catch (RuntimeException e)，但这里不需要异常对象，所以不写 as。
            print(f"第{attempt}次 暂时失败")
            # f"..." 是格式化字符串。{attempt} 会换成那个整数。对照 "第" + attempt + "次"，但整数要先变成文字，f-string 自己会转。
            if attempt >= MAX_ATTEMPTS:
                # 放进另一个 list。不要再 lpush 回 jobs，不然这笔会永远被拿出来、再失败、再放回。
                cache.lpush("dead", json.dumps(job, ensure_ascii=False))
            else:
                # 下次拿出来就是第 2 次。改的是这份字典，然后下面重新序列化。
                # job["attempt"] = ... 是给字典的这个键换一个新值。对照 map.put。
                job["attempt"] = attempt + 1
                cache.lpush("jobs", json.dumps(job, ensure_ascii=False))
        else:
            # try 的 else：没有抛异常才走到这里。对照 try 里成功才执行的代码，不要和 if 的 else 搞混。
            # Java 的 try 没有 else。失败的那次已经在 except 里打印过了，不会再进这里。
            print(f"第{attempt}次 完成")


def main() -> None:
    """两笔任务各用一个新的客户端，避免死信个数叠在一起。

    A-1 会失败一次再成功，dead 的长度是 0。
    A-2 会失败两次后进死信，长度是 1，并且能从左边第 0 项读回它的 id。
    """

    # 两笔各用一个新的客户端。死信个数就不会叠在一起。
    first = fakeredis.FakeStrictRedis(decode_responses=True)
    print("会好的那笔")
    enqueue(first, "A-1")
    drain(first)
    print("死信", first.llen("dead"))  # 0。llen 对没有的键也是 0，不是 None。
    # llen 是 list 的长度。对照 list.size()。键从未写过时也是 0，不会抛「没有这个键」。

    second = fakeredis.FakeStrictRedis(decode_responses=True)
    print("一直失败的那笔")
    enqueue(second, "A-2")
    drain(second)
    # lindex 0 是列表左边第一个。下标从 0 开始，和 Python 列表一样。对照 list.get(0)。
    # 死信只有一笔，就是刚才 lpush 进去的那份 JSON。空列表这样取会得到 None，再 loads 会抛。
    saved = json.loads(second.lindex("dead", 0))
    print("死信", second.llen("dead"), saved["id"])


if __name__ == "__main__":
    main()

# 这个脚本想说明的事：
# 队列用 list 就能模拟：左边进、右边出。失败可以放回原队列，但必须带上次数。
# 次数用尽就放进另一个 list（死信），不要再回到 jobs，否则会无限失败、无限重试。
# rpop 没有数据立刻返回 None。brpop 会一直等，本课没有别的进程往里放，用它进程就停住了。
# try 的 else 不是「出错了」，是「没出错才走」。这是 Python 有、Java 没有的语法。
