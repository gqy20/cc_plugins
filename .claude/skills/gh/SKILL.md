---
name: gh
description: GitHub CLI 专家助手，提供 gh 命令的场景化指导
user-invocable: true
version: 0.0.2
tags:
  - git
  - github
  - cli
  - devops
  - workflow
dependencies:
  gh: ">=2.0"
  git: "any"
---

# GitHub CLI 场景化助手

你是 GitHub CLI (gh) 的专家助手。请根据用户需求，引导完成 GitHub 相关操作。

---

## 前置检查

**执行任何操作前：**
1. 确认是否在 git 仓库：`git rev-parse --is-inside-work-tree`
2. 确认 gh 是否已登录：`gh auth status`
3. 如未登录执行：`gh auth login`
4. 获取当前 owner/repo：`gh repo view --json owner,name -q '.owner.login + "/" + .name'`

---

## 📊 仪表盘

```bash
gh status                                                      # 查看综合状态（issues/PRs/通知）
gh repo view                                                   # 查看当前仓库信息
gh repo view --json name,description,visibility,defaultBranchRef,owner,issues  # JSON 格式查看（使用 issues.totalCount 获取 issue 数量）
gh browse                                                      # 打开仓库主页
gh browse issues                                               # 打开 Issues 页面
gh browse pulls                                                # 打开 PRs 页面
gh browse actions                                              # 打开 Actions 页面
```

---

## 🔍 搜索与查询

```bash
# Issues 搜索
gh search issues --state open --limit 20                       # 基础搜索
gh search issues --label "bug,high-priority"                   # 按标签搜索
gh search issues --author <username>                           # 按作者搜索
gh issue list --state open --limit 20                          # 当前仓库搜索
gh issue list --state all --assignee @me                       # 我的 issues
# PRs 搜索
gh search prs --state open --limit 20                          # 基础搜索
gh search prs --reviewer <username>                            # 按审查者搜索
gh search prs --state merged --limit 20                        # 已合并 PR
gh pr list --state open --limit 20                             # 当前仓库 PR
gh pr list --author @me                                        # 我创建的 PR
gh pr list --reviewer @me                                      # 需要我审查的 PR
# 仓库搜索
gh search repos --language <language> --stars ">100"           # 按语言/星标搜索
gh search repos --topic "machine-learning"                     # 按主题搜索
gh search repos --org <organization>                           # 按组织搜索
# 查看详情
gh issue view <number>                                         # Issue 详情
gh issue view <number> --json title,body,state,labels,author   # Issue JSON 详情
gh pr view <number>                                            # PR 详情
gh pr view <number> --json title,body,state,author,reviewDecision,additions,deletions  # PR JSON 详情
gh pr diff <number>                                            # PR Diff
gh pr view <number> --json files --jq '.files[].path'         # PR 文件变更
gh pr view <number> --comments                                 # PR 评论
gh pr view <number> --json reviews --jq '.reviews[] | {author, state, body}'  # PR 审查
```

---

## 📝 Issue 管理

```bash
# 创建 Issue
gh issue create                                               # 交互式创建
gh issue create --title "标题" --body "描述"                   # 简单单行
gh issue create --web                                         # 浏览器创建
gh issue create -F issue.md                                  # 从文件读取
cat <<EOF | gh issue create --title "标题" -F -               # 多行 body
## 功能描述

详细描述...
EOF

# 编辑 Issue
gh issue edit <number> --title "新标题"                        # 修改标题/标签/指派
gh issue edit <number> --add-label "bug,urgent"
gh issue close <number>                                        # 关闭
gh issue reopen <number>                                       # 重新打开
```

---

## 🔀 Pull Request 管理

```bash
# 创建 PR
gh pr create                                                   # 交互式创建
gh pr create --base develop --title "功能" --body "描述"        # 指定 base
gh pr create --draft                                          # Draft PR
cat <<EOF | gh pr create --title "标题" -F -                   # 多行 body
## 变更说明
详细描述...
EOF

# 查看 PR
gh pr list --state open                                       # 列出 PR
gh pr view 123                                                 # 查看详情
gh pr diff 123                                                 # 查看变更
gh pr checks 123                                               # 检查状态

# 更新 PR
gh pr edit 123 --title "新标题"                               # 修改标题/标签/审查者
gh pr update 123                                               # 更新 base 分支

# 审查与合并
gh pr review 123 --approve                                     # 批准
gh pr review 123 --request-changes                             # 请求更改
gh pr merge 123 --squash                                       # 合并
```

---

## 🏷️ Labels / Milestones / Projects

```bash
# Labels
gh label list                                                  # 列出标签
gh label create "bug" --color "d73a4a"                         # 创建标签

# Milestones
gh api repos/:owner/:repo/milestones -f title="v1.0.0"        # 创建里程碑

# Projects
gh project list --owner @me                                   # 列出项目（需 gh auth refresh -s project）
```

---

## 🚀 Actions & CI/CD

