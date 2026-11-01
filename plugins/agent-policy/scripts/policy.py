#!/usr/bin/env python3
"""agent-policy：单入口策略分发器。

一个钩子进程，读项目根的 agent-policy.toml，按事件/工具/路径决定
allow / ask / deny，或在动作后执行校验命令。

用法（由 hooks/hooks.json 调用，也可手动跑）：
    policy.py hook pre|post|stop [--project DIR]
    policy.py check [--project DIR] [--strict]
    policy.py test  [--project DIR]
    policy.py list  [--project DIR]
    policy.py init  [--project DIR] [--force]

设计约束：
- 只用标准库（Python 3.11+ 的 tomllib），钩子启动要快；
- 缺配置时放行并告警，避免一个坏文件锁死所有工具调用；
- 硬规则失败策略由 defaults.on_error / then.fail 显式声明。
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    sys.stderr.write("agent-policy 需要 Python 3.11+（tomllib）\n")
    sys.exit(1)

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
PRESETS_DIR = PLUGIN_ROOT / "presets"
POLICY_NAME = "agent-policy.toml"

EVENT_MAP = {"PreToolUse": "pre", "PostToolUse": "post", "Stop": "stop"}
VALID_EVENTS = {"pre", "post", "stop"}
VALID_ACTIONS = {"deny", "ask", "allow", "run"}
VALID_BUILTINS = {"outside_workspace"}
ACTION_LEVEL = {"allow": 1, "ask": 2, "deny": 3}
PATH_KEYS = ("file_path", "path", "notebook_path", "target_file")


# ---------- 策略加载 ----------

def project_root(explicit: str | None = None) -> Path:
    return Path(explicit or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()


def _read_toml(path: Path) -> dict:
    with path.open("rb") as f:
        return tomllib.load(f)


def load_policy(root: Path) -> tuple[list[dict], dict, list[str]]:
    """返回 (rules, defaults, errors)。项目规则按 id 覆盖同名预设规则。"""
    path = root / POLICY_NAME
    if not path.exists():
        return [], {}, [f"未找到 {path}"]
    try:
        data = _read_toml(path)
    except Exception as e:  # noqa: BLE001 - 配置错误需要原样报告
        return [], {}, [f"{path} 解析失败：{e}"]

    rules: list[dict] = []
    errors: list[str] = []
    for name in data.get("extends", []):
        preset = PRESETS_DIR / f"{name}.toml"
        if not preset.exists():
            errors.append(f"预设不存在：{name}（{preset}）")
            continue
        rules.extend(_read_toml(preset).get("rule", []))
    rules.extend(data.get("rule", []))

    merged: dict[str, dict] = {}
    for rule in rules:
        rid = rule.get("id")
        if not rid:
            errors.append(f"规则缺少 id：{rule}")
            continue
        merged[rid] = rule  # 后出现的项目规则覆盖预设
    active = [r for r in merged.values() if r.get("enabled", True)]
    return active, data.get("defaults", {}), errors


# ---------- 匹配 ----------

def _as_list(value) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _glob_any(value: str, patterns) -> bool:
    return any(fnmatch.fnmatchcase(value, p) for p in _as_list(patterns))


def is_outside(path: str, root: Path) -> bool:
    resolved = os.path.realpath(path if os.path.isabs(path) else os.path.join(root, path))
    try:
        return os.path.commonpath([resolved, str(root)]) != str(root)
    except ValueError:  # Windows 跨盘符
        return True


def context_from_input(data: dict) -> dict:
    tool_input = data.get("tool_input") or {}
    path = next((tool_input[k] for k in PATH_KEYS if tool_input.get(k)), None)
    return {
        "event": EVENT_MAP.get(data.get("hook_event_name", ""), ""),
        "tool": data.get("tool_name", ""),
        "path": path,
        "command": tool_input.get("command", "") or "",
    }


def rule_event(rule: dict) -> str:
    return str(rule.get("when", {}).get("event", "")).lower()


def rule_action(rule: dict) -> str | None:
    """then.action；只写了 then.run 时视为 run。"""
    then = rule.get("then", {})
    return then.get("action") or ("run" if then.get("run") else None)


def matches(rule: dict, ctx: dict, root: Path) -> bool:
    when = rule.get("when", {})
    if rule_event(rule) != ctx["event"]:
        return False
    if when.get("tool") and not _glob_any(ctx["tool"], when["tool"]):
        return False
    if when.get("command"):
        if not any(re.search(p, ctx["command"]) for p in _as_list(when["command"])):
            return False
    if when.get("path"):
        if not ctx["path"]:
            return False
        rel = os.path.relpath(ctx["path"], root) if os.path.isabs(ctx["path"]) else ctx["path"]
        if not (_glob_any(rel, when["path"]) or _glob_any(ctx["path"], when["path"])):
            return False
    builtin = rule.get("builtin")
    if builtin == "outside_workspace":
        if not ctx["path"] or not is_outside(ctx["path"], root):
            return False
    elif builtin:
        raise ValueError(f"未知 builtin：{builtin}")
    return True


def decide(rules: list[dict], ctx: dict, root: Path) -> tuple[str | None, str]:
    """pre 事件：取最强决策（deny > ask > allow）。"""
    action, reason = None, ""
    for rule in rules:
        if rule_action(rule) not in ACTION_LEVEL:
            continue
        if not matches(rule, ctx, root):
            continue
        cand = rule["then"]["action"]
        if action is None or ACTION_LEVEL[cand] > ACTION_LEVEL[action]:
            action, reason = cand, rule["then"].get("reason", rule.get("id", ""))
    return action, reason


def run_rules(rules: list[dict], ctx: dict, root: Path) -> list[tuple[dict, bool, str]]:
    """执行 post/stop 的 run 规则，返回 (rule, ok, message)。"""
    results = []
    for rule in rules:
        then = rule.get("then", {})
        if rule_action(rule) != "run":
            continue
        if not matches(rule, ctx, root):
            continue
        cmd = then.get("run")
        if not cmd:
            results.append((rule, False, "run 规则缺少 then.run"))
            continue
        timeout = float(then.get("timeout", 15))
        try:
            proc = subprocess.run(
                cmd, shell=True, cwd=str(root), capture_output=True, text=True, timeout=timeout
            )
        except subprocess.TimeoutExpired:
            results.append((rule, False, f"超时（>{timeout:g}s）：{cmd}"))
            continue
        if proc.returncode != 0:
            lines = (proc.stderr or proc.stdout or "").strip().splitlines()
            detail = lines[-1] if lines else f"exit {proc.returncode}"
            results.append((rule, False, f"{cmd} → {detail}"))
        else:
            results.append((rule, True, ""))
    return results


# ---------- hook 入口 ----------

def _emit_pre(action: str, reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": action,
            "permissionDecisionReason": reason,
        }
    }, ensure_ascii=False))


def cmd_hook(args) -> int:
    root = project_root(args.project)
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        data = {}
    rules, defaults, errors = load_policy(root)
    on_error = defaults.get("on_error", "open")
    if errors:
        for e in errors:
            sys.stderr.write(f"[agent-policy] {e}\n")
        return 2 if on_error == "closed" else 0

    ctx = context_from_input(data)
    event = args.event or ctx["event"]
    ctx["event"] = event

    if event == "pre":
        action, reason = decide(rules, ctx, root)
        if action in ("deny", "ask"):
            _emit_pre(action, reason)
        return 0

    if event in ("post", "stop"):
        blocked = False
        for rule in rules:
            then = rule.get("then", {})
            if then.get("action") == "deny" and matches(rule, ctx, root):
                sys.stderr.write(f"[agent-policy] {then.get('reason', rule.get('id'))}\n")
                blocked = True
        for rule, ok, msg in run_rules(rules, ctx, root):
            if ok:
                continue
            fail = rule.get("then", {}).get("fail", "open")
            sys.stderr.write(f"[agent-policy] {rule.get('id')} 失败：{msg}\n")
            if fail == "closed":
                blocked = True
        return 2 if blocked else 0

    sys.stderr.write(f"[agent-policy] 未知事件：{event}\n")
    return 1


# ---------- 校验 / 测试 / 列表 ----------

def validate(root: Path, strict: bool) -> int:
    path = root / POLICY_NAME
    if not path.exists():
        print(f"❌ 未找到 {path}")
        return 1
    rules, _, errors = load_policy(root)
    problems = list(errors)
    seen: set[str] = set()
    for rule in rules:
        rid = rule.get("id", "?")
        if rid in seen:
            problems.append(f"重复 id：{rid}")
        seen.add(rid)
        event = rule_event(rule)
        if event not in VALID_EVENTS:
            problems.append(f"{rid}: when.event 必须是 {sorted(VALID_EVENTS)}")
        if rule.get("builtin") and rule["builtin"] not in VALID_BUILTINS:
            problems.append(f"{rid}: 未知 builtin {rule['builtin']}")
        then = rule.get("then", {})
        action = rule_action(rule)
        if action not in VALID_ACTIONS:
            problems.append(f"{rid}: then.action 必须是 {sorted(VALID_ACTIONS)}")
        if then.get("fail") not in (None, "open", "closed"):
            problems.append(f"{rid}: then.fail 只能是 open/closed")
        if action == "run" and not then.get("run"):
            problems.append(f"{rid}: action=run 需要 then.run")
        if action in ("deny", "ask") and strict and not rule.get("test"):
            problems.append(f"{rid}: 硬规则缺少 test 夹具（--strict）")

    if problems:
        for p in problems:
            print(f"❌ {p}")
        return 1
    print(f"✅ {len(rules)} 条规则通过校验（{path}）")
    return 0


def test_rules(root: Path) -> int:
    rules, _, errors = load_policy(root)
    if errors:
        for e in errors:
            print(f"❌ {e}")
        return 1
    total = failed = 0
    for rule in rules:
        for case in rule.get("test", []):
            total += 1
            ctx = context_from_input(case.get("input", {}))
            ctx["event"] = ctx["event"] or rule_event(rule)
            matched = matches(rule, ctx, root)
            expect = case.get("expect", "match")
            if expect == "match":
                ok = matched
            elif expect == "pass":
                ok = not matched
            else:
                action, _ = decide([rule], ctx, root)
                ok = matched and action == expect
            if not ok:
                failed += 1
                print(f"❌ {rule.get('id')}: 期望 {expect}，实际 matched={matched}")
    if failed:
        print(f"\n{failed}/{total} 条夹具失败")
        return 1
    print(f"✅ {total} 条夹具通过")
    return 0


def cmd_list(root: Path) -> int:
    rules, _, errors = load_policy(root)
    if errors:
        for e in errors:
            print(f"❌ {e}")
        return 1
    print(f"{'ID':<28} {'EVENT':<6} {'ACTION':<6} TOOL")
    for rule in rules:
        when = rule.get("when", {})
        print(f"{rule.get('id', '?'):<28} {rule_event(rule):<6} {rule_action(rule):<6} {when.get('tool', '*')}")
    return 0


INIT_TEMPLATE = """\
# agent-policy：项目策略。字段说明见插件 README。
version = 1
extends = ["recommended"]

