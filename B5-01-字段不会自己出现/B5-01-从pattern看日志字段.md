# 选修 B5 第 1 课：从 pattern 看日志字段

`extra` 里的字段不会自己出现在日志行上。格式里没有写它，它就不在。对照 logback：pattern 里没有 `%X{buyer}`，MDC 放了也打不出来。

第 48 课规定一次模型调用留下哪些栏。这一课看日志库怎么把栏交出去。不装采集器。

运行：

```bash
PYTHONUTF8=1 python B5-01-字段不会自己出现/01_日志.py
```

应看到：

```text
默认 下单
带字段 {"event": "下单", "buyer": "hudi", "title": "买牛奶"}
```

两行用的是同一次 `logger.info`。差在 Formatter。

---

## 1. 字段挂在记录上

`extra={"buyer": "hudi", "title": "买牛奶"}` 把这两个名字挂到 `LogRecord` 上。默认格式 `"%(message)s"` 只取消息，所以第一行只有「下单」。

`FieldFormatter` 自己读 `record.buyer` 和 `record.title`，收成一行 JSON。

`extra` 的键不要用 `message`、`name`、`args`。那是 `LogRecord` 自己的，会抛 `KeyError`。

不要写成 `logger.info(f"下单 {title}")`。等级关掉时，这个 f-string 也已经拼完了。字段放在 `extra` 里，格式不去读，就只是没打出来。

---

## 本课肌肉记忆

1. `extra` 不会自己出现
2. 格式里写了，字段才在行上
3. 不要用 f-string 把字段拼进消息
