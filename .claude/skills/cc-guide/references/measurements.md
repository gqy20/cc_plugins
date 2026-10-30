# 实测数据快照

> **测量环境**：Windows 11 · Claude Code **2.1.314** · 测量日期 **2026-10-30**
> 复现命令见每一节的末尾。数字会随环境变化，**引用前请重测**。
>
> ⚠️ **本文件只留"数字 + 复现命令"**。按来源拆分的完整表格、对账链与口径说明
> 全部以 `docs/cc-guide/02-上下文经济学.md` 为准 —— **不要在这里另抄一份表**。
> 改数字时先改 02 章，再同步这里。

## 1. 常驻上下文成本

### 启动时自动进入上下文的部分

| 内容 | 加载时机 | 本机实测 |
|------|---------|---------|
| skill 清单（145 个 skill 的 description） | 启动时 | **46,109 字符**（预算 6,000，**超 7.6 倍**） |
| `CLAUDE.md`（项目级） | 启动时 | 体积**随文件本身漂移** —— 现值见 02 章 |
| agent 的 description | 启动时 | **3,250 字符**（15 个生效 / 18 个文件） |

> **后果不是"描述变短"**，而是：**排在后面的 skill 的 `description` 被整个截掉 →
> Claude 不知道它们存在 → 永远不会被调用。**

> **按来源拆分、对账链（29,026 + 17,083 = 46,109）、token 估算口径**
> —— 见 [docs/cc-guide/02-上下文经济学.md · 启动时就已经占掉的部分](../../../../docs/cc-guide/02-上下文经济学.md#启动时就已经占掉的部分)。
> 要数字直接跑下面的命令，别引用记忆。

### 本项目贡献了多少

| 来源 | 文件数 | 实际生效 | 常驻字符数 |
|------|-------|---------|-----------|
| `.claude/skills/` | 23 | 22 | 1,616 |
| `.claude/agents/` | 4 | 3 | 75 |
| `plugins/*/skills/` | 15 | **0** | — |

> **插件 skill 为 0 不是笔误** —— 见"坑 2"。
> 注意 `.claude/skills/` 那 23 个目录里，`explore/SKILL.md` 解析失败被静默忽略，
> 能生效的是 **22** 个；启动日志的 `project: 23` 数的是**目录数**。

**复现**：

```bash
uv run --with pyyaml python scripts/measure_context.py
```

> **token 估算口径**：`非 ASCII 字符数 + ASCII 字符数 ÷ 4`，**逐文件取整后再求和**，
> 与官方 `claude plugin details` 的 Always-on 估算**有偏差，官方更保守**
> （实测本插件 436 字符 → 本公式 388 tok，官方报 ~232 tok）。
> **量级可用，字符数才是精确值。**

## 2. 已确认的官方文档过时之处

> 完整对照表与推导见 [docs/cc-guide/07-排错手册.md · 坑 6](../../../../docs/cc-guide/07-排错手册.md#坑-6-官方文档自相矛盾-以二进制为准)。
> 这里只留结论。

### 过时 1：`Enter` 到底排不排队

**结论**：排队用 **`Ctrl+X Enter`**（`chat:queueSubmit`）；
`Enter` = `chat:submit`（立即发送，会打断当前轮）。
官方 interactive-mode 页那句 "press Enter … queues the message" 是 **v2.1.247 之前的旧行为**。

**复现**：

```bash
uv run python scripts/extract_keybindings.py --context Chat
```

### 过时 2：`Write(.env*)` deny 规则

**结论**：只有 `Edit(path)` 规则会被文件权限检查匹配，而 `Edit` 规则覆盖所有文件编辑类工具 ——
写 `Edit(.env*)`，不要写 `Write(.env*)`。Claude Code 启动时会就此打印告警。

**复现**：看启动日志里的 `Permission deny rule` 那一行。

## 3. 出厂默认键位（2.1.314，Chat 上下文）

| 键 | 动作 |
|----|------|
| `Enter` | `chat:submit` —— 提交（立即发送） |
| `Ctrl+X Enter` | `chat:queueSubmit` —— 排队，**绝不打断**（需 v2.1.247+） |
| `Ctrl+Enter` / `Ctrl+X Ctrl+S` | `chat:sendNow` —— 立刻发出已排队消息（需 v2.1.275+） |
| `Ctrl+J` | `chat:newline` —— 换行不提交 |
| `Esc` | `chat:cancel` —— 打断，不提交草稿，已排队消息立刻发出 |
| `Ctrl+L` / `Cmd+K` | `chat:clearInput` / `chat:clearScreen` |
| `Ctrl+X Ctrl+K` | `chat:killAgents` —— 停掉所有后台 subagent |
| `Ctrl+G` / `Ctrl+X Ctrl+E` | `chat:externalEditor` |
| `Ctrl+S` | `chat:stash` |
| `Shift+Tab` | `chat:cycleMode` —— 循环权限模式 |
| `Up` / `Down` | `history:previous` / `history:next`（`Up` 在首行时取回排队消息） |
| `Ctrl+B` / `Ctrl+X Ctrl+B` | `task:background` |

**和弦规则**：`Ctrl+X` 前缀下，`Chat` 上下文占用 6 个和弦 ——
`ctrl+x ctrl+k`、`ctrl+x ctrl+e`、`ctrl+x enter`、`ctrl+x ctrl+a`、`ctrl+x ctrl+s`、`ctrl+x tab`。
两键间隔**不超过 3 秒**，超时取消并提示。

**保留键（不可改）**：`Ctrl+C`、`Ctrl+D`、`Ctrl+M`（永远当 Enter）、
`Ctrl+I`（永远当 Tab）、`Ctrl+[`（永远当 Esc）、`Ctrl+H`、Caps Lock。

## 4. 插件机制实测

| 现象 | 实测结论 |
|------|---------|
| 插件加载方式 | **装到缓存再加载**，不是就地读仓库源码 |
| `installed_plugins.json` 指向 | `~/.claude/plugins/cache/<marketplace>/<plugin>/<hash>/` |
| 改了仓库源码 | 本机**不会**自动更新 —— 缓存跟的是**远端已发布版本**，先 push 再 `claude plugin update --all` |
| 调试替代方案 | `claude --plugin-dir ./plugins/<name>`（就地加载，不经缓存） |
| 本仓库旗舰插件 | `Loaded 0 skills from plugin evolutionary-biology-expert`（缓存还停在迁移前的远端版本），但 agent 正常加载 |

## 5. 平台限制

| 事实 | 影响 |
|------|------|
| 沙箱只存在于 macOS / Linux / WSL2 | **原生 Windows 上 Claude Code 无沙箱**，命令不受限 |
| 权限模式 6 种 | `default`（UI 显示 Manual）/ `acceptEdits` / `plan` / `auto` / `dontAsk` / `bypassPermissions` |
| **v2.1.284 起 `auto` 是默认权限模式** | 本仓库三档模型全指向 `glm-4.7` 网关，auto 分类器不可靠 → 建议显式设 `"permissions.defaultMode": "manual"` |

## 6. 最近 release 说了什么

Claude Code 把最近 13 个版本的 release notes 打包进了可执行文件：

```bash
uv run python scripts/extract_changelog.py --since 2.1.305
uv run python scripts/extract_changelog.py --grep queue
```

完整趋势分析见 `docs/cc-guide/08-演进趋势.md`（基于官方仓库 433 个版本、8,442 条变更）。
