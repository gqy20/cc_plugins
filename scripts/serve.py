"""本地预览服务器：把 mkdocs 构建产物按正确的 MIME 类型发出去。

为什么需要它
------------
Windows 注册表里的 mimetypes 会把 ``.svg`` 报成 ``image/svg``，
Chrome 遇到这个非法类型就判定 <img> 加载失败 —— 图裂，而且
``naturalWidth`` 是 0，很容易被误判成"图生成坏了"。

Python 3.13 的 ``SimpleHTTPRequestHandler.guess_type()`` 返回字符串
（不是老版本的二元组），所以覆写时不要解包。

用法::

    uv run python scripts/serve.py                 # 服务 site/，默认 8765 端口
    uv run python scripts/serve.py --port 9000
    uv run python scripts/serve.py --dir docs      # 直接服务源码目录

先构建再预览::

    PYTHONPATH=. uv run --with "mkdocs-material>=9.5" mkdocs build --strict --site-dir site
    uv run python scripts/serve.py
"""
from __future__ import annotations

import argparse
import functools
import http.server
import mimetypes
import socketserver
from pathlib import Path

# 修正 Windows 上 .svg / .woff2 的 MIME 推断
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("font/woff2", ".woff2")


class Handler(http.server.SimpleHTTPRequestHandler):
    """在标准静态服务器基础上，强制 .svg 用 image/svg+xml。"""

    def guess_type(self, path: str) -> str:  # noqa: D102 - 覆写标准库
        if path.endswith(".svg"):
            return "image/svg+xml"
        ctype = super().guess_type(path)
        return ctype or "application/octet-stream"

    def end_headers(self) -> None:  # noqa: D102 - 覆写标准库
        # 本地预览不该缓存，否则改了图还要强刷
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--dir", default="site", help="要服务的目录（默认 site）")
    parser.add_argument("--port", type=int, default=8765, help="端口（默认 8765）")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址（默认只监听本机）")
    args = parser.parse_args()

    root = Path(args.dir).resolve()
    if not root.is_dir():
        parser.error(f"目录不存在：{root}（先跑 mkdocs build）")

    handler = functools.partial(Handler, directory=str(root))
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((args.host, args.port), handler) as httpd:
        print(f"serving {root} at http://{args.host}:{args.port}", flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nbye", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
