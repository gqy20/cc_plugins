# agent-policy

把“必须遵守”的约束做成策略文件，用一个钩子进程统一执行。

- **一个入口**：只注册 `PreToolUse` / `PostToolUse` / `Stop` 三个钩子，全部指向 `scripts/policy.py`；
- **一份配置**：项目根 `agent-policy.toml`，规则可 review、可测试；
- **确定性执行**：`deny` / `ask` 不依赖模型自觉；`run` 在动作后跑现有校验脚本；
- **零依赖**：只用 Python 3.11+ 标准库（`tomllib`）。

## 快速开始

### 作为 Claude Code 插件

1. 启用本插件（marketplace 里是 `agent-policy`）；
2. `/policy init` 生成 `agent-policy.toml`；
3. 按需追加规则，然后 `/policy check --strict`、`/policy test`。

插件自带 `presets/recommended.toml`，默认开启三条硬规则：

| 规则 | 行为 |
|---|---|
| `no-secrets-access` | 读 `secrets/`、`.env` 一律 deny |
| `no-write-outside-workspace` | Write/Edit 越出项目目录一律 deny |
| `ask-destructive-shell` | `rm -rf /`、`mkfs`、`dd of=/dev/…` 改为人工确认 |

### 不装插件

```bash
python3 plugins/agent-policy/scripts/policy.py init
python3 plugins/agent-policy/scripts/policy.py check --strict
python3 plugins/agent-policy/scripts/policy.py test
python3 plugins/agent-policy/scripts/policy.py list
```

钩子入口从 stdin 读 Claude Code 事件，也可以手动模拟：

```bash
echo '{"hook_event_name":"PreToolUse","tool_name":"Read","tool_input":{"file_path":"secrets/a.env"}}' \
  | python3 scripts/policy.py hook pre
```

## 策略格式

```toml
version = 1
extends = ["recommended"]

[[rule]]
id = "docs-tables-must-stay-valid"
description = "改文档后表格结构不能坏"
severity = "major"
when = { event = "post", tool = ["Edit", "Write"], path = "docs/**/*.md" }
then = { run = "python3 scripts/check_tables.py docs", fail = "closed", timeout = 15 }
```

字段：

| 字段 | 说明 |
|---|---|
| `when.event` | `pre` / `post` / `stop` |
| `when.tool` | 工具名，支持 glob（`Bash`、`Edit`、`mcp__*`） |
| `when.path` | 工具参数里的文件路径，支持 glob；同时匹配相对/绝对路径 |
| `when.command` | Bash 命令的正则（字符串或数组，任一命中） |
| `builtin` | 内置判定：`outside_workspace` |
| `then.action` | `deny` / `ask` / `allow` / `run`；只写 `then.run` 时视为 `run` |
| `then.run` | `post`/`stop` 执行的 shell 命令（cwd = 项目根） |
| `then.fail` | `open`（默认，失败只告警）或 `closed`（失败即阻断） |
| `then.timeout` | `run` 的超时秒数，默认 15 |
| `enabled` | 设为 `false` 可停用单条规则 |

预设规则按 `id` 合并：项目里同 `id` 的规则覆盖预设。

## 测试夹具

```toml
[[rule.test]]
input = { hook_event_name = "PreToolUse", tool_name = "Read", tool_input = { file_path = "secrets/a.env" } }
expect = "deny"     # 也可以是 ask / allow / match / pass
```

`check --strict` 会把“硬规则没有夹具”当作错误，避免规则写了却没人验证。

## 失效语义

- 策略文件缺失或解析失败：**默认放行并告警**；把 `defaults.on_error = "closed"` 可改为阻断。
- `run` 超时或非零退出：按 `then.fail` 处理；安全类规则应写 `closed`。
- 钩子进程异常：Claude Code 对 `PreToolUse` 的命令钩子默认不阻断，所以关键规则请同时用 `permissions.deny` 兜底。

## 已知边界

- `export`（导出到 Cursor / Copilot / Gemini / Kiro）尚未实现；
- 只覆盖 Claude Code 的钩子协议，其他宿主要靠导出器或各自的策略引擎；
- `run` 使用 `shell=True`，规则文件属于受信任配置，不要从不可信来源加载。
