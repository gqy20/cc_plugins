---
name: taste-analyzer
description: 分析 Python 项目的代码品位 — 6 维度评分（极简度/一致性/可读性/防御性/工程化/Agent Engineering），输出诊断 + 处方 + SVG 雷达图报告
user-invocable: true
version: 0.1.0
tags: [code-quality, taste, analysis, python, agent, radar-chart]
argument-hint: <项目路径>
---

# Taste Analyzer — Python 项目代码品位分析

**目标**：分析 `$1` 指向的 Python 项目，输出 6 维度评分 + 诊断 + 处方 + 雷达图报告。

---

## 工作流

> **脚本位置**：所有命令基于 `taste-analyzer` console script（在 PATH 中）。分发只需打包整个 `taste-analyzer/` 目录，使用方 `uv tool install` 即可。

### 安装（一次性）

```bash
cd taste-analyzer/                         # skill 根目录
uv tool install . --reinstall \
    --with pyscn --with radon --with vulture --with mypy --with ruff
```

完成后 `taste-analyzer` 在 `~/.local/bin/`，任意目录可调。

### 阶段 1 · 数据采集

```bash
# 推荐：用 console script（任意目录）
taste-analyzer collect <项目路径>

# 等价：直接调脚本（仅限 skill 内）
python scripts/analyze.py collect <项目路径>
```

输出到 stdout 的 JSON 结构（**这是契约，硬性**）：

```json
{
  "project": {"path": "...", "name": "...", "is_agent_project": true|false},
  "complexity": {"mean_cc": 4.2, "p95_cc": 12, "max_cc": 28, "hotspots": [{"file": "...", "cc": 28}]},
  "dead_code": {"count": 12, "samples": [{"file": "...", "line": 42, "name": "..."}]},
  "clones": {"type1": 3, "type2": 1, "type3": 0, "samples": [{"file_a": "...", "file_b": "..."}]},
  "coupling": {"cbo_top": [{"module": "...", "cbo": 18}], "cycles": []},
  "lint": {"violations": 47, "by_rule": {"E501": 12, "F401": 8}},
  "types": {"coverage_pct": 73.5, "errors": 14, "mypy_strict": false},
  "git": {"commits": 234, "contributors": 5, "conventional_pct": 78, "has_lockfile": true},
  "repo": {"has_ci": true, "has_tests": true, "test_ratio": 0.42, "readme_lines": 187},
  "agent": {
    "has_claude_dir": true,
    "has_mcp_config": false,
    "has_claude_sdk": true,
    "cli_json_flags": 4,
    "write_protection": true,
    "state_persistence": true,
    "dashboard": false
  }
}
```

> **缺字段处理**：标 `"insufficient_data"`，绝不编造。

### 阶段 2 · Claude 解读（**主 prompt 在下方**）

拿到 JSON 后，按下面 6 维度评分 prompt 写解读，最后生成完整报告 markdown。

### 阶段 3 · 报告渲染

```bash
taste-analyzer render \
    --data <阶段1的 JSON> \
    --report <Claude 写的 markdown> \
    --out report.md
```

脚本会注入 SVG 雷达图到报告顶部。

---

## 6 维度评分定义

每个维度 0-5 分，**必须基于 JSON 证据**，不可凭感觉。

### 1. 极简度 (Minimalism)

**问题**：这个项目"杀伐果断"吗？

| 分 | 标志 |
|----|------|
| 5 | 函数平均行 < 15, CC < 5, 无 FactoryOfFactory |
| 4 | 平均行 < 25, CC < 8, 抽象层次 ≤ 2 层 |
| 3 | 平均行 < 40, CC < 12 |
| 2 | 平均行 < 60, CC < 20, 偶尔有过度设计 |
| 1 | 平均行 ≥ 60 或 CC ≥ 20, 普遍过度抽象 |
| 0 | 抽象爆炸, 一个 PR 引入 3+ 抽象层 |

**证据来源**：`complexity.mean_cc` / `complexity.max_cc` / AST 统计函数平均行

### 2. 一致性 (Consistency)

**问题**：风格是否一以贯之？

| 分 | 标志 |
|----|------|
| 5 | ruff 0 violations, 命名 100% 统一 |
| 4 | ruff < 5 violations, 命名 95%+ 统一 |
| 3 | ruff 5-30 violations |
| 2 | ruff 30-100, 命名变体 3+ 种混用 |
| 1 | ruff > 100, 风格反复横跳 |
| 0 | 完全无规则可言 |

**证据来源**：`lint.violations` / `lint.by_rule` / 命名模式分析

### 3. 可读性 (Readability)

**问题**：写给"未来的自己"还是"机器"？

| 分 | 标志 |
|----|------|
| 5 | docstring > 80%, 变量名 > 12 字符, 嵌套深度 ≤ 2 |
| 4 | docstring > 60%, 变量名 > 10 |
| 3 | docstring > 40%, 变量名 > 8 |
| 2 | docstring < 40%, 大量缩写 |
| 1 | docstring < 20%, 单字母变量普遍 |
| 0 | 故意混淆 |

**证据来源**：AST 遍历 + docstring regex（脚本采）

### 4. 防御性 (Defensiveness)

**问题**："信任"还是"边界检查"？

| 分 | 标志 |
|----|------|
| 5 | mypy --strict 0 错, 错误类型具体 |
| 4 | mypy --strict 0 错（默认有警告） |
| 3 | mypy 默认 0 错 |
| 2 | 部分函数有类型 |
| 1 | 类型注解 < 30% |
| 0 | 完全无类型, bare except 普遍 |

**证据来源**：`types.coverage_pct` / `types.errors` / bare except 检测

### 5. 工程化 (Engineering)

