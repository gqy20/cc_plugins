# 09 · Hooks 参考实现

> **本章要回答的问题**：hooks 除了“拦截工具”，还能做什么？
>
> 本仓库的 `.claude/hooks/` 保留了 18 个脚本作为**可移植的参考库**，
> 覆盖六类模式：上下文注入、只读归档、阈值检查、状态维护、生命周期通知、外部服务。
> 它们不在本仓库注册运行，但可以直接抄到目标项目。

## 🧭 先分清：判定 vs 副作用

| 需求 | 首选机制 | 去哪看 |
|------|---------|--------|
| 绝不允许（读 secrets、越界写入） | `permissions.deny` / `PreToolUse` deny | [04 权限与护栏](04-权限与护栏.md) |
| 动作后必须校验 | `PostToolUse` 的 `run` 规则 | `plugins/agent-policy/` |
| 注入约定、维护状态、发通知 | **hooks 参考库** | 本章 |
| 多步流程、按需加载 | Skill | [01 能力选型矩阵](01-能力选型矩阵.md) |

一句话：**policy 管“能不能做”，hooks 管“做的时候额外做什么”。**

## 📡 事件与输入契约

| 事件 | 触发时机 | stdin 关键字段 | stdout 用途 |
|------|---------|----------------|-------------|
| `SessionStart` | 会话开始/恢复 | `source`、`session_id` | 上下文注入 |
| `UserPromptSubmit` | 用户提交、模型处理前 | `prompt`、`session_id` | **上下文注入** |
| `PostToolUse` | 工具调用成功后 | `tool_name`、`tool_input`、`tool_output` | 日志 / `exit 2` 反馈 |
| `Stop` | 回合结束 | `session_id` | 日志 / `exit 2` 阻止停止 |

> 完整事件列表（30+ 个）见 [04 权限与护栏](04-权限与护栏.md)。
> 参考库只用最常见的四个。

### 退出码

| 退出码 | 行为 |
|--------|------|
| `0` | 成功；stdout 按事件规则处理 |
| `2` | **阻断**；stderr 作为原因反馈给 Claude |
| 其他 | 非阻断错误；动作继续（除非 `onFailure: "block"`） |

**这是参考库最容易踩的坑**：很多脚本写 `exit 1` 表示“超限”，但 `exit 1` 不会拦住任何东西。

## 🗂️ 18 个脚本的分布

| 事件 | matcher | 脚本 | 做什么 |
|------|---------|------|--------|
| SessionStart | — | `session-start.sh` | 读 `.status.json`，打印画像状态 |
| SessionStart | — | `fix-reasoning.sh` | 修复 reasoning 文件与 `tasks.json` 的不一致 |
| UserPromptSubmit | — | `check-pdf-updates.sh` | 扫描 `01_articles/`，标记待处理 PDF |
| UserPromptSubmit | — | `intent-detect.sh` | 注入 `.info/info.md` 路由规则 |
| UserPromptSubmit | — | `update-status.sh` | 刷新状态摘要 |
| PostToolUse | `Write / Edit` | `track-skills-change.sh` | 维护技能元数据 |
| PostToolUse | `Write / Edit` | `update-status.sh` | 刷新状态摘要 |
| PostToolUse | `Write / Edit` | `capture-reasoning.sh` | 从 `results/<id>/` 下的 `.reasoning.md` 提取推理日志 |
| PostToolUse | `Write / Edit` | `check-skills-limit.sh` | 超阈值时写 `archive_pending` |
| PostToolUse | `TaskCreate / TaskUpdate` | `update-status.sh` | 刷新状态摘要 |
| PostToolUse | `TaskCreate / TaskUpdate` | `update-reasoning-on-task.sh` | 任务状态变化时更新推理日志 |
| PostToolUse | `TaskCreate / TaskUpdate` | `detect-task-complete.sh` | 标记技能升级待处理 |
| Stop | — | `response-complete.sh` | 终端横幅 + 浏览器通知 |
| Stop | — | `task-complete.sh` | 播放系统提示音 |
| 未绑定 | — | `notify.sh` / `notify-server.py` / `start-notify-server.sh` | ntfy / 本地通知服务 |
| 未绑定 | — | `err-catcher.py` | 按错误模式归档 |
| 手动 | — | `archive-low-frequency-skills.sh` / `promote-to-proven.sh` | 技能归档与升级 |

## 🧩 六类可复用模式

### 1. 上下文注入 —— `intent-detect.sh`

`UserPromptSubmit` 的 stdout 会进入上下文，所以“注入规则”不需要改 CLAUDE.md：

```bash
INFO_MD="$CLAUDE_PROJECT_DIR/.info/info.md"
if [ -f "$INFO_MD" ]; then
    cat "$INFO_MD"
fi
```

适合放：路由规则、当前任务约定、按项目切换的检查清单。规则文件不存在时静默跳过，避免每次输入都产生噪音。

### 2. 只读归档 —— `err-catcher.py`、`capture-reasoning.sh`

`err-catcher.py` 用模式表把 `tool_output` 归类，再交给 `/err` 命令归档：

