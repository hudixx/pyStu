"""第 20 课示例：用 TestClient 测第 18 课的 FastAPI 应用。

    cd 20-pytest测API
    PYTHONUTF8=1 python -m pytest test_hello.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

# 18 课目录名带连字符，不能当包。把那个目录加入 path 再 import 18_app。
_APP_DIR = Path(__file__).resolve().parent.parent / "18-FastAPI入门"
sys.path.insert(0, str(_APP_DIR))

import importlib.util

_spec = importlib.util.spec_from_file_location("app18", _APP_DIR / "18_app.py")
assert _spec and _spec.loader
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
client = TestClient(_mod.app)


def test_hello_default() -> None:
    r = client.get("/hello")
    assert r.status_code == 200
    assert r.json() == {"message": "你好, 陌生人"}


def test_hello_query() -> None:
    r = client.get("/hello", params={"name": "hudi"})
    assert r.status_code == 200
    assert "hudi" in r.json()["message"]


def test_hello_post() -> None:
    r = client.post("/hello", json={"name": "ada"})
    assert r.status_code == 200
    assert r.json()["message"] == "你好, ada"


def test_user_bad_id() -> None:
    r = client.get("/users/0")
    assert r.status_code == 400
