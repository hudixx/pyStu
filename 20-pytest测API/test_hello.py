"""第 20 课示例：用 TestClient 测第 18 课的 FastAPI 应用。

对照 Spring：
- TestClient(app) ≈ @AutoConfigureMockMvc 的 MockMvc，不真开 8000 端口
- client.get / post ≈ mockMvc.perform(get/post)
- r.status_code / r.json() ≈ andExpect(status()) / content().json()
- pytest：文件名 test_*.py、函数名 test_*，不必继承 TestCase（第 10 课 unittest 那套）

运行：

    cd 20-pytest测API
    PYTHONUTF8=1 python -m pytest test_hello.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

# TestClient：把 FastAPI app 包一层，调用方式和 httpx 几乎一样，但走内存，不监听端口。
from fastapi.testclient import TestClient

# 18 课目录名带连字符，不能 import 18-FastAPI入门。
# parent.parent：从 20-pytest测API 回到项目根，再进 18-FastAPI入门。
_APP_DIR = Path(__file__).resolve().parent.parent / "18-FastAPI入门"
# 先放进 sys.path，下面 importlib 按文件路径加载时，18_app 内部的 import 也能解析。
sys.path.insert(0, str(_APP_DIR))

# importlib.util：按「文件路径」加载模块。目录名非法时的正规做法，对照 URLClassLoader 加载某个 class 文件。
import importlib.util

# spec_from_file_location(模块名, 文件路径)：造一个模块说明书。名字用 app18，避免和数字开头的文件名较劲。
_spec = importlib.util.spec_from_file_location("app18", _APP_DIR / "18_app.py")
# spec 或 loader 为 None 说明路径不对。assert 失败会立刻报错，比后面 AttributeError 好懂。
assert _spec and _spec.loader
# 按说明书建空模块对象，还没执行 18_app.py 里的代码。
_mod = importlib.util.module_from_spec(_spec)
# 真正执行 18_app.py：创建 app、注册路由。不会跑 if __name__ == "__main__" 那段 uvicorn。
_spec.loader.exec_module(_mod)
# _mod.app 就是 18_app.py 里的 app = FastAPI(...)。包成 TestClient，后面测试函数共用这一个。
client = TestClient(_mod.app)


def test_hello_default() -> None:
    """不传 name，应走默认值「陌生人」。对照 @RequestParam(defaultValue=...)。"""
    r = client.get("/hello")  # 没有 params，URL 就是 /hello
    assert r.status_code == 200  # 对照 status().isOk()
    # 整段 JSON 精确相等。默认值写错、空格写错都会挂。
    assert r.json() == {"message": "你好, 陌生人"}


def test_hello_query() -> None:
    """query 参数。params= 对照 .param("name", "hudi")，httpx/TestClient 都会编成 ?name=hudi。"""
    r = client.get("/hello", params={"name": "hudi"})
    assert r.status_code == 200
    # 只断言名字出现在 message 里，不绑死整句，改文案时这题还能过。
    assert "hudi" in r.json()["message"]


def test_hello_post() -> None:
    """JSON body。json= 自动序列化并带 Content-Type，对照 content(json).contentType(APPLICATION_JSON)。"""
    r = client.post("/hello", json={"name": "ada"})
    assert r.status_code == 200
    assert r.json()["message"] == "你好, ada"


def test_user_bad_id() -> None:
    """路径 /users/0 会进 get_user，user_id<=0 抛 HTTPException(400)。

    TestClient 默认不把 4xx 变成异常，只把状态码放在 r 上，方便 assert。
    这和 16 课 httpx 一样：不 raise_for_status 就不会炸。
    """
    r = client.get("/users/0")
    assert r.status_code == 400
