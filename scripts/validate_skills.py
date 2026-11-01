#!/usr/bin/env python3
"""校验本仓库所有 skill / agent 的 frontmatter。

为什么需要它：Claude Code 对 frontmatter 解析失败的文件是**静默忽略**的 ——
不报错、不提示、只是不加载。skill 的 `description` 写坏了，Claude 就永远
不会调用它。本脚本把这类静默失败变成显式报错。

检查项：
  1. 文件存在且非空
  2. YAML 能解析
  3. `name` 存在、kebab-case、与所在目录名一致
  4. `description` 存在且长度合理
  5. skill 正文非空
  6. `allowed-tools` 等已知字段的形状正确
  7. 常见 YAML 陷阱（未加引号的 `: `、相邻流式序列、多行隐式键）

用法::

    uv run --with pyyaml python scripts/validate_skills.py
    uv run --with pyyaml python scripts/validate_skills.py --root .claude/skills
    uv run --with pyyaml python scripts/validate_skills.py --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("需要 pyyaml：uv run --with pyyaml python scripts/validate_skills.py")

# 这些目录下的 skill / agent 都参与校验
DEFAULT_ROOTS = [
    ".claude/skills",
    ".claude/agents",
    "plugins",
]

KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# 下划线：Claude Code 接受，但官方规范要求 kebab-case
KEBAB_UNDERSCORE = re.compile(r"^[a-z0-9]+([_-][a-z0-9]+)*$")

# skill 允许出现的 frontmatter 字段（Claude Code 认识的 + 常见的无害字段）
KNOWN_SKILL_KEYS = {
    "name",
    "description",
    "allowed-tools",
    "allowed_tools",
    "model",
    "disable-model-invocation",
    "argument-hint",
    "user-invocable",
    "version",
    "tags",
    "dependencies",
    "context",
    "agent",
    "hooks",
    "metadata",
}

KNOWN_AGENT_KEYS = {
    "name",
    "description",
    "tools",
    "model",
    "color",
    "isolation",
    "mode",
    "permissionMode",
    "permission_mode",
    "effort",
    "maxTurns",
    "max_turns",
    "skills",
    "mcpServers",
    "hooks",
    "version",
    "tags",
    "dependencies",
    "input_schema",
}

# agent 的 frontmatter 里 Claude Code 不认识的字段（启动时会告警）
KNOWN_AGENT_EXTRA = {"version", "input_schema"}


@dataclass
class Issue:
    path: str
    level: str  # error | warn
    code: str
    message: str
    hint: str = ""


@dataclass
class Report:
    issues: list[Issue] = field(default_factory=list)
    scanned: int = 0

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.level == "error"]

    @property
    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.level == "warn"]


def split_frontmatter(text: str) -> tuple[str | None, str, str]:
    """返回 (frontmatter 原文, 正文, 错误信息)。"""
    if not text.startswith("---"):
        return None, text, "缺少 frontmatter（文件必须以 '---' 开头）"

    parts = text.split("\n---", 1)
    if len(parts) < 2:
        return None, text, "frontmatter 没有结束标记 '---'"

    raw = parts[0][3:].strip("\n")
    body = parts[1]
    if body.startswith("\n"):
        body = body[1:]
    return raw, body, ""


def yaml_traps(raw: str) -> list[tuple[str, str]]:
    """在真正解析前，先扫一遍常见 YAML 陷阱，给出更具体的提示。"""
    traps: list[tuple[str, str]] = []
    for lineno, line in enumerate(raw.split("\n"), start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):\s+(.*)$", line)
        value = m.group(2) if m else None
        # 整值已加引号的行是合法标量，两个陷阱都不适用
        quoted = value is not None and value.startswith(("'", '"'))
        # 相邻的流式序列：[a] [b]
        if not quoted and re.search(r"\[[^\]]*\]\s+\[[^\]]*\]", line):
            traps.append(
                (
                    f"第 {lineno} 行",
                    "两个相邻的流式序列会被当成非法 YAML（Unexpected token）",
                )
            )
        # 未加引号的 ": "（只检查顶层键值对行，避免误报）
        if m:
            if ": " in value and not value.startswith(("'", '"', "|", ">", "[")):
                traps.append(
                    (
                        f"第 {lineno} 行",
                        f"值里有 ': ' 却没有引号（{m.group(1)}: {value[:40]}…）",
                    )
                )
    return traps


def validate_skill_file(path: Path, rep: Report, rel: str) -> None:
    rep.scanned += 1
    text = path.read_text(encoding="utf-8", errors="replace")

    if not text.strip():
        rep.issues.append(Issue(rel, "error", "EMPTY", "文件为空"))
        return

    raw, body, err = split_frontmatter(text)
    if raw is None:
        rep.issues.append(Issue(rel, "error", "NO_FRONTMATTER", err))
        return

    for lineno, msg in yaml_traps(raw):
        rep.issues.append(
            Issue(
                rel,
                "error",
                "YAML_TRAP",
                f"{lineno}：{msg}",
                "整句加引号，或多行文本改用 `|` 块标量",
            )
        )

    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        rep.issues.append(
            Issue(
                rel,
                "error",
                "YAML_PARSE",
                f"YAML 解析失败：{str(e).splitlines()[0]}",
                "多行文本用 `|` 块标量；含 ': ' 的整句加引号",
            )
        )
        return

    if not isinstance(data, dict):
        rep.issues.append(Issue(rel, "error", "YAML_TYPE", "frontmatter 不是映射（应是 key: value）"))
        return

    name = data.get("name")
    if not name:
        rep.issues.append(Issue(rel, "error", "NO_NAME", "缺少 name 字段"))
    else:
        if not isinstance(name, str):
            rep.issues.append(Issue(rel, "error", "NAME_TYPE", "name 不是字符串"))
        else:
            if not KEBAB.match(name):
                if KEBAB_UNDERSCORE.match(name):
                    rep.issues.append(
                        Issue(
                            rel,
                            "warn",
                            "NAME_UNDERSCORE",
                            f"name 用的是下划线而非 kebab-case：{name!r}",
                            "Claude Code 能加载，但官方规范建议 kebab-case",
                        )
                    )
                else:
                    rep.issues.append(
                        Issue(rel, "error", "NAME_FORMAT", f"name 不是 kebab-case：{name!r}")
                    )
            if name != path.parent.name and "SKILL" in path.name:
                rep.issues.append(
                    Issue(
                        rel,
                        "error",
                        "NAME_DIR_MISMATCH",
                        f"name ({name!r}) 与目录名 ({path.parent.name!r}) 不一致",
                    )
                )

    desc = data.get("description")
    if not desc:
        rep.issues.append(Issue(rel, "error", "NO_DESCRIPTION", "缺少 description 字段"))
    elif not isinstance(desc, str):
        rep.issues.append(Issue(rel, "error", "DESC_TYPE", "description 不是字符串"))
    elif len(desc.strip()) < 10:
        rep.issues.append(
            Issue(rel, "warn", "DESC_SHORT", f"description 过短（{len(desc.strip())} 字符），难以匹配触发场景")
        )
    elif len(desc) > 1024:
        rep.issues.append(
            Issue(
                rel,
                "warn",
                "DESC_LONG",
                f"description 过长（{len(desc)} 字符），description 是常驻上下文，省着点",
            )
        )

    if "SKILL" in path.name and not body.strip():
        rep.issues.append(Issue(rel, "error", "EMPTY_BODY", "skill 正文为空"))

    unknown = set(data) - KNOWN_SKILL_KEYS
    for k in sorted(unknown):
        rep.issues.append(
            Issue(
                rel,
                "warn",
                "UNKNOWN_KEY",
                f"frontmatter 字段 {k!r} 不在已知列表里（Claude Code 会告警并忽略）",
            )
        )


def validate_agent_file(path: Path, rep: Report, rel: str) -> None:
    rep.scanned += 1
    text = path.read_text(encoding="utf-8", errors="replace")

    if not text.strip():
        rep.issues.append(Issue(rel, "error", "EMPTY", "文件为空"))
        return

    raw, body, err = split_frontmatter(text)
    if raw is None:
        rep.issues.append(Issue(rel, "error", "NO_FRONTMATTER", err))
        return

    for lineno, msg in yaml_traps(raw):
        rep.issues.append(
            Issue(
                rel,
                "error",
                "YAML_TRAP",
                f"{lineno}：{msg}",
                "整句加引号，或多行文本改用 `|` 块标量",
            )
        )

    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        rep.issues.append(
            Issue(
                rel,
                "error",
                "YAML_PARSE",
                f"YAML 解析失败：{str(e).splitlines()[0]}",
                "多行文本用 `|` 块标量；含 ': ' 的整句加引号",
            )
        )
        return

    if not isinstance(data, dict):
        rep.issues.append(Issue(rel, "error", "YAML_TYPE", "frontmatter 不是映射（应是 key: value）"))
        return

    for required in ("name", "description"):
        if not data.get(required):
            rep.issues.append(Issue(rel, "error", f"NO_{required.upper()}", f"缺少 {required} 字段"))

    desc = data.get("description")
    if isinstance(desc, str) and not desc.strip():
        rep.issues.append(Issue(rel, "error", "EMPTY_DESCRIPTION", "description 为空"))

    for k in sorted(set(data) & KNOWN_AGENT_EXTRA):
        rep.issues.append(
            Issue(
                rel,
                "warn",
                "IGNORED_KEY",
                f"字段 {k!r} 不被 Claude Code 识别（启动日志会告警）",
            )
        )

    for k in sorted(set(data) - KNOWN_AGENT_KEYS):
        rep.issues.append(
            Issue(rel, "warn", "UNKNOWN_KEY", f"frontmatter 字段 {k!r} 不在已知列表里")
        )


def collect(root: Path) -> list[tuple[Path, bool]]:
    """返回 [(文件路径, 是否 skill)]。"""
    found: list[tuple[Path, bool]] = []
    if not root.exists():
        return found

    for p in sorted(root.rglob("SKILL.md")):
        found.append((p, True))
    for p in sorted(root.rglob("*.md")):
        if p.name == "SKILL.md":
            continue
        # 旧平铺布局的 skill 也要查，但要单独标记
        if p.parent.name == "skills":
            found.append((p, True))
        elif p.parent.name == "agents":
            found.append((p, False))
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", action="append", help="要扫描的目录，可重复；默认扫 .claude/skills、.claude/agents、plugins")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args()

    project = Path(__file__).resolve().parent.parent
    roots = [Path(r) for r in args.root] if args.root else [project / r for r in DEFAULT_ROOTS]
    roots = [(r if r.is_absolute() else (project / r)).resolve() for r in roots]

    rep = Report()
    scanned_paths: set[Path] = set()
    for root in roots:
        for path, is_skill in collect(root):
            if path in scanned_paths:
                continue
            scanned_paths.add(path)
            try:
                rel = path.relative_to(project).as_posix()
            except ValueError:
                rel = path.as_posix()
            if is_skill:
                validate_skill_file(path, rep, rel)
            else:
                validate_agent_file(path, rep, rel)

    if args.json:
        print(
            json.dumps(
                {
                    "scanned": rep.scanned,
                    "errors": [
                        {"path": i.path, "code": i.code, "message": i.message, "hint": i.hint}
                        for i in rep.errors
                    ],
                    "warnings": [
                        {"path": i.path, "code": i.code, "message": i.message, "hint": i.hint}
                        for i in rep.warnings
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1 if rep.errors else 0

    print(f"扫描 {rep.scanned} 个文件：{len(rep.errors)} 个错误，{len(rep.warnings)} 个警告\n")

    for level, issues in (("ERROR", rep.errors), ("WARN", rep.warnings)):
        if not issues:
            continue
        print(f"── {level} ──")
        for i in issues:
            line = f"  {i.path}: [{i.code}] {i.message}"
            if i.hint:
                line += f"\n      → {i.hint}"
            print(line)
        print()

    if rep.errors:
        print("❌ 有错误：这些文件会被 Claude Code 静默忽略。")
        return 1
    print("✅ 全部通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
