# Taste Analyzer

> Python 项目代码品位分析 — 6 维度评分 + 诊断 + SVG 雷达图报告

## 快速使用

在 Claude Code 中：

```bash
/taste-analyzer /path/to/python-project
```

Claude 会：
1. 调用 `scripts/analyze.py collect` 采集数据
2. 按 SKILL.md 里的 prompt 解读数据
3. 调用 `scripts/analyze.py render` 生成报告
4. 报告含 SVG 雷达图（自包含，任何 Markdown 阅读器可看）

## 6 个评分维度

| # | 维度 | 问题 |
|---|------|------|
| 1 | **极简度** Minimalism | 项目"杀伐果断"吗？ |
| 2 | **一致性** Consistency | 风格是否一以贯之？ |
| 3 | **可读性** Readability | 写给"未来的自己"还是"机器"？ |
| 4 | **防御性** Defensiveness | "信任"还是"边界检查"？ |
| 5 | **工程化** Engineering | 流程是否到位？ |
| 6 | **Agent Engineering** | 对 Claude Agent SDK 的利用深度？（仅 agent 项目评） |

每个维度 0-5 分。详见 `SKILL.md`。

## 数据采集依赖

| 工具 | 用途 | 必需？ |
|------|------|--------|
| **pyscn** | 结构分析（复杂度 / 死代码 / 克隆 / CBO） | 否（回退到 radon） |
| **ruff** | linter（速度极快） | 否（标 unavailable） |
| **radon** | Python API 取圈复杂度 | 否 |
| **vulture** | 死代码检测 | 否 |
| **mypy** | 类型覆盖率 | 否 |
| **git** | commit / contributor / conventional % | 是（采集元数据） |
| **jinja2** | render 模式渲染报告 | 是 |

安装所有依赖：

```bash
pip install jinja2 radon ruff vulture mypy
# pyscn（Go 二进制，推荐）：
pipx install pyscn
# 或：uv tool install pyscn
```

## 安装（首次使用）

```bash
cd taste-analyzer/                         # skill 根目录
uv tool install . --reinstall \
    --with pyscn --with radon --with vulture --with mypy --with ruff
```

完成后 `taste-analyzer` 出现在 `~/.local/bin/`，任意目录可调。

> **为什么用 `uv tool install` 而不是 `uv sync`**：tool install 把脚本装到全局 PATH，任意 cwd 都能用；sync 只在 skill 内有效。

## 直接命令行使用

不通过 Claude Code：

```bash
# 阶段 1：采集数据（任意目录）
taste-analyzer collect /path/to/project > data.json

# 阶段 2：Claude 解读（手动或通过另一个 prompt 喂给 LLM）

# 阶段 3：渲染报告（需要 Claude 写的 markdown 解读）
taste-analyzer render \
    --data data.json \
    --report interpretation.md \
    --out taste-report.md
```

## 输出示例

报告结构：

```markdown
# <项目名> — 代码品位分析报告

## 🎯 雷达图
[SVG 雷达图，6 角]

## 📊 数据快照
<details>...JSON...</details>

## 📋 快速摘要
[表格：6 维度 × 分数]

## 🧠 Claude 解读
## 维度评分
## 哲学命名
## 诊断
## 处方

## 📈 数据附录
[自动化指标]
```

## Few-shot 标杆

| 项目 | 类型 | 预期雷达 | 哲学 |
|------|------|---------|------|
| **zotero_cli** (Go) | CLI 工具为 AI 设计 | Agent 5 / 都中高 | "Agent-native CLI 旗舰" |
| **biotools_agent** (Python) | Claude SDK 工具 | Agent 4 / 都中 | "Claude SDK 分析工具" |
| **普通 Python 项目** | 传统 | Agent 0/N/A / 中低 | "草根派" |

详见 `SKILL.md` 的 Few-shot 段。

## 设计原则

1. **prompt 是核心资产**：SKILL.md 里的主 prompt 决定 skill 的"灵魂"
2. **工具给事实，LLM 给解读**：不发明指标，只串联叙事
3. **证据强制**：每条结论必须引 `file:line` 或 commit hash
4. **自适应**：检测到 agent 特征才评第 6 维
5. **自包含输出**：SVG 雷达图嵌入 Markdown，无外部依赖

## 文件结构

```
taste-analyzer/                 # 整个目录就是 skill，可打包分发
├── SKILL.md                    # Claude Code skill 元数据（必需）
├── scripts/
│   └── analyze.py              # 主脚本（collect + render + SVG）
├── templates/
│   └── report.md.j2            # 报告 Jinja2 模板
├── unit/                       # 单元测试（pytest）
│   └── test_analyze.py
├── examples/                   # 示例输出（参考用）
├── pyproject.toml              # 依赖（含 console script）
├── .taste-analyzer.toml        # 默认配置
├── uv.lock                     # 锁定依赖（uv）
└── README.md                   # 本文件
```

> **分发方式**：整个目录打包成 zip / git subtree / PyPI 都行。
> 使用方只需 `uv sync --all-extras` 安装依赖，然后 `taste-analyzer` 命令即可用。

## License

MIT
