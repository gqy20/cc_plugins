# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Claude Code 研究插件集合，包含两类插件：
1. **研究专家插件** (4个) - 进化生物学、杂交物种形成、作物育种、进化生态学领域的专家分析系统
2. **实用工具插件** (2个) - Slidev 演示文稿生成、AntV 信息图表可视化

**项目特色**：
- 严格的配置标准和自动化验证
- Error Playbook Hook 自动错误记录系统
- 完整的开发工作流命令集（11 个命令）
- 研究插件依赖统一的 MCP 服务（article-mcp + sequentialthinking）

## 验证与测试

### 本地验证命令
```bash
# 验证 marketplace 配置
claude plugin validate .claude-plugin/marketplace.json

# 运行完整验证脚本
python3 .github/scripts/check_references.py           # 文件引用检查
python3 .github/scripts/check_mcp_dependencies.py     # MCP依赖检查
python3 .github/scripts/validate_content.py <plugin>  # 内容质量检查
```

### GitHub Actions 工作流
- **plugin-validation.yml**: 自动化验证，当插件相关文件变更时触发
  - 验证插件结构（plugin.json, README.md, agents/, skills/）
  - 检查文件引用、配置格式、MCP依赖
  - 使用矩阵策略并行验证所有插件
  - 集成验证阶段确保所有插件整体一致性

## Git 提交规范

遵循 `.gitmessage` 定义的 Conventional Commits 格式：

```
<type>(<scope>): <subject>

## Summary
<brief description>

## Changes Made
### <Component> Updates
<specific changes>

## Impact
<explanation>

Co-authored-by: Claude <noreply@anthropic.com>
```

**类型**: feat, fix, docs, style, refactor, test, chore
**作用域**: agent, skill, command, template, config, docs

## 插件架构

### 目录结构
```
plugins/<plugin-name>/
├── plugin.json           # 插件元数据 (name, version, author, agents, skills, commands)
├── README.md             # 插件说明文档
├── agents/               # Agent 文件 (MD 格式，包含 input_schema)
├── skills/               # 技能模块 (MD 格式，被 Agent 调用)
├── commands/             # 用户命令接口
├── templates/            # 输出模板
└── tools/.mcp.json       # MCP 服务器配置 (可选)
```

### 配置层次
1. **marketplace.json** - 定义所有插件集合，包含 owner、metadata、plugins 数组
   - 字段 `category`: 在这里定义 (research, expert-advisor, utility)
   - 字段 `source`: 插件目录相对路径
2. **plugin.json** - 单个插件配置，使用扁平结构：
   - 必需字段: name, version, description, author (对象格式)
   - 入口点: agents (数组), skills (数组), commands (数组)
   - 禁止字段: category, entry_points (这些在 marketplace.json 中)

### Agent/Skill/Command 关系
- **Agent**: 核心分析逻辑，定义工作流程（调用技能、使用 MCP 工具）
- **Skill**: 可复用能力模块，被 Agent 调用
- **Command**: 用户触发接口，启动 Agent 或执行特定功能

### 研究插件分析流程
以 evolutionary-biology-expert 为例：
1. 使用 `search-term-optimization` 技能生成检索词
2. 调用 article-mcp MCP 的 search_literature 检索文献
3. 使用 `academic-literature-analysis` 技能深度分析
4. 使用 `six-dimensions-analysis` 技能执行六维度分析
5. 使用 `data-integration-formatting` 技能整合数据
6. 通过 sequentialthinking MCP 进行结构化推理

## Error Playbook Hook 系统

项目配置了自动错误记录系统（`.claude/settings.json` + `.claude/hooks/err-catcher.py`）：

### 工作原理
- **自动检测**：PostToolUse Hook 捕获 Bash 命令输出
- **智能分类**：根据错误模式推断 domain（tool/network/config）和 severity（blocker/major/minor）
- **知识积累**：错误记录到 `docs/error-playbook/`，形成可复用的问题解决库

### 错误模式
| 模式 | Domain | Severity | ID |
|------|--------|----------|-----|
| `FAILED`, `AssertionError` | tool | major | TEST-FAIL |
| `ImportError`, `ModuleNotFoundError` | tool | blocker | IMPORT |
| `Connection refused`, `ECONNREFUSED` | network | blocker | NET-REFUSED |
| `timeout`, `ETIMEDOUT` | network | major | TIMEOUT |
| `Permission denied` | config | blocker | PERMISSION |
| `merge.*conflict` | config | major | GIT-MERGE |

