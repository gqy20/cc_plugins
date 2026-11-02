# AGENTS.md

跨工具共享的仓库约定（Claude Code / Codex / Copilot / Cursor 等都会读取本文件）。

## 文档习惯

- **ROADMAP 只保留未完成和进行中的事项。** 一项完成就把它从路线图删掉，
  不保留“已完成”小节、勾选列表或归档区——完成的内容不进路线图。
- 详细工作约定见 `CLAUDE.md`；项目定位与优先级见 `docs/ROADMAP.md`。

## 项目定位

把 Claude Code 的扩展机制（rules / hooks / policy / plugins）工程化：
研究插件是真实用例，文档与参考实现是可复用方法，校验与 CI 保证结论可复跑。
