"""agent-policy 引擎的边界测试（不依赖 Claude Code）。"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

PLUGIN = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("agent_policy", PLUGIN / "scripts" / "policy.py")
policy = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(policy)


class PolicyEngineTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def write_policy(self, text: str) -> None:
        (self.root / "agent-policy.toml").write_text(text, encoding="utf-8")

    def ctx(self, **overrides):
        data = {"hook_event_name": "PreToolUse", "tool_name": "Read", "tool_input": {}}
        data.update(overrides)
        return policy.context_from_input(data)

    def test_outside_workspace(self) -> None:
        self.assertTrue(policy.is_outside("../outside.txt", self.root))
        self.assertFalse(policy.is_outside("src/app.py", self.root))

    def test_path_rule_matches_relative_and_absolute(self) -> None:
        rule = {
            "id": "secrets",
            "when": {"event": "pre", "tool": "Read", "path": ["secrets/**", "**/secrets/**"]},
            "then": {"action": "deny"},
        }
        self.assertTrue(policy.matches(rule, self.ctx(tool_input={"file_path": "secrets/a.env"}), self.root))
        absolute = str(self.root / "secrets/a.env")
        self.assertTrue(policy.matches(rule, self.ctx(tool_input={"file_path": absolute}), self.root))
        self.assertFalse(policy.matches(rule, self.ctx(tool_input={"file_path": "src/app.py"}), self.root))

    def test_deny_dominates_ask(self) -> None:
        rules = [
            {"id": "ask", "when": {"event": "pre", "tool": "Bash"}, "then": {"action": "ask"}},
            {"id": "deny", "when": {"event": "pre", "tool": "Bash"}, "then": {"action": "deny", "reason": "no"}},
        ]
        action, reason = policy.decide(rules, self.ctx(tool_name="Bash"), self.root)
        self.assertEqual((action, reason), ("deny", "no"))

    def test_preset_merge_and_project_override(self) -> None:
        self.write_policy(
            'version = 1\n'
            'extends = ["recommended"]\n'
            '[[rule]]\n'
            'id = "no-secrets-access"\n'
            'when = { event = "pre", tool = "Read" }\n'
            'then = { action = "ask", reason = "override" }\n'
        )
        rules, _, errors = policy.load_policy(self.root)
        self.assertEqual(errors, [])
        merged = {r["id"]: r for r in rules}
        self.assertEqual(merged["no-secrets-access"]["then"]["action"], "ask")
        self.assertIn("no-write-outside-workspace", merged)

    def test_malformed_toml_reports_error(self) -> None:
        self.write_policy("version = [")
        rules, _, errors = policy.load_policy(self.root)
        self.assertEqual(rules, [])
        self.assertTrue(errors)

    def test_run_rules_report_failure(self) -> None:
        rules = [
            {"id": "c", "when": {"event": "post", "tool": "Edit"}, "then": {"run": "exit 3", "fail": "closed"}},
            {"id": "o", "when": {"event": "post", "tool": "Edit"}, "then": {"run": "exit 3", "fail": "open"}},
        ]
        ctx = self.ctx(hook_event_name="PostToolUse", tool_name="Edit")
        results = policy.run_rules(rules, ctx, self.root)
        self.assertEqual([ok for _, ok, _ in results], [False, False])

    def test_hook_pre_deny_emits_json(self) -> None:
        self.write_policy(
            'version = 1\n'
            '[[rule]]\n'
            'id = "no"\n'
            'when = { event = "pre", tool = "Read", path = "secrets/**" }\n'
            'then = { action = "deny", reason = "blocked" }\n'
        )
        data = '{"hook_event_name":"PreToolUse","tool_name":"Read","tool_input":{"file_path":"secrets/a.env"}}'
        out = io.StringIO()
        with mock.patch("sys.stdin", io.StringIO(data)), contextlib.redirect_stdout(out):
            code = policy.cmd_hook(argparse.Namespace(event="pre", project=str(self.root)))
        self.assertEqual(code, 0)
        payload = json.loads(out.getvalue())
        self.assertEqual(payload["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertEqual(payload["hookSpecificOutput"]["permissionDecisionReason"], "blocked")

    def test_hook_post_fail_closed_blocks(self) -> None:
        self.write_policy(
            'version = 1\n'
            '[[rule]]\n'
            'id = "c"\n'
            'when = { event = "post", tool = "Edit" }\n'
            'then = { run = "exit 3", fail = "closed" }\n'
        )
        data = '{"hook_event_name":"PostToolUse","tool_name":"Edit","tool_input":{"file_path":"a.txt"}}'
        with mock.patch("sys.stdin", io.StringIO(data)):
            code = policy.cmd_hook(argparse.Namespace(event="post", project=str(self.root)))
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
