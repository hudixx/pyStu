from __future__ import annotations

import httpx

from demo_server import start_server

def main():
    server, baseurl = start_server()
    try:
        with httpx.Client(timeout=3.0) as client:
            ping = client.get(f"{baseurl}/ping")
            ping.raise_for_status()
            print(ping.json()["msg"])

            echo = client.post(f"{baseurl}/echo", json={"lang": "python"})
            echo.raise_for_status()
            print(echo.json())

            missing = client.get(f"{baseurl}/nope")
            print("GET /nope 状态码 =", missing.status_code)
            try:
                # 自己调用才会因 404 抛。不调的话程序继续，这点和「非 2xx 自动失败」的某些 Java 封装不同。
                missing.raise_for_status()
            except httpx.HTTPStatusError as e:
                print("raise_for_status 抓住了", e.response.status_code)
    finally:
        server.shutdown()

    """
        第三题不知道，请简要解答下
        with httpx.Client() as client: 对标 Java 的 try-with-resources（try (HttpClient client = ...) 或 OkHttp 用完 close）。离开 with 会关掉连接池，异常也会走清理。
        
        不要在循环里每次 httpx.get(...)：  
            httpx.get 每次新建一个短命 Client，TCP/TLS 握完手就扔。循环里等于每个请求新建连接。Client 带连接池，同一主机的请求复用，对照 Java 里复用 OkHttpClient / HttpClient，
            不要在 for 里 HttpClient.newHttpClient()。
    """

if __name__ == '__main__':
    main()