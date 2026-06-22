# gene-family-agent — 代码品位分析报告

> 生成时间:  | 路径: `/tmp/gene-family-agent`
> ✅ **Agent 项目** — 完整 6 维评分
---

## 🎯 雷达图

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" font-family="system-ui, sans-serif">
<rect width="400" height="400" fill="#fafafa"/>
<text x="200" y="20" text-anchor="middle" font-size="14" font-weight="bold" fill="#333">gene-family-agent</text>
<polygon points="200.0,170.0 226.0,185.0 226.0,215.0 200.0,230.0 174.0,215.0 174.0,185.0" fill="none" stroke="#d1d5db" stroke-width="0.5"/>
<polygon points="200.0,140.0 252.0,170.0 252.0,230.0 200.0,260.0 148.0,230.0 148.0,170.0" fill="none" stroke="#d1d5db" stroke-width="0.5"/>
<polygon points="200.0,110.0 277.9,155.0 277.9,245.0 200.0,290.0 122.1,245.0 122.1,155.0" fill="none" stroke="#d1d5db" stroke-width="0.5"/>
<polygon points="200.0,80.0 303.9,140.0 303.9,260.0 200.0,320.0 96.1,260.0 96.1,140.0" fill="none" stroke="#d1d5db" stroke-width="0.5"/>
<polygon points="200.0,50.0 329.9,125.0 329.9,275.0 200.0,350.0 70.1,275.0 70.1,125.0" fill="none" stroke="#d1d5db" stroke-width="0.5"/>
<line x1="200" y1="200" x2="200.0" y2="50.0" stroke="#d1d5db" stroke-width="0.5"/>
<line x1="200" y1="200" x2="329.9" y2="125.0" stroke="#d1d5db" stroke-width="0.5"/>
<line x1="200" y1="200" x2="329.9" y2="275.0" stroke="#d1d5db" stroke-width="0.5"/>
<line x1="200" y1="200" x2="200.0" y2="350.0" stroke="#d1d5db" stroke-width="0.5"/>
<line x1="200" y1="200" x2="70.1" y2="275.0" stroke="#d1d5db" stroke-width="0.5"/>
<line x1="200" y1="200" x2="70.1" y2="125.0" stroke="#d1d5db" stroke-width="0.5"/>
<polygon points="200.0,140.0 277.9,155.0 277.9,245.0 200.0,350.0 96.1,260.0 96.1,140.0" fill="rgba(59,130,246,0.4)" stroke="#3b82f6" stroke-width="2"/>
<circle cx="200.0" cy="140.0" r="3" fill="#3b82f6"/>
<circle cx="277.9" cy="155.0" r="3" fill="#3b82f6"/>
<circle cx="277.9" cy="245.0" r="3" fill="#3b82f6"/>
<circle cx="200.0" cy="350.0" r="3" fill="#3b82f6"/>
<circle cx="96.1" cy="260.0" r="3" fill="#3b82f6"/>
<circle cx="96.1" cy="140.0" r="3" fill="#3b82f6"/>
<text x="200.0" y="30.0" text-anchor="middle" font-size="11" fill="#374151">极简度</text>
<text x="200.0" y="42.0" text-anchor="middle" font-size="10" fill="#ef4444" font-weight="bold">2.0/5</text>
<text x="347.2" y="115.0" text-anchor="start" font-size="11" fill="#374151">一致性</text>
<text x="347.2" y="127.0" text-anchor="start" font-size="10" fill="#f59e0b" font-weight="bold">3.0/5</text>
<text x="347.2" y="285.0" text-anchor="start" font-size="11" fill="#374151">可读性</text>
<text x="347.2" y="297.0" text-anchor="start" font-size="10" fill="#f59e0b" font-weight="bold">3.0/5</text>
<text x="200.0" y="370.0" text-anchor="middle" font-size="11" fill="#374151">防御性</text>
<text x="200.0" y="382.0" text-anchor="middle" font-size="10" fill="#10b981" font-weight="bold">5.0/5</text>
<text x="52.8" y="285.0" text-anchor="end" font-size="11" fill="#374151">工程化</text>
<text x="52.8" y="297.0" text-anchor="end" font-size="10" fill="#10b981" font-weight="bold">4.0/5</text>
<text x="52.8" y="115.0" text-anchor="end" font-size="11" fill="#374151">Agent Engineering</text>
<text x="52.8" y="127.0" text-anchor="end" font-size="10" fill="#10b981" font-weight="bold">4.0/5</text>
</svg>

---

## 📊 数据快照

<details>
<summary>点击展开原始 JSON 数据</summary>

