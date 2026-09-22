# 第 12 课：从 Java 线程看 GIL

Java 里 CPU 密集任务丢线程池，常常能把多核吃满。
**CPython 不行。** 原因叫 GIL（Global Interpreter Lock）：同一时刻只有一个线程在执行 Python 字节码。

所以：

- **IO 密集**（等网络、等磁盘、`sleep`）：线程有用，等待时会释放 GIL
- **CPU 密集**（纯 Python 算数字）：线程几乎不加速，要用 **多进程**

运行示例（大约几秒到十几秒，看机器）：

若 CPU 那组「进程池」比「线程池」还慢：任务太轻，进程启动开销占了大头。这不能推翻 GIL——把循环加大，或只看 IO 那组（线程应约为串行的 1/4）。

```bash
PYTHONUTF8=1 python 12-并发与GIL/12_并发.py
```

---

## 1. 高层 API：`concurrent.futures` ≈ `ExecutorService`

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

with ThreadPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(download, urls))

with ProcessPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(heavy_calc, nums))
```

| Java | Python |
|---|---|
| `ExecutorService.submit` | `executor.submit(fn, *args)` → `Future` |
| `invokeAll` / `stream.parallel` | `executor.map(fn, iterable)` |
| `ThreadPoolExecutor` | `ThreadPoolExecutor`（名字都一样） |
| 多进程要自己上 | `ProcessPoolExecutor` 标准库就有 |

`Future.result()` 会阻塞等到结果，异常会在 `.result()` 时重新抛出。

`threading.Thread` 也能用，但日常优先 futures，少自己 `start/join`。

---

## 2. GIL 到底锁了什么

CPython 解释器里有一把全局锁。线程在跑 Python 字节码前必须拿到它。
扩展模块（如 `time.sleep`、很多 IO、部分 numpy）会在等待时 **主动释放 GIL**，所以其它线程能跑。

纯 Python 的 `for i in range(10_000_000): x += 1` 几乎不释放 GIL，四个线程 ≈ 一个线程的时间，还可能更慢（抢锁）。

这不是语言理论限制，是 **CPython 实现** 的选择。Jython / IronPython 没有这把锁，但你现在用的就是 CPython 3.13。

3.13 开始有可选的「自由线程」实验构建，默认发行版 **仍然有 GIL**。先按「有 GIL」来设计。

---

## 3. 怎么选

| 场景 | 用什么 | 不要用什么 |
|---|---|---|
| 等 HTTP / 文件 / 数据库 | `ThreadPoolExecutor` | 为 IO 去上进程（太重） |
| 纯 Python 算 CPU | `ProcessPoolExecutor` | `ThreadPoolExecutor`（加速不了） |
| 大量高并发 IO | 以后再学 `asyncio` | 先别为了酷去上 |
| 共享可变状态 | 尽量不共享；要共享加 `Lock` | 裸改同一个 list/dict |

多进程是真·多核，但：

- 参数和返回值要能 pickle 序列化
- 每个进程有独立内存，不像 Java 线程共享堆那么随便
- Windows 上入口必须在 `if __name__ == "__main__":` 里启动进程池，否则会递归派生子进程

---

## 4. `asyncio` 一句话

对标 Java 的 NIO / WebFlux：单线程事件循环 + 协程。适合海量连接。
API 是 `async def` / `await`。基础阶段 **不要求写**。知道「第三种并发模型」即可。

---

## 本课肌肉记忆

1. CPython 有 GIL：线程吃不满多核 CPU
2. IO 用线程池，CPU 用进程池
3. 优先 `concurrent.futures`，少手搓 Thread
4. Windows 多进程必须放在 `if __name__ == "__main__":`
5. 能不共享可变状态就不共享

下一课扫标准库和 pip 生态，对照 JDK + Maven Central。