**问题**：流程是否到位？

| 分 | 标志 |
|----|------|
| 5 | 锁文件 + CI + 90% 测试 + conventional commits + pre-commit |
| 4 | 锁文件 + CI + 测试 + 规范 commit |
| 3 | CI 存在 + 基础测试 |
| 2 | 只有 README, 无 CI |
| 1 | git 仓库 + 零配置 |
| 0 | 没有 README |

**证据来源**：`git.has_lockfile` / `repo.has_ci` / `git.conventional_pct`

### 6. Agent Engineering（智能体工程能力）— **可选**

**触发条件**：项目满足任一 agent 特征（`.claude/`、`agents/`、`mcp.json`、Claude SDK import、项目名/描述含 "agent"）。

**问题**：对 Claude Agent SDK / LLM 协作能力的**利用深度**？

| 分 | 含义 | 典型代表 |
|----|------|---------|
| 5 | **Agent-native 旗舰**：CLI 为 AI 设计 + skill 暴露 + MCP + 安全防护 + 多 agent | zotero_cli |
| 4 | **主力能力全用上**：SDK + MCP + skills + 错误防护 | biotools_agent, IssueLab |
| 3 | **SDK 做核心，其他维度缺失**：用 SDK 工作流但无 skill/mcp | cc-insights |
| 2 | **轻量 SDK 使用**：包装 Claude API 但缺工程化 | 多数 LLM wrapper |
| 1 | **直接调 API**：没用 SDK | 普通 LLM 项目 |
| 0 / N/A | **非 Agent 项目** | n/a |

**证据来源**：`agent.*` 字段 + CLI 子命令扫描

---

## 🎯 主解读 Prompt（Claude 必读）

你是**代码品位分析师**。输入是上面 schema 的 JSON，输出是 Markdown 报告片段。

### 输出结构（强制）

```markdown
## 维度评分

- **极简度**: X/5 [一句话] 证据: ...
- **一致性**: X/5 [一句话] 证据: ...
- **可读性**: X/5 [一句话] 证据: ...
- **防御性**: X/5 [一句话] 证据: ...
- **工程化**: X/5 [一句话] 证据: ...
- **Agent Engineering**: X/5 或 N/A [一句话] 证据: ...

## 哲学命名

[1-3 个标签] — [一句总评]

雷达图形状 → 哲学映射：
- 高 Agent + 高极简 + 高一致性 → "Agent-native 现代派"
- 高 1+2, 中 4, 低 3+5 → "学院派"
- 高 5, 中 1, 低 4 → "大厂派"
- 都 ≥ 4 → "成熟旗舰"
- 都 ≤ 2 → "草根派"
- 非 agent 项目不要给 Agent 标签

## 诊断（3-5 条）

### D1. [标题]
- **证据**: `src/foo.py:42-58`, commit `abc1234`
- **影响**: ...

### D2. ...
### D3. ...

## 处方（按优先级）

1. **[短期]** 一行行动
2. **[中期]** ...
3. **[长期]** ...
```

### 7 条铁律

1. **每条结论必须引证据**：`file:line` 或 `commit hash`，找不到证据写 `[无足够证据]`。
2. **不存在的字段不评论**：JSON 没有 `agent.*` 就不要评 Agent Engineering。
3. **不编造文件或行号**：宁可空着也别瞎写。
4. **诊断是哲学问题，不是 lint 抱怨**：删除那些"只是 ruff 报错"的"诊断"。
5. **处方要 actionable**：避免"建议改进"这种空话，要"删掉 src/foo.py:42 的 unused import"。
6. **避免给所有项目都 3-4 分**：用 few-shot 对照理解"分差"。
7. **收尾前自检**："我的诊断里有没有 2 条以上是 ruff 抱怨而非哲学问题？"如有，删掉。

---

## 📚 Few-shot 标杆

### 标杆 A · zotero_cli（Go 项目，作为高分跨语言对照）

**预期雷达**：Agent 5 / 极简 4 / 一致 4 / 可读 4 / 防御 3 / 工程化 4
**预期哲学**："Agent-native CLI 旗舰"
**预期诊断方向**：CLI 设计的 AI 友好度（JSON 优先、skill 暴露、写操作防护）

### 标杆 B · biotools_agent（Python 项目）

**预期雷达**：Agent 4 / 极简 3 / 一致 3 / 可读 4 / 防御 3 / 工程化 3
**预期哲学**："Claude SDK 分析工具"
**预期诊断方向**：多格式报告生成的复杂度、AI 分析的边界

### 标杆 C · 普通 Python 项目（对照低分）

**预期雷达**：Agent 0/N/A / 极简 3 / 一致 2 / 可读 3 / 防御 2 / 工程化 2
**预期哲学**："草根派"
**预期诊断方向**：基础工程化缺失、类型覆盖率低

---

## 🎨 雷达图规格（脚本会生成）

6 角 SVG，`viewBox="0 0 400 400"`：
- 背景：5 层同心多边形（淡灰，r=40/80/120/160/200）
- 数据多边形：填充 `rgba(59,130,246,0.4)`，描边 `#3b82f6`
- 6 个维度标签在外圈
- 分数 0-5 映射到半径
- **项目名居中顶部**

---

## 完整流程示例

```
用户: /taste-analyzer /path/to/biotools_agent

Claude:
1. cd <skill 根>  # 或确保 taste-analyzer 在 PATH
2. 调 taste-analyzer collect /path/to/biotools_agent
3. 拿到 JSON（含 agent.* 字段）
4. 按上面 prompt 写解读（标 6 维度、哲学命名、诊断、处方）
5. 调 taste-analyzer render 生成 report.md（含 SVG 雷达图）
6. 把 report.md 给用户
```
