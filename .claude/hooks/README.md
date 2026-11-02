# Hooks 参考实现

这里的脚本是**可移植的 hooks 参考库**，不是本仓库的运行时依赖。
它们演示了 Claude Code hooks 能做的几类事情：上下文注入、状态维护、
阈值检查、错误归档、通知与声音提示。

> 本仓库自己的确定性护栏在 `plugins/agent-policy/`（策略文件 + 单入口 dispatcher）。
> 两者分工：**policy 管“能不能做”，hooks 管“做的时候额外做什么”。**

## 目录

```
.claude/hooks/
├── lib/                        # 共享库（被多个脚本 source）
│   ├── common.sh               # 路径初始化、JSON 原子更新、技能计数
│   ├── reasoning-io.sh         # 推理日志读写
│   ├── reasoning-render.sh     # 进度条 / 时间线渲染
│   └── reasoning-render-mermaid.sh
├── examples/                   # 各事件的样例 stdin JSON
└── *.sh / *.py                 # 18 个 hook 脚本
```

## 事件 → 脚本

| 事件 | matcher | 脚本 | 输入字段 | 副作用 | 依赖 |
|---|---|---|---|---|---|
| SessionStart | — | `session-start.sh` | — | 读 `.info/.status.json`，输出画像提示 | jq |
| SessionStart | — | `fix-reasoning.sh` | — | 修复 `.info/reasoning/` 与 `tasks.json` 的不一致 | jq |
| UserPromptSubmit | — | `check-pdf-updates.sh` | — | 扫描 `01_articles/`，标记待处理 PDF | jq |
| UserPromptSubmit | — | `intent-detect.sh` | `.prompt` `.session_id` | **stdout 注入** `.info/info.md` | jq |
| UserPromptSubmit | — | `update-status.sh` | — | 刷新 `.info/.status.json` | jq |
| PostToolUse | `Write\|Edit` | `track-skills-change.sh` | `.tool_name` `.tool_input.file_path` | 维护 `tasks.json` 技能元数据 | jq |
| PostToolUse | `Write\|Edit` | `update-status.sh` | — | 刷新状态摘要 | jq |
| PostToolUse | `Write\|Edit` | `capture-reasoning.sh` | `.tool_input.file_path` `.tool_input.content` | 写入 reasoning 日志 | jq |
| PostToolUse | `Write\|Edit` | `check-skills-limit.sh` | `.tool_name` `.tool_input.file_path` | 超阈值时写 `archive_pending` | jq |
| PostToolUse | `TaskCreate\|TaskUpdate` | `update-status.sh` | — | 刷新状态摘要 | jq |
| PostToolUse | `TaskCreate\|TaskUpdate` | `update-reasoning-on-task.sh` | `.tool_input.subject/taskId/status` | 更新 reasoning 日志 | jq |
| PostToolUse | `TaskCreate\|TaskUpdate` | `detect-task-complete.sh` | `.tool_name` `.tool_input` | 标记技能升级待处理 | jq |
| Stop | — | `response-complete.sh` | `.hook_event_name` | 终端横幅 + 浏览器通知 | jq |
| Stop | — | `task-complete.sh` | — | 播放系统提示音 | aplay |
| （未绑定） | — | `notify.sh` | — | ntfy.sh 推送 | curl/python3 |
| （未绑定） | — | `notify-server.py` + `start-notify-server.sh` | — | 本地通知服务 | python3 |
| （未绑定） | — | `err-catcher.py` | `.tool_name` `.tool_input` `.tool_output` | 按错误模式归档 | python3 |
| （手动调用） | — | `archive-low-frequency-skills.sh` | 参数 | 归档低频技能 | jq |
| （手动调用） | — | `promote-to-proven.sh` | 参数 | k_ 技能升级为 p_ | jq |

`examples/` 下有各事件的 stdin 样例，可直接喂给脚本：

```bash
CLAUDE_PROJECT_DIR=$PWD bash .claude/hooks/intent-detect.sh \
  < .claude/hooks/examples/user-prompt-submit.json
```

## 六类可复用模式

1. **上下文注入** —— `intent-detect.sh`
   `UserPromptSubmit` 的 stdout 会进入模型上下文；适合把项目约定/路由规则注入，而不必写进 CLAUDE.md。

2. **只读观察 + 归档** —— `err-catcher.py`、`capture-reasoning.sh`
   读 `tool_input` / `tool_output`，命中模式后写文件；不改变 Claude 的行为。

