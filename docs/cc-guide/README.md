# Claude Code 使用指南

> 本指南基于 **官方文档**（`code.claude.com/docs`，共 141 页）与 **CHANGELOG**（433 个版本、8,442 条变更）整理而成。
> 每章先讲机制，再给本仓库（`cc_plugins`）的真实用法，可直接对照落地。


## 📚 章节索引

| # | 章节 | 解决什么问题 | 何时读 |
|---|------|-------------|--------|
| 01 | [能力选型矩阵](01-能力选型矩阵.md) | 12 个扩展层各自管什么，选错就是"用错工具" | 设计扩展体系前必读 |
| 02 | [上下文经济学](02-上下文经济学.md) | 上下文窗口怎么填满的、什么会被压缩掉 | 会话变慢/变贵/丢信息时 |
| 03 | [提示词与交互技巧](03-提示词与交互技巧.md) | 怎么把意图变成可执行指令 | 每天都在用，但很少有人读完 |
| 04 | [权限与护栏](04-权限与护栏.md) | 6 种权限模式 + 不可绕过的 deny + hooks 策略层 | 配置安全边界时 |
| 05 | [多代理编排](05-多代理编排.md) | subagent / teams / workflows / 跨会话 怎么选 | 任务并行化时 |
| 06 | [插件与市场](06-插件与市场.md) | 插件目录规范、manifest 语义、发布与 eval | 写插件或装插件时 |
| 07 | [排错手册](07-排错手册.md) | 从症状到根因的诊断路径 | 出问题时先查这里 |
| 08 | [演进趋势](08-演进趋势.md) | 从 release 看 Claude Code 下一步往哪走 | 做技术选型时 |
| 09 | [Hooks 参考实现](09-hooks-参考实现.md) | 18 个可移植 hook：注入、状态、阈值、通知 | 想抄一套 hooks 时 |
| 10 | [Rules 与 Hooks 的跨工具设计](10-rules-hooks-跨工具设计.md) | 同一条约束该放哪层，换一家工具怎么映射 | 做跨工具方案时 |


## 🎯 三条阅读路径

**新人（1 天）**
`01 能力选型矩阵` → `03 提示词与交互技巧` → `07 排错手册`

**写插件（半天）**
`01 能力选型矩阵` → `06 插件与市场` → `04 权限与护栏`（hooks 章节）

**调优现有项目（1 小时）**
`02 上下文经济学` → `04 权限与护栏` → `05 多代理编排`


## 🔑 三条速查

### 1. 上下文在启动时就已经被填掉一部分

会话开始时自动进入上下文的有：`CLAUDE.md`、auto memory、MCP 工具名、**所有 skill 的 description**。
**实测**：skill 清单会超出预算好几倍，Claude Code 会**截断**排在后面的 skill，
于是它**根本不知道那些 skill 存在**。其中用户级 skill 是主战场 —— 数量最多，description 也最长。
具体数字见 [02 上下文经济学](02-上下文经济学.md#启动时就已经占掉的部分)。

### 2. `deny` 规则在所有权限模式下都生效

包括 `bypassPermissions`。这是唯一"无论怎么设置都拦得住"的一层。
本仓库 `.claude/settings.json` 的 `deny` 目前只覆盖 `sudo` / `secrets` / `.env`。
→ 详见 [04 权限与护栏](04-权限与护栏.md#deny-是唯一不可绕过的层)

### 3. 插件的 `skills` 字段指向目录，`commands` 字段指向文件

```
"skills":   ["./skills/"]              ← 目录，每个技能内含 <name>/SKILL.md
"commands": ["./commands/xxx.md"]      ← 平铺的 .md 文件
```
写错会被 `claude plugin validate` 直接判为 error 而非 warning。
→ 详见 [06 插件与市场](06-插件与市场.md#各组件字段的默认位置与语义)


## 📌 官方文档索引怎么用

官方文档站提供纯 Markdown 源码版，代码围栏完整，**比浏览器抓取可靠得多**：

```bash
# 1. 拿到全部 141 页的索引
curl -sS https://code.claude.com/docs/llms.txt

# 2. 任意一页的纯 markdown 双胞胎
curl -sS https://code.claude.com/docs/en/hooks.md
```

`.md` 后缀是关键——HTML 页面在抓取时会丢掉 JSON 代码块，而 `.md` 版保留完整原文。


## 🧭 本仓库的对应实践

| 指南章节 | 本仓库的实现 |
|---------|-------------|
| 01 能力选型 | `.claude/skills/`（23 个目录，23 个生效）+ `plugins/`（7 个插件、15 个技能）+ `.claude/agents/`（4 个） |
| 02 上下文经济学 | `CLAUDE.md`（151 行）+ 全局 `AGENTS.md` + `scripts/measure_context.py`（实测常驻成本） |
| 04 权限与护栏 | `.claude/settings.json` 的 `permissions.allow/deny` + `hooks/`（18 个脚本，当前未注册） |
| 05 多代理编排 | `.claude/agents/` 4 个本地 agent + `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` |
| 06 插件与市场 | `.claude-plugin/marketplace.json` + 7 个 `plugins/*/.claude-plugin/plugin.json` + `scripts/validate_manifests.py`（按 `$schema` 校验 manifest） |
| 07 排错手册 | `.github/scripts/` 三个校验脚本 + `claude plugin validate` + `claude --debug` + `scripts/measure_context.py`、`scripts/extract_keybindings.py`、`scripts/extract_changelog.py` |
| 09 Hooks 参考实现 | `.claude/hooks/`（18 个脚本 + `lib/` + `examples/`，当前未注册） |


## 🖥️ 本地预览与构建

```bash
# 严格构建：链接写错、锚点失效都会让构建失败（CI 用的是同一条命令）
PYTHONPATH=. uv run --with "mkdocs-material>=9.5" mkdocs build --strict --site-dir site

# 本地预览（会修正 Windows 上 .svg 的 MIME，否则 <img> 加载不出来）
uv run python scripts/serve.py
# → http://127.0.0.1:8765
```

`mkdocs.yml` 里开了 `validation.anchors: warn` 与 `unrecognized_links: warn`，
配合 `--strict`，**写错的锚点会在构建期报错**，而不是等到线上点开是 404。

但**表格结构构建期抓不到** —— 列数不一致、分隔行写错，Markdown 解析器会静默补齐：

```bash
uv run python scripts/check_tables.py docs/cc-guide
```

插图由 `scripts/gen_guide_figures.py` 生成 —— 明暗两套 SVG，共 18 个文件：

```bash
uv run python scripts/gen_guide_figures.py
```

页面在深色模式下会自动换成 `.dark.svg` 变体（`docs/javascripts/theme-figures.js`），
所以改插图后要重新生成，**两种主题都要看一遍**。


**相关**：`docs/error-playbook/` — 本项目实际踩过的坑与解法（⚠️ 该目录目前还不存在，因为 error-catcher hook 没有注册，见 [04](04-权限与护栏.md#发现-4-18-个-hook-脚本全部未注册)）
