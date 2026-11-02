---
paths:
  - "docs/**"
---

# 文档规则

- 数字只写一次；易变快照标日期，能复跑就写命令，不手抄结果。
- 不用 `---` 水平分割线；章节靠标题留白分隔。
- 表格列数必须一致；长标识符允许断行，不要把正文列撑破。
- 新增章节要同步：`mkdocs.yml` 导航、cc-guide 索引、首页章节表、`CLAUDE.md` 的章节表。
- 改完跑：`mkdocs build --strict`、`check_tables.py`、`check_doc_numbers.py`、`check_skill_links.py`。