```python
ERROR_PATTERNS = [
    (r"FAILED|AssertionError", "tool", "major", "TEST-FAIL"),
    (r"ImportError|ModuleNotFoundError", "tool", "blocker", "IMPORT"),
    (r"Connection.*refused|ECONNREFUSED", "network", "blocker", "NET-REFUSED"),
]
```

`capture-reasoning.sh` 只处理约定路径（`results/<id>/.reasoning.md`），
把推理内容追加到日志，并渲染 Mermaid 流程图与步骤表。

这类脚本的共同点：**只观察、只记录，不改变 Claude 的行为**。
归档目标（`/err`、`.info/.reasoning*`）由使用方项目提供。

### 3. 阈值检查 —— `check-skills-limit.sh`

```bash
MAX_USER_SKILLS=5
MAX_PROVEN_SKILLS=10
MAX_TASK_SKILLS=20
# 超限时只做标记，交给人工处理
atomic_json_update "$TASKS_FILE" \
    --arg reason "$ARCHIVE_REASON" \
    '.archive_reason = $reason'
```

**注意**：原脚本在超限分支用 `exit 1`，这不会阻断写入。
如果目标是“不许再写”，要改成 `exit 2`；如果只是提醒，就保持 0。

### 4. 状态机维护 —— `update-status.sh`、`track-skills-change.sh`

状态文件的读取要容忍空对象，否则 `set -e` 会让钩子直接退出：

```bash
jq -r '{
  total: ((.tasks // {}) | length),
  active: ([((.tasks // {}) | to_entries[]) | select(.value.status == "active")] | length)
}'
```

多字段回传用**单元分隔符**（`\x1f`）而不是 tab：
tab 是 IFS 空白符，前导空字段会被 `read` 吞掉，导致整行列错位。

### 5. 生命周期通知 —— `response-complete.sh`、`task-complete.sh`、`notify.sh`

```bash
for cmd in python3 curl; do
    command -v "$cmd" >/dev/null 2>&1 || exit 0
done
```

通知、声音、横幅都属于副作用：**依赖缺失就静默跳过**，不要因为没装 `aplay` 或没网就让会话报错。

### 6. 外部服务 —— `notify-server.py`

本地 HTTP 服务接收 hook 事件，再推给浏览器或 ntfy。
启动脚本是 `start-notify-server.sh`。这类服务不要放进关键路径：
钩子超时只会被取消，不会自动阻断动作（除非显式设置）。

## 🗃️ 状态目录与共享库

`lib/common.sh` 的 `project_dir_init()` 定义了一套默认路径：

| 变量 | 默认值 | 用途 |
|------|--------|------|
| `PROJECT_DIR` | `$CLAUDE_PROJECT_DIR` 或 `pwd` | 项目根 |
| `TASKS_FILE` | `.info/tasks.json` | 任务/技能元数据 |
| `SKILLS_DIR` | `.claude/skills` | 技能目录（u_/p_/k_ 前缀） |
| `INFO_DIR` | `info` | 用户画像原料 |
| `STATUS_FILE` | `.info/.status.json` | 会话状态摘要 |
| `PROFILE_FILE` | `.info/usr.json` | 用户画像 |
| `CHANGELOG` | `.info/skills_changelog.jsonl` | 技能使用日志 |
| `ARCHIVE_DIR` | `.claude/skills/.archived` | 归档技能 |

> ⚠️ **两处 `info` 约定不一致**：`common.sh` 的 `INFO_DIR` 是 `info/`（画像原料），
> 而 `intent-detect.sh` 读的是 `.info/info.md`（路由规则）。
> 移植时统一成自己的目录布局，别照抄两个名字。

这些目录属于**使用方项目**。本仓库没有 `.info/`、`tasks.json`，
所以参考库在这里只看不跑。

## 🔁 移植清单

```bash
# 1. 复制脚本与共享库
cp -r .claude/hooks <target>/.claude/hooks

# 2. 安装依赖（jq 必需；aplay / curl / python3 按需）
command -v jq || sudo apt install jq

# 3. 建状态文件
mkdir -p .info .claude/skills
printf '{}' > .info/tasks.json
printf '{}' > .info/.status.json

# 4. 注册：直接用 examples/settings-minimal.json 或 settings-full.json

# 5. 用样例冒烟
CLAUDE_PROJECT_DIR=$PWD bash .claude/hooks/intent-detect.sh \
  < .claude/hooks/examples/user-prompt-submit.json
```

