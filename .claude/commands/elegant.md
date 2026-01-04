---
name: elegant
description: 优雅编码与重构规范
version: 0.0.5
tags:
  - elegance
  - refactoring
  - code-quality
  - clean-code
dependencies:
  git: "any"
---

# 优雅编码与重构规范

> **优雅代码 = 可读 + 可维护 + 可测试**

目标：让代码在六个月后仍然可读、可维护、可测试。

---

## 快捷命令

```bash
/elegant              # 交互式引导
/elegant review       # 代码审查
/elegant refactor     # 重构方案
/elegant smell        # 坏味道检测
```

---

## 1. 核心原则

| 原则 | 说明 |
|------|------|
| **KISS** | Keep It Simple, Stupid |
| **DRY** | Don't Repeat Yourself |
| **YAGNI** | You Aren't Gonna Need It |
| **SOLID** | 单一职责、开闭、里氏替换、接口隔离、依赖倒置 |
| **纯函数优先** | 无副作用、可测试、可推理 |

**关注点**：本规范专注代码质量。Git/TDD 流程请参考 `/tdd`、`/sdr`。

---

## 2. 代码质量标准

### 2.1 复杂度指标

| 指标 | 阈值 | 测量方式 |
|------|------|----------|
| **McCabe 圈复杂度** | ≤ 10 | 见 §7 |
| **函数长度** | ≤ 20 行 | 不含空行/注释 |
| **嵌套深度** | ≤ 3 层 | if/for/while 嵌套 |
| **参数数量** | ≤ 5 个 | 函数/方法参数 |
| **类方法数** | ≤ 15 个 | 单个类的公开方法 |
| **文件行数** | ≤ 300 行 | 建议拆分 |

**超标即重构**

### 2.2 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 函数 | 动词+名词 | `get_user()`, `calculate_total()`, `validate_input()` |
| 布尔函数 | `is/has/can/should` | `is_valid()`, `has_permission()`, `can_edit()` |
| 布尔变量 | `is/has` 前缀 | `is_active`, `has_error` |
| 集合 | 复数形式 | `users`, `items`, `errors` |
| 字典 | 描述性 | `user_by_id`, `config_by_key` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| 类 | PascalCase | `UserService`, `OrderProcessor` |
| 私有 | `_前缀` | `_internal_method()` |

### 2.3 设计原则

| 原则 | 要求 |
|------|------|
| **SOLID** | 单一职责、开闭、里氏替换、接口隔离、依赖倒置（详见 §1） |
| **组合优于继承** | 优先使用组合 |
| **显式优于隐式** | 避免魔法，直接表达意图 |
| **不可变数据** | 优先使用不可变结构 |
| **类型提示** | 函数签名必须有类型注解 |

### 2.4 抽象信号

**提取函数的信号**：
- 函数超过 20 行
- 代码出现 2 次以上
- 可用注释概括一段代码的意图
- 抽象层次不一致

**创建类的信号**：
- 需要维护多个相关字段
- 需要封装数据和行为
- 需要继承和多态

**不需要类的场景**：
- 仅数据容器 → `@dataclass` 或 `TypedDict`
- 仅函数集合 → 模块级函数
- 仅一个方法 → 函数

**拆分模块的信号**：
- 文件超过 300 行
- 有明显独立的功能边界
- 需要单独测试某部分

### 2.5 代码坏味道

| 坏味道 | 特征 | 重构方法 |
|--------|------|----------|
| **长函数** | >50 行，>3 层嵌套 | Extract Method |
| **重复代码** | 相同代码出现 3 次以上 | Extract Function |
| **过度嵌套** | if/for 嵌套 >4 层 | Guard Clauses |
| **上帝对象** | 类方法 >15 个 | Separate Concerns |
| **特性依恋** | 方法大量访问外部数据 | Move Method |
| **数据泥团** | 相同数据项一起出现 | Introduce Parameter Object |
| **基本类型偏执** | 用基本类型表示领域概念 | Introduce Type Alias |
| **消息链** | `a.b.c.d.e` | Hide Delegate |
| **中间人** | 类的大部分方法委托给其他类 | Remove Middle Man |
| **异曲同工** | 相似函数参数顺序不同 | Uniformize Parameter |
| **冗余兼容代码** | 为不再支持的版本保留的代码 | Delete Dead Code |
| **死代码** | 永远不会执行的代码/未使用的导入 | Remove Dead Code |

### 2.6 检测方法

| 目标 | Grep 模式 | 检测内容 |
|------|-----------|----------|
| 废弃标记 | `@deprecated\|DEPRECATED` | 明确标记的废弃代码 |
| 兼容命名 | `compat\|legacy\|backwards` | 兼容性相关变量/函数 |
| 版本检查 | `version.*<\|sys.version_info` | 版本条件分支 |
| 兼容导入 | `try:.*import.*except` | try-except 导入兼容 |
| 平台判断 | `platform.*==\|sys.platform` | 平台兼容逻辑 |

**快速扫描**：`grep -rn "@deprecated\|DEPRECATED\|compat\|legacy\|version.*<\|try:.*import.*except" src/`

---

## 3. 重构安全策略

### 3.1 重构铁律

> **重构 = 改变结构，不改变行为**

