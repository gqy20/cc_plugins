"""给 MkDocs 生成中文友好的标题锚点。

默认的 slugify 会把中文和 emoji 全部丢掉 —— "📊 启动时就已经占掉的部分"
会变成 `_1`，站内链接全部失效。

`pymdownx.slugs._uslugify` 保留了中文，但会留下 emoji 后面那个空格变成的前导 `-`。
这个模块在它基础上做三件事：

1. 去掉 emoji 与装饰性符号
2. 去掉首尾多余的分隔符
3. 小写化 ASCII，保留中文原样

用法（在 mkdocs.yml 里）：

    markdown_extensions:
      - toc:
          slugify: !!python/name:scripts.mkdocs_slug.slugify
"""

from __future__ import annotations

import re
import unicodedata

# emoji 与常见装饰符号（Variation Selector-16、ZWJ 等一并清掉）
_DECOR = re.compile(
    "["
    "\U0001f000-\U0001faff"   # emoji 主区
    "\U00002600-\U000027bf"   # 杂项符号与箭头
    "\U00002b00-\U00002bff"   # 箭头补充
    "\U0000fe00-\U0000fe0f"   # 变体选择符
    "\U0000200d"              # 零宽连接符
    "\U00002100-\U000021ff"   # 带字母符号
    "★☆✅❌⚠️⚡→←↑↓⇒•·※"
    "]",
    flags=re.UNICODE,
)

# 连续空白 / 分隔符
_SEP = re.compile(r"[\s　]+")


def slugify(text: str, sep: str = "-", case: str = "none", **_: object) -> str:
    """生成锚点 id。

    参数签名与 MkDocs `toc` 扩展期望的一致：
    ``slugify(text, sep, case)``。
    """
    # 1. 去掉 emoji / 装饰符号
    s = _DECOR.sub("", text)

    # 2. 规范化 + 折叠空白
    s = unicodedata.normalize("NFKC", s)
    s = _SEP.sub(sep, s.strip())

    # 3. 只保留可安全放进 URL 的字符（保留中文与字母数字）
    s = re.sub(r"[^\w一-鿿" + re.escape(sep) + r"]", sep, s, flags=re.UNICODE)

    # 4. 折叠重复分隔符、去掉首尾分隔符
    s = re.sub(re.escape(sep) + r"{2,}", sep, s)
    s = s.strip(sep)

    # 5. 大小写
    if case == "lower":
        s = s.lower()
    elif case == "upper":
        s = s.upper()

    return s
