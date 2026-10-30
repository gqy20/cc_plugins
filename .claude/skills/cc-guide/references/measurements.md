# 实测数据快照

> **测量环境**：Windows 11 · Claude Code **2.1.314** · 测量日期 **2026-10-30**
> 复现命令见每一节的末尾。数字会随环境变化，**引用前请重测**。

## 1. 常驻上下文成本

### 启动时自动进入上下文的部分

| 内容 | 加载时机 | 本机实测 |
|------|---------|---------|
| skill 清单（145 个 skill 的 description） | 启动时 | **46,109 字符**（预算 6,000，**超 7.6 倍**） |
| CLAUDE.md（项目级，416 行） | 启动时 | **10,748 字符** |
| agent 的 description | 启动时 | **3,250 字符**（15 个生效 / 18 个文件） |

> **后果不是"描述变短"**，而是：**排在后面的 skill 的 `description` 被整个截掉 →
> Claude 不知道它们存在 → 永远不会被调用。**

### 按来源拆分

| 来源 | 数量 | description 字符数 | 估算 tokens |
|------|------|------------------|------------|
| 用户级 `~/.claude/skills/` | 101 | **26,269** | ≈12,088 |
| 项目级 `.claude/skills/` | 22/23 | 1,616 | ≈978 |
| 插件 skill（已启用） | 9 | 1,141 | ≈360 |
| 已安装但本项目未启用 | — | 11,960 | ≈2,974 |

> **token 估算口径**：`CJK 字数 + ASCII 字符数 ÷ 4`，与官方
> `claude plugin details` 的 Always-on 估算**有偏差，官方更保守**
> （实测本插件 436 字符 → 本公式 388 tok，官方报 ~232 tok）。
> **量级可用，字符数才是精确值。**

### 本项目贡献了多少

| 来源 | 文件数 | 实际生效 | 常驻字符数 |
|------|-------|---------|-----------|
| `.claude/skills/` | 23 | 22 | 1,616 |
| `.claude/agents/` | 4 | 3 | 75 |
| `plugins/*/skills/` | 15 | **0** | — |

> **插件 skill 为 0 不是笔误** —— 见"坑 2"。

**复现**：

```bash
uv run --with pyyaml python scripts/measure_context.py
```

## 2. 已确认的官方文档过时之处

### 过时 1：`Enter` 到底排不排队

| 来源 | 说法 | 权威度 |
|------|------|-------|
| [interactive-mode](https://code.claude.com/docs/en/interactive-mode) §Queue messages | "press `Enter` … queues the message" | ❌ **v2.1.247 之前的旧行为** |
| [keybindings](https://code.claude.com/docs/en/keybindings) §Chat actions | `chat:submit`=`Enter`=Submit message；`chat:queueSubmit`=`Ctrl+X Enter`=queues it and **never interrupts the turn**（需 v2.1.247+） | ✅ 权威 |
| 二进制（2.1.314） | `enter:"chat:submit"`、`"ctrl+x enter":"chat:queueSubmit"` | ✅ 事实 |

**结论**：排队用 **`Ctrl+X Enter`**；`Enter` = `chat:submit`（立即发送，会打断当前轮）。

**复现**：

```bash
uv run python scripts/extract_keybindings.py --context Chat
```

### 过时 2：`Write(.env*)` deny 规则

Claude Code 启动时会打印告警：

```text
Permission deny rule (.claude\settings.json): Write(.env*) is not matched by
file permission checks — only Edit(path) rules are.
Use Edit(.env*) instead (Edit rules cover all file-editing tools).
```

只有 `Edit(path)` 规则会被文件权限检查匹配，而 `Edit` 规则覆盖所有文件编辑类工具。

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
