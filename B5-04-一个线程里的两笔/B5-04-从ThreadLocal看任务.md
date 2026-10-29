# 选修 B5 第 4 课：从 ThreadLocal 看任务

一条线程上有两笔任务时，`threading.local` 只有一份。后写的盖掉先写的。`contextvars` 各有一份。

对照 `ThreadLocal`。它能隔开，是因为一笔请求占住一条线程。asyncio 不是这样。

运行：

```bash
PYTHONUTF8=1 python B5-04-一个线程里的两笔/04_任务.py
```

应看到：

```text
A local B context A
B local B context B
```

`A` 让出之后，`B` 把 `local.value` 写成了 `B`。`A` 再回来，`local` 已经是 `B`，自己的 `context` 仍是 `A`。

---

## 1. await 不换线程

`await asyncio.sleep(0)` 只是把这条线程让给另一笔任务，线程没有换。所以 `threading.local` 不会「因为 await 就丢失」。只有一笔任务时，让出再回来，`local` 还是它写的那个。

两笔用 `gather` 排在一起，中间这一让就串了。`contextvars` 在任务创建时复制，`B` 的 `set` 改不到 `A` 的那一份。

生产里把这个号放进第 1 课的日志字段，或者交给 OpenTelemetry。本课不装采集器。不要把 `threading.local` 当成请求号的存放处。

---

## 本课肌肉记忆

1. 一条线程上的任务共用一份 `threading.local`
2. `contextvars` 按任务复制
3. 串号发生在两笔交错的时候，不是 `await` 本身换了线程
