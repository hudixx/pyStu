"""第 31 课的接口测试。只发请求，不负责启动或关闭假模型。

怎么跑（假模型常驻，本文件可以反复执行）：
1. 另开终端，进入 26-模型SDK入门，执行 python mock_llm.py，挂着别关。
   它听 127.0.0.1:8001，就是下面和 31_client._client() 的默认地址。
2. 再执行本文件：python 31_test.py。

本文件用 TestClient，请求在进程内直接进 FastAPI，不走网卡，
也不会打到你另外挂着的 uvicorn（31_client.py 的 8000）。
对照 Java：这是 MockMvc，不是去打一台已经 java -jar 起来的服务。
应用内部的 AsyncOpenAI 仍会通过网络访问常驻假模型。

31_client.py 那个 uvicorn 可以一直开着给人看 /docs 或手调，但本测试用不到它。
"""

import sys  # 预检失败时 sys.exit(1)。对照 System.exit(1)。
from pathlib import Path  # 拼出 31_client.py 的绝对路径。对照 Path.of(...)。

from fastapi.testclient import TestClient  # 进程内调用 ASGI 应用，不占用 8000 端口。
import importlib.util as im_util  # 文件名以数字开头，不能写 import 31_client，只能按路径加载。

# 本文件在 31-FastAPI流式接口/ 下。parent.parent 是仓库根，再拼回本目录。
# 不再把 26-模型SDK入门 加进 sys.path：测试不 import mock_llm，也不再 start_mock()。
_APP_DIR = Path(__file__).resolve().parent.parent / "31-FastAPI流式接口"

# 目录名以数字开头，常规 import 会失败。按文件路径加载。
# 对照 Java 里用 URLClassLoader 加载一个不在默认 classpath 上的类。
sys.path.insert(0, str(_APP_DIR))
_spec = im_util.spec_from_file_location("app31", _APP_DIR / "31_client.py")
assert _spec and _spec.loader  # 路径写错时 spec 是 None，尽早失败，不要等到下面才 AttributeError。
_mod = im_util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)  # 执行 31_client.py。FastAPI 实例在 _mod.app 上。

def main() -> None:
    client = TestClient(_mod.app)  # 构造客户端不访问网络。打到 8001 的是路由里的 AsyncOpenAI。
    streamed = client.post("/chat", json={"text": "你好hudi"})
    print("GET 不是这个接口，POST /chat = ", streamed.status_code, streamed.text)
    ok = client.post("/extract", json={"text": "你好hudi"})
    # ok.json() 把响应体解析成 dict。合法时假模型回 hudi / 70，状态码 200。
    print("POST /extract 合法 =", ok.status_code, ok.json())

    bad = client.post("/extract", json={"text": "TRIGGER:BADJSON"})
    # 路由里 raise 了 HTTPException(422)。这里只打印状态码，不调用 .json() 也行。
    print("POST /extract 脏 JSON =", bad.status_code)


if __name__ == "__main__":
    main()
