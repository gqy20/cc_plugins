# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Claude Code 研究插件集合，包含两类插件：
1. **研究专家插件** (4个) - 进化生物学、杂交物种形成、作物育种、进化生态学领域的专家分析系统
2. **实用工具插件** (2个) - Slidev 演示文稿生成、AntV 信息图表可视化

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
2. **plugin.json** - 单个插件配置，使用扁平结构：
   - 必需字段: name, version, description, author
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

## 本地命令集

项目根目录的 `.claude/commands/` 提供开发工作流命令：

| 命令 | 用途 |
|------|------|
| `/tdd` | 测试驱动开发流程，包含 Git 提交规范 |
| `/gh` | GitHub CLI 专家助手，场景化指导 |
| `/sdr` | 规格驱动开发流程，包含 Git 工作流管理 |
| `/linus` | 实用主义代码审查与重构 |
| `/elegant` | 优雅编码与 Git 协作工作流（TDD + 重构 + PR 管理） |
| `/lint` | 代码质量检查工具集 (shellcheck, yamllint, ruff, eslint) |

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
