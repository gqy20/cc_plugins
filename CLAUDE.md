# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Claude Code 插件集合，共 7 个插件：4 个研究专家插件（进化生物学、杂交物种形成、作物育种、进化生态学）+ 3 个实用工具插件（Slidev 生成、AntV 信息图表、agent-policy 策略/钩子）。研究插件依赖 article-mcp + sequentialthinking。

## 验证与测试

```bash
claude plugin validate .claude-plugin/marketplace.json

python3 .github/scripts/check_references.py           # 文件引用
python3 .github/scripts/check_mcp_dependencies.py     # MCP 依赖
python3 .github/scripts/validate_content.py <plugin>  # 内容质量

uv run --with pyyaml python scripts/validate_skills.py        # skill/agent frontmatter
uv run --with pyyaml python scripts/measure_context.py        # 常驻上下文成本
uv run --with jsonschema python scripts/validate_manifests.py # manifest schema
uv run python scripts/check_tables.py docs/cc-guide           # 表格结构
uv run python scripts/check_skill_links.py                    # skill 内链接
uv run --with pyyaml python scripts/check_doc_numbers.py      # 文档里的 CLAUDE.md 尺寸
uv run python scripts/extract_keybindings.py --context Chat   # 出厂默认键位（从二进制）
uv run python scripts/extract_changelog.py --since 2.1.305    # 内嵌 CHANGELOG（从二进制）

python3 plugins/agent-policy/scripts/policy.py check --strict  # agent-policy.toml 校验
python3 plugins/agent-policy/scripts/policy.py test            # 规则夹具
```

CI（`.github/workflows/`）：

- **plugin-validation.yml** —— 插件结构 / 引用 / MCP 检查；`skills-validation` 作业对 `plugins/` 阻塞、对 `.claude/` 非阻塞
- **docs.yml** —— `mkdocs build --strict` 后部署到 GitHub Pages

## Claude Code 使用指南（docs/cc-guide/）

9 章实操文档，结论来自本机实测 + 二进制逆向 + 官方文档。**改 Claude Code 配置前先查这里，别凭记忆**（入口是 `/cc-guide` skill）。

```bash
PYTHONPATH=. uv run --with "mkdocs-material>=9.5" mkdocs serve
PYTHONPATH=. uv run --with "mkdocs-material>=9.5" mkdocs build --strict --site-dir site
```

| 文件 | 用途 |
|------|------|
| `README.md` | 章节索引 + 三条速查 |
| `01-能力选型矩阵.md` | 12 个扩展层各自管什么 |
| `02-上下文经济学.md` | 上下文预算、压缩保留/丢弃规则 |
| `03-提示词与交互技巧.md` | 提示词配方、快捷键、消息队列 |
| `04-权限与护栏.md` | 权限模式、deny、hook、沙箱 |
| `05-多代理编排.md` | subagent / teams / workflows |
| `06-插件与市场.md` | manifest 语义、缓存模型、校验 |
| `07-排错手册.md` | 诊断方法论 + 踩坑记录 |
| `08-演进趋势.md` | 从 release 看演进主线 |
| `09-hooks-参考实现.md` | 18 个可移植 hook 的六类模式与移植清单 |

配套：`.claude/skills/cc-guide/`（操作入口）、`scripts/mkdocs_slug.py`（中文锚点 slugify）、`scripts/gen_guide_figures.py`（生成 9 张 SVG，明暗两套）。

## Git 提交规范

遵循 `.gitmessage`：`<type>(<scope>): <subject>`，正文含 `## Summary` / `## Changes Made` / `## Impact`，结尾 `Co-authored-by: Claude <noreply@anthropic.com>`。

类型：feat, fix, docs, style, refactor, test, chore。作用域：agent, skill, command, template, config, docs。

## 插件架构

```
plugins/<plugin-name>/
├── .claude-plugin/plugin.json  # 元数据 + agents/skills/commands 入口
├── README.md
├── agents/                     # MD + frontmatter
├── skills/<skill-name>/SKILL.md
├── commands/                   # 平铺 .md
├── templates/
└── .mcp.json                   # MCP 服务器（可选）
```

官方规范硬约束（写错是 `claude plugin validate` 的 error，不是 warning）：

