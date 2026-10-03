# 第 25 课：从 Checkstyle 看 ruff 和 mypy

进组之后别人要能 clone、跑检查、看出类型对不对。第 15 课的 `pyproject.toml` 已经能声明依赖；本课加上 **检查器**。

不要求把整个练习仓库扫到零警告。要求：知道两条命令，知道它们各自对标 Java 里哪一层。

先装（和 15 课同一套 extras 机制）：

```bash
cd E:/myGitRepositorysx/pyStu
source .venv/Scripts/activate
python -m pip install -e ".[lint]"
```

运行示例（装完后）：

```bash
PYTHONUTF8=1 python 25-打包与检查/25_检查.py
python -m ruff check 25-打包与检查/25_检查.py
python -m mypy 25-打包与检查/25_检查.py
```

后两行都应安静退出（exit code 0）。

---

## 1. 分工：谁像编译器，谁像 Checkstyle

| Java | Python | 拦什么 |
|---|---|---|
| javac 类型错误 | **mypy / pyright** | 注解对不上：`int` 当成 `str` 用 |
| Checkstyle / SpotBugs 风格 | **ruff** | 未使用变量、明显 bug、部分风格 |
| IDE 红线 | PyCharm / Pylance | 两者都做一点，但 CI 不能只靠 IDE |
| pydantic / Bean Validation | 运行时 | 请求体真假，检查器不管线上数据 |

Python **没有** javac 这一关。所以：

- ruff 快，当提交前的 Checkstyle
- mypy 或 pyright 当「可选编译器」。Pylance 背后就是 pyright；命令行本课用 mypy，错误信息好读
- 真正进接口的数据仍靠 pydantic（17 课）

两个检查器都 **不会执行你的业务代码**。`ruff check` 不是测试，`mypy` 也不是。测试仍是 pytest。

---

## 2. ruff

```bash
python -m ruff check 某文件.py
```

只报告，不改文件。自动改（谨慎，本课练习不要对整个仓库乱 format）：

```bash
python -m ruff check --fix 某文件.py
```

配置写在根目录 `pyproject.toml` 的 `[tool.ruff]`，对标 `checkstyle.xml`。现在只开了 `E`（pycodestyle 错）和 `F`（明显错误，比如未定义名）。先够用。

---

## 3. mypy

```bash
python -m mypy 某文件.py
```

它读你的注解。第 10 课那个 `add("a", "b")` 运行时能拼成 `"ab"`，mypy 会报。这正是你要的。

```python
def add(a: int, b: int) -> int:
    return a + b

add("a", "b")   # 运行 OK；mypy 说类型不对
```

对不上时，先改代码，不要一上来 `# type: ignore`。忽略是给第三方烂注解留的后门。

pyright / Pylance 和 mypy 偶有分歧，日常听 IDE 即可。CI 里锁一个（组里定）。本课锁 mypy。

---

## 4. extras 又见一次

`pyproject.toml` 里：

```toml
[project.optional-dependencies]
lint = ["ruff>=0.8", "mypy>=1.13"]
```

对标 Maven profile / optional：不是跑服务的必需品，检查才装。

```bash
python -m pip install -e ".[web,test,lint]"
```

一次装齐也行。

---

## 本课肌肉记忆

1. ruff ≈ Checkstyle，快，拦低级错误
2. mypy ≈ 可选的 javac，只看注解
3. 两者都不替代 pytest，也不替代 pydantic
4. 依赖用 extras 声明，别口头说「我机器上有」
5. 先对自己的新文件跑通，不要幻想把 01–20 练习一次性 mypy 全绿

阶段五结束标准：能写 async 函数、并发两个 HTTP、超时能取消、类型检查能对这份新代码跑过。

阶段六才是模型 API。你说「开始阶段六」再写教程。
