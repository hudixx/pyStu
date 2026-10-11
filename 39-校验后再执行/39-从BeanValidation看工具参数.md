# 第 39 课：从 Bean Validation 看工具参数

说明书（`tools=` 里的 JSON Schema）是给模型看的。真正拦住脏参数的，是你的 pydantic，和普通接口的 `@Valid` 一样。模型经常不照着说明书填。

运行：

```bash
PYTHONUTF8=1 python 39-校验后再执行/39_执行.py
```

应看到：`记一条 买牛奶` 进列表；`TOOL:BADJSON`、`TOOL:EMPTY`、`TOOL:UNKNOWN` 都是「拒绝」，列表里始终只有「买牛奶」。

实现在 `38-工具调用入门/todos.py` 的 `run_tool`。假模型里没有这份列表。

---

## 1. 白名单，不要反射

```text
名字不在 list_todos / add_todo → 拒绝，连 JSON 都不信
JSON 解析失败                 → 拒绝
pydantic 失败（空标题、多字段）→ 拒绝
通过                           → 才改 TODOS
```

对照：不要 `method = Class.forName(用户给的名字).getMethod(...)`。工具名是不可信输入，和 URL 路径一样，只能落到你写好的那几个方法。

失败要 **return 一段说明**，不要抛到循环外面。下一课这段说明会作为 `role=tool` 喂回去。模型看不到拒绝，就会当这张工单成功了。

---

## 2. 说明书拦不住请求

`additionalProperties: false` 写在 schema 里，只是希望模型别多写字段。假模型的 `TOOL:EMPTY` 仍会交出 `{"title": ""}`。空字符串能通过 `json.loads`，过不了 `min_length=1`。

对照：前端校验过了，后端仍要 `@NotBlank`。

---

## 本课肌肉记忆

1. `json.loads` 然后 `model_validate`，两道都要
2. 未知工具名直接拒绝
3. 拒绝是结果字符串，不是未捕获异常
