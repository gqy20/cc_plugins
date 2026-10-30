#!/usr/bin/env python3
"""校验文档里写死的 `CLAUDE.md` 尺寸数字与现实一致。

**为什么需要这个脚本**：文档里反复出现同一个量（`CLAUDE.md` 的行数 / 字符数 /
token 估算 / 超标百分比），而这些数字**会随文件本身变化**。
手抄必然漂移，漂移之后读者按文档里的命令复跑对不上，整章的可信度就没了。

本脚本的做法：**从源文件算出真值，再回文档里找写死的数字逐个比对**。
文档里任何一处数字与真值不符 → exit 1。

**作用域怎么定的**（这个边界很关键，划宽了会满屏假警报）：

| 量 | 作用域 | 理由 |
|----|--------|------|
| 行数 / 字符数 / token | **单行** | 只有"同一行里既提到 `CLAUDE.md` 又写了数字"才是尺寸声明 |
| 超标百分比 | **段落** | `超标 108%` 常被 Markdown 拆到下一行（见 01 章） |

"官方建议 ≤ 200 行"里的 200 是**限额**不是尺寸，单独放行。

用法：
    uv run --with pyyaml python scripts/check_doc_numbers.py
    uv run --with pyyaml python scripts/check_doc_numbers.py --json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
# 要扫的目录：文档站 + 内部 skill（skill 里的数字同样会被 Claude 读进上下文）
SCAN_DIRS = [
    PROJECT / "docs" / "cc-guide",
    PROJECT / ".claude" / "skills" / "cc-guide",
]
CLAUDE_MD = PROJECT / "CLAUDE.md"

# 官方建议的 CLAUDE.md 行数上限
OFFICIAL_LIMIT = 200


def _load_est_tokens():
    """复用 measure_context.py 的 token 估算口径（保持全仓库一个公式）。"""
    spec = importlib.util.spec_from_file_location(
        "measure_context", PROJECT / "scripts" / "measure_context.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.est_tokens


def truth() -> dict:
    text = CLAUDE_MD.read_text(encoding="utf-8")
    est_tokens = _load_est_tokens()
    lines = text.count("\n")
    chars = len(text)
    return {
        "lines": lines,
        "chars": chars,
        "tokens": est_tokens(text),
        "over_pct": round((lines - OFFICIAL_LIMIT) / OFFICIAL_LIMIT * 100),
    }


# 尺寸数字的模式。带单位的是"尺寸"，不带的是别的量（预算、条数…），不查。
LINE_COUNT = re.compile(r"(\d[\d,]*)\s*行")
CHAR_COUNT = re.compile(r"(\d[\d,]*)\s*字符")
TOKEN_COUNT = re.compile(r"≈?\s*(\d[\d,]*)\s*tok")
OVER_PCT = re.compile(r"超标\s*(\d+)%|超\s*(\d+)%")

# 图片标签里的 alt/src/title 是自动生成的（gen_guide_figures.py 从真值推导），
# 不参与扫描，否则会把 skill 清单 / agent / 预算的数字误判成 CLAUDE.md 的尺寸
IMG_ATTR = re.compile(r'(alt|src|title)="[^"]*"')

# 提到 CLAUDE.md 的写法：文件名本身，或 "项目级 CLAUDE.md" 这类别名
CLAUDE_MD_MENTION = re.compile(r"CLAUDE\.md")


def _num(s: str) -> int:
    return int(s.replace(",", ""))


def scan() -> list[dict]:
    """扫出文档里所有写死的 CLAUDE.md 尺寸数字。"""
    t = truth()
    findings: list[dict] = []
    # 「行数」允许官方建议值同时出现
    allowed_lines = {OFFICIAL_LIMIT, t["lines"]}

    for md in _markdown_files():
        raw = md.read_text(encoding="utf-8")
        # 尺寸数字按行扫（行号要对得上原文，所以不 strip，只把 img 属性换空）
        lines = [IMG_ATTR.sub("", ln) for ln in raw.splitlines()]
        paras = _paragraphs(lines)

        for start, para in paras:
            flat = " ".join(para)
            if not CLAUDE_MD_MENTION.search(flat):
                continue
            where = f"{md.relative_to(PROJECT).as_posix()}:{start}"

            # —— 百分比：段落作用域 ——
            for m in OVER_PCT.finditer(flat):
                found = int(m.group(1) or m.group(2))
                if found != t["over_pct"]:
                    findings.append(_f(where, "超标百分比", found, t["over_pct"], flat))

        # —— 行数 / 字符数 / token：单行作用域 ——
        for lineno, line in enumerate(lines, 1):
            if not CLAUDE_MD_MENTION.search(line):
                continue
            where = f"{md.relative_to(PROJECT).as_posix()}:{lineno}"

            for m in LINE_COUNT.finditer(line):
                found = _num(m.group(1))
                if found not in allowed_lines:
                    findings.append(_f(where, "行数", found, t["lines"], line))

            for m in CHAR_COUNT.finditer(line):
                found = _num(m.group(1))
                if found != t["chars"]:
                    findings.append(_f(where, "字符数", found, t["chars"], line))

            for m in TOKEN_COUNT.finditer(line):
                found = _num(m.group(1))
                if found != t["tokens"]:
                    findings.append(_f(where, "token 估算", found, t["tokens"], line))

    return findings


def _markdown_files() -> list[Path]:
    """要扫描的 Markdown：文档站全部 + cc-guide skill 全部。"""
    out: list[Path] = []
    for d in SCAN_DIRS:
        if d.is_dir():
            out.extend(sorted(d.rglob("*.md")))
    return out


def _paragraphs(lines: list[str]) -> list[tuple[int, list[str]]]:
    """按空行切段，每段记录起始行号。"""
    out = []
    buf: list[str] = []
    start = 1
    for lineno, line in enumerate(lines, 1):
        if not line.strip():
            if buf:
                out.append((start, buf))
                buf = []
            continue
        if not buf:
            start = lineno
        buf.append(line)
    if buf:
        out.append((start, buf))
    return out


def _f(where: str, kind: str, found: int, expected: int, text: str) -> dict:
    return {
        "where": where,
        "kind": kind,
        "found": found,
        "expected": expected,
        "text": text.strip()[:140],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="校验文档里的 CLAUDE.md 尺寸数字")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args()

    t = truth()
    findings = scan()

    if args.json:
        print(json.dumps({"truth": t, "mismatches": findings}, ensure_ascii=False, indent=2))
        return 1 if findings else 0

    print(
        f"CLAUDE.md 真值：{t['lines']} 行 / {t['chars']:,} 字符 / "
        f"≈{t['tokens']:,} tok / 超标 {t['over_pct']}%"
    )

    for f in findings:
        print(
            f"❌ {f['where']} · {f['kind']}：文档写 {f['found']}，实际 {f['expected']}\n"
            f"   {f['text']}"
        )

    if findings:
        print(f"\n{len(findings)} 处数字与现实不符")
        return 1

    print("✅ 文档里所有写死的 CLAUDE.md 尺寸数字都与文件一致")
    return 0


if __name__ == "__main__":
    sys.exit(main())
