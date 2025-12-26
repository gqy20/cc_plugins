# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个Claude Code研究插件集合，专门设计用于专家分析和研究工作流。当前包含4个专业领域插件：进化生物学专家(v0.1.1)、杂交物种形成专家(v0.1.0)、作物育种专家(v0.1.0)和进化生态学专家(v0.1.1)。

## 开发命令

### 验证插件配置
```bash
# 验证 marketplace.json
claude plugin validate .claude-plugin/marketplace.json

# 运行完整验证脚本
./scripts/pre-commit-validate.sh

# 跳过验证提交（仅调试用）
git commit --no-verify
```

### Pre-commit Hook
项目配置了自动验证，提交时会自动运行 `scripts/pre-commit-validate.sh`。该脚本：
- 检查是否安装 Claude CLI
- 验证 `.claude-plugin/marketplace.json` 格式
- 仅在插件相关文件变更时触发（`.claude-plugin/*` 或 `plugins/*`）

### 提交规范
提交信息遵循 `.gitmessage` 定义的 Conventional Commits 格式：

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

### 标准目录结构
每个插件遵循统一的目录结构：
```
plugins/<plugin-name>/
├── plugin.json           # 插件元数据和入口点定义
├── agents/               # 分析智能体（MD格式）
│   └── <agent-name>.md
├── skills/               # 技能模块（MD格式）
│   └── <skill-name>.md
├── commands/             # 用户命令接口
│   └── <command-name>.md
└── templates/            # 输出模板
    ├── <analysis>_template.md
    └── analysis_workflows.md
```

### 插件配置层次
1. **marketplace.json** (`.claude-plugin/marketplace.json`)
   - 定义所有插件的集合
   - 包含 owner、metadata、plugins 数组

2. **plugin.json** (每个插件目录)
   - 定义单个插件的入口点
   - `entry_points.agents`: 智能体文件列表
   - `entry_points.skills`: 技能模块列表
   - `entry_points.commands`: 命令接口列表

### 智能体与技能关系
- **Agent**: 核心分析逻辑，定义工作流程和质量控制标准
- **Skill**: 可复用的专业能力模块，被 Agent 调用
- **Command**: 用户触发接口，通常启动一个 Agent

## MCP 依赖

### 核心依赖（所有插件必需）
```bash
claude mcp add article-mcp uvx article-mcp server
claude mcp add sequentialthinking npx -y @modelcontextprotocol/server-sequential-thinking@latest
```

### 可选依赖
```bash
# 维基百科信息
claude mcp add mediawiki-mcp-server npx @professional-wiki/mediawiki-mcp-server@latest

# 网页分析
claude mcp add playwright npx @playwright/mcp@latest --browser chrome --headless

# 基因组分析（特定插件）
claude mcp add genome-mcp npx genome-mcp-server
```

### 环境变量
```bash
export EASYSCHOLAR_SECRET_KEY="your_key"  # 提升期刊质量评估
```

## 添加新插件

1. 在 `plugins/` 创建新目录
2. 创建 `plugin.json`，定义入口点
3. 创建对应的 agents、skills、commands、templates 文件
4. 更新 `.claude-plugin/marketplace.json` 的 plugins 数组
5. 运行 `claude plugin validate .claude-plugin/marketplace.json` 验证

## 添加新技能到现有插件

1. 在对应插件的 `skills/` 目录创建新 MD 文件
2. 更新插件的 `plugin.json` 中 `entry_points.skills` 数组
3. 如需被 Agent 调用，更新对应的 Agent 文件
4. 验证配置：`claude plugin validate .claude-plugin/marketplace.json`

## 版本控制

- **marketplace.json version**: 整个插件集合的版本（当前 0.1.1）
- **plugin.json version**: 单个插件的版本
- 两者应保持同步更新

## 许可证

MIT License
