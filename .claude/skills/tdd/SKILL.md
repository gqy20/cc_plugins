---
name: tdd
description: 测试驱动开发（TDD）流程助手
user-invocable: true
version: 0.0.4
tags:
  - testing
  - tdd
  - workflow
  - git
  - session
dependencies:
  git: "any"
---

# TDD 编程模式

> **快速反馈是 TDD 的核心**

严格遵循测试驱动开发（Test-Driven Development）流程：红 → 绿 → 重构。

---

## 1. TDD 循环

### 1.1 🔴 红 - 编写失败的测试

```bash
# 只运行新测试
pytest tests/test_new_feature.py -v

# 或关键字过滤
pytest -k "test_new_function" -v
```

**Git**：`git commit -m "test: 添加 xxx 功能的失败测试"`

### 1.2 🟢 绿 - 编写最少代码使测试通过

```bash
# 只运行当前功能测试
pytest tests/test_new_feature.py -v
```

**Git**：`git commit -m "feat: 实现使测试通过的 xxx 功能"`

### 1.3 ♻️ 重构 - 在测试保护下优化代码

```bash
# 运行受影响的模块测试
pytest tests/test_module.py -v
```

**Git**：`git commit -m "refactor: 重构 xxx 功能代码"`

---

## 2. 测试运行策略

| 场景 | 命令 |
|------|------|
| 开发单个功能 | `pytest tests/test_xxx.py` |
| 调试特定测试 | `pytest -k "test_login"` |
| 重跑失败测试 | `pytest --lf` |
| 失败优先 | `pytest --ff` |
| 按类型运行 | `pytest -m unit` |

**提交前验证**：`pytest && uv run ruff check && uv run mypy .`

---

## 3. 测试规范（简述）

| 规范 | 要求 |
|------|------|
| **AAA 模式** | Arrange（准备）→ Act（执行）→ Assert（断言） |
| **命名规范** | `test_<功能>_<条件>_<期望>` |
| **单一职责** | 一个测试一个行为，≤20 行 |
| **测试金字塔** | 单元 70% / 集成 20% / E2E 10% |
| **Mock 规则** | 只隔离外部依赖（API/DB/文件系统） |
| **覆盖率** | 核心 ≥80%，整体 ≥70% |

---

## 4. 性能优化

### 4.1 增量测试

| 技巧 | 命令 |
|------|------|
| 指定文件 | `pytest tests/test_user.py` |
| 关键字过滤 | `pytest -k "login"` |
| Marker 分组 | `pytest -m unit` |
| 并行执行 | `pytest -n auto` |
| 失败重跑 | `pytest --lf` |

### 4.2 加速命令

```bash
pytest -n auto          # 并行执行（需 pytest-xdist）
pytest --lf             # 只运行上次失败的
pytest --ff             # 先运行失败的
pytest -x               # 第一个失败后停止
pytest --durations=10   # 显示最慢的 10 个测试
```

### 4.3 Mock 外部依赖

```python
# ❌ 慢：真实数据库调用
def test_get_user():
    user = db.query(User, 1)  # 慢！
    assert user.name == "Alice"

# ✅ 快：Mock 数据库
def test_get_user(mock_db):
    mock_db.return_value = User(id=1, name="Alice")
    user = get_user(1)
    assert user.name == "Alice"
```

---

## 5. 遗留代码处理

1. 先补充测试（测试先行重构）
2. 运行测试确认通过
3. 再进行修改

```bash
pytest tests/test_legacy.py -v
git commit -m "test: 补充遗留代码的测试"
```

---

## 6. Git 提交规范

| 阶段 | 前缀 | 示例 |
|------|------|------|
| 红（测试） | `test:` | `test: 添加用户登录的失败测试` |
| 绿（实现） | `feat:` | `feat: 实现用户登录功能` |
| 重构 | `refactor:` | `refactor: 优化登录验证逻辑` |
| 修复 | `fix:` | `fix: 修复登录验证 bug` |

---

## 7. 状态报告

### 7.1 手动状态报告

```markdown
## 当前状态
**阶段**：[🔴 红 / 🟢 绿 / ♻️ 重构]

## 测试结果
- 运行：`pytest tests/test_xxx.py`
- 结果：通过/失败

## Git 提交
- `test/feat/refactor: 描述`

## 下一步
继续实现 / 重构 / 提交验证
```

### 7.2 会话状态报告

使用会话模式时，自动追踪状态：

```bash
/tdd --status
```

输出：
```
🔄 TDD 会话（第 3 次迭代）

┌─────────────────────────────────────────┐
│  📊 当前状态                            │
├─────────────────────────────────────────┤
│  阶段：🟢 绿                            │
│  测试：tests/test_auth.py               │
│  结果：❌ FAILED                        │
│  失败：AssertionError                   │
├─────────────────────────────────────────┤
│  📦 Git：2 个 commit                    │
│  🔄 限制：3 / 20 次迭代                 │
└─────────────────────────────────────────┘
```

---

## 8. TDD 会话模式

### 8.1 自动会话

运行 `/tdd` 时自动管理会话，无需额外参数。

首次运行：创建会话文件 `tmp/tdd-session-<timestamp>.json`
后续运行：自动恢复最新会话

### 8.2 会话文件

会话状态保存在 `tmp/tdd-session-<timestamp>.json`：

```json
{
  "session_id": "tdd-20250104-143022",
  "phase": "green",
  "iteration": 3,
  "max_iterations": 20,
  "current_test_file": "tests/test_auth.py",
  "current_test_function": "test_login_success",
  "last_test_result": "FAILED",
  "last_test_output": "tests/test_auth.py:5: AssertionError\nassert login_result.success == True",
  "git_commit_count": 2,
  "start_time": "2025-01-04T14:30:22",
  "last_update": "2025-01-04T14:35:10"
}
```

### 8.3 会话恢复

检测到会话时自动显示：

```
🔄 TDD 会话恢复

┌─────────────────────────────────────────┐
│  📊 会话信息                            │
├─────────────────────────────────────────┤
│  开始时间：2小时前                      │
│  迭代次数：3 次                         │
│  当前阶段：🟢 绿                        │
│  当前测试：tests/test_auth.py          │
│  上次结果：❌ FAILED                    │
├─────────────────────────────────────────┤
│  💬 失败原因：                          │
│  AssertionError: Expected True, got False│
├─────────────────────────────────────────┤
│  📦 Git：2 个 commit                    │
│  🔄 限制：3 / 20 次迭代                 │
└─────────────────────────────────────────┘

继续上次工作...
```

### 8.4 手动管理

```bash
# 取消当前会话
rm tmp/tdd-session-*.json

# 查看所有会话
ls -lh tmp/tdd-session-*.json

# 清理旧会话（>7天）
find tmp/ -name "tdd-session-*.json" -mtime +7 -delete
```

### 8.5 权限处理

如果 `tmp/` 不可写，自动降级：
1. `/tmp/` 目录
2. `$HOME/.cache/claude-code/`

如果都失败，TDD 正常运行但不保存状态。

### 8.6 Git Worktree 支持

文件名包含时间戳，多个 worktree 不会冲突：
```
project/          → tmp/tdd-session-20250104-143022.json
project-feature/  → tmp/tdd-session-20250104-150530.json
```

---

**快速反馈 → 快速迭代 → 高质量代码**