### 修改路径
Hook 脚本中的 `cwd` 需要指向当前项目路径：
```python
cwd="/home/qy113/workspace/project/2601/cc_plugins"  # 修改此路径
```

## MCP 依赖

### 核心依赖（研究插件必需）
```bash
claude mcp add article-mcp uvx article-mcp server
claude mcp add sequentialthinking npx -y @modelcontextprotocol/server-sequential-thinking@latest
```

### 可选依赖
```bash
claude mcp add mediawiki-mcp-server npx @professional-wiki/mediawiki-mcp-server@latest
claude mcp add playwright npx @playwright/mcp@latest --browser chrome --headless
```

### 环境变量
```bash
export EASYSCHOLAR_SECRET_KEY="your_key"  # 提升期刊质量评估
```

## 本地技能集

项目根目录的 `.claude/skills/` 提供开发工作流技能（以 `SKILL.md` 格式）：

| 技能 | 用途 |
|------|------|
| `/tdd` | 测试驱动开发流程，增量测试策略 |
| `/bdd` | 行为驱动开发流程，可执行文档 |
| `/gh` | GitHub CLI 专家助手，场景化指导 |
| `/sdr` | 规格驱动开发流程，Git 工作流管理 |
| `/docs` | 活文档维护，文档健康检查 |
| `/linus` | 实用主义代码审查与重构 |
| `/elegant` | 优雅编码与重构规范 |
| `/squash` | Commit 历史整理与合并 |
| `/lint` | 代码质量检查工具集 |
| `/worktree` | Git Worktree 工作流 - PR Review、并行开发 |
| `/cleanup` | Python 代码冗余检测清单 |
| `/explore` | 并行代码库探索 |

**技能协同**：
- `/tdd` → `/squash`：TDD 产生小 commit → 功能完成后合并
- `/elegant` + `/tdd`：优雅编码 + 测试驱动
- `/sdr` → `/gh`：规格驱动 → GitHub 操作
- `/bdd` + `/tdd`：BDD (验收) + TDD (单元)，双层测试
- `/worktree` + `/gh`：多 worktree 并行 PR review + gh 操作
- `/cleanup` + `/elegant`：冗余检测 + 优雅重构
- `/docs` + 任何技能：代码变更后更新文档

## 版本控制

- **marketplace.json version**: 整个插件集合版本 (当前 0.1.4)
- **plugin.json version**: 单个插件版本
- 更新插件时同步更新两者版本号

## 添加新插件

1. 在 `plugins/` 创建新目录
2. 创建 `plugin.json`，定义 agents/skills/commands 数组
3. 创建对应的 agents、skills、commands、templates 文件
4. 更新 `.claude-plugin/marketplace.json` 的 plugins 数组
5. 运行 `claude plugin validate .claude-plugin/marketplace.json` 验证

## 修改现有插件

1. 修改对应 MD 文件
2. 如新增技能/命令，更新 `plugin.json` 中对应数组
3. 如需被 Agent 调用，更新对应 Agent 文件
4. 验证配置

## 插件列表

### 研究专家插件
- **evolutionary-biology-expert** (v0.1.2) - 专家思想地图重建，学术网络分析
- **hybrid-speciation-expert** (v0.1.0) - 杂交物种形成，基因组渐渗分析
- **crop-breeding-expert** (v0.1.0) - 分子育种，品种改良策略
- **evolutionary-ecology-expert** (v0.1.1) - 自然选择机制，生态相互作用

### 实用工具插件
- **slidev-generator** (v0.1.1) - Markdown 转 Slidev 演示文稿
- **infographic-viz** (v0.1.0) - AntV 信息图表可视化

---

# 本地技能详细说明

## /tdd - 测试驱动开发

**核心**：快速反馈 → 增量测试 → 性能优化

```bash
# 开发时：只运行相关测试
pytest tests/test_new_feature.py -v

# 提交前：完整验证
pytest && uv run ruff check && uv run mypy .
```

**TDD 循环**：
- 🔴 红：编写测试 → `pytest tests/test_xxx.py`
- 🟢 绿：实现功能 → `pytest tests/test_xxx.py`
- ♻️ 重构：优化代码 → `pytest tests/test_module.py`

## /squash - Commit 历史整理

**核心**：TDD 产生小 commit → 功能完成后合并

```bash
# 合并最近 N 个 commit 为 1 个
git rebase -i HEAD~N

# 快速合并（软重置）
git reset --soft HEAD~N
git commit -m "feat: 完整功能描述"
```

