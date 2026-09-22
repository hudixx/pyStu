# 第 09 课：从 Java IO 看 pathlib 和 JSON

Java 里你用 `Path` / `Files` / Jackson。
Python 标准库就够用：`pathlib.Path` 管路径和文件，`json` 管序列化。

运行示例：

```bash
PYTHONUTF8=1 python 09-文件路径与JSON/09_文件.py
```

Windows 上 **读写文本一律带 `encoding="utf-8"`**，否则可能是系统默认 GBK，中文会乱码或报错。

---

## 1. `Path` ≈ `java.nio.file.Path`

```python
from pathlib import Path

here = Path(__file__).resolve().parent   # 当前脚本所在目录
p = here / "data" / "users.json"         # 用 / 拼接，不要自己拼反斜杠
```

| Java | Python |
|---|---|
| `Paths.get("a", "b")` | `Path("a") / "b"` |
| `path.resolve()` | `path.resolve()` |
| `Files.exists(path)` | `path.exists()` |
| `Files.isDirectory(path)` | `path.is_dir()` |
| `Files.readString(path)` | `path.read_text(encoding="utf-8")` |
| `Files.writeString(path, s)` | `path.write_text(s, encoding="utf-8")` |
| `Files.newBufferedReader` | `path.open("r", encoding="utf-8")` |
| `path.getFileName()` | `path.name` |
| `path.getParent()` | `path.parent` |

目录：

```python
p.parent.mkdir(parents=True, exist_ok=True)  # 类似 Files.createDirectories
```

遍历：

```python
for item in here.iterdir():      # 一层
    print(item.name)

for item in here.glob("*.py"):   # 当前目录匹配
    print(item)

for item in here.rglob("*.py"):  # 递归，类似 Files.walk
    print(item)
```

路径对象不是字符串。需要字符串时用 `str(p)`，或在 f-string 里直接 `{p}`。
判断、拼接、存在性，都用 Path 的方法，不要靠字符串 `+ "\\"`。

---

## 2. 打开文件：继续用 `with`

第 08 课的 `with` 在这里落地：

```python
with path.open("r", encoding="utf-8") as f:
    text = f.read()

with path.open("w", encoding="utf-8") as f:   # w 会覆盖
    f.write("hello\n")

with path.open("a", encoding="utf-8") as f:   # a 追加
    f.write("下一行\n")
```

短内容可以直接：

```python
text = path.read_text(encoding="utf-8")
path.write_text(text, encoding="utf-8")
```

二进制用 `"rb"` / `"wb"`，不要加 encoding。

---

## 3. `json` ≈ 内置的 Jackson

`json` 只处理 **dict / list / str / int / float / bool / None** 这些基本类型。
自定义 class 不能直接 `json.dumps(user_obj)`，要先变成 dict。

```python
import json

user = {"name": "hudi", "years": 30}
text = json.dumps(user, ensure_ascii=False, indent=2)
# ensure_ascii=False：中文原样写入，不要变成 \uXXXX
# indent=2：pretty print，方便人看

data = json.loads(text)          # 字符串 → Python 对象
```

读写文件：

```python
path.write_text(json.dumps(user, ensure_ascii=False, indent=2), encoding="utf-8")
user2 = json.loads(path.read_text(encoding="utf-8"))
```

也可以流式：

```python
with path.open("w", encoding="utf-8") as f:
    json.dump(user, f, ensure_ascii=False, indent=2)

with path.open("r", encoding="utf-8") as f:
    user2 = json.load(f)
```

`dump/load` 对文件，`dumps/loads` 对字符串。多一个 `s` 就是 string。

和 Jackson 的差异：

| Jackson | json 模块 |
|---|---|
| 可直接序列化 Java Bean | 只认 dict/list 等基本类型 |
| `@JsonIgnore` 等注解 | 没有，自己先转 dict |
| `ObjectMapper` 要 new | `import json` 直接用 |

配合 dataclass：

```python
from dataclasses import dataclass, asdict

@dataclass
class User:
    name: str
    years: int

json.dumps(asdict(User("hudi", 30)), ensure_ascii=False)
```

---

## 4. 常见坑

1. Windows 忘了 `encoding="utf-8"`
2. `json.dumps(obj)` 里夹了 `Path`、`datetime`、自定义对象 → `TypeError`
3. JSON 的 `null` 对应 Python 的 `None`，不是 `"null"` 字符串
4. JSON 的 key **永远是字符串**。`{1: "a"}` dump 再 load 会变成 `{"1": "a"}`
5. 用 `Path` 拼接，不要 `'C:\\foo' + name`

---

## 本课肌肉记忆

1. 路径用 `Path`，拼接用 `/`
2. 文本读写带 `encoding="utf-8"`
3. 文件必须 `with`，或用 `read_text` / `write_text`
4. `dumps/loads` 对字符串，`dump/load` 对文件
5. 中文 JSON 加 `ensure_ascii=False`
6. 自定义对象先变成 dict 再 dump

下一课讲测试和类型提示，对照 JUnit / 泛型。
