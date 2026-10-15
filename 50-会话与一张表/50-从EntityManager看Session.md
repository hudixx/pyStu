# 第 50 课：从 EntityManager 看 Session

待办不再放在第 38 课那个内存列表里。列表只活在当前进程。表里的一行，提交之后还在。

先装依赖（虚拟环境里）：

```bash
python -m pip install -e ".[db]"
PYTHONUTF8=1 python 50-会话与一张表/50_会话.py
```

应打印一行：`1 买牛奶`。库是 SQLite 内存库，脚本结束就没了，不会在目录里留下 db 文件。

---

## 1. 三个东西不要混

| 这一课 | Java |
|---|---|
| `Todo` 类 | `@Entity` |
| `Session` | `EntityManager`，一次工作单元 |
| `commit()` | 事务提交。没提交，别的会话看不到 |

`session.add` 只是放进会话。`commit` 才写进库。对照 `persist` 和 `commit` 不是同一步。

模型（大语言模型）不存待办。它最多返回一张工单。写库的是你的 `Session`。

---

## 本课肌肉记忆

1. 实体是表，不是内存列表
2. `add` 之后还要 `commit`
3. `Session` 用 `with` 关掉
