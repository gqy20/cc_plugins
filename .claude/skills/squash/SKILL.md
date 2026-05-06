---
name: squash
description: Commit 历史整理与合并
user-invocable: true
version: 0.0.2
tags:
  - git
  - rebase
  - commit
  - workflow
dependencies:
  git: "any"
---

# Commit 历史整理

> **TDD 产生的小 commit 应该在功能完成后整理**

将 TDD 循环产生的多个细碎 commit 合并为有意义的功能 commit。

---

## 快捷命令

```bash
/squash              # 交互式引导（自动安全检查）
/squash feature       # 合并单个功能的所有 commit
/squash interactive   # 交互式 rebase
/squash abort         # 中止 rebase
```

**⚠️ 安全警告**：Squash 仅适用于**本地未推送的 commit**。如果 commit 已推送，会重写远程历史，这是危险操作。

---

## 1. 整理策略

### 1.1 TDD Commit 模式

```
单个功能开发过程：
test: 添加 xxx 测试
feat: 实现使测试通过的 xxx
refactor: 提取函数
refactor: 优化逻辑
...
```

**问题**：细碎、中间态、难以审查

### 1.2 推荐策略（方案 B）

| 阶段 | 策略 | 说明 |
|------|------|------|
| **开发中** | 保持小 commit | 便于回滚和调试 |
| **功能完成后** | 合并为 1 个 commit | 有意义的 commit message |
| **推送前整理** | 清理本地历史 | 保持分支干净 |

### 1.3 合并时机

```
✅ 适合合并：
- 功能开发完成
- 本地功能分支
- 准备推送到远程

❌ 不适合合并：
- 已推送到远程共享分支
- 与他人协作的分支
- 公共分支（main/master）
```

---

## 2. 安全检查

### 2.0 强制安全检查

执行 squash 前，**必须**通过以下检查：

#### 检查脚本

```bash
# 检查 1：不在保护分支
PROTECTED_BRANCHES="main master develop"
CURRENT_BRANCH=$(git branch --show-current)
if [[ " $PROTECTED_BRANCHES " =~ " $CURRENT_BRANCH " ]]; then
  echo "❌ 错误：不能在保护分支（$CURRENT_BRANCH）上执行 squash"
  exit 1
fi

# 检查 2：commit 仅在本地
UNPUSHED=$(git log --oneline @{u}.. 2>/dev/null)
if [ -z "$UNPUSHED" ]; then
  echo "❌ 错误：所有 commit 已推送到远程"
  echo "   Squash 会重写远程历史，这是危险操作"
  exit 1
fi

# 检查 3：工作区干净
if [ -n "$(git status --porcelain)" ]; then
  echo "⚠️  警告：工作区有未提交的更改"
  read -p "继续？[y/N] "
  [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1
fi

echo "✅ 安全检查通过"
```

#### 快速检查

