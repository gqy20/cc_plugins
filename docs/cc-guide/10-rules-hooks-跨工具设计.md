# 10 · Rules 与 Hooks 的跨工具设计

> **本章要回答的问题**：同一条约束，应该写成规则、策略还是钩子？
> 换到 Cursor / Copilot / Codex / Gemini / Kiro，又该怎么映射？

## 🧭 四层模型

| 层 | 管什么 | 典型载体 | 保证强度 |
|---|---|---|---|
| **指令层** | 告诉模型“应该怎么做” | CLAUDE.md、AGENTS.md、`.claude/rules/`、`.mdc` | 概率性 |
| **准入层** | 工具调用前判定能不能做 | `permissions`、Gemini policy、Codex approval + sandbox | 确定性 |
| **事件层** | 生命周期事件触发代码 | hooks、guardrails、interrupt | 确定性 |
| **验证层** | 事后兜底 | CI、pre-commit | 确定性但滞后 |

**判据：违反后果决定层，而不是工具偏好。**

- 后果是事故（泄露、越界、不可逆）→ 准入 + 事件；
- 后果只是“不好看/不一致” → 指令层；
- 后果是“发布后才发现” → 验证层。

## 🌍 横向对比（以官方文档为准）

| 系统 | 软规则 | 路径作用域 | 声明式准入 | 生命周期钩子 | 强制阻断 |
|---|---|---|---|---|---|
| **Claude Code** | CLAUDE.md | `.claude/rules` + `paths` | `permissions` deny / allow / ask | Pre/PostToolUse、SessionStart、Stop 等 | ✅ |
| **Cursor** | AGENTS.md / `.cursor/rules`（`.mdc`） | `globs` | 规则文档未提供 | 规则文档未提及 | ❌ |
| **GitHub Copilot** | `copilot-instructions.md` | `.instructions.md` + `applyTo` | 未提供 | 未提供 | ❌ |
| **OpenAI Codex** | AGENTS.md 层级 + override | 目录级 AGENTS.md | `config.toml` 的 approvals + sandbox | 另有 hooks 文档 | ✅（沙箱/审批） |
| **Gemini CLI** | GEMINI.md | — | **policy engine**（TOML，allow / deny / ask_user，分层优先级） | hooks | ✅ |
| **Kiro** | steering rules / specs | 文件 matcher | confirm | PostFileSave、Pre/PostToolUse、Stop | ✅（PreToolUse） |
| **Cline** | `.clinerules` | `paths` frontmatter | 未提供 | SDK plugins | ❌ |
| **OpenAI Agents SDK** | instructions | — | guardrails（input / output / tool + tripwire） | lifecycle hooks | ✅（tripwire） |
| **LangGraph** | prompt / state | — | 人工审批 + 条件边 | `interrupt()` + checkpointer | ✅（人工） |

> 表中“未提供 / 未提及”是按各自官方文档核对的结果，不代表产品绝对没有。
> 跨工具选型时，**先假设对方只有软规则**，再逐项确认。

## 🧩 三条规律

### 1. 软规则正在收敛到 `AGENTS.md`

Codex、Copilot、Cursor、Cline 都读 `AGENTS.md`。跨工具项目把“怎么做”写进
`AGENTS.md`，把“必须拦住”写进各宿主的确定性层，是最省维护的拆法。

### 2. policy 是钩子的声明式特化

Gemini 的 policy engine 和 Claude 的 `permissions` 本质是同一件事：
**只做 allow / deny / ask 的钩子**，但用配置而不是脚本表达，带分层优先级。

- 能用声明式策略表达的 → 不要写脚本；
- 需要任意逻辑、改写入参、注入上下文 → 才用钩子。

### 3. guardrails / interrupts 是“带状态的钩子”

OpenAI Agents SDK 的 tripwire 是“命中即中止”；LangGraph 的 `interrupt()`
是“暂停 + checkpoint + 人工恢复”。代价是状态与幂等：
LangGraph 恢复时节点会**从头重跑**，`interrupt()` 之前的副作用必须幂等。

## 🗺️ 单一策略源 → 多宿主映射