# 追加项目规则：
# [[rule]]
# id = "docs-tables"
# when = { event = "post", tool = ["Edit", "Write"], path = "docs/**" }
# then = { run = "python3 scripts/check_tables.py docs", fail = "closed", timeout = 15 }
"""


def cmd_init(root: Path, force: bool) -> int:
    path = root / POLICY_NAME
    if path.exists() and not force:
        print(f"已存在 {path}（用 --force 覆盖）")
        return 1
    path.write_text(INIT_TEMPLATE, encoding="utf-8")
    print(f"✅ 已写入 {path}")
    print("下一步：编辑规则，然后运行 policy.py check --strict && policy.py test")
    return 0


# ---------- CLI ----------

def main() -> int:
    parser = argparse.ArgumentParser(description="agent-policy")
    sub = parser.add_subparsers(dest="cmd", required=True)

    hook = sub.add_parser("hook", help="钩子入口（从 stdin 读 Claude Code 事件）")
    hook.add_argument("event", choices=sorted(VALID_EVENTS))
    hook.add_argument("--project")

    check = sub.add_parser("check", help="校验策略文件")
    check.add_argument("--project")
    check.add_argument("--strict", action="store_true", help="硬规则必须有 test 夹具")

    test = sub.add_parser("test", help="运行规则夹具")
    test.add_argument("--project")

    lst = sub.add_parser("list", help="列出生效规则")
    lst.add_argument("--project")

    init = sub.add_parser("init", help="生成 agent-policy.toml")
    init.add_argument("--project")
    init.add_argument("--force", action="store_true")

    args = parser.parse_args()
    root = project_root(getattr(args, "project", None))

    if args.cmd == "hook":
        return cmd_hook(args)
    if args.cmd == "check":
        return validate(root, args.strict)
    if args.cmd == "test":
        return test_rules(root)
    if args.cmd == "list":
        return cmd_list(root)
    return cmd_init(root, args.force)


if __name__ == "__main__":
    sys.exit(main())
