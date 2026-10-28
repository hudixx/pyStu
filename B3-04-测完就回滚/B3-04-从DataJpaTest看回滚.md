# 选修 B3 第 4 课：从 DataJpaTest 看回滚

测试里可以 `commit`。夹具结束时把外层事务滚回去，下一份测试看不到「买牛奶」。

先确认依赖（装过一次就不用再装）：

```bash
python -m pip install -e ".[test]"
PYTHONUTF8=1 python -m pytest "B3-04-测完就回滚" -q
```

应看到 `3 passed`。`pytest-asyncio` 已经写在 `test` 这个 extra 里。

---

## 1. 外层事务

这个文件共用一块内存库，表只建一次。每个测试另开一个事务。

测试里的 `session.commit()` 提交的是保存点，不是那层外层事务。夹具结束执行 `rollback`，插入就没了。下一个测试数出来是 `0`。

SQLite 的驱动会自己开事务。不关掉的话，测试里的 `commit` 会真的落库，外层 `rollback` 撤不掉。示例里把驱动的自动事务关掉，改由 SQLAlchemy 发 `BEGIN`。换到别的数据库通常不用这两行。

对照 `@DataJpaTest`：测试方法上的事务在结束时回滚。不是每个测试换一个新的数据库文件。

`async def` 的测试函数，pytest 自己不会跑。`@pytest.mark.asyncio` 把它交给 pytest-asyncio。不要在同步测试里再包一层 `asyncio.run` 来假装。

本课目录里的 `pytest.ini` 只给这一课。不要为了异步测试去改仓库根上的配置。

---

## 本课肌肉记忆

1. 测试可以 commit，收尾要 rollback
2. 下一个测试必须看不到上一笔
3. `async def` 测试要 pytest-asyncio
