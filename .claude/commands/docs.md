---
name: docs
description: 活文档维护
version: 0.0.4
tags:
  - documentation
  - maintenance
  - workflow
dependencies:
  git: "any"
---

# /docs - 活文档维护

> **代码即真相，文档跟随代码**

智能分析项目代码，维护 `docs/` 核心文档和 `README.md`

---

## 用法

```bash
/docs                       # 默认：显示健康状态
/docs @docs/architecture.md # 更新指定文档（等同于 update）
/docs init                  # 初始化文档骨架
/docs update                # 更新所有过时文档
/docs update --preview      # 预览变更
/docs score                 # 质量评分
```

---

## 默认模式：健康检查

执行 `/docs` 显示文档健康状态：

```
📊 文档健康状态

| 文档 | 状态 | 最后更新 | 更新时间 | 相关代码变更 |
|------|------|----------|----------|-------------|
| README.md | ✅ 新鲜 | 2天前 | - | 无 |
| docs/architecture.md | ⚠️ 过时 | 今天 | 14:30 | src/auth.py 新增 OAuth |
| docs/components.md | ⚠️ 过时 | 今天 | 09:15 | 发现 3 个新模块 |
| docs/changelog.md | ⚠️ 过时 | 15天前 | - | 有 5 个新 commit |

建议操作：/docs update
```

**说明**：
- **最后更新**：相对时间（今天/2天前/30天前）
- **更新时间**：当日精确时间（HH:MM），非今天显示 `-`

---

## init 模式：初始化文档骨架

当项目缺少 `docs/` 目录时：

```bash
/docs init
```

自动创建完整的文档骨架：

```
📁 创建文档结构

docs/
├── architecture.md     # 架构设计（从代码分析生成）
├── components.md       # 组件清单（扫描模块生成）
├── development.md      # 开发指南（从配置文件提取）
├── testing.md          # 测试策略（从测试代码推断）
├── contributing.md     # 贡献指南（使用模板）
└── reference/          # 参考文档（自动生成）
    ├── api/
    ├── configuration.md
    └── data-models.md

✅ 初始化完成！现在可以运行：
   /docs        # 查看健康状态
   /docs update # 更新过时文档
```

---

## update 模式：更新文档

### 智能更新

根据代码变更自动选择更新目标：

| 代码变更 | 自动更新 | 理由 |
|----------|----------|------|
| 新增模块 | components.md | 模块清单 |
| 修改导入关系 | architecture.md | 依赖关系 |
| 修改配置文件 | development.md | 环境配置 |
| 新增测试 | testing.md | 测试覆盖 |
| 修改 package.json | README.md | 项目元数据 |

```bash
/docs update              # 更新所有过时文档
/docs update --auto       # 根据最近代码变更智能选择
```

### 预览变更

```bash
/docs update --preview
```

显示变更预览：

```diff
# docs/architecture.md

## 模块关系

### src/auth.py
- **依赖**: `db`, `crypto`
+ **依赖**: `db`, `crypto`, `httpx`

+ ### src/oauth_providers.py
+ - **职责**: OAuth 提供商集成
+ - **导出**: `get_provider()`, `exchange_code()`
```

确认后写入文件。

---

## score 模式：质量评分

```bash
/docs score
```

输出：

```
📊 文档质量评分

| 维度 | 得分 | 目标 | 状态 |
|------|------|------|------|
| 覆盖度 | 75% | ≥80% | ⚠️ |
| 新鲜度 | 60% | ≥70% | ❌ |
| 完整性 | 85% | ≥80% | ✅ |
| 链接有效 | 98% | 100% | ⚠️ |

总体评分: C+ (79.5/100)

主要问题：
1. docs/architecture.md 已过时（30天前 14:30）
2. src/new_module.py 无文档
3. docs/api/invalid.md 链接失效

建议操作：
1. /docs update docs/architecture.md
2. /docs add-component src/new_module.py
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

---

## 工作流程

```
1. 扫描阶段
   ├── 目录结构
   ├── 导入关系
   └── 模块边界

2. 检查阶段
   ├── 过时检测（mtime 对比）
   │   ├── 今日更新：显示 HH:MM 时间戳
   │   └── 历史更新：显示相对时间（X天前）
   ├── 链接检查
   └── 覆盖度计算

3. 分析阶段
   ├── 新增文件/模块
   ├── 修改的导出
   └── 删除的内容

4. 更新阶段（需确认）
   ├── 显示预览
   ├── 用户确认
   └── 写入文件
```

---

## 代码阅读深度策略

| 来源 | 提取内容 | 深度 |
|------|----------|------|
| **函数签名 + 类型注解** | API 骨架 | ⭐⭐⭐⭐⭐ |
| **Docstring** | 参数说明、返回值、异常 | ⭐⭐⭐⭐ |
| **测试代码** | 边界条件、预期行为 | ⭐⭐⭐⭐ |
| **ADR（/sdr）** | 设计决策原因 | ⭐⭐⭐⭐⭐ |

### 局限性

- ❌ 无法理解复杂业务逻辑
- ❌ 无法提取隐式规则
- ❌ 依赖代码质量

**原则**：生成骨架，依赖开发者填充细节

---

## 时间戳获取

```bash
# 获取文件修改时间（推荐）
git log -1 --format="%ci" -- path/to/file
mtime=$(git log -1 --format="%ct" -- path/to/file); date -d "@$mtime" "+%H:%M"
```

---

## Git 提交规范

| 场景 | 前缀 | 示例 |
|------|------|------|
| 更新核心文档 | `docs:` | `docs: 更新架构文档` |
| 新增参考文档 | `docs:` | `docs: 添加 API 参考` |
| 修正过时内容 | `docs:` | `docs: 修正组件清单` |

---

## 与其他命令协同

```bash
# 新功能开发
/sdr          # 创建规格
/tdd          # 测试驱动开发
/docs update  # 更新文档

# 代码重构
/linus        # 审查代码
/elegant      # 重构方案
/docs update --preview  # 预览文档更新

# 项目初始化
/init         # 创建 CLAUDE.md
/docs init    # 初始化文档体系
/docs score   # 查看健康状态
```

---

**文档过时 = 项目失活**
