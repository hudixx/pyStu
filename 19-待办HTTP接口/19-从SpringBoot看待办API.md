# 第 19 课：把第 14 课待办做成 HTTP API

第 14 课是命令行。本课换成 HTTP，持久化仍然用旁边的 `todos.json`。
对标：同一个 Service / Repository，换一个 Controller。

先激活 venv。示例是 **便签 notes**，不是待办——作业请自己写待办，不要把示例改名交差。

```bash
cd 19-待办HTTP接口
PYTHONUTF8=1 python 19_notes.py
```

- GET http://127.0.0.1:8002/notes
- POST http://127.0.0.1:8002/notes  body: `{"text": "hello"}`
- `/docs` 看文档

---

## 你要交的接口（`19_练习.py`）

| 方法 | 路径 | 行为 |
|---|---|---|
| GET | `/todos` | 返回全部待办数组 |
| POST | `/todos` | body `{"title": "..."}`，追加，id 自增，返回新建那条 |
| POST | `/todos/{todo_id}/done` | 标记完成，返回那条；找不到 404 |

数据文件：脚本同目录 `todos.json`，格式和第 14 课相同：

```json
[{"id": 1, "title": "买牛奶", "done": false}]
```

规则沿用第 14 课：utf-8、`ensure_ascii=False`、id 用最大 id+1、文件不存在当空列表。
title 用 pydantic 校验，空字符串 422。

启动：

```bash
cd 19-待办HTTP接口
python -m uvicorn 19_练习:app --port 8002
```

---

## 分层怎么放在一个文件里

```text
pydantic 模型     ≈ DTO
load/save 函数    ≈ Repository
cmd / 路由函数    ≈ Controller 里调 Service
```

还没有数据库，不必上 SQLAlchemy。JSON 文件就是你的 DAO。

---

## 本课肌肉记忆

1. 命令行和 HTTP 应复用同一套 load/save，不要复制两份业务
2. 找不到资源 → `HTTPException(404)`
3. 入参用 pydantic，不要裸 dict
4. 仍然要 `if __name__ == "__main__"` 才能直接 python 跑

下一课用 pytest + TestClient 测这些接口，不必真的监听端口。