3. **阈值检查 + 标记** —— `check-skills-limit.sh`
   统计配额，超阈值时写 `archive_pending`；适合“提醒人去处理”，而不是阻断。

4. **状态机维护** —— `update-status.sh`、`track-skills-change.sh`
   每次工具调用后增量更新 `tasks.json` / `.status.json`，供其他 hook 和 skill 读取。

5. **会话生命周期动作** —— `response-complete.sh`、`task-complete.sh`、`notify.sh`
   回合结束/会话结束时发通知、播声音；都是副作用型，不参与判定。

6. **外部服务集成** —— `notify-server.py`、`notify.sh`
   通过本地 HTTP 服务或 ntfy.sh 把事件推给外部。

## 共享库与状态约定

`lib/common.sh` 的 `project_dir_init()` 定义了一套可覆盖的路径：

| 变量 | 默认值 | 用途 |
|---|---|---|
| `PROJECT_DIR` | `$CLAUDE_PROJECT_DIR` 或 `pwd` | 项目根 |
| `TASKS_FILE` | `.info/tasks.json` | 任务/技能元数据 |
| `SKILLS_DIR` | `.claude/skills` | 技能目录（u_/p_/k_ 前缀） |
| `INFO_DIR` | `info` | 用户画像原料 |
| `STATUS_FILE` | `.info/.status.json` | 会话状态摘要 |
| `PROFILE_FILE` | `.info/usr.json` | 用户画像 |
| `CHANGELOG` | `.info/skills_changelog.jsonl` | 技能使用日志 |
| `ARCHIVE_DIR` | `.claude/skills/.archived` | 归档技能 |

这些文件在**使用方项目**里要自己建；本仓库没有 `.info/`、`tasks.json`，
所以这套脚本在这里只作为参考运行，不会自动生效。

## 移植清单

1. 复制 `.claude/hooks/`（含 `lib/`）到目标项目；
2. 安装依赖：`jq` 必需；`aplay`（声音）、`curl`/`python3`（通知）可选；
3. 建状态目录与文件：
   ```bash
   mkdir -p .info .claude/skills
   echo '{}' > .info/tasks.json
   echo '{}' > .info/.status.json
   ```
4. 按需在 `settings.json` 注册事件（见上表）；可直接复制
   `examples/settings-minimal.json`（4 个核心钩子）或
   `examples/settings-full.json`（全部事件）；
5. 用 `examples/*.json` 逐个冒烟：
   ```bash
   CLAUDE_PROJECT_DIR=$PWD bash .claude/hooks/<script> < .claude/hooks/examples/<event>.json
   ```
6. 按目标项目修改 `project_dir_init()` 里的路径或环境变量。

## 失效语义（很重要）

- **退出码 2 才会阻断**；`exit 1` 只是非阻塞错误。`track-skills-change.sh` /
  `check-skills-limit.sh` 里的 `exit 1` 是历史写法，不会拦住写入。
- `UserPromptSubmit` 的 **stdout 会注入上下文**；其他事件的 stdout 只作为日志。
- Stop / PostToolUse 的阻断会把 stderr 反馈给 Claude。
- 钩子应**幂等**：超时或重试时不能重复写坏状态。
- 多个同类钩子会并行执行，决策冲突遵循 deny > ask > allow。

## 已知问题

| 脚本 | 问题 | 建议 |
|---|---|---|
| `err-catcher.py` | 原 `cwd` 写死 `.../2512/cc_plugins`；依赖目标项目提供 `/err` 命令 | 已改为 `CLAUDE_PROJECT_DIR`；`/err` 需自行实现 |
| `check-skills-limit.sh` | `ARCHAVE_REASON` 拼写错误（已修）；配额超限用 `exit 1` 不会阻断 | 如需阻断改为 `exit 2` |
| `notify.sh` | ntfy topic 写死 | 改成环境变量 `NTFY_TOPIC` |
| `task-complete.sh` | 依赖系统提示音文件 | 无 `aplay` 时静默跳过 |

## 与 agent-policy 的分工

| 需求 | 用哪个 |
|---|---|
| 读 secrets / 越界写入 / 高危命令拦截 | `agent-policy` 的 pre 规则 |
| 改文档后跑校验、失败阻断 | `agent-policy` 的 post `run` 规则 |
| 注入项目约定、维护状态、发通知、播声音 | 本目录的脚本 |
| 错误模式归档 | `err-catcher.py`（需按项目改归档路径） |

不要把“通知/状态维护”塞进 policy，也不要用脚本重写 allow/deny —— 两边各做各的。
