#!/usr/bin/env python3
"""检查 Markdown 表格的结构完整性。

为什么需要它
------------
表格的列数不一致、分隔行位置写错，**Markdown 解析器不会报错** ——
它会静默地把行补齐或截断，渲染成"某几列全是空的"或"整行左移"。
`mkdocs build --strict` 也抓不到（那只查链接和锚点）。

实测踩过的三个坑：
  1. 分隔行写在"合计"行**之后** → "合计"被当成表头，语义整个反了
  2. 数据行只写了 1 格 → 表格多出两列全空
  3. 数据行比表头少 1 格 → 整行内容左移，最后一列空着

用法::

    uv run python scripts/check_tables.py                    # 查 docs/cc-guide/
    uv run python scripts/check_tables.py docs/ plugins/     # 查指定目录
    uv run python scripts/check_tables.py --quiet             # 只报问题

退出码：有问题时返回 1，可以直接进 CI。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# 一行表格：| a | b |   （含转义竖线 \| 的单元格要按 1 个算）
ROW = re.compile(r"^\s*\|.*\|\s*$")
# 分隔行：|---|---|  或 |:--|--:|
SEP = re.compile(r"^\|(?:[\s:\-|]*)\|$")


def cell_count(row: str) -> int:
    """数一行的单元格数。`\\|` 是转义竖线，属于内容不是分隔符。"""
    return len(re.split(r"(?<!\\)\|", row.strip())) - 2


def scan(path: Path) -> list[str]:
    """返回该文件里所有结构问题的描述。"""
    problems: list[str] = []
    lines = path.read_text(encoding="utf-8").split("\n")
    in_fence = False
    table: tuple[int, list[str]] | None = None

    def flush(tbl: tuple[int, list[str]] | None) -> None:
        if not tbl or len(tbl[1]) < 3:
            return
        start, rows = tbl
        widths = [cell_count(r) for r in rows]
        head_w = widths[0]
        # 分隔行必须在表头之后 —— 否则第一行数据会被当成表头
        if not SEP.match(rows[1].strip()):
            problems.append(f"L{start + 2}: 分隔行不在表头后（第一行会被渲染成表头）")
        for i, w in enumerate(widths):
            if w != head_w:
                problems.append(
                    f"L{start + i + 1}: 列数 {w} ≠ 表头 {head_w} :: {rows[i].strip()[:60]}"
                )
        # 整列为空（跳过表头和分隔行）
        cells = [re.split(r"(?<!\\)\|", r.strip())[1:-1] for r in rows]
        for ci in range(head_w):
            body = [c[ci] if ci < len(c) else "" for c in cells[2:]]
            if body and all(not c.strip() for c in body):
                problems.append(f"L{start + 3}: 第 {ci + 1} 列整列为空")

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("```"):
            flush(table)
            table = None
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if ROW.match(line):
            if table is None:
                table = (i, [])
            table[1].append(line)
        else:
            flush(table)
            table = None
    flush(table)
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("paths", nargs="*", default=["docs/cc-guide"], help="要扫描的目录或文件")
    parser.add_argument("--quiet", action="store_true", help="只输出问题，不输出 OK")
    args = parser.parse_args()

    targets: list[Path] = []
    for raw in args.paths:
        p = Path(raw)
        if p.is_dir():
            targets.extend(sorted(p.rglob("*.md")))
        elif p.is_file():
            targets.append(p)
        else:
            print(f"跳过（不存在）：{raw}", file=sys.stderr)

    bad = 0
    for f in targets:
        problems = scan(f)
        if problems:
            bad += 1
            print(f"\n❌ {f}")
            for p in problems:
                print(f"   - {p}")
        elif not args.quiet:
            print(f"✅ {f}")

    print(f"\n扫描 {len(targets)} 个文件，{bad} 个有问题")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