**策略**：
- 开发中：保持小 commit（便于回滚）
- 功能完成后：合并为 1 个 commit
- 推送前：清理本地历史

## /elegant - 优雅编码规范

**核心**：代码质量标准 + 重构手法

**复杂度指标**：
- McCabe 圈复杂度 ≤ 10
- 函数长度 ≤ 20 行
- 嵌套深度 ≤ 3 层

**代码坏味道**：长函数、重复代码、过度嵌套、上帝对象、死代码

## /sdr - 规格驱动开发

**核心**：宪法 → 规格 → 计划 → 任务 → 代码

**状态检测**：自动进入对应阶段
- 无宪法 → 阶段 0：创建宪法
- 无规格 → 阶段 1：创建规格
- 无计划 → 阶段 2：创建计划
- 无任务 → 阶段 3：分解任务
- 就绪 → 阶段 4：执行实现

**Git 分支**：`###-feature-name` 格式，自动递增编号

## /gh - GitHub CLI 助手

**场景化指导**：常用 gh 命令的最佳实践

## /linus - 实用主义审查

**核心原则**：Talk is cheap, show me the code

**数据结构 > 代码逻辑**

## /lint - 代码质量检查

**工具集**：shellcheck, yamllint, ruff, eslint

## /docs - 活文档维护

**核心**：代码即真相，文档跟随代码

- **健康检查**: 检测文档新鲜度、完整性
- **智能更新**: 根据代码变更自动更新相关文档
- **质量评分**: 覆盖度、新鲜度、完整性评分
- **代码阅读深度**: 函数签名、Docstring、测试代码、ADR

**用法**: `/docs` (健康) | `/docs init` | `/docs update` | `/docs score`

## /bdd - 行为驱动开发

**核心**：业务语言描述测试，连接需求与代码

- **Gherkin 语法**: Feature/Scenario/Given/When/Then
- **可执行文档**: 业务、开发、测试共识
- **双层测试**: BDD (behave, 验收) + TDD (pytest, 单元)

**用法**: `/bdd` (引导) | `/bdd feature` | `/bdd step` | `/bdd run`

## /worktree - Git Worktree 工作流

**核心**：并行开发、PR Review、完整开发生命周期

- **场景 1：PR Review** - 为每个 PR 创建独立 worktree，避免频繁切换分支
- **场景 2：并行开发** - 同时在多个功能分支工作，互不干扰
- **场景 3：热修复** - 在主分支保持工作的同时处理紧急 bug

**用法**: `/worktree` (引导) | `/worktree create` | `/worktree list` | `/worktree remove`

## /cleanup - Python 代码冗余检测

**核心**：先看有什么，再看写什么

检测代码中是否有可用标准库或已安装包替代的冗余实现。

**冗余模式对照表**：
| 当前模式 | 应该用 | 检测命令 |
|----------|--------|----------|
| `os.path.join` | `pathlib.Path` | `grep -rn "os.path\."` |
| `class X: def __init__` | `@dataclass` | `grep -rn "def __init__"` |
| `urllib.request` | `requests` | `grep -rn "urllib"` |
| `datetime.strptime` | `dateutil.parser` | `grep -rn "strptime"` |
| `csv.reader/open` | `pandas.read_csv` | `grep -rn "csv\\.reader\|open.*\\.csv"` |

**核心原则**：依赖优先、标准库优先、删除而非兼容

**用法**: `/cleanup` (完整清单) | `/cleanup scan` (快速扫描) | `/cleanup <pattern>`

---

# 本地开发 Agent

项目 `.claude/agents/` 目录包含本地开发智能体：

## python-zen-coding-expert

**用途**：编写符合 Python Zen 原则的代码，优先可读性和简洁性

**适用场景**：
- 编写新 Python 代码时
- 重构现有代码使其更 Pythonic
- 需要确保代码风格符合 PEP 20 原则

**Zen of Python 核心原则**：
- Beautiful is better than ugly
- Explicit is better than implicit
- Simple is better than complex
- Readability counts

---

# tmp/ 目录说明

`tmp/` 目录用于存放临时性、实验性代码和工具：

- **spec-kit/**: GitHub Spec Kit 工具（`specify-cli`），用于规格驱动开发（SDD）
  - 包含 `pyproject.toml`，定义了 specify CLI 的依赖
  - 提供 `specify` 命令，用于项目初始化和管理

**注意**：`tmp/` 目录内容不作为项目核心部分，可根据需要清理或迁移。
