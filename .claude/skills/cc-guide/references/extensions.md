# 扩展层选型 + manifest 规范速查

> 完整版见 `docs/cc-guide/01-能力选型矩阵.md` 与 `docs/cc-guide/06-插件与市场.md`。

## 选型矩阵：先确定"要不要它生效"

| 层 | 生效方式 | 确定性 | 该用它做什么 |
|----|---------|--------|-------------|
| **CLAUDE.md** | 每次会话注入 | 建议性 | 项目约定、命令、结构 |
| **AGENTS.md** | 同上（可 `import`） | 建议性 | 跨项目复用约定 |
| **`.claude/rules/`** | 按 `paths:` 命中 | 建议性 | 只在某类文件生效的约定 |
| **Auto memory** | 自动写入 | 建议性 | Claude 自己记的偏好 |
| **Output style** | 整个会话 | 建议性 | 语气/长度/格式 |
| **Skill** | 匹配/调用时加载正文 | 建议性 | 一类任务的指令 |
| **Subagent** | 独立上下文调用 | 建议性 | 有独立指令/模型/工具的助手 |
| **Agent Teams** | 多 agent 并行 | 建议性 | 并行子任务 |
| **Dynamic workflow** | 脚本编排 | 建议性 | 确定性多 agent 流水线 |
| **MCP** | 常驻工具 | 工具本身是确定的 | 接入外部系统 |
| **Hook** | Claude Code 自己执行 | ✅ **确定** | 每次都必须发生的事 |
| **Permission** | Claude Code 自己执行 | ✅ **确定** | 不允许发生的事 |
| **Sandbox** | 内核/容器级 | ✅ **确定** | 兜底隔离 |

> **核心判据**：模型可能会不遵守"建议性"的指令。
> **"绝不允许"只有三种写法**：permission 的 `deny`、hook、沙箱。

### 官方给的对照表

| 你想要 | 用什么 |
|--------|-------|
| 每次回答都某种语气/长度/格式 | **output style** |
| Claude 知道项目约定、命令、结构 | **CLAUDE.md** |
| 某一类任务的指令 | **skill** |
| **每次都必须发生**（每次编辑后格式化、拦截某命令） | **hook** |
| 一个有独立指令/模型/工具的助手 | **subagent** |

## 权限规则的三类与评估顺序

| 类别 | 例子 | 语义 |
|------|------|------|
| `allow` | `"Bash(npm run test:*)"` | 直接允许，不弹窗 |
| `ask` | `"Bash(git push:*)"` | 每次确认 |
| `deny` | `"Edit(.env*)"` | **禁止**，且在**所有**模式下都生效 |

**评估顺序固定为 deny → ask → allow，与规则的具体程度无关。**

> ⚠️ **裸工具名 allow 是"移除工具"不是"免批准"**：
> `"allow": ["Bash"]` 会让 Bash 整个从上下文里消失。
> ⚠️ **`Write(...)` 不被文件权限检查匹配**，只有 `Edit(...)` 会被匹配。
> ⚠️ **受保护路径永远不自动批准**，allow 求值在安全检查之后。

## 插件目录规范

```
plugins/<plugin-name>/
├── .claude-plugin/
│   └── plugin.json       # 必需，扁平结构
├── README.md             # 必需
├── agents/<name>.md      # 平铺
├── skills/<name>/SKILL.md # 目录！每个技能一个目录
├── commands/<name>.md    # 平铺
├── templates/
└── tools/.mcp.json
```

### manifest 字段的关键差异

```json
{
  "name": "my-plugin",
  "version": "0.1.0",
  "description": "…",
  "author": { "name": "…" },
  "agents":   ["./agents/analyst.md"],
  "skills":   ["./skills/"],              ← 目录，内含 <name>/SKILL.md
  "commands": ["./commands/consult.md"]   ← 平铺的 .md 文件
}
```

| 字段 | 合并语义 |
|------|---------|
| `commands` / `agents` / `outputStyles` / `workflows` / `experimental.themes` / `experimental.monitors` | **替换**默认值 |
| `skills` | **追加**到默认值 |
| `hooks` / `mcpServers` / `lspServers` | **合并** |

**所有路径必须以 `./` 开头。**
写错 `skills` 的形状（指到单个 `.md`）会被 `claude plugin validate` 判为 **error 而非 warning**。

### marketplace.json

```json
{
  "owner": { "name": "…" },
  "metadata": { "description": "…", "version": "0.1.4" },
  "plugins": [
    {
      "name": "my-plugin",
      "source": "./plugins/my-plugin",
      "description": "…",
      "category": "utility",
      "version": "0.1.0",
      "strict": true
    }
  ]
}
```

`category` 和 `source` 定义在 **marketplace.json**，`plugin.json` 里**不能有**这两个字段。
`strict` 默认 `true`；**未知的顶层字段被静默忽略，不报错**。

## 校验命令

```bash
claude plugin validate .claude-plugin/marketplace.json --strict
claude plugin validate plugins/<name> --strict
claude plugin details <name>          # 看这个插件常驻花多少
claude plugin update --all            # 改了仓库源码后重装
claude plugin marketplace update <m>  # 市场副本过期
```

退出码：`0` 通过（含 warning）/ `1` 失败 / `2` 意外错误。

## skill 规范

```
skills/<name>/SKILL.md
```

frontmatter 最少要有：

```yaml
---
name: <kebab-case，与目录名一致>
description: <一句话说清"什么时候该用它"，含触发场景>
---
```

**两条铁律**（见 `references/diagnostics.md`）：
多行文本用 `|` 块标量；含 `: ` 的整句加引号。
