#!/usr/bin/env python3
"""
taste-analyzer: Python 项目代码品位分析

两种模式：
  collect  采集数据 → JSON 到 stdout
  render   渲染报告（注入 SVG 雷达图）

依赖：
  pyscn (subprocess), ruff (subprocess), radon (Python API),
  vulture (subprocess), git (subprocess)
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

# 可选依赖：Jinja2 (render 模式必需)
try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    HAS_JINJA = True
except ImportError:
    HAS_JINJA = False

# 可选依赖：radon (collect 模式更好用)
try:
    from radon.complexity import cc_visit, cc_rank
    from radon.metrics import mi_visit, mi_rank
    from radon.raw import analyze as radon_raw
    HAS_RADON = True
except ImportError:
    HAS_RADON = False


# ============================================================
# PATH 增强：让 uv tool 装的依赖（如 pyscn）能在任何环境找到
# ============================================================

def _augment_path() -> None:
    """把常见 uv tool / venv bin 加到 PATH，让 subprocess 能找到 pyscn 等。

    适用场景：
    - `uv tool install taste-analyzer` 后：tool 的 bin 在 ~/.local/share/uv/tools/taste-analyzer/bin
    - 直接 uv run：VIRTUAL_ENV/bin 已在 PATH
    - 系统 python：当前 PATH 即可
    """
    extra_paths = []
    # uv tool 装的每个 tool 的 venv bin
    uv_tools_dir = Path.home() / ".local" / "share" / "uv" / "tools"
    if uv_tools_dir.exists():
        for tool_dir in uv_tools_dir.iterdir():
            bin_dir = tool_dir / "bin"
            if bin_dir.exists():
                extra_paths.append(str(bin_dir))
    # pipx 的 venv bin
    pipx_venvs = Path.home() / ".local" / "pipx" / "venvs"
    if pipx_venvs.exists():
        for venv in pipx_venvs.iterdir():
            bin_dir = venv / "bin"
            if bin_dir.exists():
                extra_paths.append(str(bin_dir))
    # VIRTUAL_ENV 当前 venv 的 bin（uv run / pip install -e）
    venv = os.environ.get("VIRTUAL_ENV")
    if venv:
        venv_bin = Path(venv) / "bin"
        if venv_bin.exists():
            extra_paths.append(str(venv_bin))

    if extra_paths:
        # 放到 PATH 最前面，优先于系统 PATH
        current = os.environ.get("PATH", "")
        os.environ["PATH"] = os.pathsep.join(extra_paths + [current])


_augment_path()


# ============================================================
# 数据模型
# ============================================================

@dataclass
class ProjectMeta:
    path: str
    name: str
    is_agent_project: bool = False


@dataclass
class ComplexityResult:
    mean_cc: float = 0.0
    p95_cc: float = 0.0
    max_cc: float = 0.0
    hotspots: list[dict] = field(default_factory=list)
    source: str = "none"


@dataclass
class DeadCodeResult:
    count: int = 0
    samples: list[dict] = field(default_factory=list)
    source: str = "none"


@dataclass
class CloneResult:
    type1: int = 0
    type2: int = 0
    type3: int = 0
    samples: list[dict] = field(default_factory=list)
    source: str = "none"


@dataclass
class CouplingResult:
    cbo_top: list[dict] = field(default_factory=list)
    cycles: list[list[str]] = field(default_factory=list)
    source: str = "none"


@dataclass
class LintResult:
    violations: int = 0
    by_rule: dict[str, int] = field(default_factory=dict)
    source: str = "none"


@dataclass
class TypesResult:
    coverage_pct: float = 0.0
    errors: int = 0
    mypy_strict: bool = False
    source: str = "none"


@dataclass
class GitResult:
    commits: int = 0
    contributors: int = 0
    conventional_pct: float = 0.0
    has_lockfile: bool = False
    sample_messages: list[str] = field(default_factory=list)


@dataclass
class RepoResult:
    has_ci: bool = False
    has_tests: bool = False
    test_ratio: float = 0.0
    readme_lines: int = 0


@dataclass
class AgentSignals:
    has_claude_dir: bool = False
    has_mcp_config: bool = False
    has_claude_sdk: bool = False
    cli_json_flags: int = 0
    write_protection: bool = False
    state_persistence: bool = False
    dashboard: bool = False
    claude_subdirs: list[str] = field(default_factory=list)


@dataclass
class AnalysisData:
    project: ProjectMeta
    complexity: ComplexityResult
    dead_code: DeadCodeResult
    clones: CloneResult
    coupling: CouplingResult
    lint: LintResult
    types: TypesResult
    git: GitResult
    repo: RepoResult
    agent: AgentSignals

    def to_dict(self) -> dict:
        return asdict(self)


# ============================================================
# 工具函数
# ============================================================

def run(cmd: list[str], cwd: str | None = None, timeout: int = 120) -> tuple[int, str, str]:
    """执行命令，返回 (returncode, stdout, stderr)"""
    try:
        r = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout
        )
        return r.returncode, r.stdout, r.stderr
    except FileNotFoundError:
        return 127, "", f"command not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return 124, "", f"timeout after {timeout}s"


def check_tool(name: str) -> bool:
    return shutil.which(name) is not None


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def find_files(root: Path, pattern: str, limit: int = 5000) -> list[Path]:
    """递归找文件，限制数量避免卡死"""
    out = []
    try:
        for p in root.rglob(pattern):
            # 跳过常见忽略目录
            parts = p.parts
            if any(x in parts for x in (".git", "node_modules", ".venv", "venv", "__pycache__", ".tox", "dist", "build")):
                continue
            out.append(p)
            if len(out) >= limit:
                break
    except Exception:
        pass
    return out


# ============================================================
# 各维度数据采集
# ============================================================

def collect_complexity(root: Path) -> ComplexityResult:
    """优先 pyscn，回退到 radon"""
    result = ComplexityResult()

    # 1. 尝试 pyscn（pyscn 1.24 会把 JSON 写到 .pyscn/reports/，stdout 只有摘要文字）
    if check_tool("pyscn"):
        code, out, _ = run(
            ["pyscn", "analyze", "--json", "--select", "complexity", "."],
            cwd=str(root),
            timeout=300,
        )
        data = None
        # 优先尝试解析 stdout（未来版本可能直接输出 JSON）
        if code == 0:
            try:
                data = json.loads(out)
            except (json.JSONDecodeError, ValueError):
                # 当前 pyscn 把 JSON 写到 .pyscn/reports/，从那里读
                reports_dir = root / ".pyscn" / "reports"
                if reports_dir.exists():
                    reports = sorted(reports_dir.glob("analyze_*.json"), reverse=True)
                    if reports:
                        try:
                            data = json.loads(reports[0].read_text())
                        except (json.JSONDecodeError, OSError, ValueError):
                            pass

        if data and "complexity" in data:
            comp = data["complexity"]
            funcs = comp.get("Functions", [])
            ccs = []
            for f in funcs:
                metrics = f.get("Metrics", {})
                cc = metrics.get("Complexity")
                if isinstance(cc, (int, float)):
                    ccs.append((cc, f))

            if ccs:
                # Summary 已包含预计算数字（pyscn 字段: AverageComplexity / MaxComplexity）
                summary = comp.get("Summary", {})
                if "AverageComplexity" in summary:
                    result.mean_cc = float(summary["AverageComplexity"])
                else:
                    result.mean_cc = sum(c[0] for c in ccs) / len(ccs)
                if "MaxComplexity" in summary:
                    result.max_cc = float(summary["MaxComplexity"])
                else:
                    result.max_cc = max(c[0] for c in ccs)
                # p95 自己算
                sorted_ccs = sorted(c[0] for c in ccs)
                if sorted_ccs:
                    p95_idx = int(len(sorted_ccs) * 0.95)
                    result.p95_cc = sorted_ccs[min(p95_idx, len(sorted_ccs) - 1)]

                # hotspots: CC >= 10 的函数
                for cc, f in sorted(ccs, key=lambda x: -x[0])[:5]:
                    if cc >= 10:
                        result.hotspots.append({
                            "file": f.get("FilePath", "?"),
                            "function": f.get("Name", "?"),
                            "cc": cc,
                            "risk": f.get("RiskLevel", "?"),
                            "nesting": f.get("Metrics", {}).get("NestingDepth", 0),
                            "cognitive": f.get("Metrics", {}).get("CognitiveComplexity", 0),
                        })

                result.source = "pyscn"
                return result

    # 2. 回退 radon
    if HAS_RADON:
        py_files = [str(p) for p in find_files(root, "*.py")]
        if py_files:
            all_ccs = []
            for f in py_files[:200]:  # 限制文件数
                try:
                    with open(f, "r", encoding="utf-8", errors="replace") as fh:
                        source = fh.read()
                    blocks = cc_visit(source)
                    for b in blocks:
                        all_ccs.append((f, b.name, b.complexity))
                except Exception:
                    continue
            if all_ccs:
                ccs = [c[2] for c in all_ccs]
                result.mean_cc = sum(ccs) / len(ccs)
                result.p95_cc = sorted(ccs)[int(len(ccs) * 0.95)] if len(ccs) > 1 else ccs[-1]
                result.max_cc = max(ccs)
                result.hotspots = [
                    {"file": f, "function": n, "cc": c}
                    for f, n, c in sorted(all_ccs, key=lambda x: -x[2])[:5]
                    if c >= 10
                ]
                result.source = "radon"
                return result

    result.source = "unavailable"
    return result


def collect_dead_code(root: Path) -> DeadCodeResult:
    """vulture 优先，回退到 pyscn"""
    result = DeadCodeResult()

    if check_tool("vulture"):
        # vulture returncode: 0=clean, 1=error, 2=CLI error, 3=has findings
        code, out, _ = run(["vulture", str(root), "--min-confidence", "60"], cwd=str(root))
        if code in (0, 1, 3) and out.strip():
            lines = [l for l in out.splitlines() if l.strip() and ":" in l]
            result.count = len(lines)
            for line in lines[:5]:
                # 格式: path:line: message (name%)
                m = re.match(r"^(.+?):(\d+):\s*(.+)$", line)
                if m:
                    msg = m.group(3)
                    name_m = re.search(r"`?(\w+)`?\s*\((\d+)%\)", msg)
                    name = name_m.group(1) if name_m else "?"
                    result.samples.append({
                        "file": m.group(1),
                        "line": int(m.group(2)),
                        "name": name,
                    })
            result.source = "vulture"
            return result

    result.source = "unavailable"
    return result


def collect_lint(root: Path) -> LintResult:
    """ruff 优先，回退 pylint"""
    result = LintResult()

    if check_tool("ruff"):
        code, out, _ = run(["ruff", "check", "--output-format=json", "."], cwd=str(root))
        if out.strip():
            try:
                items = json.loads(out)
                if isinstance(items, list):
                    result.violations = len(items)
                    for item in items:
                        code_str = item.get("code", "unknown")
                        result.by_rule[code_str] = result.by_rule.get(code_str, 0) + 1
                    result.source = "ruff"
                    return result
            except json.JSONDecodeError:
                pass

    result.source = "unavailable"
    return result


def collect_types(root: Path) -> TypesResult:
    """mypy --json 优先"""
    result = TypesResult()

    if check_tool("mypy"):
        # 先粗扫：统计有类型注解的函数比例
        py_files = [str(p) for p in find_files(root, "*.py")]
        if py_files:
            total_funcs = 0
            typed_funcs = 0
            for f in py_files[:200]:
                src = read_text(Path(f))
                funcs = re.findall(r"^\s*def\s+(\w+)\s*\(([^)]*)\)", src, re.MULTILINE)
                for _, params in funcs:
                    total_funcs += 1
                    # 简化判断：参数都有注解 或 有返回注解
                    has_return = "->" in params or bool(re.search(r"\)\s*->", src))
                    params_typed = "self" in params or bool(re.search(r":\s*\w", params))
                    if params_typed or has_return:
                        typed_funcs += 1
            if total_funcs > 0:
                result.coverage_pct = round(typed_funcs * 100 / total_funcs, 1)

        # 检查 mypy strict 配置
        tomls = list(root.rglob("pyproject.toml"))[:5]
        for t in tomls:
            content = read_text(t)
            if "strict = true" in content or "disallow_untyped_defs = true" in content:
                result.mypy_strict = True
                break

        # 错误数（轻量调用）
        code, out, _ = run(["mypy", "--no-error-summary", "--json", "."], cwd=str(root), timeout=180)
        if out.strip():
            try:
                errors = json.loads(out) if out.strip().startswith("[") else []
                result.errors = len(errors) if isinstance(errors, list) else 0
            except json.JSONDecodeError:
                # mypy --json 输出每行一个对象
                try:
                    lines = [l for l in out.splitlines() if l.strip().startswith("{")]
                    result.errors = len(lines)
                except Exception:
                    pass

        result.source = "mypy"
        return result

    result.source = "unavailable"
    return result


def collect_git(root: Path) -> GitResult:
    result = GitResult()

    # commit 数 + contributors + 消息采样
    code, out, _ = run(["git", "log", "--pretty=format:%H|%an|%ae|%s", "-n", "500"], cwd=str(root))
    if code == 0 and out.strip():
        lines = [l for l in out.splitlines() if l]
        result.commits = len(lines)
        authors = set()
        conventional = 0
        msgs = []
        for l in lines:
            parts = l.split("|", 3)
            if len(parts) >= 4:
                authors.add(parts[1])
                msg = parts[3]
                msgs.append(msg)
                if re.match(r"^(feat|fix|docs|style|refactor|test|chore|perf|build|ci)(\(.+\))?!?:\s", msg):
                    conventional += 1
        result.contributors = len(authors)
        if lines:
            result.conventional_pct = round(conventional * 100 / len(lines), 1)
        result.sample_messages = msgs[:10]

    # 锁文件
    lockfiles = ["uv.lock", "poetry.lock", "Pipfile.lock", "pdm.lock", "requirements.txt"]
    for lf in lockfiles:
        if (root / lf).exists():
            result.has_lockfile = True
            break

    return result


def collect_repo(root: Path) -> RepoResult:
    result = RepoResult()

    # CI
    if (root / ".github" / "workflows").exists() and any((root / ".github" / "workflows").iterdir()):
        result.has_ci = True

    # tests
    test_dirs = [root / "tests", root / "test"]
    for td in test_dirs:
        if td.exists() and any(td.iterdir()):
            result.has_tests = True
            break

    # 测试代码比
    py_files = find_files(root, "*.py")
    test_files = [p for p in py_files if "test" in p.name.lower() or "/tests/" in str(p)]
    if py_files:
        total = sum(len(read_text(p).splitlines()) for p in py_files[:200])
        tests = sum(len(read_text(p).splitlines()) for p in test_files[:100])
        if total > 0:
            result.test_ratio = round(tests / total, 2)

    # README
    for name in ["README.md", "README.rst", "README.txt", "README"]:
        p = root / name
        if p.exists():
            result.readme_lines = len(read_text(p).splitlines())
            break

    return result


def collect_agent_signals(root: Path, project_name: str, project_desc: str = "") -> AgentSignals:
    """检测 agent 特征"""
    result = AgentSignals()

    # .claude/ 目录
    claude_dir = root / ".claude"
    if claude_dir.exists() and claude_dir.is_dir():
        result.has_claude_dir = True
        for sub in claude_dir.iterdir():
            if sub.is_dir():
                result.claude_subdirs.append(sub.name)

    # mcp 配置
    mcp_paths = [
        root / ".mcp.json",
        root / "mcp.json",
        claude_dir / "mcp.json",
        root / "tools" / ".mcp.json",
    ]
    if any(p.exists() for p in mcp_paths):
        result.has_mcp_config = True

    # Claude SDK 依赖
    for fname in ["pyproject.toml", "requirements.txt", "setup.py", "Pipfile"]:
        content = read_text(root / fname)
        if any(pkg in content.lower() for pkg in [
            "claude-code-sdk", "claude-agent-sdk", "@anthropic-ai/claude",
            "claude-sdk", "anthropic-sdk",
        ]):
            result.has_claude_sdk = True
            break

    # CLI JSON 标志数
    if check_tool("git"):
        # 用 git grep 找 click/typer/argparse 的 --json 选项
        code, out, _ = run([
            "git", "grep", "-l", "--json",
            "--", "*.py", "*.go", "*.ts", "*.js"
        ], cwd=str(root))
        if code == 0:
            files = [l for l in out.splitlines() if l]
            result.cli_json_flags = len(files)

    # 写操作防护（dry-run / --safe / --no-write）
    code, out, _ = run([
        "git", "grep", "-l", "-E",
        "(dry[_-]?run|--safe|--no[_-]?write|confirm)",
        "--", "*.py", "*.go", "*.ts", "*.js"
    ], cwd=str(root))
    if code == 0:
        result.write_protection = bool(out.strip())

    # 状态持久化（JSONL / sqlite）
    for ext in [".jsonl", ".db", ".sqlite", ".sqlite3"]:
        matches = list(root.rglob(f"*{ext}"))
        if matches:
            result.state_persistence = True
            break

    # Dashboard（HTTP server / web 路由）
    code, out, _ = run([
        "git", "grep", "-l", "-E",
        "(dashboard|web\\.run|app\\.run|uvicorn|gunicorn|fastapi\\(|flask|express)",
        "--", "*.py", "*.go", "*.ts", "*.js"
    ], cwd=str(root))
    if code == 0:
        result.dashboard = bool(out.strip())

    return result


def detect_agent_project(root: Path, agent: AgentSignals, name: str, desc: str = "") -> bool:
    """综合判断是否 agent 项目"""
    if agent.has_claude_dir:
        return True
    if agent.has_claude_sdk:
        return True
    if agent.has_mcp_config:
        return True
    # 名称/描述含 agent
    text = (name + " " + desc).lower()
    # "claude" 单独出现也算（claude-tool, claude-cli 等）
    has_claude_word = bool(re.search(r"\bclaude\b", text)) or "-claude" in text or "claude-" in text
    if any(k in text for k in ["agent", "mcp"]) or has_claude_word:
        return True
    # .claude 子目录含 agents
    if "agents" in agent.claude_subdirs or "skills" in agent.claude_subdirs:
        return True
    return False


# ============================================================
# 主采集
# ============================================================

def collect_all(project_path: str) -> dict:
    root = Path(project_path).resolve()
    if not root.exists():
        print(json.dumps({"error": f"path not found: {project_path}"}), file=sys.stderr)
        sys.exit(1)

    name = root.name
    desc = read_text(root / "pyproject.toml")[:500] if (root / "pyproject.toml").exists() else ""

    print(f"# Collecting data from {root}...", file=sys.stderr)

    complexity = collect_complexity(root)
    print(f"  complexity: mean={complexity.mean_cc:.1f} max={complexity.max_cc:.0f} src={complexity.source}", file=sys.stderr)

    dead_code = collect_dead_code(root)
    print(f"  dead_code: {dead_code.count} findings", file=sys.stderr)

    clones = CloneResult(source="unavailable")  # pyscn 内部做，单列字段暂未用
    coupling = CouplingResult(source="unavailable")

    lint = collect_lint(root)
    print(f"  lint: {lint.violations} violations", file=sys.stderr)

    types = collect_types(root)
    print(f"  types: {types.coverage_pct}% coverage, {types.errors} errors", file=sys.stderr)

    git_r = collect_git(root)
    print(f"  git: {git_r.commits} commits, {git_r.contributors} contributors", file=sys.stderr)

    repo = collect_repo(root)
    print(f"  repo: CI={repo.has_ci}, tests={repo.has_tests}, ratio={repo.test_ratio}", file=sys.stderr)

    agent_sigs = collect_agent_signals(root, name, desc)
    print(f"  agent: claude_dir={agent_sigs.has_claude_dir}, sdk={agent_sigs.has_claude_sdk}", file=sys.stderr)

    is_agent = detect_agent_project(root, agent_sigs, name, desc)

    data = AnalysisData(
        project=ProjectMeta(path=str(root), name=name, is_agent_project=is_agent),
        complexity=complexity,
        dead_code=dead_code,
        clones=clones,
        coupling=coupling,
        lint=lint,
        types=types,
        git=git_r,
        repo=repo,
        agent=agent_sigs,
    )

    return data.to_dict()


# ============================================================
# SVG 雷达图生成
# ============================================================

def generate_radar_svg(
    scores: dict[str, float],
    project_name: str,
    is_agent: bool = True,
    size: int = 400,
) -> str:
    """生成 5 或 6 角雷达图 SVG"""
    # 选择维度顺序
    if is_agent:
        keys = ["极简度", "一致性", "可读性", "防御性", "工程化", "Agent Engineering"]
    else:
        keys = ["极简度", "一致性", "可读性", "防御性", "工程化"]

    values = [scores.get(k, 0) for k in keys]
    n = len(keys)
    cx, cy = size // 2, size // 2
    max_r = size // 2 - 50

    # 多边形顶点
    def vertex(i: int, value: float) -> tuple[float, float]:
        # 角度从顶部开始，顺时针
        angle = -math.pi / 2 + 2 * math.pi * i / n
        r = max_r * (value / 5.0)
        return (cx + r * math.cos(angle), cy + r * math.sin(angle))

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" font-family="system-ui, sans-serif">',
        f'<rect width="{size}" height="{size}" fill="#fafafa"/>',
        f'<text x="{cx}" y="20" text-anchor="middle" font-size="14" font-weight="bold" fill="#333">{project_name}</text>',
    ]

    # 背景网格（5 层）
    for level in range(1, 6):
        r = max_r * level / 5
        points = []
        for i in range(n):
            angle = -math.pi / 2 + 2 * math.pi * i / n
            points.append(f"{cx + r * math.cos(angle):.1f},{cy + r * math.sin(angle):.1f}")
        svg_parts.append(
            f'<polygon points="{" ".join(points)}" fill="none" '
            f'stroke="#d1d5db" stroke-width="0.5"/>'
        )

    # 轴线
    for i in range(n):
        angle = -math.pi / 2 + 2 * math.pi * i / n
        x = cx + max_r * math.cos(angle)
        y = cy + max_r * math.sin(angle)
        svg_parts.append(
            f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" '
            f'stroke="#d1d5db" stroke-width="0.5"/>'
        )

    # 数据多边形
    data_points = [vertex(i, values[i]) for i in range(n)]
    points_str = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in data_points)
    svg_parts.append(
        f'<polygon points="{points_str}" fill="rgba(59,130,246,0.4)" '
        f'stroke="#3b82f6" stroke-width="2"/>'
    )

    # 数据点
    for p in data_points:
        svg_parts.append(
            f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="3" fill="#3b82f6"/>'
        )

    # 维度标签
    for i, key in enumerate(keys):
        angle = -math.pi / 2 + 2 * math.pi * i / n
        lx = cx + (max_r + 20) * math.cos(angle)
        ly = cy + (max_r + 20) * math.sin(angle)
        # 调整文本锚点
        if abs(math.cos(angle)) < 0.1:
            anchor = "middle"
        elif math.cos(angle) > 0:
            anchor = "start"
        else:
            anchor = "end"
        # 分数标注
        score = values[i]
        score_color = "#10b981" if score >= 4 else "#f59e0b" if score >= 2.5 else "#ef4444"
        svg_parts.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" '
            f'font-size="11" fill="#374151">{key}</text>'
        )
        svg_parts.append(
            f'<text x="{lx:.1f}" y="{ly + 12:.1f}" text-anchor="{anchor}" '
            f'font-size="10" fill="{score_color}" font-weight="bold">{score}/5</text>'
        )

    svg_parts.append("</svg>")
    return "\n".join(svg_parts)


# ============================================================
# Render 模式
# ============================================================

def render_report(data: dict, report_md: str, out_path: str) -> None:
    if not HAS_JINJA:
        print("ERROR: jinja2 not installed. pip install jinja2", file=sys.stderr)
        sys.exit(1)

    template_dir = Path(__file__).parent.parent / "templates"
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("report.md.j2")

    # 生成 SVG 雷达图
    project = data.get("project", {})
    project_name = project.get("name", "Project")
    is_agent = project.get("is_agent_project", False)

    # 提取雷达图分数（从 Claude 写的 markdown 中提取）
    scores = _extract_scores_from_markdown(report_md, is_agent)
    radar_svg = generate_radar_svg(scores, project_name, is_agent)

    rendered = template.render(
        project=project,
        data=data,
        report=report_md,
        radar_svg=radar_svg,
        scores=scores,
    )

    Path(out_path).write_text(rendered, encoding="utf-8")
    print(f"Report written to {out_path}", file=sys.stderr)


def _extract_scores_from_markdown(md: str, is_agent: bool) -> dict[str, float]:
    """从 Claude 写的 markdown 提取分数"""
    scores = {}
    default_keys = ["极简度", "一致性", "可读性", "防御性", "工程化"]
    keys = default_keys + (["Agent Engineering"] if is_agent else [])

    for key in keys:
        # 匹配 "- **极简度**: 4/5 ..." 或类似格式
        pattern = rf"\*?\*?{re.escape(key)}\*?\*?\s*[:：]\s*(\d+(?:\.\d+)?)\s*/\s*5"
        m = re.search(pattern, md)
        if m:
            scores[key] = float(m.group(1))
        else:
            scores[key] = 0  # 默认值

    return scores


# ============================================================
# CLI
# ============================================================

def main() -> None:
    parser = argparse.ArgumentParser(description="Taste Analyzer for Python projects")
    sub = parser.add_subparsers(dest="mode", required=True)

    # collect
    p_collect = sub.add_parser("collect", help="采集数据并输出 JSON")
    p_collect.add_argument("path", help="项目路径")

    # render
    p_render = sub.add_parser("render", help="渲染报告（含 SVG 雷达图）")
    p_render.add_argument("--data", required=True, help="collect 输出的 JSON 文件")
    p_render.add_argument("--report", required=True, help="Claude 写的 markdown 解读")
    p_render.add_argument("--out", required=True, help="输出报告路径")

    args = parser.parse_args()

    if args.mode == "collect":
        data = collect_all(args.path)
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif args.mode == "render":
        data = json.loads(read_text(Path(args.data)))
        report_md = read_text(Path(args.report))
        render_report(data, report_md, args.out)


if __name__ == "__main__":
    main()
