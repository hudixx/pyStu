# 选修 B2 第 4 课：从 EntityGraph 看加载策略

关系可以设成「没加载就不许再查」。要用订单，就在这一次查询上写明。

运行：

```bash
PYTHONUTF8=1 python B2-04-先声明再加载/04_加载.py
```

应看到：

```text
没加载 InvalidRequestError
selectin 买牛奶
joined 买牛奶
```

---

## 1. 三种选择

| 写法 | 查询 | 适合 | Java |
|---|---|---|---|
| `lazy="raise"`，查询上什么都不加 | 点到关系就失败 | 不想在视图里偷偷再查 | 关掉 Open Session In View 之后漏加载就失败 |
| `selectinload` | 先查用户，再一条 `IN` 查订单 | 集合。两个用户不会把用户行乘开 | `@BatchSize` 或按批的图 |
| `joinedload` | 一条 `JOIN` | 多对一，或你确定行数不会乘得很大 | `JOIN FETCH` |

`joinedload` 之后要 `.unique()`。一条用户配两张订单时，SQL 返回两行用户。`unique()` 按主键收成一个用户。不收的话，`.one()` 会看到两行。

`selectinload` 和 `joinedload` 都只作用于这一次查询。映射上的 `lazy="raise"` 仍然是默认：忘了写 `options`，就失败。这比在循环里悄悄多查一次更容易发现。

---

## 本课肌肉记忆

1. 要加载的关系写在这次查询上
2. 集合常用 `selectinload`，多对一常用 `joinedload`
3. `raise` 用来让漏加载立刻失败
