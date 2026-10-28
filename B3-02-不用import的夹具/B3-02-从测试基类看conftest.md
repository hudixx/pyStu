# 选修 B3 第 2 课：从测试基类看 conftest

夹具要给这个目录里的好几个测试文件用，就放进 `conftest.py`。测试不用 `import` 它。

运行：

```bash
PYTHONUTF8=1 python -m pytest "B3-02-不用import的夹具" -q
```

应看到 `1 passed`。

---

## 1. 为什么不用 import

pytest 收集这个目录时，会先执行同目录的 `conftest.py`。里面的 fixture 按名字配给测试参数。

`test_订单.py` 里没有 `from conftest import buyer`。参数叫 `buyer`，就拿到 `"hudi"`。

这只覆盖这个目录和它的子目录。对照一个测试基类只被这个包里的测试继承。放到仓库根，别的课的测试也会看见，名字一撞就难查。

---

## 本课肌肉记忆

1. 文件名就是 `conftest.py`
2. 测试靠参数名接夹具，不靠 import
3. 夹具放在用它的那一课目录，不放仓库根
