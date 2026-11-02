---
paths:
  - ".claude/hooks/**"
---

# Hook 规则

- 这套脚本是参考库，不在本仓库注册；新增脚本要加 `examples/` 样例并跑 `scripts/test_hooks.py`。
- 只有 `exit 2` 会阻断；`exit 1` 是非阻断错误。
- 写状态要幂等；空状态用 `// {}` 兜底。
- 依赖缺失时静默跳过，不要因为没装 `aplay` / `curl` 让会话报错。
- 测试外部命令用 `ERR_CATCHER_DRY_RUN=1` 之类的开关，避免真的发包。