| 检查 | 命令 | 安全 | 危险 |
|------|------|------|------|
| 保护分支 | `git branch --show-current` | feature/* | main/master |
| 未推送 | `git log @{u}..` | 有输出 | 无输出 |
| 远程分支 | `git branch -r \| grep $(git branch --show-current)` | 无输出 | 有输出 |

**Golden Rule**：只整理**本地未推送**的 commit。

---

### 2.1 合并前检查

```bash
# 1. 检查分支状态
git status

# 2. 检查是否已推送
git log --oneline @{u}..
# 如果有输出，说明有未推送的 commit（安全）

# 3. 检查远程分支
git branch -r
# 如果分支在远程，不要重写已推送的历史
```

### 2.2 风险信号

| 信号 | 风险等级 | 处理 |
|------|----------|------|
| 已推送到个人远程分支 | 🟡 中 | 可合并，需 force push（与团队确认） |
| 已推送到共享分支 | 🔴 高 | **禁止重写历史** |
| 他人基于此分支工作 | 🔴 高 | **禁止重写历史** |
| 当前是 main/master | 🔴 高 | **禁止任何 rebase** |

**如果已推送**：
1. 不要 squash，直接推送小 commit
2. 或创建新分支重新开发
3. 如必须 squash，先与团队确认

---

## 3. 交互式 Rebase

### 3.1 合并最近 N 个 commit

```bash
# 查看最近 commit
git log --oneline -10

# 合并最近 6 个 commit（1 个功能 = 3~5 个 commit）
git rebase -i HEAD~6

# 或指定起始 commit
git rebase -i <commit-hash>
```

### 3.2 Rebase Todo 命令

| 命令 | 说明 |
|------|------|
| `pick` | 保留此 commit |
| `squash` | 合并到前一个 commit |
| `fixup` | 合并到前一个，丢弃 commit message |
| `drop` | 删除此 commit |
| `reword` | 修改 commit message |
| `edit` | 停在此 commit 修改内容 |

### 3.3 合并示例

**Before**（rebase -i 编辑器）：
```
pick abc1234 test: 添加订单测试
pick def5678 feat: 实现订单功能
pick ghi9012 refactor: 提取验证函数
pick jkl3456 refactor: 优化折扣计算
```

**After**（合并为 1 个）：
```
pick abc1234 test: 添加订单测试
fixup def5678 feat: 实现订单功能
fixup ghi9012 refactor: 提取验证函数
fixup jkl3456 refactor: 优化折扣计算
```

**结果**：保留第一个 commit 的 message，合并其他 commit 的变更

---

## 4. 常见场景

### 4.1 合并单个功能的所有 commit

```bash
# 1. 确定功能起始 commit
git log --oneline -10

# 2. 交互式 rebase
git rebase -i HEAD~4

# 3. 将后续 commit 改为 fixup
# pick abc1234 feat: 实现订单功能
# fixup def5678 refactor: 提取函数
# fixup ghi9012 refactor: 优化逻辑

# 4. 保存退出，Git 自动合并
```

### 4.2 删除调试 commit

```bash
# 1. 交互式 rebase
git rebase -i HEAD~5

# 2. 将调试 commit 改为 drop
# pick abc1234 feat: 实现功能
# drop def5678 debug: 修复测试
# drop ghi9012 debug: 调整逻辑
# pick jkl3456 refactor: 优化代码
```

### 4.3 修改 Commit Message

```bash
# 1. 交互式 rebase
git rebase -i HEAD~3

# 2. 将要修改的 commit 改为 reword
# pick abc1234 feat: 实现功能
# reword def5678 refactor: 优化代码

# 3. 保存后会进入编辑器修改 message
```

### 4.4 快速合并（自动脚本）

```bash
# 方式 A：软重置后重新提交
git reset --soft HEAD~4      # 撤销 4 个 commit，保留变更
git commit -m "feat: 实现完整订单功能"  # 重新提交

# 方式 B：使用 fixup 自动合并
GIT_SEQUENCE_EDITOR="sed -i '2,$s/^pick/fixup/'" git rebase -i HEAD~4
```

---

## 5. 强制推送

### 5.1 推送重写的历史

```bash
# 合并完成后，强制推送到远程
git push --force-with-lease origin feature-branch

# 或使用简写（更危险）
git push -f origin feature-branch
```

### 5.2 Force With Lease

| 命令 | 说明 |
|------|------|
| `--force-with-lease` | **推荐**：如果远程有新提交则失败 |
| `--force` / `-f` | 强制覆盖，可能丢失他人提交 |

---

## 6. 故障恢复

### 6.1 中止 Rebase

```bash
# 在 rebase 过程中放弃
git rebase --abort

# 恢复到 rebase 前的状态
git reflog
git reset --hard HEAD@{N}
```

### 6.2 冲突处理

```bash
# Rebase 过程中遇到冲突
# 1. 解决冲突
# 2. git add <files>
# 3. git rebase --continue
# 4. 重复直到完成

# 放弃 rebase
git rebase --abort
```

---

## 7. 完整示例

### 场景：订单功能完成后整理 commit

**原始 commit 历史**：
```
abc1234 feat: 实现订单创建
def5678 refactor: 提取库存验证
ghi9012 refactor: 提取折扣计算
jkl3456 refactor: 优化订单保存
mno6789 test: 补充订单测试
```

**操作**：
```bash
# 1. 交互式 rebase
git rebase -i HEAD~5

# 2. 编辑为（保留第一个，其他 fixup）
pick abc1234 feat: 实现订单创建
fixup def5678 refactor: 提取库存验证
fixup ghi9012 refactor: 提取折扣计算
fixup jkl3456 refactor: 优化订单保存
fixup mno6789 test: 补充订单测试

# 3. 保存退出，自动合并

# 4. 清理不可达对象（快速）
git gc --prune=now
```

**结果**：
```
abc1234 feat: 实现订单创建
```

---

## 8. 清理空间

Squash 后，原始 commit 变为不可达对象，占用空间。

### 快速清理（推荐）

```bash
git gc --prune=now
```

- **耗时**：几秒到几分钟
- **效果**：删除不可达对象，减小 .git 大小
- **建议**：每次 squash 后运行

### 激进清理（可选）

```bash
git gc --aggressive --prune=now
```

- **耗时**：数分钟到数小时
- **效果**：重新压缩所有对象，最大化减小空间
- **建议**：仅在 .git 过大（>500MB）时使用

---

## 9. 最佳实践

| 原则 | 说明 |
|------|------|
| **本地可以乱** | 开发时保持小 commit |
| **推送前整理** | 合并为有意义的 commit |
| **保护共享分支** | 不要重写已推送的共享历史 |
| **团队约定** | 与团队约定 commit 整理策略 |

### 安全判断（一键检查）

```bash
# 如果这条命令有输出，就是安全的
git log --oneline @{u}..
```

| 检查 | 安全 | 危险 |
|------|------|------|
| `git log @{u}..` | 有输出 | 无输出 |
| `git branch --show-current` | feature/* | main/master |

**如果已推送**：不要 squash，直接推送或创建新分支。

---

**小 commit 开发 → 整理后推送 → 干净的历史**
