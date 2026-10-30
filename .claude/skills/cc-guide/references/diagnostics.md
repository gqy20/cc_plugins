# 诊断 runbook —— 症状 → 命令 → 动作

> 完整版（诊断方法论 + 三层证据源 + 本仓库踩过的 6 个坑）见
> [`docs/cc-guide/07-排错手册.md`](../../../../docs/cc-guide/07-排错手册.md)。
> **本文件只留可直接执行的部分** —— 叙述一律回指 07 章，不在这里另抄一份。

## 起手式：拿到日志

```bash
claude --debug -p "回复 OK 两个字即可"        # 1) 起最小会话，留启动日志
LOG=$(ls -t ~/.claude/debug/*.txt | head -1)   # 2) 找最新日志
grep -iE "skill|agent|plugin" "$LOG"          # 3) 按症状 grep
```

更多开关：`--debug --verbose`（更啰嗦）、`--debug <插件名>`（只看某个插件）、
`--debug-file <path>`（日志直接写到文件）。
完整说明见 07 章「标准诊断流程」。

## 日志关键字速查表

| 症状 | grep 关键字 | 含义 |
|------|------------|------|
| skill 没被加载 | `Loaded [0-9]+ unique skills` | 数字比预期少 |
| skill 清单超预算 | `Skill listing over budget` | description 被截断，后面的 skill Claude 根本不知道 |
| frontmatter 解析失败 | `Failed to parse YAML frontmatter` | 该文件被**静默忽略** |
| 字段名不认识 | `does not recognize or apply` | 字段拼错了 |
| 插件 skill 为 0 | `Loaded 0 skills from plugin` | 布局不对，或缓存跟的是**远端**旧版本 |
| 插件整体没加载 | `not cached at` / `plugin-cache-miss` | 市场副本过期 |
| 权限规则不生效 | `Permission deny rule` | 写成了 `Write(...)`，只有 `Edit(...)` 会被匹配（见 07 坑 4） |
| 沙箱相关 | `sandbox` | 原生 Windows 上没有沙箱 |

## 常见症状 → 具体动作

### skill / agent 没生效

```bash
claude --debug -p "hi" 2>&1 | grep -i "failed to parse"
```

frontmatter 的两条铁律：

```yaml
# ✘ 两个相邻的流式序列 → Unexpected token
argument-hint: [topic] [parallel]
# ✔ 加引号
argument-hint: "[topic] [parallel]"

# ✘ 纯标量里含 ": " → Unexpected token
description: 编写代码时: 遵循 Python 之禅
# ✔ 整句加引号
description: "编写代码时: 遵循 Python 之禅"
# ✔✔ 多行文本用块标量（推荐）
description: |
  编写代码时遵循 Python 之禅：
  优先可读性，其次简洁性。
```

**一条规律：frontmatter 里的多行文本一律用 `|` 块标量。**

### 插件内容没更新

```bash
git push                                      # 缓存同步的是远端版本，先 push
claude plugin update --all                     # 重新复制到缓存
claude --plugin-dir ./plugins/<name>           # 或就地加载（调试首选，不经缓存）
```

### 插件整体不加载

```bash
claude plugin marketplace update <name>
```

检查市场副本有多旧：

```bash
python -c "
import json,pathlib
d=json.loads((pathlib.Path.home()/'.claude/plugins/known_marketplaces.json').read_text('utf-8'))
for k,v in d.items(): print(k, v.get('lastUpdated'))
"
```

### 权限规则不生效

启动时 Claude Code 会打印告警，原文形如：

```text
Permission deny rule (.claude\settings.json): Write(.env*) is not matched by
file permission checks — only Edit(path) rules are.
```

| 写法 | 是否被文件权限检查匹配 |
|------|------------------------|
| `Write(.env*)` | ❌ **不匹配**（启动时告警） |
| `Edit(.env*)` | ✅ 匹配，覆盖所有文件编辑类工具 |

注意：Bash 仍能绕过（`Bash(echo "SECRET=x" > .env)`）——
权限规则按**工具名**匹配，不按**副作用**匹配。真要封禁得靠沙箱的 `filesystem.denyWrite`，
而**原生 Windows 没有沙箱**。

### 上下文很贵

```bash
uv run --with pyyaml python scripts/measure_context.py
/skills        # 停用当前项目用不到的 skill
/skill-doctor  # 官方报告：哪些 skill 从没被调用过、各占多少上下文
/context       # 运行时视角的上下文分解
```

### 想知道插件花了多少

```bash
claude plugin details <插件名>
```

### 快捷键行为对不上文档

```bash
uv run python scripts/extract_keybindings.py --context Chat
```

出厂绑定以二进制为准，文档会过时。

### 想知道最近的 release 说了什么

```bash
uv run python scripts/extract_changelog.py --since 2.1.305
uv run python scripts/extract_changelog.py --grep queue
```

## 本仓库的体检脚本

| 脚本 | 查什么 |
|------|--------|
| `scripts/measure_context.py` | 常驻上下文成本 + frontmatter 体检 |
| `scripts/extract_keybindings.py` | 出厂键位表（`--context Chat` / `--json`） |
| `scripts/extract_changelog.py` | 内嵌 CHANGELOG（`--since` / `--grep`） |
| `scripts/validate_skills.py` | 全仓库 skill/agent frontmatter 合规性 |
| `scripts/check_skill_links.py` | skill 里指向 cc-guide 的链接与锚点是否还有效 |
| `scripts/check_doc_numbers.py` | 文档里写死的 CLAUDE.md 尺寸数字是否与文件一致 |
| `.github/scripts/check_references.py` | Markdown 里引用的文件是否存在 |
| `.github/scripts/check_mcp_dependencies.py` | MCP 依赖是否声明齐全 |
| `.github/scripts/validate_content.py <plugin>` | 插件内容质量 |
