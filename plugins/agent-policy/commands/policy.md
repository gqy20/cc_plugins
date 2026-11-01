---
description: 管理 agent-policy 策略（init / check / test / list）
argument-hint: <init|check|test|list>
---

# /policy

对 `$ARGUMENTS` 指定的子命令，运行本插件的策略引擎：

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/policy.py" "$ARGUMENTS" --project .
```

子命令：

- `init` —— 在项目根生成 `agent-policy.toml`（已存在时不覆盖，除非加 `--force`）
- `check` —— 校验 schema、预设引用与重复 id；加 `--strict` 时要求每条 deny/ask 规则都有测试夹具
- `test` —— 运行策略里的测试夹具
- `list` —— 列出生效规则

改完策略后，先跑 `check --strict` 和 `test`，再把结果如实汇报给用户。若 `$ARGUMENTS` 为空，先运行 `list`，并提示可用的四个子命令。
