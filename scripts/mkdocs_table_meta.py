"""给变更日志表补列标签，并把「版本（日期）」拆成两行。

为什么在构建期改，而不是用 JS 改 DOM：同 mkdocs_chapter_head.py ——
`navigation.instant` 会整块替换 `<article>`，前端改写要靠 MutationObserver 兜底，
而且首屏会先闪一下旧样子。

改三件事（都不动表格里的文字）：

1. 表头里有「变更条目」的表 = 变更日志表，表格外包一层 `.cc-changelog`。
   08 章的证据表都是这类表：三列，第二列是一整段上游 CHANGELOG 原文，
   窄屏上只能横着拖 600px 才看得全 —— 靠这个类名换成卡片流（见 extra.css）。
2. 每个单元格补 `data-label`（表头文字）—— 卡片流用它当小标题，
   读者不用记住列序。
3. `<code>v2.0.68</code>（2025-12-12）` 拆成版本号 + `<time>` 日期。
   挤在一格里时，日期会从连字符处断成「（2026-04-」+「22）」——
   桌面端也断，因为连字符本来就是合法的断行点。

用法（在 mkdocs.yml 里）：

    hooks:
      - scripts/mkdocs_chapter_head.py
      - scripts/mkdocs_table_meta.py
"""

from __future__ import annotations

import html as html_lib
import logging
import re

log = logging.getLogger("mkdocs.plugins")

# Python-Markdown 的表格扩展吐出的结构是固定的：
# <table>\n<thead>\n<tr><th>…</th></tr>\n</thead>\n<tbody>\n<tr><td>…</td></tr>\n</tbody>\n</table>
_TABLE = re.compile(
    r"<table>\s*<thead>(?P<head>.*?)</thead>\s*<tbody>(?P<body>.*?)</tbody>\s*</table>",
    re.DOTALL,
)
_ROW = re.compile(r"<tr>(?P<row>.*?)</tr>", re.DOTALL)
_CELL = re.compile(r"<td(?P<attrs>(?:\s[^>]*)?)>(?P<body>.*?)</td>", re.DOTALL)
_TH = re.compile(r"<th(?:\s[^>]*)?>(?P<body>.*?)</th>", re.DOTALL)
_TAG = re.compile(r"<[^>]+>")

# <td><code>v2.0.68</code>（2025-12-12）</td>
_VER = re.compile(
    r"^\s*<code>(?P<ver>[^<]+)</code>\s*（(?P<date>\d{4}-\d{2}-\d{2})）\s*$"
)
# <td>2025-06-30</td>
_BARE_DATE = re.compile(r"^\s*(?P<date>\d{4}-\d{2}-\d{2})\s*$")

# 变更日志表的标志性列 —— 首列是「版本」且有这列的表才按卡片流排。
# 光看「变更条目」会误伤统计表（阶段 | 版本数 | 变更条目 | …），那张表的
# 三列都是数字，卡片流反而不如表格清楚。
_ENTRY_COL = "变更条目"
_VER_COL = "版本"


def _labels(head: str) -> list[str]:
    """表头文字（去掉标签和空白）。"""
    out = []
    for m in _TH.finditer(head):
        text = _TAG.sub("", m.group("body"))
        out.append(html_lib.unescape(text).strip())
    return out


def _rewrite_cell(body: str) -> str:
    """把单元格里的版本+日期、裸日期换成不折行的结构。"""
    m = _VER.match(body)
    if m:
        ver = html_lib.escape(m.group("ver"), quote=False)
        date = m.group("date")
        return (
            f'<code class="cc-ver">{ver}</code>'
            f'<time class="cc-date" datetime="{date}">{date}</time>'
        )

    m = _BARE_DATE.match(body)
    if m:
        date = m.group("date")
        return f'<time class="cc-nb" datetime="{date}">{date}</time>'

    return body


def _rewrite_body(body: str, labels: list[str], is_log: bool) -> str:
    """逐行重写单元格：补 data-label、拆版本+日期。"""
    out = []
    last = 0
    for row in _ROW.finditer(body):
        out.append(body[last : row.start()])
        out.append(_rewrite_row(row.group("row"), labels, is_log))
        last = row.end()
    out.append(body[last:])
    return "".join(out)


def _rewrite_row(row: str, labels: list[str], is_log: bool) -> str:
    out = []
    last = 0
    for i, cell in enumerate(_CELL.finditer(row)):
        out.append(row[last : cell.start()])
        out.append(_rewrite_cell_tag(cell, labels, i, is_log))
        last = cell.end()
    out.append(row[last:])
    return "<tr>" + "".join(out) + "</tr>"


def _rewrite_cell_tag(
    cell: re.Match[str], labels: list[str], index: int, is_log: bool
) -> str:
    attrs = cell.group("attrs")
    label = labels[index] if index < len(labels) else ""

    if is_log and label:
        attrs += f' data-label="{html_lib.escape(label, quote=True)}"'
        if label == _ENTRY_COL:
            # 原文列的行内 code 会按行断开边框，样式单独挂一个类
            attrs += ' class="cc-entry"'

    return f"<td{attrs}>{_rewrite_cell(cell.group('body'))}</td>"


def on_page_content(html: str, **_: object) -> str:
    """MkDocs hook：改写渲染后的页面 HTML。"""

    def repl(m: re.Match[str]) -> str:
        labels = _labels(m.group("head"))
        is_log = bool(labels) and labels[0] == _VER_COL and _ENTRY_COL in labels
        body = _rewrite_body(m.group("body"), labels, is_log)
        table = f"<table><thead>{m.group('head')}</thead><tbody>{body}</tbody></table>"
        if is_log:
            return f'<div class="cc-changelog">{table}</div>'
        return table

    new_html = _TABLE.sub(repl, html)

    # 表头和表体的列数对不上时提醒一句 ——
    # `mkdocs build --strict` 会把 warning 变成构建失败，
    # 免得 data-label 错位之后卡片流把标题安到别的列上。
    for m in _TABLE.finditer(new_html):
        labels = _labels(m.group("head"))
        for row in _ROW.finditer(m.group("body")):
            n = len(_CELL.findall(row.group("row")))
            if n and n != len(labels):
                log.warning(
                    "表格的表头列数（%d）和表体列数（%d）对不上：%s",
                    len(labels),
                    n,
                    " / ".join(labels),
                )

    return new_html
