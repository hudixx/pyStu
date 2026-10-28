# 选修 B3 第 3 课：从 ParameterizedTest 看参数化

同一条断言要跑好几组输入，用 `parametrize`。不要复制三份测试函数。

运行：

```bash
PYTHONUTF8=1 python -m pytest "B3-03-一组参数" -q
```

应看到 `3 passed`。

---

## 1. 一组就是一次测试

`("n", "expected")` 是参数名。下面每个元组是一组。三组就跑三次 `test_days`。

某一组失败时，报告里会带上这组的参数，例如 `n=8, expected='不知道'`。你不用猜是哪一次。

对照 `@ParameterizedTest` 和 `@CsvSource`。断言只有一份，数据有多行。

---

## 本课肌肉记忆

1. 同样的断言用参数化，不复制函数
2. 每一组都是一次独立的测试
3. 失败报告里能看见是哪一组
