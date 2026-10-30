#!/usr/bin/env python3
"""从 Claude Code 可执行文件里提取出厂默认键位表。

官方文档会过时（本仓库实测：interactive-mode 说 "按 Enter 排队"，
keybindings 说 Enter = chat:submit，两者矛盾），而二进制里的默认绑定
是**一手事实**。这个脚本把 `context:"Chat"` 那段默认绑定原样挖出来。

用法::

    uv run python scripts/extract_keybindings.py
    uv run python scripts/extract_keybindings.py --context Chat
    uv run python scripts/extract_keybindings.py --json

已知局限：计算属性形式的键（如 ``{[g]:"chat:cycleMode"}``）无法解析，会被跳过。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from extract_changelog import find_binary

# 出厂绑定在二进制里是这个形态：
#   context:"Chat",bindings:{escape:"chat:cancel",…,enter:"chat:submit",…}
# 块内可能有嵌套花括号（{[g]:"chat:cycleMode"}），所以用括号配对来截取，不能用正则。
BLOCK_START = re.compile(r'context:"(?P<ctx>[A-Za-z]+)",bindings:\{')

# 一个绑定项： "key":"action"  或  key:"action"
PAIR = re.compile(r'(?:"(?P<k1>[^"]+)"|(?P<k2>[A-Za-z][A-Za-z0-9_]*))\s*:\s*"(?P<action>[^"]+)"')


def _block_body(text: str, start: int) -> str:
    """从 '{' 处开始，按花括号配对截出块内容。start 指向 '{'。"""
    depth = 0
    i = start
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "\\":
            i += 2
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1 : i]
        i += 1
    return text[start + 1 :]


def extract(binary: Path) -> list[tuple[str, dict[str, str]]]:
    """返回 [(context, {键: 动作})]。"""
    text = binary.read_bytes().decode("utf-8", "replace")
    out: list[tuple[str, dict[str, str]]] = []
    for m in BLOCK_START.finditer(text):
        ctx = m.group("ctx")
        body = _block_body(text, m.end() - 1)
        bindings: dict[str, str] = {}
        for p in PAIR.finditer(body):
            key = p.group("k1") or p.group("k2")
            bindings[key] = p.group("action")
        if bindings:
            out.append((ctx, bindings))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--binary", help="claude 可执行文件路径")
    ap.add_argument("--context", help="只看某个上下文，例如 Chat")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args()

    binary = find_binary(args.binary)
    blocks = extract(binary)
    if not blocks:
        sys.exit("没解析出绑定表，二进制格式可能变了。")

    if args.context:
        blocks = [(c, b) for c, b in blocks if c.lower() == args.context.lower()]
        if not blocks:
            sys.exit(f"没有上下文 {args.context!r}，可选：{sorted({c for c, _ in blocks})}")
        # 同名上下文可能有多处（不同渲染器），合并去重
        merged: dict[str, str] = {}
        for _, b in blocks:
            merged.update(b)
        blocks = [(args.context, merged)]

    if args.json:
        print(json.dumps({c: b for c, b in blocks}, ensure_ascii=False, indent=2))
        return 0

    for ctx, bindings in blocks:
        print(f"# context: {ctx}\n")
        width = max(len(k) for k in bindings)
        for key in sorted(bindings, key=lambda k: (len(k), k)):
            print(f"  {key:<{width}}  ->  {bindings[key]}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
