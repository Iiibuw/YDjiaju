"""YD 家具演示服务器：静态文件 + /api 反向代理到后端 8000。

用法：
  python ydf_demo_server.py [--port 5280] [--api http://127.0.0.1:8000] [--dir .]

浏览器只需访问这一个端口：页面和接口同源，彻底避免跨主机/跨域问题。
"""
import argparse
import http.server
import json
import os
import socketserver
import sys
import urllib.error
import urllib.request
from urllib.parse import urlparse


# 后端响应需要透传到浏览器的 CORS 响应头（否则跨域预检 OPTIONS 失败 → 浏览器拦真实请求）
_CORS_PASS_HEADERS = (
    'Access-Control-Allow-Origin',
    'Access-Control-Allow-Credentials',
    'Access-Control-Allow-Methods',
    'Access-Control-Allow-Headers',
    'Access-Control-Expose-Headers',
    'Access-Control-Max-Age',
)


class Handler(http.server.SimpleHTTPRequestHandler):
    api_base = "http://127.0.0.1:8000"
    root = "."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=self.root, **kwargs)

    # ---------- 代理 /api ----------
    def _proxy(self, method):
        parsed = urlparse(self.path)
        if not parsed.path.startswith("/api/"):
            self.send_error(404, "Not Found")
            return
        target = self.api_base + parsed.path
        if parsed.query:
            target += "?" + parsed.query
        body = None
        clen = self.headers.get("Content-Length")
        if clen:
            body = self.rfile.read(int(clen))
        req = urllib.request.Request(target, data=body, method=method)
        for h in ("Content-Type", "Authorization"):
            v = self.headers.get(h)
            if v:
                req.add_header(h, v)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                self.send_response(resp.status)
                self.send_header("Content-Type", resp.headers.get("Content-Type", "application/json"))
                self.send_header("Content-Length", str(len(data)))
                for h in _CORS_PASS_HEADERS:
                    v = resp.headers.get(h)
                    if v:
                        self.send_header(h, v)
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as e:
            data = e.read()
            self.send_response(e.code)
            self.send_header("Content-Type", e.headers.get("Content-Type", "application/json"))
            self.send_header("Content-Length", str(len(data)))
            for h in _CORS_PASS_HEADERS:
                v = e.headers.get(h)
                if v:
                    self.send_header(h, v)
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            body = json.dumps({"code": 502, "detail": f"代理后端失败：{e}"}, ensure_ascii=False).encode()
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    # 预检直接放行（避免每一次都到后端）
    def do_OPTIONS(self):
        if self.path.startswith("/api/"):
            self.send_response(204)
            origin = self.headers.get("Origin", "*")
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
            self.send_header("Access-Control-Allow-Credentials", "true")
            self.send_header("Access-Control-Max-Age", "86400")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        return super().do_OPTIONS()

    def do_GET(self):
        if self.path.startswith("/api/"):
            return self._proxy("GET")
        return super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            return self._proxy("POST")
        return super().do_POST()

    def do_PUT(self):
        if self.path.startswith("/api/"):
            return self._proxy("PUT")
        return super().do_PUT()

    def do_DELETE(self):
        if self.path.startswith("/api/"):
            return self._proxy("DELETE")
        return super().do_DELETE()

    # 中文文件名：正确 Content-Type
    def guess_type(self, path):
        ext = os.path.splitext(path)[1].lower()
        if ext == ".html":
            return "text/html; charset=utf-8"
        if ext == ".js":
            return "application/javascript; charset=utf-8"
        if ext == ".css":
            return "text/css; charset=utf-8"
        return super().guess_type(path)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stdout.write("[ydf] %s %s\n" % (self.address_string(), fmt % args))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=5280)
    ap.add_argument("--api", default="http://127.0.0.1:8000")
    ap.add_argument("--dir", default=".")
    args = ap.parse_args()

    Handler.api_base = args.api
    Handler.root = os.path.abspath(args.dir)

    class Server(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        daemon_threads = True

    with Server(("0.0.0.0", args.port), Handler) as httpd:
        print(f"[ydf] demo server http://localhost:{args.port}  (dir={Handler.root}, api→{args.api})")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
