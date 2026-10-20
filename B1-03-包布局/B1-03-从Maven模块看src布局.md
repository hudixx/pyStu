# 选修 B1 第 3 课：从 Maven 模块看 src 布局

课目录里有文档、示例、练习。能被别人导入的代码要单独放在 `src` 下。

运行：

```bash
PYTHONUTF8=1 python B1-03-包布局/03_布局.py
```

应打印：`7 400-100-1000`。

---

## 1. 哪个目录才是包

| 位置 | 算不算库 |
|---|---|
| `B1-03-包布局/` | 不算。名字里有横线，不是合法的包名。文档也在这里 |
| `src/handbook/` | 算。有 `__init__.py`，下面的 `refund.py` 才能被导入 |

`sys.path.insert` 只是为了这个脚本能跑。安装进环境时，对应的是 `pyproject.toml` 里的：

```toml
[tool.setuptools.packages.find]
where = ["src"]
```

这门课不改成这套布局。现有课目录仍按原来的方式运行。

`from handbook.refund import days` 写清从哪个模块来。不要把所有函数都堆进 `__init__.py` 再星号导入。

---

## 本课肌肉记忆

1. 包放在 `src` 下，文档留在课目录
2. 横线目录名不能当包名
3. 先放好路径，再导入
