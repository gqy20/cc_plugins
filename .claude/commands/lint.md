---
name: lint
description: 代码质量检查工具集
version: 0.0.1
tags: lint, quality, check
dependencies: {}
---

# Lint 代码检查

快速检查代码质量。

## 支持的语言

| 语言 | 工具 | 命令 |
|------|------|------|
| Shell | shellcheck | `shellcheck file.sh` |
| YAML | yamllint | `yamllint file.yaml` |
| Python | ruff | `ruff check file.py` |
| Python | mypy | `mypy file.py` |
| JS/TS | eslint | `eslint file.js` |
| Markdown | markdownlint | `markdownlint file.md` |
| Git | gitlint | `gitlint` |

## 快捷命令

```bash
/lint              # 自动检测并检查
/lint shell        # 检查 Shell 脚本
/lint yaml         # 检查 YAML 文件
/lint python       # 检查 Python 代码
/lint js           # 检查 JavaScript/TypeScript
/lint all          # 检查所有
```

---

## Shell

```bash
# 安装
sudo apt install shellcheck

# 检查
shellcheck script.sh
```

**常见问题**：
- 未引用的变量 → `use "$var"`
- 未处理的错误 → `set -e`
- 可移植性 → `#!/bin/bash` vs `#!/bin/sh`

---

## YAML

```bash
# 安装
pip install yamllint

# 检查
yamllint file.yaml
```

**常见问题**：
- 缩进不一致 → 统一用 2 空格
- 行尾空格 → 删除
- 过长行 → 拆分

---

## Python

```bash
# 安装
pip install ruff mypy

# 检查
ruff check file.py
mypy file.py
```

**ruff**: 代码风格、潜在问题
**mypy**: 类型检查

**常见问题**：
- 未使用导入 → 删除
- 类型缺失 → 添加类型注解
- 命名不规范 → 遵循 PEP 8

---

## JavaScript/TypeScript

```bash
# 安装
npm install -g eslint

# 检查
eslint file.js
```

---

## Markdown

```bash
# 安装
npm install -g markdownlint-cli

# 检查
markdownlint file.md
```

---

## Git Commit

```bash
# 安装
pip install gitlint

# 检查最近的 commit
gitlint
```

---

## 批量检查

```bash
# 所有 Shell 文件
find . -name "*.sh" -exec shellcheck {} \;

# 所有 Python 文件
ruff check .

# 所有 YAML 文件
find . -name "*.yaml" -o -name "*.yml" | xargs yamllint
```

---

## 配置文件

在项目根目录创建配置：

**Shell**: `.shellcheckrc`
**YAML**: `.yamllint`
**Python**: `ruff.toml` / `pyproject.toml`
**ESLint**: `.eslintrc.json`

---

**先检查，再提交。**
