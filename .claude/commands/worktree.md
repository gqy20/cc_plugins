---
name: worktree
description: Git Worktree 工作流 - PR Review、并行开发、完整开发生命周期
version: 0.0.1
tags:
  - git
  - worktree
  - github
  - workflow
  - parallel
dependencies:
  git: "2.19+"
  gh: "any"
---

# Git Worktree 工作流

> **不切换分支，并行处理多个任务**

---

## 工作流 1: PR Review

**场景**: 收到 PR 通知，需要本地审查代码

### 步骤

#### 1. 创建 worktree 检出 PR

```bash
# 方式 A: 使用 gh（推荐）
gh pr checkout 123 --branch ../pr-123

# 方式 B: 手动创建
git worktree add ../pr-123 origin/pr/123
```

#### 2. 进入 worktree 运行测试

```bash
cd ../pr-123
npm install  # 或依赖安装命令
npm test     # 或 pytest, make test 等
```

#### 3. 审查代码

```bash
# 查看变更
git log main..HEAD

# 使用 gh 查看文件变更
gh pr diff 123
```

#### 4. 提交评论或批准

```bash
# 在主仓库目录执行
cd -
gh pr review 123 --approve              # 批准
# 或
gh pr review 123 --comment -m "建议..."  # 评论
```

#### 5. 删除 worktree

```bash
git worktree remove ../pr-123
```

---

## 工作流 2: 并行多 Feature 开发

**场景**: 同时负责 feature-A、feature-B、feature-C，需要在不同上下文间切换

### 步骤

#### 1. 为每个 feature 创建 worktree

```bash
# 主仓库在 /project
cd /project

# 创建 feature-A
git worktree add -b feature/A ../feature-A main

# 创建 feature-B
git worktree add -b feature/B ../feature-B main

# 创建 feature-C
git worktree add -b feature/C ../feature-C main
```

#### 2. 查看所有 worktree

```bash
git worktree list

# 输出示例：
# /project                         main           [主工作树]
# /project/../feature-A          feature/A      [附属]
# /project/../feature-B          feature/B      [附属]
# /project/../feature-C          feature/C      [附属]
```

#### 3. 在不同 worktree 间工作

```bash
# 在 feature-A 工作
cd ../feature-A
# ... 开发、测试、提交 ...

# 切换到 feature-B（无需 stash 或 commit）
cd ../feature-B
# ... 开发、测试、提交 ...
```

#### 4. 每个 worktree 独立推送

```bash
# 在 feature-A
cd ../feature-A
git push origin feature/A
gh pr create --title "Feature A" --body "实现..."
```

```bash
# 在 feature-B
cd ../feature-B
git push origin feature/B
gh pr create --title "Feature B" --body "实现..."
```

#### 5. PR 合并后清理对应 worktree

```bash
# feature-A 合并后
git worktree remove ../feature-A
git branch -d feature/A
```

---

## 工作流 3: Issue → Branch → PR → Review → Merge

**场景**: 完整的开发生命周期，从 Issue 到合并

### 步骤

#### 1. 从 Issue 创建分支 worktree

```bash
# 获取 issue 信息
gh issue view 456 --json title

# 创建分支及 worktree
git worktree add -b "fix/issue-456-bug-fix" ../fix-456 main
```

#### 2. 开发与测试

```bash
cd ../fix-456

# 开发工作（可结合 /tdd）
# ... 编写代码、测试 ...

# 提交
git add .
git commit -m "fix: resolve issue-456"
```

#### 3. 推送并创建 PR

```bash
git push origin fix/issue-456-bug-fix

# 关联 issue 创建 PR
gh pr create --title "Fix: issue-456" --body "Closes #456"
```

#### 4. Review 流程

此时进入 **工作流 1 (PR Review)** 的反向视角：

- 其他人审查你的 PR
- 收到 feedback 后，直接在 `../fix-456` 修改
- 推送更新

#### 5. 合并后清理

```bash
# PR 合并后
cd -  # 回到主仓库
git worktree remove ../fix-456
git branch -d fix/issue-456-bug-fix

# 拉取最新 main
git pull
```

---

## 清理与维护

### 定期清理策略

#### 1. 列出所有 worktree

```bash
git worktree list
```

#### 2. 删除已完成的 worktree

```bash
git worktree remove ../worktree-path
git branch -d branch-name
```

#### 3. 清理无效引用

```bash
# 如果 worktree 目录被手动删除，运行：
git worktree prune
```

#### 4. 批量清理脚本

```bash
# 删除所有已合并分支的 worktree
for wt in $(git worktree list | grep -o '../[^ ]*' | grep -v '^..$'); do
    branch=$(git worktree list | grep "$wt" | awk '{print $3}' | sed 's/[\[\]]//g')
    if git branch --merged main | grep -q "$branch"; then
        git worktree remove "$wt"
        git branch -d "$branch"
    fi
done
```

---

## 与现有命令协同

| 工作流 | 协同命令 |
|--------|---------|
| PR Review | `/worktree` → `/gh` (评论/批准) |
| 并行 Feature | `/worktree` + `/tdd` (每个 worktree 独立 TDD) |
| 完整开发 | `/sdr` (规格) → `/worktree` (开发) → `/gh` (PR) |

---

## 常见问题

### Q: push 时冲突？
```bash
# 在 worktree 中
git pull --rebase
# 解决冲突后
git push
```

### Q: worktree 路径管理？
建议放在主仓库同级目录：
```
~/workspace/
├── project/          # 主仓库
├── feature-A/        # worktree
├── feature-B/        # worktree
└── pr-123/           # worktree
```

### Q: 多少个 worktree 合适？
- 日常 2-3 个
- 超过 5 个考虑清理旧分支
