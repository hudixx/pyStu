# 选修 B3 第 1 课：从 BeforeEach 看 fixture

第 20 课会跑 pytest。这一课看夹具活多久：每个测试一份，还是这个文件共用一份。

运行：

```bash
PYTHONUTF8=1 python -m pytest "B3-01-每个测试一份" -q
```

应看到 `4 passed`。

---

## 1. 两份寿命

| scope | 造几次 | Java |
|---|---|---|
| `function`（默认） | 每个测试一次 | `@BeforeEach` |
| `module` | 这个文件一次 | `@BeforeAll`，而且测试之间会留下改动 |

`box` 是默认作用域。`test_box_first` 往里放了 `"a"`，`test_box_second` 仍看到空列表。那是另一份。

`shared` 是 `scope="module"`。第一个测试放进 `"a"`，第二个测试还看得到。共用一份时，测试顺序会影响结果。

`yield` 把值交给测试。测试结束，才执行 `yield` 下面的清理。对照 `@AfterEach`。清理的是这一份，不是下一份。

---

## 本课肌肉记忆

1. 默认每个测试一份
2. `module` 会把上一个测试的改动留到下一个
3. `yield` 后面是清理
