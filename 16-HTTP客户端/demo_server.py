"""本机演示用 HTTP 服务，给 16_httpx.py 和练习 import。

对照 Java：
- BaseHTTPRequestHandler ≈ HttpServlet（按 HTTP 方法分发到 do_GET / do_POST）
- ThreadingHTTPServer ≈ 内嵌 Tomcat/Jetty：每个请求一个线程
- 标准库自带，不用 FastAPI；本课只为了给 httpx 当靶子，下一课才上正经服务端
"""

# 让类型注解变成字符串延迟求值。写法上可以互引用、少踩循环导入。
# Java 没有这句；Python 3.7+ 常用，3.11 起逐渐变成默认行为。
from __future__ import annotations

# json：把 dict ↔ JSON 文本互转。对照 Java 的 Jackson ObjectMapper。
import json
# threading：起后台线程。对照 Java 的 new Thread(...).start()。
import threading
# BaseHTTPRequestHandler：一个请求一个实例，按方法调 do_GET / do_POST。
# ThreadingHTTPServer：多线程版 HTTP 服务器（默认 HTTPServer 是单线程的）。
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class DemoHandler(BaseHTTPRequestHandler):
    """只认识 GET /ping 和 POST /echo。其它路径一律 404。

    对照 Java：继承 HttpServlet 后覆盖 doGet/doPost。
    框架收到请求后会 new 一个本类实例，再按方法名调进来。
    """

    def log_message(self, format: str, *args) -> None:
        """覆盖父类的访问日志。默认每次请求都会 print 一行，演示时太吵。

        空 return 等于什么都不打。对照 Java：覆盖一个空的 log 方法。
        format / *args 必须留着，签名要和父类一致，否则覆盖不生效。
        """
        return

    def do_GET(self) -> None:
        """处理 GET。方法名是约定：父类看到 GET 就调 do_GET。对照 HttpServlet.doGet。"""
        # self.path 是路径+查询串，例如 /ping?x=1。对照 request.getRequestURI() + QueryString。
        # split("?", 1) 最多切 1 次，得到 [路径, 查询串]；没有 ? 时列表只有一项。
        # [0] 取出纯路径，避免 /ping?foo=bar 被当成未知路径。
        if self.path.split("?", 1)[0] != "/ping":
            # 不是 /ping：回 404 JSON，然后 return，别再往下走成功分支。
            self._send(404, {"error": "not found"})
            return
        # 命中 /ping：200 + {"ok": true, "msg": "pong"}。httpx 那边会 .json() 拿到 dict。
        self._send(200, {"ok": True, "msg": "pong"})

    def do_POST(self) -> None:
        """处理 POST。对照 HttpServlet.doPost。这里只认 /echo。"""
        # POST 一般不靠查询串路由，直接拿完整 path 比是不是 /echo。
        if self.path != "/echo":
            self._send(404, {"error": "not found"})
            return
        # Content-Length 告诉你 body 有多少字节。没有这个头就当 0（空 body）。
        # headers.get 对照 request.getHeader("Content-Length")；缺省返回 "0"，避免 int(None) 崩。
        length = int(self.headers.get("Content-Length", "0"))
        # rfile 是请求体输入流。对照 request.getInputStream()。必须按 Length 读，不能瞎 read() 到 EOF。
        raw = self.rfile.read(length)
        # raw 是 bytes。有内容才 decode + json.loads；空 body 当 {}，避免 json.loads("") 抛异常。
        # json.loads 对照 ObjectMapper.readValue(str, Map.class)，得到 Python dict。
        payload = json.loads(raw.decode("utf-8")) if raw else {}
        # 原样包一层返回，客户端就能验证「我发出去的 JSON 服务端原样收到了」。
        self._send(200, {"echo": payload})

    def _send(self, code: int, body: dict) -> None:
        """统一写 JSON 响应。GET/POST/404 都走这里，避免复制粘贴。

        对照 Java：
        response.setStatus(code);
        response.setContentType("application/json; charset=utf-8");
        response.getOutputStream().write(bytes);
        """
        # dumps：dict → JSON 字符串。ensure_ascii=False 让中文原样输出，不要变成 \uXXXX。
        # encode("utf-8")：str → bytes。HTTP 响应体必须是字节，不能直接写 str。
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        # 状态行，例如 HTTP/1.1 200 OK。对照 response.setStatus(code)。
        self.send_response(code)
        # 告诉客户端：这是 JSON，编码 UTF-8。httpx 的 .json() 靠这个判断。
        self.send_header("Content-Type", "application/json; charset=utf-8")
        # Content-Length 必须是字节数（len(data)），不是字符数。客户端靠它知道 body 在哪结束。
        self.send_header("Content-Length", str(len(data)))
        # 头写完，空行隔开 body。少这一句，客户端会一直等头，看起来像卡死。
        self.end_headers()
        # wfile 是响应输出流。对照 response.getOutputStream()。把 JSON 字节写出去。
        self.wfile.write(data)


def start_server() -> tuple[ThreadingHTTPServer, str]:
    """端口 0 = 系统分配空闲端口。返回 (server, base_url)。

    对照 Java：new ServerSocket(0) 也会让 OS 挑空闲端口，避免写死 8000 和别人撞车。
    返回 server 是为了调用方 finally 里 shutdown()；返回 base_url 是为了拼 httpx 的请求地址。
    """
    # ("127.0.0.1", 0)：只绑本机回环，外网访问不了；0 表示让 OS 分配端口。
    # 第二个参数 DemoHandler：每个请求都会实例化这个 Handler 去处理。
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoHandler)
    # serve_forever 是阻塞死循环，必须丢到后台线程，否则 start_server() 永远 return 不了。
    # daemon=True：主线程结束时这个线程跟着死，对照 thread.setDaemon(true)，避免进程挂着不退出。
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()  # 真正开始听端口。对照 thread.start()，不是 run()。
    # server_address 此时已经是 (实际 host, 实际 port)，因为 bind 时 0 已被 OS 换成真实端口。
    host, port = server.server_address
    # f-string 拼出 http://127.0.0.1:xxxxx，给 httpx 当 base URL。
    return server, f"http://{host}:{port}"