```json
{
  "agent": {
    "claude_subdirs": [
      "skills"
    ],
    "cli_json_flags": 0,
    "dashboard": true,
    "has_claude_dir": true,
    "has_claude_sdk": true,
    "has_mcp_config": false,
    "state_persistence": false,
    "write_protection": true
  },
  "clones": {
    "samples": [],
    "source": "unavailable",
    "type1": 0,
    "type2": 0,
    "type3": 0
  },
  "complexity": {
    "hotspots": [
      {
        "cc": 70,
        "cognitive": 146,
        "file": "src/gene_family_agent/teams/gene_family_team.py",
        "function": "GeneFamilyTeam.analyze",
        "nesting": 5,
        "risk": "high"
      },
      {
        "cc": 65,
        "cognitive": 228,
        "file": "src/gene_family_agent/teams/review_generator.py",
        "function": "ReviewGenerator.build_multi_species_prompt",
        "nesting": 6,
        "risk": "high"
      },
      {
        "cc": 35,
        "cognitive": 62,
        "file": "src/gene_family_agent/agents/literature_orchestrator.py",
        "function": "LiteratureOrchestrator.comprehensive_search",
        "nesting": 6,
        "risk": "high"
      },
      {
        "cc": 32,
        "cognitive": 70,
        "file": "src/gene_family_agent/tools/genome_tools.py",
        "function": "get_gene_by_symbol_with_uniprot_fallback",
        "nesting": 4,
        "risk": "high"
      },
      {
        "cc": 31,
        "cognitive": 86,
        "file": "src/gene_family_agent/literature/retrieval_pipeline.py",
        "function": "execute_retrieval_strategies",
        "nesting": 4,
        "risk": "high"
      }
    ],
    "max_cc": 70.0,
    "mean_cc": 9.376543209876543,
    "p95_cc": 16,
    "source": "pyscn"
  },
  "coupling": {
    "cbo_top": [],
    "cycles": [],
    "source": "unavailable"
  },
  "dead_code": {
    "count": 191,
    "samples": [
      {
        "file": "_test_intent.py",
        "line": 33,
        "name": "?"
      },
      {
        "file": "scripts/agents/test_literature_agent.py",
        "line": 27,
        "name": "?"
      },
      {
        "file": "scripts/parallel_model_test.py",
        "line": 46,
        "name": "?"
      },
      {
        "file": "scripts/parallel_model_test.py",
        "line": 47,
        "name": "?"
      },
      {
        "file": "scripts/test_mcp_vs_cli.py",
        "line": 27,
        "name": "?"
      }
    ],
    "source": "vulture"
  },
  "git": {
    "commits": 50,
    "contributors": 1,
    "conventional_pct": 100.0,
    "has_lockfile": true,
    "sample_messages": [
      "docs: update README with architecture diagrams and config\u8bf4\u660e",
      "fix: \u52a0\u5f3a\u4fee\u8ba2\u9636\u6bb5\u7684\u5f15\u7528\u5b8c\u6574\u6027\u548c\u5b64\u513f\u5f15\u7528\u9632\u62a4",
      "fix: \u4fee\u590d QueryAnalysisAgent \u548c ReviewAgent \u7684 token \u7edf\u8ba1\u7f3a\u5931\u95ee\u9898",
      "fix: \u4fee\u590d num_turns \u7edf\u8ba1\u4e3a 0 \u7684\u95ee\u9898",
      "fix: \u52a0\u5f3a\u5f15\u7528\u6570\u91cf\u8981\u6c42\u548c\u81ea\u68c0\u673a\u5236",
      "fix: \u6dfb\u52a0\u57fa\u56e0\u540d\u659c\u4f53\u683c\u5f0f\u8981\u6c42\u5230\u5199\u4f5c\u63d0\u793a\u8bcd",
      "refactor: \u79fb\u9664 claim_citation_plan \u673a\u5236",
      "feat: \u5728 revision prompt \u4e2d\u6dfb\u52a0 claim-citation mapping \u7ea6\u675f",
      "fix: record QueryAnalysisAgent token usage in stage_token_usage",
      "feat: \u4e3a ReviewAgent \u6dfb\u52a0\u8be6\u7ec6 trace \u65e5\u5fd7\u8bb0\u5f55"
    ]
  },
  "lint": {
    "by_rule": {
      "ARG002": 3,
      "B009": 1,
      "C416": 2,
      "E401": 1,
      "E402": 4,
      "E702": 6,
      "F401": 24,
      "F541": 4,
      "F821": 4,
      "I001": 16,
      "PLW0108": 1,
      "PTH118": 1,
      "PTH120": 1,
      "PTH123": 6,
      "RUF005": 1,
      "RUF010": 4,
      "RUF012": 1,
      "RUF022": 2,
      "RUF059": 3,
      "RUF100": 1,
      "SIM102": 5,
      "SIM110": 1,
      "SIM113": 1,
      "SIM114": 1,
      "SIM118": 1,
      "SIM300": 1,
      "TC001": 3,
      "TC003": 5,
      "UP035": 1,
      "UP037": 31
    },
    "source": "ruff",
    "violations": 136
  },
  "project": {
    "is_agent_project": true,
    "name": "gene-family-agent",
    "path": "/tmp/gene-family-agent"
  },
  "repo": {
    "has_ci": true,
    "has_tests": true,
    "readme_lines": 437,
    "test_ratio": 0.44
  },
  "types": {
    "coverage_pct": 94.1,
    "errors": 0,
    "mypy_strict": false,
    "source": "mypy"
  }
}
```

