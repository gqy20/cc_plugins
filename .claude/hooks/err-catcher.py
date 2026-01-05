#!/usr/bin/env python3
import json
import sys
import subprocess
import re

# 错误模式 → (domain, severity, id_suffix)
ERROR_PATTERNS = [
    # pytest 错误
    (r"FAILED|AssertionError", "tool", "major", "TEST-FAIL"),
    (r"ImportError|ModuleNotFoundError", "tool", "blocker", "IMPORT"),
    (r"FixtureNotFound|fixture.*not found", "tool", "major", "FIXTURE"),

    # Git 错误
    (r"merge.*conflict|conflict.*content", "config", "major", "GIT-MERGE"),
    (r"git.*failed|fatal:", "config", "minor", "GIT-ERROR"),

    # 网络/依赖错误
    (r"Connection.*refused|ECONNREFUSED", "network", "blocker", "NET-REFUSED"),
    (r"timeout|ETIMEDOUT", "network", "major", "TIMEOUT"),

    # 配置/权限错误
    (r"Permission denied", "config", "blocker", "PERMISSION"),
    (r"config.*not found|No such file", "config", "major", "CONFIG"),

    # 数据库/API 错误
    (r"database.*error|db.*error", "network", "blocker", "DB-ERROR"),
    (r"API.*error|500|502|503", "network", "major", "API-ERROR"),
]


def detect_error(output: str) -> tuple:
    """检测错误类型，返回 (domain, severity, id_suffix)"""
    for pattern, domain, severity, suffix in ERROR_PATTERNS:
        if re.search(pattern, output, re.IGNORECASE):
            return domain, severity, suffix
    return "other", "minor", "UNKNOWN"


def guess_phase(command: str) -> str:
    """根据命令猜测 TDD 阶段"""
    cmd_lower = command.lower()
    if "pytest" in cmd_lower or "test" in cmd_lower:
        return "test"
    elif any(x in cmd_lower for x in ["git commit", "git add"]):
        return "git"
    elif any(x in cmd_lower for x in ["mypy", "ruff", "black"]):
        return "lint"
    else:
        return "unknown"


def main():
    # 读取 Claude 传递的 JSON
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    if tool_name != "Bash":
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    tool_output = input_data.get("tool_output", "")

    command = tool_input.get("command", "")

    # 检测错误
    domain, severity, suffix = detect_error(tool_output)

    # 如果检测到已知错误模式
    if suffix != "UNKNOWN":
        phase = guess_phase(command)

        # 构建 /err 命令的 payload
        payload = f"""## Command
{command}

## Error Output
{tool_output[:1000]}

## Context
- Phase: {phase}
- Domain: {domain}
- Severity: {severity}
"""

        # 调用 /err 命令
        try:
            subprocess.run(
                ["claude", "/err", "add", "--", payload],
                capture_output=True,
                timeout=10,
                cwd="/home/qy113/workspace/project/2512/cc_plugins"
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    sys.exit(0)


if __name__ == "__main__":
    main()
