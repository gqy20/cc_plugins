#!/usr/bin/env python3
"""校验 .claude/rules/*.md 的 frontmatter 与正文。

路径规则写错（缺 paths、YAML 坏了）时，Claude Code 会静默忽略整条规则，
所以和 skill frontmatter 一样需要一个守卫。

用法：
    uv run --with pyyaml python scripts/check_rules.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
RULES = ROOT / ".claude" / "rules"


def split_frontmatter(text: str) -> tuple[str | None, str]:
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---", 4)
    if end == -1:
        return None, text
    return text[4:end], text[end + 4:]


def main() -> int:
    files = sorted(RULES.glob("*.md")) if RULES.is_dir() else []
    if not files:
        print(f"未找到规则文件：{RULES}")
        return 1

    errors: list[str] = []
    for path in files:
        frontmatter, body = split_frontmatter(path.read_text(encoding="utf-8"))
        if frontmatter is None:
            errors.append(f"{path.name}: 缺少 `---` frontmatter")
            continue
        try:
            data = yaml.safe_load(frontmatter) or {}
        except yaml.YAMLError as exc:
            errors.append(f"{path.name}: YAML 解析失败：{exc}")
            continue
        paths = data.get("paths")
        if not isinstance(paths, list) or not paths or not all(
            isinstance(p, str) and p.strip() for p in paths
        ):
            errors.append(f"{path.name}: paths 必须是非空字符串数组")
        if not body.strip():
            errors.append(f"{path.name}: 正文为空")

    if errors:
        for error in errors:
            print(f"❌ {error}")
        return 1
    print(f"✅ {len(files)} 条路径规则通过校验")
    return 0


if __name__ == "__main__":
    sys.exit(main())
