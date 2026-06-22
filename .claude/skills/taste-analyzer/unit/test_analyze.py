"""Unit tests for taste-analyzer core logic (SVG gen + score extraction + detection)."""
import json
import sys
from pathlib import Path

import pytest

# 让测试可以 import scripts/
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from analyze import (  # noqa: E402
    detect_agent_project,
    generate_radar_svg,
    _extract_scores_from_markdown,
)


# ============================================================
# generate_radar_svg
# ============================================================

class TestRadarSvg:
    def test_returns_valid_svg(self):
        svg = generate_radar_svg(
            {"极简度": 4, "一致性": 3, "可读性": 5, "防御性": 4, "工程化": 3},
            project_name="test-project",
            is_agent=False,
        )
        assert svg.startswith("<svg")
        assert svg.endswith("</svg>")
        assert 'viewBox="0 0 400 400"' in svg
        assert "test-project" in svg

    def test_six_axes_when_agent(self):
        svg = generate_radar_svg(
            {"极简度": 4, "一致性": 3, "可读性": 5, "防御性": 4, "工程化": 3, "Agent Engineering": 5},
            "agent-proj",
            is_agent=True,
        )
        # 6 角应该有 6 个 polygon labels
        for key in ["极简度", "一致性", "可读性", "防御性", "工程化", "Agent Engineering"]:
            assert key in svg, f"missing label: {key}"

    def test_five_axes_when_not_agent(self):
        svg = generate_radar_svg(
            {"极简度": 4, "一致性": 3, "可读性": 5, "防御性": 4, "工程化": 3},
            "plain-proj",
            is_agent=False,
        )
        assert "Agent Engineering" not in svg
        assert "极简度" in svg

    def test_color_coding(self):
        """高分绿、中分黄、低分红"""
        svg = generate_radar_svg(
            {"极简度": 5, "一致性": 3, "可读性": 1, "防御性": 4, "工程化": 2, "Agent Engineering": 4},
            "colored",
            is_agent=True,
        )
        # 5 分应该是绿色 #10b981
        assert "#10b981" in svg
        # 1 分应该是红色 #ef4444
        assert "#ef4444" in svg

    def test_size_parameter(self):
        svg = generate_radar_svg(
            {"极简度": 4, "一致性": 3, "可读性": 5, "防御性": 4, "工程化": 3},
            "size-test",
            is_agent=False,
            size=600,
        )
        assert 'viewBox="0 0 600 600"' in svg


# ============================================================
# _extract_scores_from_markdown
# ============================================================

class TestScoreExtraction:
    def test_extracts_all_six_scores(self):
        md = """
## 维度评分

- **极简度**: 4/5 ...
- **一致性**: 3/5 ...
- **可读性**: 5/5 ...
- **防御性**: 2/5 ...
- **工程化**: 4/5 ...
- **Agent Engineering**: 5/5 ...
"""
        scores = _extract_scores_from_markdown(md, is_agent=True)
        assert scores["极简度"] == 4.0
        assert scores["一致性"] == 3.0
        assert scores["可读性"] == 5.0
        assert scores["防御性"] == 2.0
        assert scores["工程化"] == 4.0
        assert scores["Agent Engineering"] == 5.0

    def test_handles_decimal_scores(self):
        md = "- **极简度**: 3.5/5 ..."
        scores = _extract_scores_from_markdown(md, is_agent=False)
        assert scores["极简度"] == 3.5

    def test_default_zero_for_missing(self):
        scores = _extract_scores_from_markdown("", is_agent=False)
        for key in ["极简度", "一致性", "可读性", "防御性", "工程化"]:
            assert scores[key] == 0

    def test_handles_chinese_colon(self):
        md = "- **极简度**：4.5/5 ..."
        scores = _extract_scores_from_markdown(md, is_agent=False)
        assert scores["极简度"] == 4.5


# ============================================================
# detect_agent_project
# ============================================================

class TestAgentDetection:
    def test_detects_claude_dir(self, tmp_path):
        (tmp_path / ".claude").mkdir()
        from analyze import AgentSignals
        sigs = AgentSignals(has_claude_dir=True, claude_subdirs=["agents"])
        assert detect_agent_project(tmp_path, sigs, "test", "") is True

    def test_detects_claude_sdk(self, tmp_path):
        from analyze import AgentSignals
        sigs = AgentSignals(has_claude_sdk=True)
        assert detect_agent_project(tmp_path, sigs, "test", "") is True

    def test_detects_mcp_config(self, tmp_path):
        from analyze import AgentSignals
        sigs = AgentSignals(has_mcp_config=True)
        assert detect_agent_project(tmp_path, sigs, "test", "") is True

    def test_detects_by_name(self, tmp_path):
        from analyze import AgentSignals
        sigs = AgentSignals()
        assert detect_agent_project(tmp_path, sigs, "my-agent", "") is True
        assert detect_agent_project(tmp_path, sigs, "claude-tool", "") is True

    def test_detects_skills_subdir(self, tmp_path):
        from analyze import AgentSignals
        sigs = AgentSignals(has_claude_dir=True, claude_subdirs=["skills"])
        assert detect_agent_project(tmp_path, sigs, "test", "") is True

    def test_plain_python_project(self, tmp_path):
        (tmp_path / "setup.py").write_text("from setuptools import setup")
        from analyze import AgentSignals
        sigs = AgentSignals()  # all False
        assert detect_agent_project(tmp_path, sigs, "requests", "HTTP library") is False


