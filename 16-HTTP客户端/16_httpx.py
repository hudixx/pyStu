"""第 16 课示例：本机起服务，再用 httpx 去调。不访问公网。

对照 Java：
- httpx.Client ≈ HttpClient / OkHttp
- client.get / client.post ≈ HttpRequest.GET / POST
- response.json() ≈ Jackson 把响应体解析成 Map
- raise_for_status() ≈ 自己判断 statusCode 非 2xx 就抛
- with ... as client ≈ try-with-resources，用完关连接池
"""

# 类型注解延迟求值，和 demo_server.py 同一句，养成习惯即可。
from __future__ import annotations

# sys：改 Python 的模块搜索路径。对照 Java 往 classpath 里临时加一个目录。
import sys
# Path：路径对象。对照 java.nio.file.Path。
from pathlib import Path

# 目录名是「16-HTTP客户端」，带连字符，不能写成 import 16-HTTP客户端.demo_server。
# __file__ 是本文件路径；resolve().parent 得到本目录的绝对路径。
# insert(0, ...) 插到 sys.path 最前面，后面 import demo_server 就会先在这里找。
sys.path.insert(0, str(Path(__file__).resolve().parent))

# httpx：第三方 HTTP 客户端。对照 HttpClient。一次性脚本也能 httpx.get(url)，多次请求请复用 Client。
import httpx

# start_server：上一份文件里的函数，返回 (server, "http://127.0.0.1:端口")。
from demo_server import start_server


def main() -> None:
    """起本机服务 → 发 GET/POST → 演示 404 → 关掉服务。"""
    # 后台线程开始听端口。base 形如 http://127.0.0.1:54321，端口每次可能不同。
    server, base = start_server()
    try:
        # Client 带连接池，多次请求复用。timeout=3.0 秒，避免挂死。
        # with 结束会 close，对照 try-with-resources 关 HttpClient。
        with httpx.Client(timeout=3.0) as client:
            # f"{base}/ping" 拼出完整 URL。GET 无 body。
            ping = client.get(f"{base}/ping")
            # 非 2xx 就抛 HTTPStatusError。200 则安静通过。
            ping.raise_for_status()
            # .json() 把响应体解析成 dict。对照 ObjectMapper.readValue。
            print("GET /ping =", ping.json())

            # json={...}：httpx 自动 dumps 成 JSON，并带 Content-Type: application/json。
            # 对照 BodyPublishers.ofString(objectMapper.writeValueAsString(map))。
            echoed = client.post(f"{base}/echo", json={"name": "hudi"})
            echoed.raise_for_status()
            # 服务端原样包一层，应看到 {"echo": {"name": "hudi"}}。
            print("POST /echo =", echoed.json())

            # 故意打一个不存在的路径。demo_server 会回 404，httpx 默认不抛，只把状态码放在对象上。
            missing = client.get(f"{base}/nope")
            print("GET /nope 状态码 =", missing.status_code)
            try:
                # 自己调用才会因 404 抛。不调的话程序继续，这点和「非 2xx 自动失败」的某些 Java 封装不同。
                missing.raise_for_status()
            except httpx.HTTPStatusError as e:
                # e.response 是那次 404 的响应。对照你 catch 之后再 response.statusCode()。
                print("raise_for_status 抓住了", e.response.status_code)
    finally:
        # 无论上面成功还是异常，都停掉后台 HTTP 服务，否则进程可能迟迟不退出。
        # 对照 server.stop() / Tomcat.destroy()。
        server.shutdown()


# 直接 python 16_httpx.py 时 __name__ 为 "__main__"，才跑 main。
# 被别人 import 时不跑，避免一导入就发 HTTP。对照 Java 的 public static void main。
if __name__ == "__main__":
    main()
