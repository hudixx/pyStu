# 第 52 课：从 Flyway 看版本表

第 50 课的 `create_all` 只适合演示。它不会帮你改一张已经有数据的表，也不会告诉你这台机器执行过哪一版。

运行：

```bash
PYTHONUTF8=1 python 52-版本表迁移/52_迁移.py
```

第一次应打印 `['001']`。第二次应打印 `[]`。库里有 `schema_versions` 和 `todos`。

---

## 1. 执行过的版本记下来

```text
001 的 SQL 还没在 schema_versions 里 → 执行，再插入版本号
已经有 001 → 跳过
```

对照 Flyway 的 `flyway_schema_history`。Alembic 也是这个循环，只是 SQL 由它生成，入口是 `alembic upgrade`。本课不生成那一层，避免第一次就读 `env.py`。

建表和插入版本号放在同一个 `engine.begin()` 里。建表成功、记账失败，下次还会再执行 `CREATE TABLE`，然后因为表已存在而失败。

---

## 本课肌肉记忆

1. 变更有编号，执行过就跳过
2. 记账和变更在同一个事务
3. 启动时 `create_all` 不是迁移
