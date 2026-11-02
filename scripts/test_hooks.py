#!/usr/bin/env python3
"""对 .claude/hooks/ 的参考脚本做冒烟测试。

在临时项目里建好状态目录，按 examples/*.json 逐个喂 stdin，
断言退出码为 0。依赖外部服务的脚本显式跳过（不联网）。

用法：
    python3 scripts/test_hooks.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOKS = ROOT / ".claude" / "hooks"
EXAMPLES = HOOKS / "examples"

# (脚本, 样例事件, 解释器)
CASES = [
    ("session-start.sh", "session-start.json", "bash"),
    ("fix-reasoning.sh", "session-start.json", "bash"),
    ("check-pdf-updates.sh", "user-prompt-submit.json", "bash"),
    ("intent-detect.sh", "user-prompt-submit.json", "bash"),
    ("update-status.sh", "user-prompt-submit.json", "bash"),
    ("track-skills-change.sh", "post-tool-use-write.json", "bash"),
    ("capture-reasoning.sh", "post-tool-use-write.json", "bash"),
    ("check-skills-limit.sh", "post-tool-use-write.json", "bash"),
    ("update-reasoning-on-task.sh", "post-tool-use-task.json", "bash"),
    ("detect-task-complete.sh", "post-tool-use-task.json", "bash"),
    ("response-complete.sh", "stop.json", "bash"),
    ("task-complete.sh", "stop.json", "bash"),
    ("err-catcher.py", "post-tool-use-bash-error.json", "python3"),
]

# 需要网络、常驻服务或人工参数的脚本，不在 CI 里跑
SKIPPED = {
    "notify.sh": "会向 ntfy.sh 发请求",
    "notify-server.py": "常驻 HTTP 服务",
    "start-notify-server.sh": "常驻 HTTP 服务",
    "archive-low-frequency-skills.sh": "手动工具，需要参数",
    "promote-to-proven.sh": "手动工具，需要参数",
}


def make_project() -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="hooks-smoke-"))
    (tmp / ".info").mkdir()
    (tmp / "info").mkdir()
    (tmp / ".claude/skills/u_demo").mkdir(parents=True)
    (tmp / "01_articles").mkdir()
    (tmp / "results/1").mkdir(parents=True)

    (tmp / ".info/tasks.json").write_text('{"tasks":{},"proven_skills":{}}', encoding="utf-8")
    (tmp / ".info/.status.json").write_text('{"profile_fresh":true}', encoding="utf-8")
    (tmp / ".info/usr.json").write_text(
        '{"basic_info":{"name":"Test","role":"QA"}}', encoding="utf-8"
    )
    (tmp / ".info/info.md").write_text("## 路由规则\n先查 07\n", encoding="utf-8")
    (tmp / ".claude/skills/u_demo/SKILL.md").write_text("# demo\n", encoding="utf-8")
    (tmp / "01_articles/demo.pdf").write_text("pdf", encoding="utf-8")
    (tmp / "results/1/.reasoning.md").write_text("# reasoning\n", encoding="utf-8")
    return tmp


def run_case(script: str, example: str, interpreter: str, project: Path) -> tuple[int, str]:
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(project)
    env["ERR_CATCHER_DRY_RUN"] = "1"
    proc = subprocess.run(
        [interpreter, str(HOOKS / script)],
        input=(EXAMPLES / example).read_text(encoding="utf-8"),
        text=True,
        capture_output=True,
        env=env,
        cwd=str(project),
        timeout=30,
    )
    return proc.returncode, (proc.stderr or "").strip()


def main() -> int:
    if not HOOKS.is_dir():
        print(f"未找到 {HOOKS}")
        return 1

    project = make_project()
    failed = 0
    try:
        for script, example, interpreter in CASES:
            code, err = run_case(script, example, interpreter, project)
            if code == 0:
                print(f"✅ {script}（{example}）")
            else:
                failed += 1
                print(f"❌ {script}（{example}）exit={code}")
                if err:
                    print(f"   {err.splitlines()[-1]}")
    finally:
        shutil.rmtree(project, ignore_errors=True)

    for script, reason in SKIPPED.items():
        print(f"⏭️  {script}：{reason}")

    if failed:
        print(f"\n{failed} 个脚本冒烟失败")
        return 1
    print(f"\n✅ {len(CASES)} 个脚本冒烟通过（跳过 {len(SKIPPED)} 个）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
