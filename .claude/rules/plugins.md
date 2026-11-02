---
paths:
  - "plugins/**"
---

# 插件规则

- `plugin.json` 必须位于 `.claude-plugin/`，使用扁平结构；禁止 `category` / `entry_points`。
- `skills` 指向目录（内含 `<name>/SKILL.md`）；`commands` 是平铺的 `.md` 文件数组。
- 研究插件的 MCP 依赖写在插件根目录 `.mcp.json`；可选依赖不要写进必需列表。
- 改插件时同步 `marketplace.json` 与插件自己的 `version`。
- 改完跑 `claude plugin validate .claude-plugin/marketplace.json` 与 `check_references.py`。