1. **有测试覆盖** — 或先补充测试
2. **测试全过** — 重构过程中保持通过
3. **小步提交** — 每个 commit 可独立回滚

### 3.2 重构流程

```
test: 补充测试
refactor: 提取函数
refactor: 继续重构
...

每个步骤：uv run pytest && uv run ruff check
```

### 3.3 常用重构手法

| 手法 | 说明 |
|------|------|
| **Extract Method** | 提取函数 |
| **Extract Class** | 提取类 |
| **Introduce Parameter Object** | 引入参数对象 |
| **Replace Conditional with Polymorphism** | 用多态替换条件 |
| **Decompose Conditional** | 分解条件表达式 |
| **Consolidate Conditional** | 合并条件表达式 |
| **Replace Magic Number with Constant** | 用常量替换魔法数 |
| **Replace Nested Conditional with Guard Clauses** | 卫语句替换嵌套 |
| **Introduce Factory** | 引入工厂 |
| **Form Template Method** | 形成模板方法 |
| **Remove Dead/Compatibility Code** | 删除死代码/兼容代码 |

---

## 4. Git 协作规范（简化）

详细流程参考 `/tdd`、`/sdr`。

| 原则 | 说明 |
|------|------|
| **小 PR** | <300 行 diff，一个主题 |
| **独立 commit** | 每个 commit 可通过测试 |
| **Commit 前缀** | `test:`, `refactor:`, `fix:` |
| **参考 `.gitmessage`** | 完整格式规范 |

---

## 5. 输出格式

### 5.1 代码审查（`/elegant review`）

```markdown
## 审查结果

### 整体评价
[通过/需修改/重写]

### 问题清单
| 位置 | 问题 | 严重度 | 建议 |
|------|------|--------|------|
| `file:line` | 圈复杂度 12 | 高 | 提取函数 |

### 复杂度报告
| 函数 | 圈复杂度 | 行数 | 评级 |
|------|----------|------|------|
| `process_order` | 12 | 45 | ❌ |

### 坏味道
- [ ] 长函数
- [ ] 重复代码
- [ ] 过度嵌套
```

### 5.2 重构方案（`/elegant refactor`）

```markdown
## 重构方案

### 问题
- 圈复杂度 15（阈值 ≤10）
- 函数 60 行（阈值 ≤20）

### 步骤
1. Extract Method: `validate_stock()`
2. Extract Method: `calculate_discount()`
3. Replace Nested with Guard Clauses

### 预期
| 指标 | 前 | 后 | 改善 |
|------|----|----|----|
| 圈复杂度 | 15 | 3 | ↓80% |
```

### 5.3 坏味道检测（`/elegant smell`）

```markdown
## 坏味道报告

### 长函数
| 函数 | 位置 | 行数 |
|------|------|------|
| `process` | `svc.py:23` | 78 |

### 重复代码
| 代码块 | 出现 | 次数 |
|--------|------|------|
| `db.query+loop` | 3 处 | 3 |
```

---

## 6. 完整示例

### 场景：订单处理重构

**问题**：
- 圈复杂度 15，函数 60 行，嵌套 5 层

**重构方案**：

```python
# Before: 60 行，复杂度 15
def process_order(order_id):
    # 验证库存（4 层嵌套）
    for item in order.items:
        if product.stock < item.quantity:
            if product.backorder_allowed:
                item.backorder = True
            else:
                return error
    # 计算折扣（3 层嵌套）
    if order.user:
        if order.user.is_vip:
            if order.user.level >= 3:
                discount = 0.3
    # ... 共 60 行

# After: 3 个函数，各 10-18 行，复杂度 3
def validate_item_stock(item: OrderItem) -> tuple[bool, str | None]:
    """提取库存验证逻辑，返回 (是否有效, 错误信息)"""
    ...

def calculate_order_discount(order: Order) -> float:
    """提取折扣计算逻辑，返回最大折扣率"""
    ...

def process_order(order_id: int) -> dict:
    """主函数：调用上述函数，18 行，复杂度 3"""
    for item in order.items:
        is_valid, error = validate_item_stock(item)
        if not is_valid:
            return {"error": error}
    discount = calculate_order_discount(order)
    # ... 保存订单、发送通知
```

**效果**：

| 指标 | 前 | 后 | 改善 |
|------|----|----|----|
| 圈复杂度 | 15 | 3 | ↓80% |
| 函数行数 | 60 | 18 | ↓70% |
| 最大嵌套 | 5 层 | 1 层 | ↓80% |

**Commit 顺序**：
```bash
git commit -m "test: 补充订单处理测试"
git commit -m "refactor: 提取库存验证函数"
git commit -m "refactor: 提取折扣计算函数"
git commit -m "refactor: 用卫语句替换嵌套条件"
```

---

## 7. 工具推荐

| 工具 | 用途 | 命令 |
|------|------|------|
| **radon** | 圈复杂度分析 | `uv run radon cc . -a` |
| **ruff** | Lint & Format | `uv run ruff check .` |
| **mypy** | 类型检查 | `uv run mypy .` |
| **pytest** | 测试 | `uv run pytest` |

---

**代码是写给人看的，只是顺便能在机器上运行。**