```bash
# Workflows
gh workflow list                                               # 列出 workflows
gh workflow view <name> --yaml                                # 查看 workflow YAML

# Runs
gh run list --limit 20                                        # 列出运行
gh run view <run_id> --log                                   # 查看日志
gh run watch <run_id>                                        # 实时查看
gh run rerun <run_id>                                        # 重新运行

# Caches
gh cache list                                                 # 列出缓存
gh cache delete --all                                         # 删除所有缓存
```

---

## 🔐 Secrets / Variables

```bash
# Secrets
gh secret list                                                 # 列出 secrets
gh secret set MY_SECRET                                        # 设置 secret
echo -n "value" | gh secret set MY_SECRET                      # 从环境变量

# 组织/环境 Secrets
gh secret list --org <organization>                           # 组织 secrets
gh secret set ENV_SECRET --env <environment_name>             # 环境秘密

# Variables
gh variable list                                               # 列出变量
gh variable set MY_VAR --body "value"                          # 设置变量
```

---

## 💻 Codespaces

```bash
# 创建
gh codespace create                                            # 创建
gh codespace create --machine "premiumLinux"                   # 指定机器

# 管理
gh codespace list                                              # 列出
gh codespace stop <name>                                       # 停止
gh codespace ssh <name>                                        # SSH 连接
gh codespace delete <name>                                     # 删除
```

---

## 📦 Release 管理

```bash
gh release create v1.0.0 --notes "第一个版本"                    # 创建
gh release create v1.0.0 --notes-file RELEASE_NOTES.md            # 从文件
gh release create v1.0.0 --draft                               # Draft
gh release list                                                # 列出
gh release download v1.0.0                                     # 下载
```

---

## 🏠 仓库管理

```bash
gh repo create my-repo --public                                # 创建
gh repo fork owner/repo                                       # Fork
gh repo clone owner/repo                                       # 克隆
gh repo view                                                   # 查看
gh repo edit --description "描述"                              # 编辑
gh repo delete --yes                                           # 删除
```

---

## 🗝️ 认证与密钥

```bash
# 登录/登出
gh auth login                                                  # 登录
gh auth logout                                                 # 登出
gh auth status                                                 # 查看状态
# SSH Keys
gh ssh-key list                                                # 列出 SSH keys
gh ssh-key add ~/.ssh/id_ed25519.pub --title "我的电脑"         # 添加 SSH key
gh ssh-key delete <key_id>                                     # 删除 SSH key
# GPG Keys
gh gpg-key list                                                # 列出 GPG keys
cat ~/.ssh/id_ed25519.pub | gh gpg-key add -                   # 添加 GPG key
gh gpg-key delete <key_id>                                     # 删除 GPG key
```

---

## 🏢 组织管理

```bash
gh org list                                                    # 列出组织
gh org view <organization>                                     # 查看组织详情
gh repo list <organization> --limit 50                         # 列出组织仓库
gh api orgs/<organization>/members --jq '.[].login'            # 列出组织成员
```

---

## 📦 Gists 管理

```bash
echo "代码" | gh gist create                                   # 创建 gist
gh gist create file.py --public --desc "Python 示例"           # 公开 gist
gh gist create file1.py file2.js --desc "多文件"                # 多文件 gist
gh gist list --limit 20                                        # 列出 gists
gh gist view <gist_id>                                         # 查看 gist
gh gist edit <gist_id> --file new_file.py                      # 编辑 gist
gh gist delete <gist_id>                                       # 删除 gist
```

---

## 🛠️ 高级功能（API）

```bash
# API 基础
gh api /user                                                   # GET 请求
gh api /repos/:owner/:repo/issues -f title="标题" -f body="内容"  # POST 请求
gh api /repos/:owner/:repo/issues/:number -X PATCH -f state="closed"  # PATCH 请求
gh api /repos/:owner/:repo/issues/:number -X DELETE            # DELETE 请求
gh api /repos/:owner/:repo/issues -f title="..." -f body='{"labels":["bug"]}' -H "Accept: application/vnd.github.v3+json"  # JSON body
gh api /user/repos --jq '.[].name'                            # jq 过滤
gh api /user/repos --paginate --jq '.[].full_name'            # 分页请求
# API 高级用法
gh api repos/:owner/:repo/pulls --paginate --jq '.[].title'   # 获取所有 PR 标题
gh api repos/:owner/:repo/issues -f title="..." -F labels[]=bug -F labels[]=urgent -F assignees[]=user1  # 复杂字段 issue
gh api repos/:owner/:repo -X PATCH -f allow_auto_merge=true -f delete_branch_on_merge=true  # 自动合并设置
gh api repos/:owner/:repo/branches/main/protection -X PUT -H "Accept: application/vnd.github.v3+json" -f required_pull_request_reviews='{"required_approving_review_count":1}' -f enforce_admins=true  # 分支保护
gh api repos/:owner/:repo/hooks --jq '.[].name'               # 查看 Webhooks
gh api repos/:owner/:repo/hooks -f name="web" -f active=true -f config='{"url":"https://example.com/webhook"}'  # 创建 webhook
# 别名
gh alias set prs 'pr list --state open --limit 20'             # 创建别名
gh alias set mine 'issue list --assignee @me'
gh alias set co 'pr checkout'
gh alias list                                                  # 查看别名
gh alias delete prs                                             # 删除别名
# 配置
gh config                                                      # 查看配置
gh config set git_protocol ssh                                 # 设置协议
gh config set editor vim                                       # 设置编辑器
gh config set prompt disabled                                  # 禁用提示
gh config get git_protocol                                     # 获取配置
# 扩展
gh extension search                                            # 搜索扩展
gh extension install owner/extension-repo                       # 安装扩展
gh extension list                                              # 列出已安装
gh extension upgrade <name>                                    # 升级扩展
gh extension remove <name>                                     # 删除扩展
```

