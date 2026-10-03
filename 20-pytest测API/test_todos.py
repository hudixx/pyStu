import sys
from pathlib import Path

from fastapi.testclient import TestClient

_APP_DIR = Path(__file__).resolve().parent.parent / "19-待办HTTP接口"

sys.path.insert(0, str(_APP_DIR))

import importlib.util as im_util

_spec = im_util.spec_from_file_location("app19", _APP_DIR / "19_练习.py")
assert _spec and _spec.loader
_mod = im_util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
client = TestClient(_mod.app)

def test_get_todos():
    todos = client.get("/todos")
    assert todos.status_code == 200
    # assert type(todos.json()) == list
    assert isinstance(todos.json(), list)
def test_post_todos():
    todos = client.post("/todos", json = {"title": "pytest-demo"})
    assert todos.status_code in (200, 201)
    assert todos.json()["title"] == "pytest-demo"
    assert todos.json()["done"] == False

def test_post_done():
    todos = client.post("/todos/99999/done")
    assert todos.status_code == 404
"""
题4对照题不知道，请在注释中给出简要答案
"""


