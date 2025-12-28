---
name: sdr
description: 规格驱动开发（SDD）流程助手，包含 Git 工作流管理
version: 0.0.1
tags:
  - workflow
  - planning
  - spec-driven
  - git
dependencies:
  git: "any"
---

# 规格驱动开发（SDD）工作流

**检测当前项目状态，引导下一步行动，全程 Git 管理**

---

## 状态检测

按顺序检查项目状态，进入对应阶段：

| 检查项 | 文件/目录 | 进入阶段 |
|--------|-----------|----------|
| 无宪法 | `specs/000-constitution/spec.md` | 阶段0：创建宪法 |
| 无规格 | `specs/001-*/` 目录 | 阶段1：创建规格 |
| 无计划 | `specs/*/spec.md` 存在但无 `plan.md` | 阶段2：创建计划 |
| 无任务 | `plan.md` 存在但无 `tasks.md` | 阶段3：分解任务 |
| 就绪 | 以上都有 | 阶段4：执行实现 |

**执行 `/sdr` 自动检测并进入对应阶段**

---

## Git 分支管理

**每个功能对应一个独立分支**：

| 时机 | 分支命名格式 | 示例 |
|------|-------------|------|
| 创建规格 | `###-feature-name` | `001-photo-albums` |
| 实现中 | 保持不变 | - |
| 完成后 | 合并到 `main` 后删除 | - |

**分支编号规则**：
- 三位数字：001, 002, 003, ...（000 保留给宪法）
- 自动递增，基于现有分支和 `specs/` 目录
- 名称长度 ≤ 244 字节（Git 限制）

---

## Git 提交规范

| 阶段 | 前缀 | 示例 |
|------|------|------|
| 创建宪法 | `chore:` | `chore: 初始化项目宪法` |
| 创建规格 | `docs:` | `docs: 添加图片上传功能规格` |
| 澄清需求 | `docs:` | `docs: 澄清图片格式限制` |
| 创建计划 | `docs:` | `docs: 添加技术实现计划` |
| 分解任务 | `docs:` | `docs: 生成任务列表` |
| 实现功能 | `feat:` | `feat: 实现图片上传接口` |
| 修复问题 | `fix:` | `fix: 修复上传失败bug` |
| 重构代码 | `refactor:` | `refactor: 优化上传逻辑` |

---

## 阶段0：创建项目宪法

**目标**：定义不可变更的开发原则

**输出**：`specs/000-constitution/spec.md`

**操作**：
1. 创建目录：`specs/000-constitution/`
2. 创建文件：`specs/000-constitution/spec.md`

**模板**：
```markdown
# 项目宪法

## 开发原则
- Library-First: 每个功能作为独立库开始
- CLI Interface: 所有库必须暴露命令行接口
- Test-First: 强制 TDD（不可协商）
- Simplicity: 限制项目数量（初始最多3个），禁止过度抽象

## 质量标准
- 测试覆盖率：核心逻辑 ≥ 80%，整体 ≥ 70%
- 文档要求：每个功能必须有规格说明
- 代码审查：所有代码必须经过审查

## 技术约束
- 语言版本：
- 禁止使用的库：
- 必须使用的工具：
```

**完成标志**：
- [ ] 文件已创建
- [ ] 原则已明确

**Git 提交**：`git commit -m "chore: 初始化项目宪法"`

---

## 阶段1：创建功能规格

**目标**：描述"做什么"，不涉及"怎么做"

**操作**：
1. 创建 Git 分支：`git checkout -b ###-feature-name`
2. 创建目录：`specs/###-feature-name/`
3. 创建文件：`specs/###-feature-name/spec.md`

**模板**：
```markdown
# [功能名称]

## 概述
[一句话描述功能]

## 用户故事
作为 [角色]，我想要 [功能]，以便 [价值]

## 功能需求
### 核心功能
- [ ] 功能点1 [NEEDS CLARIFICATION]
- [ ] 功能点2

### 边界条件
- 输入限制：
- 输出要求：

## 验收标准
- [ ] 场景1：Given-When-Then
- [ ] 场景2：

## 非功能性需求
- 性能要求：
- 安全要求：
```

**完成标志**：
- [ ] 无 `[NEEDS CLARIFICATION]` 标记
- [ ] 验收标准完整

**Git 提交**：`git commit -m "docs: 添加[功能名称]规格"`

---

## 阶段2：创建技术计划

**目标**：定义"怎么做"的技术路径

