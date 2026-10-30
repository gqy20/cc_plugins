#!/usr/bin/env python3
"""测量 skill / agent 的 description 常驻成本，并识别不会生效的布局。

分词器未公开，所以本脚本一律以 **字符数** 为准（精确），
token 数只给量级估算（CJK 1 字 ≈ 1 tok，ASCII 4 字符 ≈ 1 tok）。

关键诊断：
  * `<name>/SKILL.md` —— 标准布局，Claude Code 才会加载
  * `<name>.md`      —— 旧的平铺布局，**会被静默忽略**

用法：
    uv run --with pyyaml python scripts/measure_context.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

HOME = Path.home()
PROJECT = Path(__file__).resolve().parent.parent


def frontmatter(path: Path) -> dict:
    """解析 YAML frontmatter，失败时返回 {}。"""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return {}
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    try:
        data = yaml.safe_load(text[3:end])
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def split_layout(root: Path) -> tuple[list[Path], list[Path]]:
    """返回 (标准布局 `<name>/SKILL.md`, 旧平铺布局 `<name>.md`)。"""
    if not root.is_dir():
        return [], []
    return sorted(root.glob("*/SKILL.md")), sorted(root.glob("*.md"))


def agent_files(root: Path) -> list[Path]:
    return sorted(root.glob("*.md")) if root.is_dir() else []


def desc_len(meta: dict) -> int:
    desc = meta.get("description")
    return len(desc.strip()) if isinstance(desc, str) else 0


def est_tokens(text: str) -> int:
    """估算 token 数。

    分词器未公开，这里用社区常用的经验值：
      * CJK / 全角字符 ≈ 1 token / 字
      * ASCII ≈ 4 字符 / token

    与官方 `claude plugin details` 的 Always-on 估算**有偏差，官方更保守**
    （实测本插件 436 字符 → 本函数 388 tok，官方报 ~232 tok）。
    所以：**量级可用，别当精确值**；字符数才是精确的。
    """
    cjk = sum(1 for c in text if ord(c) > 0x2E80)
    ascii_n = len(text) - cjk
    return cjk + ascii_n // 4


def report(label: str, files: list[Path]) -> tuple[int, int, int]:
    """统计能解析出 description 的文件数、字符数与估算 token。"""
    chars = counted = 0
    tokens = 0
    broken: list[Path] = []
    for f in files:
        meta = frontmatter(f)
        desc = meta.get("description")
        if isinstance(desc, str) and desc.strip():
            chars += len(desc.strip())
            tokens += est_tokens(desc.strip())
            counted += 1
        else:
            broken.append(f)
    flag = ""
    if broken:
        flag = "   ← " + ", ".join(f.name for f in broken[:3]) + " 解析失败"
    print(f"{label:<40} {counted:>4}/{len(files):<4} {chars:>8,} 字符  ≈{tokens:>6,} tok{flag}")
    return counted, chars, tokens


def installed_plugin_paths() -> dict[str, Path]:
    """从 installed_plugins.json 读出每个插件**实际生效**的安装路径。

    cache/ 下可能有多个版本，只有这里登记的那个才生效。
    """
    f = HOME / ".claude/plugins/installed_plugins.json"
    if not f.is_file():
        return {}
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    out: dict[str, Path] = {}
    for key, entries in (data.get("plugins") or {}).items():
        if not isinstance(entries, list) or not entries:
            continue
        entry = next((e for e in entries if e.get("scope") == "user"), entries[-1])
        p = entry.get("installPath")
        if p and Path(p).is_dir():
            out[key.split("@")[0]] = Path(p)
    return out


def enabled_plugin_names() -> set[str]:
    """本项目启用的插件名（用户级 + 项目级 settings 的并集）。"""
    out: set[str] = set()
    for f in (HOME / ".claude/settings.json", PROJECT / ".claude/settings.json"):
        if not f.is_file():
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for key, val in (data.get("enabledPlugins") or {}).items():
            if val:
                out.add(key.split("@")[0])
    return out


def main() -> int:
    print("=== skill / agent description 常驻成本 ===")
    print(f"{'来源':<40} {'可用/总数':>9}     {'字符数':>8}    {'估算 tokens':>10}")
    print("-" * 108)

    enabled = enabled_plugin_names()
    totals = {"skill": [0, 0], "agent": [0, 0], "off": [0, 0]}  # [字符数, token数]

    for label, root in (
        ("用户级 ~/.claude/skills/", HOME / ".claude/skills"),
        ("项目级 .claude/skills/", PROJECT / ".claude/skills"),
    ):
        std, legacy = split_layout(root)
        _, c, t = report(label + " (标准布局)", std)
        totals["skill"][0] += c
        totals["skill"][1] += t
        if legacy:
            report(label + " (旧平铺布局，不加载)", legacy)

    for label, root in (
        ("用户级 ~/.claude/agents/", HOME / ".claude/agents"),
        ("项目级 .claude/agents/", PROJECT / ".claude/agents"),
    ):
        _, c, t = report(label, agent_files(root))
        totals["agent"][0] += c
        totals["agent"][1] += t

    for name, root in sorted(installed_plugin_paths().items()):
        on = name in enabled
        note = "" if on else "  [本项目未启用]"
        std, legacy = split_layout(root / "skills")
        if std:
            _, c, t = report(f"插件 {name} · skill{note}", std)
            key = "skill" if on else "off"
            totals[key][0] += c
            totals[key][1] += t
        if legacy:
            report(f"插件 {name} · skill (旧平铺，不加载)", legacy)
        ag = agent_files(root / "agents")
        if ag:
            _, c, t = report(f"插件 {name} · agent{note}", ag)
            key = "agent" if on else "off"
            totals[key][0] += c
            totals[key][1] += t

    print("-" * 108)
    for label, key in (("本项目生效的 skill description", "skill"),
                       ("本项目生效的 agent description", "agent")):
        chars, toks = totals[key]
        print(f"{label:<40} {chars:>8,} 字符  ≈{toks:>6,} tok")
    chars, toks = totals["off"]
    print(f"{'已安装但本项目未启用（不计入）':<40} {chars:>8,} 字符  ≈{toks:>6,} tok")
    print()
    print("提示：完整清单（含内置 skill 与插件 skill）见 Claude Code 启动日志：")
    print("  claude --debug -p hi   →  ~/.claude/debug/<session-id>.txt")
    print("  grep 'Skill listing over budget' ~/.claude/debug/<session-id>.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