---

## 常见工作流

```bash
# 新功能开发
git checkout -b feature/new-feature && git add . && git commit -m "feat: 添加新功能" && git push -u origin feature/new-feature && gh pr create --title "添加新功能" --body "..." --base main
# Bug 修复
git checkout -b fix/bug-123 && git commit -m "fix: 修复 #123" && git push -u origin fix/bug-123 && gh pr create --title "修复 #123" --body "Fixes #123"
# 批量关闭已解决 issues
gh issue list --label "resolved" --json number --jq '.[].number' | xargs -I {} gh issue close {} --comment "已在 v1.2.0 中解决"
# 批量添加标签
gh issue list --state open --json number --jq '.[].number' | xargs -I {} gh issue edit {} --add-label "triaged"
```

---

## 注意事项

1. **占位符**：`:owner`、`:repo`、`<number>` 等需替换为实际值
2. **权限**：某些操作需要相应仓库权限
3. **速率限制**：API 请求有速率限制
4. **危险操作**：删除/合并前务必确认
5. **--help**：任何命令可加 `--help` 查看详情
6. **多行 body**：避免使用 `--body "$(cat <<EOF...EOF)"`，推荐方法：
   - 交互式：`gh issue create`（不提供 --body）
   - 文件：`gh issue create -F issue.md`
   - Stdin：`cat <<EOF | gh issue create -F -`
   - 浏览器：`gh issue create --web`

---

## 常见问题排查

### 权限相关
```bash
# 检查当前权限
gh auth status

# 添加缺少的 scope（如 project）
gh auth refresh -s project

# 添加多个 scope
gh auth refresh -s project:write,read:org

# Fine-grained token 问题：需要特定权限
# Organization 相关操作需要 "Organization members" 权限
```

### 仓库默认设置
```bash
# 报错：No default remote repository
gh repo set-default                                          # 设置默认仓库
gh repo set-default -u                                       # 取消默认设置

# 或者直接指定仓库
gh issue list --repo owner/repo
```

### Git 配置冲突
```bash
# gh auth login 后 git push 仍失败
# 检查 git credential 配置
git config --list | grep credential

# 重置为 gh 管理
git config --global credential.helper # 清空
gh auth setup-git                                            # 重新配置
```

### Token 问题
```bash
# 查看当前 token scopes
gh auth status

# Token 过期或权限不足
gh auth logout && gh auth login                              # 重新登录

# 手动设置 token（使用 GH_TOKEN 环境变量）
export GH_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

### 网络问题
```bash
# 连接超时/代理问题
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890

# 或配置 git 代理
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890
```

### API 字段问题
```bash
# 错误：openIssuesCount 不是顶层字段
gh repo view --json openIssuesCount

# 正确：使用嵌套的 issues 对象
gh repo view --json issues --jq '.issues.totalCount'

# 类似地，PR 统计使用 pullRequests.totalCount
gh repo view --json pullRequests --jq '.pullRequests.totalCount'

# 一起获取多个统计
gh repo view --json issues,pullRequests,watchers,stargazerCount --jq '
  "Issues: \(.issues.totalCount)",
  "PRs: \(.pullRequests.totalCount)",
  "Stars: \(.stargazerCount)",
  "Watchers: \(.watchers.totalCount)"
'
```

### 常见错误码
| 错误 | 原因 | 解决方案 |
|-----|------|---------|
| `HTTP 403` | 权限不足/速率限制 | `gh auth status` 或等待后重试 |
| `HTTP 404` | 资源不存在/仓库名错误 | 检查 owner/repo 是否正确 |
| `unauthenticated` | Token 过期 | `gh auth login` |
| `No default remote` | 未设置默认仓库 | `gh repo set-default` 或 `--repo` 参数 |
| `Too many requests` | API 速率限制 | 等待一分钟后重试 |
| `Unknown JSON field` | 字段名错误或不存在 | 使用 `--json name,description` 查看可用字段 |

---

## GitHub MCP vs gh CLI

| 维度 | gh CLI | GitHub MCP |
|------|--------|------------|
| **速度** | ~1.0s | ~0.8-1.2s（接近） |
| **输出格式** | JSON 字符串（需 jq 解析） | 结构化对象（直接可用） |
| **稳定性** | 中（API 变化需升级 gh） | 高（工具接口稳定） |
| **学习曲线** | 陡峭（记忆 `--json`/`--jq` 参数） | 平缓（LLM 友好） |

**使用建议**：
- **批量操作**、**脚本自动化** → gh CLI
- **单次查询**、**LLM 协同** → GitHub MCP
