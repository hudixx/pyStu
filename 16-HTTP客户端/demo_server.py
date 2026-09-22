"""本机演示用 HTTP 服务，给 16_httpx.py 和练习 import。"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class DemoHandler(BaseHTTPRequestHandler):
    """只认识 GET /ping 和 POST /echo。"""

    def log_message(self, format: str, *args) -> None:
        return

    def do_GET(self) -> None:
        if self.path.split("?", 1)[0] != "/ping":
            self._send(404, {"error": "not found"})
            return
        self._send(200, {"ok": True, "msg": "pong"})

    def do_POST(self) -> None:
        if self.path != "/echo":
            self._send(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        payload = json.loads(raw.decode("utf-8")) if raw else {}
        self._send(200, {"echo": payload})

    def _send(self, code: int, body: dict) -> None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def start_server() -> tuple[ThreadingHTTPServer, str]:
    """端口 0 = 系统分配空闲端口。返回 (server, base_url)。"""
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    return server, f"http://{host}:{port}"
