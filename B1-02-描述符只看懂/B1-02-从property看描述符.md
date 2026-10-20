# 选修 B1 第 2 课：从 property 看描述符

点一个属性时，不一定是去读袋子里的值。有些属性被点到时会跑一段代码。这种对象叫描述符。

运行：

```bash
PYTHONUTF8=1 python B1-02-描述符只看懂/02_描述符.py
```

应看到：

```text
类上 Positive
实例 100
拒绝 不能为负
property 100
类上的 property property
```

---

## 1. 只求看懂

`Account.balance` 写在类上，点它得到的是 `Positive` 自己。`account.balance` 点它，才进 `__get__`，读到 `100`。

这就是第 50 课里两件不同的事：

- 类上的 `Todo.title` 是列
- 某一行上的 `row.title` 是这行的标题

`@property` 是同一套机制，只是语言帮你写好了。`Ticket.price` 在类上是 `property`，在实例上才是整数。

这一课不写 ORM，不写 `mapped_column`。能认出 `__get__` 和 `__set__` 就够了。

---

## 本课肌肉记忆

1. 类上点到的，可能是描述符，不是那份值
2. `property` 就是描述符
3. 看懂即可，不自己做框架