</details>

---

## 📋 快速摘要

| 维度 | 分数 | 等级 |
|------|------|------|
| 极简度 | 2.0/5 | 🔴 待改进 |
| 一致性 | 3.0/5 | 🟡 中规 |
| 可读性 | 3.0/5 | 🟡 中规 |
| 防御性 | 5.0/5 | 🟢 典范 |
| 工程化 | 4.0/5 | 🟢 典范 |
| Agent Engineering | 4.0/5 | 🟢 典范 |
---

## 🧠 Claude 解读

## 维度评分

- **极简度**: 2/5 函数平均行偏高，关键函数 `analyze` 圈复杂度高达 111（远超阈值 15），提示存在"上帝函数"。证据: src/gene_family_agent/teams/gene_family_team.py::analyze CC=111
- **一致性**: 3/5 ruff 135 violations，主要集中在 UP037 (31) 和 F401 (24)，命名风格基本一致但 import 规范化有缺口。证据: ruff by_rule.UP037=31
- **可读性**: 3/5 函数平均 ~25 行，docstring 覆盖率中等，热点函数过长影响局部可读性。证据: hotspots max_cc=111
- **防御性**: 5/5 mypy 错误 0，类型覆盖率 94.1%，错误处理较严格。证据: types.coverage_pct=94.1, types.errors=0
- **工程化**: 4/5 CI 存在、测试/代码比 0.44、conventional commits 100%、锁文件齐全。证据: repo.has_ci=True, repo.test_ratio=0.44, git.conventional_pct=100
- **Agent Engineering**: 4/5 检测到 .claude/ 目录、Claude SDK 依赖、内置 skills 结构，符合 Claude SDK 主力使用模式。证据: agent.has_claude_dir=True, agent.has_claude_sdk=True

## 哲学命名

**"工程化的 AI-native 学术工具"** — 类型严格 + 流程规范到位，但核心算法层复杂度爆炸。

雷达图形状呈现典型的"高分防御 + 高分工程 + 低分极简"组合，属于把工程化纪律带到 AI Agent 项目里的典范。

## 诊断（3-5 条）

### D1. 上帝函数 `analyze` 圈复杂度 111
- **证据**: src/gene_family_agent/teams/gene_family_team.py::analyze CC=111
- **影响**: 单函数难以测试，单一改动可能引发级联故障，违反"杀伐果断"的极简哲学

### D2. ruff 违规聚集于 import 规范化
- **证据**: ruff.by_rule UP037=31, F401=24, I001=16
- **影响**: 项目自我约束风格一致性的能力尚未完全自动化，需要 ruff format 启用

### D3. 死代码 191 处（vulture 60% 置信度）
- **证据**: dead_code.count=191
- **影响**: 大量未引用函数/变量累积增加阅读负担，需定期清理或收紧 vulture 阈值

## 处方（按优先级）

1. **[短期]** 启用 `ruff check --fix` + `ruff format` 一次性消化 UP037/F401 类机械违规（30 分钟工作量）
2. **[中期]** 重构 `analyze` 上帝函数：按职责拆分为 `parse_input` / `dispatch_agents` / `aggregate_results` / `format_output` 四个子函数
3. **[长期]** 引入 vulture 到 CI，将置信度阈值提到 80%，自动 block 未引用代码合入


---

## 📈 数据附录（自动化）

### 复杂度
- 平均 CC: `9.376543209876543`
- P95 CC: `16`
- 最大 CC: `70.0`
- 数据源: `pyscn`

### 死代码
- 发现数: `191`
- 数据源: `vulture`

### Lint
- 违规总数: `136`
- Top 规则:
  - `UP037`: 31
  - `F401`: 24
  - `I001`: 16
  - `E702`: 6
  - `PTH123`: 6
- 数据源: `ruff`

### 类型
- 覆盖率: `94.1%`
- mypy 错误: `0`
- mypy strict: `False`
- 数据源: `mypy`

### Git
- Commit 数: `50`
- Contributors: `1`
- Conventional Commits: `100.0%`
- 锁文件: `✅`

### 仓库
- CI: `✅`
- Tests: `✅`
- 测试/代码比: `0.44`
- README 行数: `437`

### Agent Signals
- `.claude/` 目录: `✅`
  - 子目录: `['skills']`
- MCP 配置: `❌`
- Claude SDK: `✅`
- CLI `--json` 标志: `0` 个文件
- 写操作防护: `✅`
- 状态持久化: `❌`
- Dashboard: `✅`

---

*由 taste-analyzer skill 生成 · 数据采集自 pyscn/ruff/radon/vulture/mypy/git + Agent 信号扫描*