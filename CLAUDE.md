# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个Claude Code研究插件集合，专门设计用于专家分析和研究工作流。当前包含进化生物学专家分析插件v0.1.0，提供深度的专家思想地图重建、学术网络分析和研究影响评估功能。

## 核心插件架构

### 进化生物学专家插件 (`plugins/evolutionary-biology-expert/`)

该插件采用模块化设计，包含以下核心组件：

#### 1. 命令接口 (`commands/`)
- **analyze-evolutionary-expert.md**: 主要分析命令接口
- 使用方法：`/analyze-evolutionary-expert <专家姓名> [研究主题]`
- 支持中英文专家姓名，可选研究主题参数

#### 2. 分析智能体 (`agents/`)
- **evolutionary-biology-analyst.md**: 核心分析智能体，定义六维度分析框架
- 集成article mcp工具，支持高级检索语法和批量处理
- 包含严格的30篇文献最低要求和质量控制机制

#### 3. 技能模块 (`skills/`)
该插件包含8个专业技能模块：

- **expert-network-mapping**: 学术网络拓扑分析
- **academic-literature-analysis**: 学术文献深度分析
- **search-term-optimization**: 智能检索词优化
- **google-scholar-analysis**: Google Scholar数据整合分析
- **temporal-dynamics-analysis**: 时间动态和演化轨迹分析
- **critical-thinking-analysis**: 批判性思维和理论边界分析
- **context-aware-analysis**: 上下文感知分析
- **reference-formatting**: Nature格式引用标准化（新增）

#### 4. 模板系统 (`templates/`)
- **expert_analysis_report_template.md**: 标准化分析报告模板
- 包含完整的参考文献格式和统计信息展示

#### 5. 工具配置 (`tools/`)
- **.mcp.json**: MCP服务器配置文件

## MCP依赖管理

插件依赖以下MCP服务器，必须在分析前正确配置：

```bash
# 学术文献检索核心工具
claude mcp add article-mcp uvx article-mcp server

# 结构化思考分析
claude mcp add sequentialthinking npx -y @modelcontextprotocol/server-sequential-thinking@latest

# 维基百科信息获取
claude mcp add mediawiki-mcp-server npx @professional-wiki/mediawiki-mcp-server@latest

# 网页分析和数据抓取
claude mcp add playwright npx @playwright/mcp@latest --browser chrome --headless
```

### 可选环境变量
```bash
export EASYSCHOLAR_SECRET_KEY="your_secret_key"  # 提升期刊质量评估精度
```

## 分析流程和架构

### 数据获取层
- **主要数据源**: Europe PMC + PubMed
- **高级检索**: 支持布尔运算符、字段限定、通配符、时间范围过滤
- **多轮检索**: 5阶段检索策略确保30篇文献最低要求
- **质量控制**: 相关性评分≥0.6，核心期刊占比≥40%

### 分析处理层
- **六维度分析框架**: 时间、背景、网络、批判、方法论、影响力
- **结构化思考**: sequentialthinking工具确保分析逻辑一致性
- **网络分析**: 合作网络拓扑、引用传播路径、知识结构映射
- **批判评估**: 主动寻找反驳证据，识别理论边界

### 输出规范层
- **引用格式**: 严格遵循Nature期刊标准
- **PubMed链接**: 每篇引用包含可验证的PubMed URL
- **统计信息**: 文献总数、期刊分类、时间分布分析
- **质量控制**: 多源验证、置信度评估、局限性说明

## 开发和维护指南

### 添加新技能模块
1. 在 `plugins/evolutionary-biology-expert/skills/` 创建新目录
2. 创建 `SKILL.md` 文件，遵循现有格式模板
3. 更新 `marketplace.json` 中的skills数组
4. 更新agent文件中的技能使用流程
5. 更新total_skills计数

### 修改现有功能
- 技能更新需要同时更新对应的SKILL.md文件
- agent文件中的工具使用规范需要保持同步
- marketplace.json版本号和元数据需要及时更新
- 提交信息遵循 `.gitmessage` 中的Conventional Commits格式规范，确保提交信息的一致性和可追踪性

### 质量保证标准
- 所有分析必须基于≥30篇高质量文献
- 核心期刊（IF>5）比例≥40%
- 文献相关性评分≥0.6
- 必须包含批评性文献和反驳观点
- 所有引用必须有完整的PubMed URL或DOI

## 技术架构特点

### 模块化设计
- 每个技能模块独立可测试
- 通过skills数组管理依赖关系
- 支持渐进式功能加载

### 错误处理
- 严格的拒绝条件定义
- 多层质量检查机制
- 透明的局限性说明

### 可扩展性
- 支持添加新领域专家分析
- 技能模块可复用于其他学科
- 模板系统支持自定义输出格式

## 版本和兼容性

- **当前版本**: 0.1.0
- **Claude Code版本要求**: ≥1.0.0
- **支持平台**: Linux, macOS, Windows
- **许可证**: MIT License

该插件架构设计确保了专业级学术分析的深度和广度，同时保持了良好的可维护性和可扩展性。