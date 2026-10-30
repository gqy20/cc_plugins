#!/usr/bin/env python3
"""从 Claude Code 可执行文件里提取内嵌的 CHANGELOG。

Claude Code 把最近若干个版本的 release notes 以 JS 字符串的形式打包进了
可执行文件。这是**一手**证据：比官网文档新，也比 `git log` 更贴近用户实际
跑的那个版本。

用法::

    uv run python scripts/extract_changelog.py                    # 全部版本
    uv run python scripts/extract_changelog.py --since 2.1.305     # 只看某个版本之后
    uv run python scripts/extract_changelog.py --grep queue       # 只看匹配的行
    uv run python scripts/extract_changelog.py --out other.md     # 指定输出路径
    uv run python scripts/extract_changelog.py --print            # 打到 stdout

没有 ``--out`` 时默认写到 ``tmp/claude-changelog.md``（该目录已被 .gitignore 忽略）。
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

# Windows / macOS / Linux 下 claude 可执行文件的候选位置
CANDIDATES = [
    Path.home() / ".local/bin/claude.exe",
    Path.home() / ".local/bin/claude",
    Path.home() / ".claude/local/claude",
    Path("/usr/local/bin/claude"),
    Path("/opt/homebrew/bin/claude"),
]

# 内嵌 changelog 在二进制里的 JS 源码形态
CHANGELOG_ANCHOR = "function Rko(){return'## "

# JS 单引号字符串里的转义序列 -> 真实字符
ESCAPES = {
    "n": "\n",
    "t": "\t",
    "r": "\r",
    "'": "'",
    '"': '"',
    "\\": "\\",
    "/": "/",
    "`": "`",
    "$": "$",
}


def find_binary(explicit: str | None) -> Path:
    """定位 claude 可执行文件。"""
    if explicit:
        p = Path(explicit).expanduser()
        if not p.exists():
            sys.exit(f"找不到可执行文件：{p}")
        return p

    env = os.environ.get("CLAUDE_CODE_BINARY")
    if env:
        p = Path(env).expanduser()
        if p.exists():
            return p

    for p in CANDIDATES:
        if p.exists():
            return p

    found = shutil_which("claude")
    if found:
        return Path(found)

    sys.exit(
        "找不到 claude 可执行文件。\n"
        "用 --binary <路径> 指定，或设环境变量 CLAUDE_CODE_BINARY。"
    )


def shutil_which(name: str) -> str | None:
    """在 PATH 上找可执行文件（Windows 上优先找 .exe）。"""
    from shutil import which

    return which(name) or which(f"{name}.exe")


def unescape_js(raw: str) -> str:
    """把 JS 单引号字符串字面量还原成普通文本。"""
    out: list[str] = []
    i = 0
    n = len(raw)
    while i < n:
        ch = raw[i]
        if ch == "\\" and i + 1 < n:
            nxt = raw[i + 1]
            if nxt in ESCAPES:
                out.append(ESCAPES[nxt])
                i += 2
                continue
            if nxt == "u" and i + 5 < n and raw[i + 2] == "{":
                end = raw.find("}", i + 3)
                if end != -1:
                    try:
                        out.append(chr(int(raw[i + 3 : end], 16)))
                        i = end + 1
                        continue
                    except ValueError:
                        pass
            # 未知转义：保留转义字符本身
            out.append(nxt)
            i += 2
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def extract(binary: Path) -> str:
    """从二进制里挖出 changelog 文本。"""
    text = binary.read_bytes().decode("utf-8", "replace")

    start = text.find(CHANGELOG_ANCHOR)
    if start == -1:
        sys.exit(f"在 {binary} 里没找到内嵌 changelog（锚点 {CHANGELOG_ANCHOR!r} 不存在）。")

    # changelog 是一段 JS 字符串字面量，结束于未转义的引号
    body_start = text.find("'", start) + 1
    i = body_start
    while i < len(text):
        if text[i] == "\\":
            i += 2
            continue
        if text[i] == "'":
            break
        i += 1
    raw = text[body_start:i]

    decoded = unescape_js(raw)
    idx = decoded.find("## 2.")
    return decoded[idx:] if idx >= 0 else decoded


def split_versions(text: str) -> list[tuple[str, str]]:
    """切成 [(版本号, 该版本的条目列表)]，只保留形如 2.x.y 的版本。"""
    out: list[tuple[str, str]] = []
    for chunk in re.split(r"^## ", text, flags=re.MULTILINE):
        head = chunk.split("\n", 1)[0].strip()
        if re.fullmatch(r"\d+\.\d+\.\d+", head):
            out.append((head, chunk))
    return out


def version_key(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in v.split("."))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--binary", help="claude 可执行文件路径")
    ap.add_argument("--out", help="输出文件（默认 tmp/claude-changelog.md）")
    ap.add_argument("--since", help="只保留 >= 该版本，例如 2.1.305")
    ap.add_argument("--grep", help="只保留匹配该正则的条目")
    ap.add_argument("--print", dest="to_stdout", action="store_true", help="打到 stdout 而不是写文件")
    args = ap.parse_args()

    binary = find_binary(args.binary)
    text = extract(binary)
    versions = split_versions(text)

    if not versions:
        sys.exit("解析出了 0 个版本，格式可能变了。")

    if args.since:
        floor = version_key(args.since)
        versions = [(v, b) for v, b in versions if version_key(v) >= floor]

    if args.grep:
        pattern = re.compile(args.grep, re.IGNORECASE)
        kept: list[tuple[str, str]] = []
        for ver, body in versions:
            lines = [l for l in body.split("\n") if l.strip().startswith("- ") and pattern.search(l)]
            if lines:
                kept.append((ver, "\n".join(lines)))
        versions = kept

    rendered = "\n".join(f"## {v}\n\n{b.rstrip()}\n" for v, b in versions)

    if args.to_stdout:
        sys.stdout.write(rendered)
        return 0

    out = Path(args.out) if args.out else Path("tmp/claude-changelog.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(rendered, encoding="utf-8")
    print(f"已写出 {out}（{len(versions)} 个版本，{len(rendered)} 字符）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