| 概念 | Claude Code | Cursor | Copilot | Gemini CLI | Kiro |
|---|---|---|---|---|---|
| 常驻规则 | CLAUDE.md | AGENTS.md / `.mdc` | `copilot-instructions.md` | GEMINI.md | steering |
| 路径规则 | `.claude/rules` + `paths` | `.mdc` 的 `globs` | `applyTo` | — | matcher |
| 拒绝 | `permissions.deny` / PreToolUse | 无，降级为规则 | 无，降级为规则 | policy `deny` | confirm |
| 询问 | `ask` / PermissionRequest | 无 | 无 | `ask_user` | confirm |
| 动作后 | PostToolUse / Stop | 无 | 无 | hooks | hooks |
| 环境边界 | sandbox | 靠 CI | 靠 CI | sandbox | — |
| 事后 | CI | CI | CI | CI | CI |

**能力不足的宿主必须显式降级**——不要在 Cursor 项目里承诺“这条规则一定会被拦”。

## ⚠️ 失效语义对照

| 场景 | Claude Code | Gemini CLI | Cline | Codex |
|---|---|---|---|---|
| 钩子超时 | command 钩子超时**默认不阻断** `PreToolUse` | — | — | — |
| 非零退出 | `2` 阻断；其他退出码非阻断 | — | — | — |
| 配置解析失败 | 规则 YAML 失败会**静默忽略** | — | 规则 **fail-open** | AGENTS.md 超上限被截断 |
| 无人值守的 ask | 走权限模式 | `ask_user` 等同 deny | — | approval 策略决定 |
| 上下文预算 | skill 清单会被截断 | — | — | 指令文件有大小上限 |

> “—” 表示本次没有逐项核对，不写猜测。真正迁移前，用样例输入实测一遍。

本章的两条核心契约在真实会话中验证过：`PreToolUse` 返回 `deny` 会让模型放弃调用并复述原因；
`PostToolUse` 的 `command` 钩子按预期执行。验证方式见 [09 章](09-hooks-参考实现.md#验证注册是否生效)。

## ✅ 选型决策表

| 约束类型 | 放哪层 | 例子 |
|---|---|---|
| 不可逆 / 安全 | 准入 + 事件 | 读 secrets、写工作区外、删库 |
| 需要人判断 | 准入（ask） | 生产部署、强推、批量删除 |
| 每次必须执行 | 事件 / 验证 | 格式化、校验、测试 |
| 只在某类文件成立 | 指令（路径规则） | API 错误格式、迁移脚本规范 |
| 多步流程 | Skill | 发版、插件发布 |
| 口味与偏好 | 指令 / 记忆 | 命名、注释密度 |

## 🧪 本仓库怎么落地

- **判定**：`plugins/agent-policy/` 的 pre 规则（deny / ask）；
- **动作后**：agent-policy 的 post `run` 规则；更复杂的副作用走 `.claude/hooks/` 参考库；
- **硬规则治理**：`policy.py check --strict` 要求每条 deny/ask 都有测试夹具；
- **跨工具**：先写 `AGENTS.md` 承载软规则，再按上表映射确定性层。

一条经验：**先写规则，再问“违反后果是什么”**。后果是事故，就下沉到准入或事件层；
只是风格问题，就留在指令层，别为它增加钩子延迟。

## 📖 来源

- [Claude Code · memory / rules](https://code.claude.com/docs/en/memory)
- [Claude Code · hooks](https://code.claude.com/docs/en/hooks)
- [Cursor · Rules](https://cursor.com/docs/context/rules)
- [GitHub Copilot · custom instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)
- [OpenAI Codex · AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Gemini CLI · policy engine](https://geminicli.com/docs/reference/policy-engine/)
- [Kiro · Agent hooks](https://kiro.dev/docs/hooks/)
- [Cline · Rules](https://docs.cline.bot/features/customization/cline-rules)
- [OpenAI Agents SDK · Guardrails](https://openai.github.io/openai-agents-python/guardrails/)
- [LangGraph · Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)

## 🔗 相关

- [09 Hooks 参考实现](09-hooks-参考实现.md) —— 具体怎么写、怎么移植
- [04 权限与护栏](04-权限与护栏.md) —— Claude Code 的准入与事件契约
- [01 能力选型矩阵](01-能力选型矩阵.md) —— 扩展层总览
- [路线图](../ROADMAP.md) —— 这一章对应的 P0