- `plugin.json` 必须位于 `.claude-plugin/` 子目录
- `skills` 指向**目录**（内含 `<name>/SKILL.md`）；`commands` 是**平铺的 .md 文件**数组
- `plugin.json` 是扁平结构，禁止 `category` / `entry_points`（这些在 marketplace.json）
- `$schema` 指向 SchemaStore（Anthropic 官方地址已 404，别改回去）

配置层次：

- **marketplace.json**：owner、metadata、plugins 数组；`category`（research/expert-advisor/utility）与 `source` 在这里
- **plugin.json**：单插件元数据；必需 name/version/description/author，入口点 agents/skills/commands

Agent 定义工作流并调用技能与 MCP；Skill 是可复用能力模块；Command 是用户触发入口。

### 研究插件分析流程

以 evolutionary-biology-expert 为例：`search-term-optimization` 生成检索词 → article-mcp `search_literature` 检文献 → `academic-literature-analysis` 深读 → `six-dimensions-analysis` 六维分析 → `data-integration-formatting` 整合 → sequentialthinking 结构化推理。

## Error Playbook Hook

`.claude/settings.json` + `.claude/hooks/err-catcher.py`：PostToolUse 捕获 Bash 输出，按模式推断 domain（tool/network/config）与 severity（blocker/major/minor），记录到 `docs/error-playbook/`。

| 模式 | Domain | Severity | ID |
|------|--------|----------|-----|
| `FAILED`, `AssertionError` | tool | major | TEST-FAIL |
| `ImportError`, `ModuleNotFoundError` | tool | blocker | IMPORT |
| `Connection refused`, `ECONNREFUSED` | network | blocker | NET-REFUSED |
| `timeout`, `ETIMEDOUT` | network | major | TIMEOUT |
| `Permission denied` | config | blocker | PERMISSION |
| `merge.*conflict` | config | major | GIT-MERGE |

hook 脚本里的 `cwd` 需指向当前项目路径。

## MCP 依赖

研究插件在各自 `.mcp.json` 声明依赖，启用插件即可拉起；也可手动安装：

```bash
claude mcp add article-mcp uvx article-mcp server
claude mcp add sequentialthinking npx -y @modelcontextprotocol/server-sequential-thinking@latest
```

可选：mediawiki-mcp-server、playwright。环境变量 `EASYSCHOLAR_SECRET_KEY` 提升期刊质量评估。

## 本地技能集

`.claude/skills/` 下的开发工作流技能，详细用法见各自 `SKILL.md`（description 常驻上下文，此处不重复）：

| 技能 | 用途 |
|------|------|
| `/tdd` `/bdd` | 测试驱动 / 行为驱动开发 |
| `/sdr` `/gh` `/worktree` | 规格驱动 / GitHub CLI / 多 worktree |
| `/docs` `/cc-guide` | 活文档维护 / Claude Code 实测指南 |
| `/elegant` `/linus` `/cleanup` `/lint` | 重构、审查、冗余检测、代码检查 |
| `/squash` `/explore` | 提交历史整理 / 并行代码库探索 |

协同：`/tdd`→`/squash`；`/bdd`+`/tdd`；`/sdr`→`/gh`；`/worktree`+`/gh`；`/cleanup`+`/elegant`；`/docs` 与各技能搭配；改 Claude Code 配置先走 `/cc-guide`。

## 版本与发布

- `marketplace.json` version = 集合版本（当前 0.1.5）；`plugin.json` version = 单插件版本；改插件时两者同步
- 新增插件：建目录 → 写 `.claude-plugin/plugin.json` → 建 agents/skills/commands/templates → 更新 marketplace.json → `claude plugin validate`

## 插件列表

- **研究专家**：evolutionary-biology-expert (v0.1.3)、hybrid-speciation-expert (v0.1.2)、crop-breeding-expert (v0.1.2)、evolutionary-ecology-expert (v0.1.3)
- **实用工具**：slidev-generator (v0.1.1)、infographic-viz (v0.1.0)

## 其他

- `.claude/agents/python-zen-coding-expert.md`：Pythonic 代码编写与重构
- `tmp/`：临时工具（如 spec-kit），非核心，可清理
