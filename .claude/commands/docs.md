---
name: docs
description: 活文档维护
version: 0.0.2
tags:
  - documentation
  - maintenance
  - workflow
dependencies:
  git: "any"
---

# /docs - 活文档维护

> **代码即真相，文档跟随代码**

自动分析项目代码，更新 `docs/` 核心文档和 `README.md`

---

## 用法

```bash
/docs                        # 更新所有核心文档
/docs @docs/architecture.md  # 只更新架构文档
/docs @README.md             # 只更新 README
/docs @reference/            # 更新所有参考文档
```

---

## 工作流程

```
1. 扫描阶段
   ├── 目录结构
   ├── 导入关系
   └── 模块边界

2. 分析阶段
   ├── 新增文件/模块
   ├── 修改的导出
   └── 删除的内容

3. 更新阶段
   ├── README.md
   ├── docs/changelog.md
   ├── docs/architecture.md
   ├── docs/components.md
   ├── docs/development.md
   ├── docs/testing.md
   ├── docs/contributing.md
   └── docs/reference/（按需）
```

---

## 核心文档清单

| 文件 | 内容 | 更新触发 |
|------|------|----------|
| `README.md` | 项目概述、安装、快速开始 | 结构变更 |
| `docs/changelog.md` | 版本变更历史 | 每次 commit |
| `docs/architecture.md` | 系统架构、模块关系 | 依赖变更 |
| `docs/components.md` | 组件清单、职责边界 | 新增/删除模块 |
| `docs/development.md` | 开发环境、工作流 | 工具链变更 |
| `docs/testing.md` | 测试策略、覆盖率 | 测试框架变更 |
| `docs/contributing.md` | 贡献流程、规范 | 流程变更 |

---

## 参考文档（按需生成）

| 目录 | 来源 | 说明 |
|------|------|------|
| `docs/reference/api/` | 代码提取 | 函数、类签名 |
| `docs/reference/configuration.md` | 配置文件 | 配置项说明 |
| `docs/reference/data-models.md` | 类型定义 | 数据结构 |

**特点**：可自动生成、可过时、可按需

---

## 分析策略

| 层级 | 方法 | 输出 | 更新目标 |
|------|------|------|----------|
| **文件** | glob 扫描 | 目录树 | README.md, components.md |
| **导入** | AST 分析 | 依赖图 | architecture.md |
| **配置** | 解析 toml/json | 配置项 | configuration.md |
| **类型** | 类型注解提取 | 数据结构 | data-models.md |

---

## 文档模板

### README.md

```markdown
# 项目名称

## 概述
[项目描述]

## 安装
```bash
uv install
```

## 快速开始
```bash
python -m app.main
```

## 文档
- 架构: docs/architecture.md
- 组件: docs/components.md
- 开发: docs/development.md
- 贡献: docs/contributing.md
```

### docs/architecture.md

```markdown
# 架构设计

## 系统分层
[分层图]

## 模块关系
[依赖图]

## 核心概念
[关键设计]
```

### docs/components.md

```markdown
# 组件清单

## 目录结构
```
project/
├── src/
│   ├── auth.py
│   └── db.py
└── tests/
```

## 核心模块

### src/auth.py
- **职责**: 用户认证、权限验证
- **导出**: `authenticate()`, `verify_token()`
- **依赖**: `db`, `crypto`

### src/db.py
- **职责**: 数据库连接、查询封装
- **导出**: `query()`, `execute()`
- **依赖**: `psycopg2`
```

### docs/development.md

```markdown
# 开发指南

## 环境准备
```bash
uv sync
pre-commit install
```

## 开发工作流
1. 功能规格: `/sdr`
2. 测试驱动: `/tdd`
3. 代码检查: `/lint`
4. 提交: 按 Conventional Commits

## 工具链
- 包管理: uv
- 测试: pytest
- 代码检查: ruff, mypy
```

### docs/testing.md

```markdown
# 测试策略

## 测试金字塔
- 单元测试: 70% (pytest)
- 集成测试: 20% (pytest)
- E2E 测试: 10% (behave)

## 覆盖率要求
- 核心逻辑: ≥80%
- 整体: ≥70%

## 运行测试
```bash
pytest                 # 单元测试
behave                 # E2E 测试
pytest --cov          # 覆盖率
```
```

### docs/contributing.md

```markdown
# 贡献指南

## 报告问题
使用 GitHub Issues

## 提交代码
1. Fork 项目
2. 创建功能分支
3. 编写测试
4. 提交 PR

## 代码规范
- 遵循 PEP 8
- 测试覆盖率 ≥70%
- 通过 ruff 和 mypy 检查
```

### docs/changelog.md

```markdown
# Changelog

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- 新功能

### Changed
- 变更

### Fixed
- 修复

## [0.1.0] - 2025-01-03

### Added
- 初始化项目
```

---

## Git 提交规范

| 场景 | 前缀 | 示例 |
|------|------|------|
| 更新核心文档 | `docs:` | `docs: 更新架构文档` |
| 新增参考文档 | `docs:` | `docs: 添加 API 参考` |
| 修正过时内容 | `docs:` | `docs: 修正组件清单` |

**注意**：文档变更使用 `docs:` 前缀

---

## 维护频率

| 文档 | 频率 | 理由 |
|------|------|------|
| `README.md` | 架构变更时 | 项目门面 |
| `docs/changelog.md` | 每次发布 | 版本历史 |
| `docs/architecture.md` | 模块关系变更 | 核心理解 |
| `docs/components.md` | 新增/删除组件 | 导航索引 |
| `docs/development.md` | 工具链变更 | 开发环境 |
| `docs/testing.md` | 测试策略变更 | 质量标准 |
| `docs/contributing.md` | 流程变更 | 贡献门槛 |
| `docs/reference/` | 代码变更时 | 自动生成 |

---

## 文档健康检查

### 内置检查

**过时检测**：对比文档与源代码的修改时间
- 源代码修改时间 > 文档修改时间 → 标记为需更新
- 关联规则：`docs/architecture.md` ↔ `src/`, `docs/api/*.md` ↔ 对应模块

**链接检查**：验证 markdown 链接有效性
- 内部链接：检查文件是否存在
- 外部链接：检查 HTTP 200

**覆盖度计算**：统计有文档的模块比例
- 扫描 `src/` 获取所有模块
- 扫描 `docs/components.md` 统计已文档化模块
- 覆盖率 = 已文档化 / 总模块

### 阈值

| 指标 | 目标 | 失败标准 |
|------|------|----------|
| 覆盖度 | ≥80% | <60% |
| 新鲜度 | ≥70% | <50% |
| 链接 | 100% | <95% |

---

**文档过时 = 项目失活**