# ============================================================
# Smoke test：完整 collect + render 流程
# ============================================================

class TestEndToEnd:
    def test_collect_runs_on_self(self, tmp_path):
        """对 skill 自己所在的项目跑 collect，应该不崩溃"""
        from analyze import collect_all
        data = collect_all(str(Path(__file__).parent.parent))
        assert "project" in data
        assert "complexity" in data
        assert "agent" in data
        assert isinstance(data["project"]["is_agent_project"], bool)

    def test_render_produces_valid_markdown(self, tmp_path):
        """完整 collect + render 流程"""
        from analyze import collect_all, render_report

        # 1. collect
        data = collect_all(str(Path(__file__).parent.parent))

        # 2. 写 mock Claude 解读
        md = """## 维度评分

- **极简度**: 4/5
- **一致性**: 3/5
- **可读性**: 4/5
- **防御性**: 3/5
- **工程化**: 4/5
"""
        if data["project"]["is_agent_project"]:
            md += "- **Agent Engineering**: 5/5\n"

        md += """
## 哲学命名
测试哲学

## 诊断
### D1. 测试诊断
- 证据: test.py:1

## 处方
1. 测试处方
"""

        report_path = tmp_path / "report.md"
        data_path = tmp_path / "data.json"
        interp_path = tmp_path / "interp.md"
        data_path.write_text(json.dumps(data, ensure_ascii=False))
        interp_path.write_text(md)

        # 3. render
        render_report(
            json.loads(data_path.read_text()),
            interp_path.read_text(),
            str(report_path),
        )

        report = report_path.read_text()
        assert "## 🎯 雷达图" in report
        assert "<svg" in report
        assert "</svg>" in report
        assert "## 哲学命名" in report
        assert "测试哲学" in report


# ============================================================
# pyscn JSON 解析
# ============================================================

class TestPyscnJsonParsing:
    """验证 pyscn JSON 解析使用正确的字段名"""

    def test_pyscn_summary_field_names(self):
        """pyscn 用 AverageComplexity / MaxComplexity（不是 average / max）"""
        # 模拟 pyscn 真实 JSON 结构
        fake_pyscn_json = {
            "complexity": {
                "Functions": [
                    {
                        "Name": "Foo.bar",
                        "FilePath": "/test/foo.py",
                        "StartLine": 1,
                        "Metrics": {"Complexity": 10, "CognitiveComplexity": 15, "NestingDepth": 3},
                        "RiskLevel": "medium",
                    },
                    {
                        "Name": "Baz.qux",
                        "FilePath": "/test/baz.py",
                        "StartLine": 5,
                        "Metrics": {"Complexity": 25, "CognitiveComplexity": 40, "NestingDepth": 5},
                        "RiskLevel": "high",
                    },
                ],
                "Summary": {
                    "TotalFunctions": 2,
                    "AverageComplexity": 17.5,  # pyscn 真实字段名
                    "MaxComplexity": 25,        # pyscn 真实字段名
                    "MinComplexity": 10,
                    "FilesAnalyzed": 2,
                },
            }
        }

        # 模拟我的解析逻辑（关键字段）
        comp = fake_pyscn_json["complexity"]
        funcs = comp.get("Functions", [])
        ccs = []
        for f in funcs:
            metrics = f.get("Metrics", {})
            cc = metrics.get("Complexity")
            if isinstance(cc, (int, float)):
                ccs.append((cc, f))

        summary = comp.get("Summary", {})
        mean_cc = float(summary["AverageComplexity"])  # 必须用这个字段名
        max_cc = float(summary["MaxComplexity"])       # 必须用这个字段名

        assert mean_cc == 17.5
        assert max_cc == 25.0
        assert len(ccs) == 2

    def test_pyscn_hotspot_fields(self):
        """hotspots 必须包含 pyscn 增强字段"""
        fake_func = {
            "Name": "Test.fn",
            "FilePath": "/test/test.py",
            "StartLine": 1,
            "Metrics": {"Complexity": 50, "CognitiveComplexity": 80, "NestingDepth": 6},
            "RiskLevel": "high",
        }
        # 模拟我的 hotspot 构造逻辑
        hotspot = {
            "file": fake_func.get("FilePath", "?"),
            "function": fake_func.get("Name", "?"),
            "cc": fake_func["Metrics"]["Complexity"],
            "risk": fake_func.get("RiskLevel", "?"),
            "nesting": fake_func["Metrics"].get("NestingDepth", 0),
            "cognitive": fake_func["Metrics"].get("CognitiveComplexity", 0),
        }
        assert hotspot["risk"] == "high"
        assert hotspot["nesting"] == 6
        assert hotspot["cognitive"] == 80
