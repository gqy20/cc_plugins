#!/usr/bin/env python3
"""检查 `.claude/skills/` 下的 Markdown 链接指向 `docs/cc-guide/` 时是否有效。

**为什么需要这个脚本**：`mkdocs build --strict` 只校验 `docs/` 里的链接。
`.claude/skills/` 不在 MkDocs 的构建范围内 —— 那里的坏锚点是**隐形**的，
而 skill 是 Claude 实际读进上下文的载体，链接坏了它照样会把错的内容读进去。

检查两件事：
1. 目标文件存在
2. 目标文件里有对应的锚点（标题），锚点规则与 `scripts/mkdocs_slug.py` 一致

用法：
    uv run python scripts/check_skill_links.py
    uv run python scripts/check_skill_links.py --json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
GUIDE = PROJECT / "docs" / "cc-guide"
SKILLS = PROJECT / ".claude" / "skills"

# Markdown 行内链接：[文字](目标) —— 排除图片、代码块里的假链接
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)")
# ATX 标题
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$", re.MULTILINE)


def _load_slugify():
    """复用 mkdocs.yml 里配置的同一个 slugify。"""
    spec = importlib.util.spec_from_file_location(
        "mkdocs_slug", PROJECT / "scripts" / "mkdocs_slug.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.slugify


def anchors_of(path: Path, slugify) -> set[str]:
    """收集一个 Markdown 文件里所有标题生成的锚点 id。"""
    text = path.read_text(encoding="utf-8")
    # 去掉围栏代码块 —— 里面的 # 不是标题
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    out = set()
    for _, title in HEADING.findall(text):
        # Markdown 渲染器会去掉行内代码的 ` 和强调的 *，slugify 结果一致
        cleaned = title.replace("`", "").replace("*", "")
        out.add(slugify(cleaned))
    return out


def check_link(target: str, source: Path, slugify) -> tuple[bool, str, Path | None]:
    """返回 (是否有效, 失败原因, 解析后的目标路径)。"""
    path_part, _, anchor = target.partition("#")
    if not path_part:
        # 同页锚点
        anchors = anchors_of(source, slugify)
        if anchor in anchors:
            return True, "", source
        return False, f"同页锚点不存在：#{anchor}", None

    dest = (source.parent / path_part).resolve()
    if not dest.is_file():
        return False, f"目标文件不存在：{path_part}", dest

    if not anchor:
        return True, "", dest

    anchors = anchors_of(dest, slugify)
    if anchor not in anchors:
        return False, f"锚点不存在：{path_part}#{anchor}", dest
    return True, "", dest


def main() -> int:
    parser = argparse.ArgumentParser(description="检查 skill 目录里指向 cc-guide 的链接")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args()

    slugify = _load_slugify()

    if not SKILLS.is_dir():
        print(f"❌ 目录不存在：{SKILLS}")
        return 1

    results: list[dict] = []
    checked = 0
    for md in sorted(SKILLS.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        # 去掉围栏代码块，避免把示例里的路径当成链接
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        for target in LINK.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            ok, reason, dest = check_link(target, md, slugify)
            # 只关心指向 docs/cc-guide/ 的链接
            if dest is None or not dest.is_relative_to(GUIDE):
                continue
            checked += 1
            results.append(
                {
                    "source": md.relative_to(PROJECT).as_posix(),
                    "target": target,
                    "ok": ok,
                    "reason": reason,
                }
            )

    failed = [r for r in results if not r["ok"]]

    if args.json:
        print(json.dumps({"checked": checked, "failed": failed}, ensure_ascii=False, indent=2))
        return 1 if failed else 0

    for r in failed:
        print(f"❌ {r['source']} → {r['target']}\n   {r['reason']}")

    if failed:
        print(f"\n{len(failed)}/{checked} 条链接失效")
        return 1

    print(f"✅ {checked} 条指向 docs/cc-guide/ 的链接全部有效")
    return 0


if __name__ == "__main__":
    sys.exit(main())
