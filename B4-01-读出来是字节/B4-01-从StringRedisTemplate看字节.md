# 选修 B4 第 1 课：从 StringRedisTemplate 看字节

Redis 里存的是字节。`redis-py` 默认把字节原样交给你。`StringRedisTemplate` 会先解码成字符串，所以 Java 里不容易看见这件事。

本课不启动 Redis，不写地址，也不写密码。`fakeredis` 在进程里实现同一套命令。

先装依赖（装过一次就不用再装）：

```bash
python -m pip install -e ".[cache]"
PYTHONUTF8=1 python B4-01-读出来是字节/01_缓存.py
```

应看到：

```text
不解码 b'hudi'
没有这个键 None
解码 hudi
```

---

## 1. 两处不要看错

| 这一课 | 结果 | Java |
|---|---|---|
| 默认 `get` | `b'hudi'`，类型是 `bytes` | 没配序列化的 `RedisTemplate` |
| `decode_responses=True` | `hudi`，类型是 `str` | `StringRedisTemplate` |
| 没有这个键 | `None` | 未命中，一般是 `null` |

`decode_responses=True` 只改客户端。服务器不会因此改成「存字符串」。后面三课都打开它，省得每次自己 `decode`。

没有这个键不是 `""`。用 `if hit is not None` 判断命中。`if hit` 会把空字符串也当成没有。

---

## 本课肌肉记忆

1. 默认拿到的是 `bytes`
2. 要字符串就在客户端解码
3. 没有这个键是 `None`
