"""第 20 课参考答案。三个用例都 PASSED，加载 19_练习.py 的方式也对。

题 4：TestClient 和 MockMvc 相同的一点：都不监听真实端口，
把 HTTP 请求直接灌进应用对象。所以测试不必先手动启动 uvicorn。
对照：MockMvc 打 DispatcherServlet，TestClient 打 FastAPI app。

注意：
- `200 | 201` 不是「或」。应写成 `status in (200, 201)` 或 `or`。
- 测试会往 19 课的 todos.json 里追加 pytest-demo。测完应删掉，或像下面这样改到临时文件。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from fastapi.testclient import TestClient

_APP_DIR = Path(__file__).resolve().parent.parent / "19-待办HTTP接口"
sys.path.insert(0, str(_APP_DIR))

_spec = importlib.util.spec_from_file_location("app19", _APP_DIR / "19_练习.py")
assert _spec and _spec.loader
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

# 不要写真实 todos.json，避免手工数据和测试数据搅在一起。
_tmp = Path(__file__).with_name("_pytest_todos.json")
_mod.todos = _tmp
client = TestClient(_mod.app)


def setup_module() -> None:
    if _tmp.exists():
        _tmp.unlink()


def teardown_module() -> None:
    if _tmp.exists():
        _tmp.unlink()


def test_get_todos() -> None:
    r = client.get("/todos")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_post_todos() -> None:
    r = client.post("/todos", json={"title": "pytest-demo"})
    assert r.status_code in (200, 201)
    body = r.json()
    assert body["title"] == "pytest-demo"
    assert body["done"] is False


def test_post_done_missing() -> None:
    r = client.post("/todos/99999/done")
    assert r.status_code == 404