**输出**：`specs/###-feature-name/plan.md`

**模板**：
```markdown
# 技术实现计划

## 技术上下文
- 语言/框架版本：
- 主要依赖库：

## 架构决策（ADR）
### 决策1：选型 X 而非 Y
- 理由：
- 权衡：
- 后果：

## 数据模型
```
[类型/表定义]
```

## API 契约
### 接口1：[名称]
- 请求：
- 响应：
- 错误处理：

## 关键验证场景
1. 场景1：
2. 场景2：
```

**完成标志**：
- [ ] 技术选型明确
- [ ] 无未决技术问题

**Git 提交**：`git commit -m "docs: 添加技术实现计划"`

---

## 阶段3：分解任务

**目标**：将计划分解为可执行任务列表

**输出**：`specs/###-feature-name/tasks.md`

**格式**：
```markdown
# 任务列表

## [P] 用户故事1：[标题]
### 任务1.1 [P]
- 文件：`path/to/file.py`
- 描述：[具体操作]
- 测试：[测试点]

### 任务1.2
- 依赖：任务1.1
- 文件：
- 描述：

## 用户故事2：[标题]
### 任务2.1 [P]
- 文件：
- 描述：
```

**说明**：
- `[P]` = 可并行执行（Parallel）
- 每个任务包含：文件路径、描述、测试点、依赖关系
- 按用户故事分组

**完成标志**：
- [ ] 所有功能已覆盖
- [ ] 任务可独立验证

**Git 提交**：`git commit -m "docs: 生成任务列表"`

---

## 阶段4：执行实现

**目标**：按任务列表实现，遵循 TDD

**流程**：
1. 读取下一个任务
2. 🔴 编写失败的测试
   - **Git 提交**：`git commit -m "test: 添加[功能]的失败测试"`
3. 🟢 编写最少代码使测试通过
   - **Git 提交**：`git commit -m "feat: 实现[功能]"`
4. ♻️ 重构优化代码
   - **Git 提交**：`git commit -m "refactor: 优化[功能]代码"`
5. 重复直到所有任务完成

**完成标志**：
- [ ] 所有任务完成
- [ ] 规格验收通过
- [ ] 代码审查通过

**合并流程**：
```bash
git checkout main
git merge ###-feature-name
git branch -d ###-feature-name
```

---

## 快捷跳转

```bash
/sdr              # 自动检测状态，引导下一步
/sdr constitution # 强制创建/更新项目宪法
/sdr spec         # 强制创建功能规格
/sdr plan         # 强制创建技术计划
/sdr tasks        # 强制分解任务列表
/sdr implement    # 强制执行实现
```

---

## 完整工作流

```
/sdr constitution
  ↓
创建 specs/000-constitution/spec.md
  ↓
git commit -m "chore: 初始化项目宪法"

/sdr spec
  ↓
git checkout -b 001-feature-name
  ↓
创建 specs/001-feature-name/spec.md
  ↓
git commit -m "docs: 添加功能规格"

/sdr plan
  ↓
创建 specs/001-feature-name/plan.md
  ↓
git commit -m "docs: 添加技术计划"

/sdr tasks
  ↓
创建 specs/001-feature-name/tasks.md
  ↓
git commit -m "docs: 生成任务列表"

/sdr implement
  ↓
逐个任务执行（每个任务 TDD 循环）
  - 🔴 测试 → git commit -m "test: ..."
  - 🟢 实现 → git commit -m "feat: ..."
  - ♻️ 重构 → git commit -m "refactor: ..."
  ↓
合并到 main
```

---

## 状态报告

**每阶段完成后报告**：
1. 当前阶段
2. 创建/修改的文件
3. Git 分支名称
4. Git 提交信息
5. 下一步行动

**示例**：
```
✅ 阶段1完成：创建功能规格
📁 specs/001-photo-albums/spec.md
🌿 分支：001-photo-albums
💬 提交：docs: 添加图片上传功能规格
➡️  下一步：执行 /sdr plan 创建技术计划
```

---

## 核心原则

1. **规格即真相**：规格说明是主要文档，代码是规格的表达
2. **渐进式细化**：宪法 → 规格 → 计划 → 任务 → 代码，逐层深入
3. **Git 追踪**：每个阶段都有对应的 Git 提交
4. **质量门控**：每阶段有明确的完成标志，未完成不进入下一阶段
5. **可逆性**：任何阶段都可以回退修正

**记住：宁可多花时间澄清需求，也不要在错误的方向上狂奔**