参考库自带 `examples/`：SessionStart、UserPromptSubmit、
PostToolUse（Write / Task / Bash 错误）、Stop 各一份 stdin 样例。
可复制的注册片段在同目录的 `settings-minimal.json` 与 `settings-full.json`
（[GitHub 直达](https://github.com/gqy20/cc_plugins/tree/main/.claude/hooks/examples)）。

## 📋 可复制的 settings.json 片段

> 前提：`.claude/hooks/` 已复制到项目根，`jq` 已安装。
> 所有命令都用 `$CLAUDE_PROJECT_DIR` 定位；Windows 原生环境请用 WSL / Git Bash。

### SessionStart

```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [
        { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/session-start.sh", "timeout": 10 },
        { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/fix-reasoning.sh", "timeout": 30 }
      ] }
    ]
  }
}
```

### UserPromptSubmit

```json
{
  "hooks": {
    "UserPromptSubmit": [
      { "hooks": [
        { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/check-pdf-updates.sh", "timeout": 5 },
        { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/intent-detect.sh", "timeout": 10 },
        { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/update-status.sh", "timeout": 5 }
      ] }
    ]
  }
}
```

### PostToolUse：文件写入

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/track-skills-change.sh", "timeout": 5 },
          { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/update-status.sh", "timeout": 5 },
          { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/capture-reasoning.sh", "timeout": 3 },
          { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/check-skills-limit.sh", "timeout": 5 }
        ]
      }
    ]
  }
}
```

### PostToolUse：任务状态

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "TaskCreate|TaskUpdate",
        "hooks": [
          { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/update-status.sh", "timeout": 5 },
          { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/update-reasoning-on-task.sh", "timeout": 10 },
          { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/detect-task-complete.sh", "timeout": 5 }
        ]
      }
    ]
  }
}
```

### PostToolUse：Bash 错误归档

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/err-catcher.py", "timeout": 10 }
        ]
      }
    ]
  }
}
```

### Stop

```json
{
  "hooks": {
    "Stop": [
      { "hooks": [
        { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/response-complete.sh", "timeout": 3 },
        { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/task-complete.sh", "timeout": 5 }
      ] }
    ]
  }
}
```

### 通知（可选）

`notify.sh` 没有默认绑定。想用就把它挂到 `Stop`：

```json
{
  "hooks": {
    "Stop": [
      { "hooks": [
        { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/notify.sh", "timeout": 10 }
      ] }
    ]
  }
}
```

### 注册时的六个坑

| 坑 | 说明 |
|---|---|
| matcher 是**正则**，不是 glob | 多个工具用竖线分隔（如 Write 与 Edit）；`Write*` 不匹配任何东西 |
| 用相对路径 | hook 的 cwd 不保证是项目根，统一用 `$CLAUDE_PROJECT_DIR` |
| 重复注册同一脚本 | 多个钩子**并行**执行，副作用会翻倍 |
| 把耗时检查放 `PreToolUse` | 每次工具调用都要等；重检查放 `PostToolUse` / `Stop` |
| 以为超时会阻断 | `PreToolUse` 超时默认**放行**，要阻断需 `onFailure: "block"` |
| 原生 Windows 直接跑 bash | 用 WSL 或 Git Bash；路径分隔符也要注意 |

### 验证注册是否生效

```bash
# 1. 单脚本冒烟（不依赖 Claude Code）
CLAUDE_PROJECT_DIR=$PWD bash .claude/hooks/intent-detect.sh \
  < .claude/hooks/examples/user-prompt-submit.json

# 2. 启动日志里确认钩子被加载
claude --debug
```

## ⚠️ 失效语义与坑

| 现象 | 原因 | 处理 |
|------|------|------|
| 超限了但没拦住 | 用了 `exit 1` | 改成 `exit 2` |
| 钩子超时但动作继续 | `PreToolUse` 超时默认不阻断 | 设 `onFailure: "block"` |
| 空状态文件把钩子打挂 | jq 对 `null` 取 `to_entries` 报错 | 统一加 `// {}` |
| 多字段读串列 | tab 被 IFS 当空白吞掉 | 用 `\x1f` 分隔 |
| 输出没有进上下文 | 只有部分事件的 stdout 注入 | 确认事件类型 |
| 脚本能改任何文件 | hooks 以完整权限运行，不走沙箱 | 只依赖可信脚本 |

另外两条通用规则：

1. **幂等**：超时或重试时可能重复执行，写状态要用 upsert，不要 append 两次；
2. **并行**：多个同类钩子同时跑，决策按 `deny > defer > ask > allow` 合并。

## 🆚 与 agent-policy 的分工

| 场景 | 用哪个 |
|------|--------|
| 读 secrets、越界写入、高危命令 | `agent-policy` 的 pre 规则 |
| 改文档后跑校验，失败阻断 | `agent-policy` 的 post `run` 规则 |
| 注入约定、维护状态、发通知 | 本章的 hooks |
| 错误模式归档 | `err-catcher.py`（按项目改归档目标） |

不要用脚本重写 allow/deny，也不要把通知/状态维护塞进 policy —— 两边各做各的。

## 📖 参考索引

完整的事件表、每个脚本的输入/副作用/依赖、已知问题，见仓库里的
`.claude/hooks/README.md`。新增 hook 时建议按这个顺序做：

1. 选事件 → 2. 用 `examples/` 的 JSON 跑通 → 3. 写清副作用与失败策略 → 4. 注册。

## 🔗 相关

- [04 权限与护栏](04-权限与护栏.md) —— hooks 的完整事件与退出码契约
- [01 能力选型矩阵](01-能力选型矩阵.md) —— 判定与副作用的分层判据
- [06 插件与市场](06-插件与市场.md) —— 把 hook 打包进插件分发
