"""把章节页的 h1 拆成「章号徽章 + 标题」。

为什么在构建期改，而不是用 JS 改 DOM：
- `navigation.instant` 会整块替换 `<article>`，前端改写得靠 MutationObserver 兜底，
  而且首屏会先闪一下「02 · 上下文经济学」再跳成徽章；
- 构建期改完，HTML 里就是最终形态 —— 打印、禁用 JS、instant 导航表现一致。

只匹配「NN · 标题」这种形状：8 个章节页命中，首页和 README 的 h1 不受影响。
锚点 id 原样保留（改的是 h1 内部结构，不是标题文本）。

用法（在 mkdocs.yml 里）：

    hooks:
      - scripts/mkdocs_chapter_head.py
"""

from __future__ import annotations

import logging
import re

log = logging.getLogger("mkdocs.plugins")

# 形如 <h1 id="02-上下文经济学">02 · 上下文经济学<a class="headerlink" …>&para;</a></h1>
_H1 = re.compile(
    r'<h1 id="(?P<id>[^"]+)">'
    r"\s*(?P<no>\d{2})\s*·\s*(?P<title>[^<]+?)\s*"
    r'(?P<link><a class="headerlink".*?</a>)?'
    r"</h1>",
    re.DOTALL,
)

# 章号没写够两位（或写成别的分隔符）时的兜底检查
_LOOSE_H1 = re.compile(r'<h1 id="[^"]+">\s*\d{1,3}\s*[·.\-–—|]\s*[^<]+')


def _split(m: re.Match[str]) -> str:
    return (
        f'<h1 id="{m["id"]}" class="cc-chapter-h1">'
        f'<span class="cc-chapter-no">{m["no"]}</span>'
        f'<span class="cc-chapter-title">{m["title"]}</span>'
        f'{m["link"] or ""}'
        "</h1>"
    )


def on_page_content(html: str, **_: object) -> str:
    """MkDocs hook：改写渲染后的页面 HTML。"""
    new_html = _H1.sub(_split, html)

    # 章号形状不对（比如写成 "2 · 标题"）时提醒一句 ——
    # `mkdocs build --strict` 会把 warning 变成构建失败，改错格式不会静默溜过去。
    if _LOOSE_H1.search(new_html):
        log.warning(
            "章节 h1 的形状不是「NN · 标题」，章号徽章没有生效："
            "请检查是不是章号没写够两位，或者分隔符被换掉了。"
        )

    return new_html
