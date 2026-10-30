#!/usr/bin/env python3
"""生成 docs/cc-guide/assets/ 下的全部 SVG 插图。

为什么用脚本而不是手写 SVG：
  1. 主题一致 —— 配色、字号、圆角只有一处定义
  2. 深浅色自适应 —— 同一份 SVG 在 light/dark 主题下都可读
  3. 可重生成 —— 改了配色只改这一个文件
  4. 动画统一降级 —— 全部尊重 prefers-reduced-motion

用法：
    python3 scripts/gen_guide_figures.py

输出：
    docs/cc-guide/assets/fig-*.svg        （浅色）
    docs/cc-guide/assets/fig-*.dark.svg   （深色，由前端按主题切换）
"""

from __future__ import annotations

import math
import pathlib

OUT_DIR = pathlib.Path(__file__).resolve().parent.parent / "docs" / "cc-guide" / "assets"
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent


def claude_md_size() -> tuple[int, int]:
    """现读 CLAUDE.md，返回 (行数, 字符数)。

    为什么现读而不是写死：CLAUDE.md 自己一改，写死的数字就过期了 ——
    而这张图会把它印在正文里，比正文还显眼。
    """
    text = (PROJECT_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    return text.count("\n"), len(text)

# --------------------------------------------------------------------------
# 主题 token。
#
# 为什么不靠 `@media (prefers-color-scheme: dark)`：
#   SVG 用 <img> 引用时是**独立文档**，媒体查询只看操作系统/浏览器设置，
#   看不到 MkDocs Material 的主题开关。用户手动切到深色而系统是浅色时，
#   页面是深色的、插图还是浅色的 —— 割裂。
#   所以每张图生成**两份**：`<name>.svg`（浅色）与 `<name>.dark.svg`（深色），
#   由 `docs/javascripts/theme-figures.js` 按页面的 data-md-color-scheme 切换。
# --------------------------------------------------------------------------
TOKENS_LIGHT = """
    --ink:#0f172a; --muted:#64748b; --line:#cbd5e1;
    --panel:#f8fafc; --panel2:#f1f5f9;
    --accent:#4f46e5; --accent-bg:#eef2ff; --accent-line:#c7d2fe;
    --danger:#dc2626; --danger-bg:#fef2f2; --danger-line:#fecaca;
    --warn:#b45309; --warn-bg:#fffbeb; --warn-line:#fde68a;
    --ok:#047857; --ok-bg:#ecfdf5; --ok-line:#a7f3d0;
    --shadow:rgba(15,23,42,.06);
"""

TOKENS_DARK = """
    --ink:#e2e8f0; --muted:#94a3b8; --line:#475569;
    --panel:#1e293b; --panel2:#172033;
    --accent:#a5b4fc; --accent-bg:#312e81; --accent-line:#4f46e5;
    --danger:#fca5a5; --danger-bg:#4c1d1d; --danger-line:#7f1d1d;
    --warn:#fcd34d; --warn-bg:#451a03; --warn-line:#78350f;
    --ok:#6ee7b7; --ok-bg:#064e3b; --ok-line:#065f46;
    --shadow:rgba(0,0,0,.35);
"""

THEME = """
  :root {
__TOKENS__
  }
  text {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
                 "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
    fill: var(--ink);
  }
  /* 字号是按「图在正文列里显示后的实际大小」定的：
     正文列约 740px，图的设计宽度是 960 → 缩放约 0.77。
     所以这里的 15px 在页面上大约是 11.6px，不能再小了。 */
  .t-title  { font-size:22px; font-weight:700; }
  .t-sub    { font-size:15.5px; fill:var(--muted); }
  .t-h      { font-size:17px; font-weight:650; }
  .t-body   { font-size:15px; }
  .t-small  { font-size:13px; fill:var(--muted); }
  .t-mono   { font-family: ui-monospace, SFMono-Regular, "Cascadia Code", Consolas, monospace; font-size:13.5px; }
  .t-badge  { font-size:12.5px; font-weight:700; letter-spacing:.4px; }
  .panel    { fill:var(--panel); stroke:var(--line); stroke-width:1.2; }
  .panel-a  { fill:var(--accent-bg); stroke:var(--accent-line); stroke-width:1.2; }
  .panel-d  { fill:var(--danger-bg); stroke:var(--danger-line); stroke-width:1.2; }
  .panel-w  { fill:var(--warn-bg);   stroke:var(--warn-line);   stroke-width:1.2; }
  .panel-o  { fill:var(--ok-bg);     stroke:var(--ok-line);     stroke-width:1.2; }
  .edge     { stroke:var(--line); stroke-width:1.6; fill:none; }
  .edge-a   { stroke:var(--accent); stroke-width:2; fill:none; }
  .edge-d   { stroke:var(--danger); stroke-width:2; fill:none; }
  .edge-w   { stroke:var(--warn);   stroke-width:2; fill:none; }
  .ink-a    { fill:var(--accent); }
  .ink-d    { fill:var(--danger); }
  .ink-w    { fill:var(--warn); }
  .ink-o    { fill:var(--ok); }
  .ink-m    { fill:var(--muted); }

  /* —— 动画 —— */
  @keyframes dash  { to { stroke-dashoffset:-40; } }
  @keyframes pulse { 0%,100% { opacity:.35; } 50% { opacity:1; } }
  @keyframes rise  { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:none; } }
  @keyframes sweep { from { transform:translateX(-40px); } to { transform:translateX(40px); } }

  .flow    { stroke-dasharray:7 13; animation:dash 1.6s linear infinite; }
  .pulse   { animation:pulse 2.2s ease-in-out infinite; }
  .rise    { animation:rise .5s ease-out both; }
  .rise-2  { animation:rise .5s .12s ease-out both; }
  .rise-3  { animation:rise .5s .24s ease-out both; }
  .rise-4  { animation:rise .5s .36s ease-out both; }
  .sweep   { animation:sweep 2.6s ease-in-out infinite alternate; }

  @media (prefers-reduced-motion: reduce) {
    .flow,.pulse,.rise,.rise-2,.rise-3,.rise-4,.sweep { animation:none; }
  }
"""


_MODE = "light"


def build_theme() -> str:
    """按当前模式生成 <style> 内容。"""
    tokens = TOKENS_LIGHT if _MODE == "light" else TOKENS_DARK
    return THEME.replace("__TOKENS__", tokens)


def svg(w: int, h: int, title: str, desc: str, body: str, extra_style: str = "") -> str:
    """组装一个完整的 SVG 文档。"""
    # 自带底色：图和正文之间有一层明确的"卡片"边界，
    # 文字描边（paint-order）也能借这个底色做遮罩。
    backdrop = f'  <rect width="{w}" height="{h}" fill="var(--panel)"/>\n'
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"
     width="{w}" height="{h}" role="img" aria-labelledby="t d">
  <title id="t">{title}</title>
  <desc id="d">{desc}</desc>
  <style>{build_theme()}{extra_style}</style>
  <defs>
    <marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/>
    </marker>
    <marker id="ah-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="var(--accent)"/>
    </marker>
    <marker id="ah-d" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="var(--danger)"/>
    </marker>
    <filter id="sh" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="var(--shadow)"/>
    </filter>
  </defs>
{backdrop}{body}
</svg>
"""


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(x, y, s, cls="t-body", anchor=None, extra=""):
    a = f' text-anchor="{anchor}"' if anchor else ""
    return f'  <text x="{x}" y="{y}" class="{cls}"{a}{extra}>{esc(s)}</text>'


def rect(x, y, w, h, rx=10, cls="panel", extra=""):
    return f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="{cls}"{extra}/>'


def line(x1, y1, x2, y2, cls="edge", extra=""):
    return f'  <path d="M{x1},{y1} L{x2},{y2}" class="{cls}"{extra}/>'


def path(d, cls="edge", extra=""):
    return f'  <path d="{d}" class="{cls}"{extra}/>'


def badge(x, y, label, kind="a", w=None):
    """右上角的小标签。"""
    w = w or (len(label) * 7.4 + 16)
    bg = {"a": "var(--accent-bg)", "d": "var(--danger-bg)",
          "w": "var(--warn-bg)", "o": "var(--ok-bg)"}[kind]
    fg = {"a": "var(--accent)", "d": "var(--danger)",
          "w": "var(--warn)", "o": "var(--ok)"}[kind]
    return (
        f'  <rect x="{x}" y="{y}" width="{w}" height="20" rx="10" fill="{bg}" stroke="none"/>'
        f'  <text x="{x + w/2}" y="{y + 14}" class="t-badge" text-anchor="middle" fill="{fg}">{esc(label)}</text>'
    )


# ==========================================================================
# 图 1-1 · 同一规则，两种写法，两种强度
# ==========================================================================
def fig_determinism():
    W, H = 960, 400
    b = [f'  <rect width="{W}" height="{H}" fill="none"/>']

    # 左：非确定性
    b.append(rect(40, 60, 400, 280, 14, "panel", ' filter="url(#sh)"'))
    b.append(badge(52, 52, "非确定性 · 靠模型自觉", "w"))
    b.append(txt(60, 100, "写在 CLAUDE.md 里", "t-h"))
    b.append(txt(60, 124, '「永远不要提交 secrets」', "t-mono", extra=' fill="var(--muted)"'))
    b.append(path("M240,140 L240,178", "edge-w", ' marker-end="url(#ah)"'))
    b.append(rect(60, 182, 360, 48, 10, "panel-w"))
    b.append(txt(78, 212, "模型读到这段指令", "t-body"))
    b.append(path("M240,234 L240,268", "edge-w", ' marker-end="url(#ah)"'))
    b.append(rect(60, 272, 360, 48, 10, "panel-w", ' stroke-dasharray="6 4"'))
    b.append(txt(78, 302, "「通常会遵守」—— 但没有保证", "t-body ink-w"))

    # 右：确定性
    b.append(rect(520, 60, 400, 280, 14, "panel", ' filter="url(#sh)"'))
    b.append(badge(532, 52, "确定性 · Claude Code 执行", "d"))
    b.append(txt(540, 100, "写在 permissions.deny 里", "t-h"))
    b.append(txt(540, 124, '"deny": ["Read(*/secrets/*)"]', "t-mono", extra=' fill="var(--muted)"'))
    b.append(path("M740,140 L740,178", "edge-d", ' marker-end="url(#ah)"'))
    b.append(rect(540, 182, 360, 48, 10, "panel-d"))
    b.append(txt(558, 212, "Claude Code 在工具调用前拦截", "t-body"))
    b.append(path("M740,234 L740,268", "edge-d", ' marker-end="url(#ah)"'))
    b.append(rect(540, 272, 360, 48, 10, "panel-d"))
    b.append(txt(558, 302, "「拒绝执行」—— 所有模式都拦得住", "t-body ink-d"))

    # 中缝对比
    b.append(f'  <line x1="480" y1="70" x2="480" y2="330" stroke="var(--line)" stroke-width="1" stroke-dasharray="4 5"/>')
    b.append(rect(456, 160, 48, 48, 24, "panel", ' stroke-width="1.4"'))
    b.append(txt(480, 191, "VS", "t-badge ink-m", "middle"))
    b.append(txt(480, 250, "保护强度", "t-small", "middle"))
    b.append(txt(480, 272, "差一个数量级", "t-small ink-m", "middle"))

    b.append(txt(W/2, 32, "同一条规则，两种写法，保护强度差一个数量级", "t-title", "middle"))
    b.append(txt(W/2, 372, "官方 best-practices：指令机制分「确定性」（权限规则 / hooks / 沙箱）与「非确定性」（CLAUDE.md / skill / prompt 型 hook）",
                 "t-small", "middle"))
    return svg(W, H, "同一规则两种写法的强度对比",
               "左侧把规则写在 CLAUDE.md 里，模型只是「通常会遵守」；右侧写进 permissions.deny，Claude Code 在工具调用前直接拦截。",
               "\n".join(b))


# ==========================================================================
# 图 1-2 · 能力选型决策树
# ==========================================================================
def fig_decision():
    W, H = 960, 620
    b = [f'  <rect width="{W}" height="{H}" fill="none"/>']
    b.append(txt(W/2, 34, "能力选型：先问「这条约束需要多强」", "t-title", "middle"))

    # 起点
    b.append(rect(330, 56, 300, 52, 12, "panel-a", ' filter="url(#sh)"'))
    b.append(txt(480, 88, "需要解决什么问题？", "t-h", "middle"))

    rows = [
        ("绝对不能违反的规则", "permissions.deny", "+ 必要时 command 型 hook", "d", 140),
        ("每次会话都要知道的事实", "CLAUDE.md（< 200 行）", "启动即加载", "a", 210),
        ("只在某类文件上成立", ".claude/rules/ + paths:", "按需加载", "a", 280),
        ("可复用的多步流程", "Skill 或 Subagent", "要不要隔离上下文？", "w", 350),
        ("外部系统的数据", "MCP server", "提供新工具", "a", 420),
        ("确定性的动作编排", "Hook（command 型）", "代码执行", "o", 490),
        ("跨会话 / 跨机器协同", "跨会话消息 或 Workflow", "规模决定", "w", 560),
    ]

    # 主干
    b.append(path("M480,108 L480,140", "edge-a", ' marker-end="url(#ah-a)"'))
    for i, (q, ans, note, kind, y) in enumerate(rows):
        cls = {"d": "panel-d", "a": "panel-a", "w": "panel-w", "o": "panel-o"}[kind]
        ink = {"d": "ink-d", "a": "ink-a", "w": "ink-w", "o": "ink-o"}[kind]
        ec = {"d": "edge-d", "a": "edge-a", "w": "edge-w", "o": "edge-a"}[kind]
        # 左侧：问题
        b.append(rect(60, y, 300, 46, 10, cls))
        b.append(txt(76, y + 28, q, "t-body"))
        # 连接
        b.append(path(f"M360,{y+23} L420,{y+23}", ec, ' marker-end="url(#ah)"'))
        # 右侧：答案
        b.append(rect(420, y, 480, 46, 10, "panel"))
        b.append(txt(438, y + 21, ans, "t-h ink-a" if kind == "a" else f"t-h {ink}"))
        b.append(txt(438, y + 38, note, "t-small"))
        # 主干竖线
        if i < len(rows) - 1:
            b.append(path(f"M480,{y+46} L480,{rows[i+1][4]}", "edge"))
    return svg(W, H, "能力选型决策树",
               "从「需要绝对不能违反的规则」到「跨会话协同」，每类问题对应一个首选机制：permissions.deny、CLAUDE.md、rules+paths、Skill/Subagent、MCP、Hook、跨会话消息或 Workflow。",
               "\n".join(b))


# ==========================================================================
# 图 2-1 · 启动时的上下文预算
# ==========================================================================
def fig_context_budget():
    """图 2-1 · 启动时的上下文预算（全部实测，统一用「字符」作单位）"""
    W, H = 960, 404
    b = [f'  <rect width="{W}" height="{H}" fill="none"/>']
    b.append(txt(W/2, 34, "会话还没开口，skill 清单就已经超预算 7.6 倍", "t-title", "middle"))

    # 全部来自 `claude --debug` 日志，单位统一为「字符」
    md_lines, md_chars = claude_md_size()
    rows = [
        ("skill 清单（145 个 skill 的 description）", 46109, "d",
         "101 用户级 + 23 项目级 + 9 插件 + 内置"),
        (f"CLAUDE.md（项目级，{md_lines} 行）", md_chars, "a",
         "官方建议 ≤ 200 行"),
        ("agent description（15 个生效 / 18 个文件）", 3250, "w",
         "8 用户级 + 3 项目级 + 4 插件"),
    ]
    BUDGET = 6000
    MAXV = max(r[1] for r in rows)
    x0, barw, barh = 50, 860, 30
    scale = barw / MAXV
    bx = x0 + BUDGET * scale

    b.append(txt(x0, 64, "统一单位：字符（chars）。数据源：claude --debug 启动日志。", "t-small"))

    # 预算线先画 —— 行名用描边做遮罩，虚线从字底下穿过去也不影响阅读
    b.append(f'  <path d="M{bx:.1f},86 L{bx:.1f},262" stroke="var(--danger)" '
             f'stroke-width="1.6" stroke-dasharray="5 4" opacity="0.65"/>')

    for i, (name, val, kind, note) in enumerate(rows):
        y = 100 + i * 66
        fill = {"a": "var(--accent-bg)", "w": "var(--warn-bg)", "d": "var(--danger-bg)"}[kind]
        stroke = {"a": "var(--accent)", "w": "var(--warn)", "d": "var(--danger)"}[kind]
        fg = {"a": "var(--accent)", "w": "var(--warn)", "d": "var(--danger)"}[kind]
        # 行名在左、来源说明在同一行右对齐 —— 不占竖向空间，避免串行
        b.append(txt(x0, y - 10, name, "t-body", None,
                     ' paint-order="stroke" stroke="var(--panel)" stroke-width="5"'))
        b.append(txt(x0 + barw, y - 10, note, "t-small", "end"))
        w = max(barw * val / MAXV, 3)
        b.append(f'  <rect x="{x0}" y="{y}" width="{w:.1f}" height="{barh}" rx="6" '
                 f'fill="{fill}" stroke="{stroke}" stroke-width="1.4"/>')
        label = f"{val:,} 字符"
        if w > 170:
            b.append(txt(x0 + w - 12, y + 21, label, "t-h", "end", f' fill="{fg}"'))
        else:
            b.append(txt(x0 + w + 10, y + 21, label, "t-h", "start", f' fill="{fg}"'))

    # 预算线：标签放在线下方，避开左上角的说明文字
    b.append(txt(bx + 8, 284, f"预算 {BUDGET:,} 字符 —— 超出即截断 description", "t-small ink-d"))

    # 结论条
    b.append(rect(x0, 312, 860, 78, 10, "panel-d"))
    b.append(txt(x0 + 18, 338, "Claude Code 自己给出的告警：", "t-h ink-d"))
    b.append(txt(x0 + 18, 360, "Skill listing over budget: 145 skills, 46109 chars > 6000 budget — descriptions will be truncated.",
                 "t-mono ink-d"))
    b.append(txt(x0 + 18, 378, "解法：/skills 停用不用的 skill，或调高 settings 里的 skillListingBudgetFraction。",
                 "t-small"))
    return svg(W, H, "启动时的上下文预算：skill 清单已超预算",
               f"三条横向条形共用同一比例尺，单位为字符：skill 清单 46109 字符（145 个 skill）、"
               f"CLAUDE.md {md_chars} 字符、agent description 3250 字符（15 个生效）。"
               "红色虚线标出 6000 字符的 skill 清单预算线，超出后 description 会被截断。",
               "\n".join(b))


# ==========================================================================
# 图 3-1 · agentic loop
# ==========================================================================
def fig_agentic_loop():
    W, H = 960, 470
    b = [f'  <rect width="{W}" height="{H}" fill="none"/>']
    b.append(txt(W/2, 34, "agentic loop：提示词的作用是让循环更快收敛", "t-title", "middle"))

    cx, cy = 300, 258
    r_node, r_arrow = 116, 158
    nodes = [
        ("收集上下文", "读文件 · 搜代码 · 查文档", -90),
        ("采取行动", "编辑 · 运行 · 调用工具", 30),
        ("验证结果", "跑测试 · 看报错 · 确认", 150),
    ]

    def pt(r, a):
        return (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))

    # 环形箭头：实线打底 + 流动虚线叠加
    for i in range(3):
        a0 = nodes[i][2] + 22
        a1 = nodes[(i + 1) % 3][2] - 22
        x0, y0 = pt(r_arrow, a0)
        x1, y1 = pt(r_arrow, a1)
        d = f"M{x0:.1f},{y0:.1f} A{r_arrow},{r_arrow} 0 0 1 {x1:.1f},{y1:.1f}"
        b.append(path(d, "edge", ' stroke-width="2" opacity="0.55"'))
        b.append(path(d, "edge-a flow", ' stroke-width="3" marker-end="url(#ah-a)"'))

    # 回到起点的反馈箭头
    a0, a1 = 150 + 22, 270 - 22
    x0, y0 = pt(r_arrow, a0)
    x1, y1 = pt(r_arrow, a1)
    d = f"M{x0:.1f},{y0:.1f} A{r_arrow},{r_arrow} 0 0 1 {x1:.1f},{y1:.1f}"
    b.append(path(d, "edge", ' stroke-width="2" opacity="0.55"'))
    b.append(path(d, "edge-w flow", ' stroke-width="3" marker-end="url(#ah)"'))

    for name, note, ang in nodes:
        x, y = pt(r_node, ang)
        b.append(rect(x - 96, y - 32, 192, 64, 12, "panel-a", ' filter="url(#sh)"'))
        b.append(txt(x, y - 4, name, "t-h", "middle"))
        b.append(txt(x, y + 17, note, "t-small", "middle"))

    # 圆心的三行说明要避开下方两个节点框（上边缘在 cy+58）
    b.append(txt(cx, cy - 30, "一个提示", "t-h", "middle"))
    b.append(txt(cx, cy - 8, "→ 一轮轮迭代", "t-small", "middle"))
    b.append(txt(cx, cy + 14, "未完成 → 回到第一步", "t-small ink-w", "middle"))

    # 右侧对比
    bx = 540
    b.append(rect(bx, 90, 380, 150, 12, "panel-d"))
    b.append(txt(bx + 20, 122, "模糊的提示", "t-h ink-d"))
    b.append(txt(bx + 20, 148, "「帮我优化一下这个插件的加载速度」", "t-mono", extra=' fill="var(--muted)"'))
    b.append(txt(bx + 20, 180, "3–5 轮才收敛 · 每轮都贵", "t-body"))
    b.append(txt(bx + 20, 206, "Claude 猜「完成」是什么，顺手改了别的地方", "t-small"))

    b.append(rect(bx, 258, 380, 150, 12, "panel-o"))
    b.append(txt(bx + 20, 290, "精确的提示", "t-h ink-o"))
    b.append(txt(bx + 20, 316, "目标 + 约束 + 验收标准", "t-mono", extra=' fill="var(--muted)"'))
    b.append(txt(bx + 20, 348, "1–2 轮收敛", "t-body"))
    b.append(txt(bx + 20, 374, "「完成」可判定，模型不需要猜", "t-small"))

    b.append(txt(W/2, 436, "官方 best-practices 的原话：Delegate, don't dictate —— 给出目标与验收标准，而不是逐步指令。",
                 "t-small", "middle"))
    return svg(W, H, "agentic loop 三段循环与提示词收敛对比",
               "左侧是一个三段循环：收集上下文、采取行动、验证结果，箭头沿圆周循环，底部一条橙色箭头标出「未完成则回到第一步」。右侧对比模糊提示需要三到五轮收敛，精确提示只需一到两轮。",
               "\n".join(b))


# ==========================================================================
# 图 4-1 · 三层防线
# ==========================================================================
def fig_defense_layers():
    W, H = 960, 500
    b = [f'  <rect width="{W}" height="{H}" fill="none"/>']
    b.append(txt(W/2, 34, "三层防线：越往外越可靠", "t-title", "middle"))

    # 从外到内画矩形（越外层越大）
    layers = [
        (30, 60, 620, 400, "第 3 层 · 外层隔离（容器 / VM）", "唯一真正的安全边界", "d"),
        (80, 110, 520, 300, "第 2 层 · 沙箱 sandbox", "操作系统强制，限制可达文件与主机", "w"),
        (130, 160, 420, 200, "第 1 层 · 权限规则 + 权限模式", "决定「要不要问」和「能不能」", "a"),
    ]
    for x, y, w, h, name, note, kind in layers:
        cls = {"d": "panel-d", "w": "panel-w", "a": "panel-a"}[kind]
        b.append(rect(x, y, w, h, 14, cls, ' opacity="0.55"'))
        b.append(txt(x + 18, y + 28, name, "t-h"))
        b.append(txt(x + 18, y + 48, note, "t-small"))
        # 角标
        b.append(f'  <rect x="{x+w-64}" y="{y+12}" width="52" height="22" rx="6" fill="none" stroke="none"/>')
        b.append(txt(x + w - 18, y + 28, {"d": "最外", "w": "中间", "a": "最内"}[kind], "t-badge", "end"))

    # 第 0 层：模型的意图
    b.append(rect(190, 200, 300, 120, 12, "panel", ' filter="url(#sh)"'))
    b.append(txt(340, 232, "模型想做什么", "t-h", "middle"))
    b.append(txt(340, 256, "CLAUDE.md / skill / 提示词", "t-small", "middle"))
    b.append(txt(340, 284, "只是建议 —— 模型可以不遵守", "t-body ink-w", "middle"))
    b.append(badge(300, 190, "非确定性", "w", 80))

    # 一条被拦下的命令
    b.append(rect(700, 120, 220, 90, 12, "panel-d", ' filter="url(#sh)"'))
    b.append(txt(810, 152, "Bash(curl …)", "t-mono", "middle"))
    b.append(txt(810, 178, "命令真的执行了", "t-small", "middle"))
    b.append(badge(770, 108, "第 2 层拦住", "d", 100))
    b.append(path("M810,214 L810,250", "edge-d", ' marker-end="url(#ah)"'))
    b.append(rect(700, 254, 220, 90, 12, "panel-o", ' filter="url(#sh)"'))
    b.append(txt(810, 286, "被沙箱边界挡住", "t-h ink-o", "middle"))
    b.append(txt(810, 312, "网络只走本机代理", "t-small", "middle"))

    b.append(rect(700, 380, 220, 74, 12, "panel"))
    b.append(txt(810, 410, "本仓库现状", "t-h", "middle"))
    b.append(txt(810, 432, "原生 Windows → 无沙箱", "t-small ink-d", "middle"))

    b.append(txt(W/2, 480, "官方原话：Permission rules are enforced by Claude Code, not by the model.", "t-small", "middle"))
    return svg(W, H, "权限与护栏的三层防线",
               "三层嵌套：最外层是容器或虚拟机的外层隔离，中间是操作系统强制的沙箱，最内层是权限规则与权限模式。模型意图在最内层，只是建议。右侧展示一条命令在第二层被沙箱边界挡住。",
               "\n".join(b))


# ==========================================================================
# 图 5-1 · 四种编排方式对比
# ==========================================================================
def fig_orchestration():
    W, H = 960, 470
    b = [f'  <rect width="{W}" height="{H}" fill="none"/>']
    b.append(txt(W/2, 34, "四种「并行」：计划在谁手里？", "t-title", "middle"))

    panels = [
        ("Subagents", "Claude 逐轮决定", "结果回到 Claude 的上下文", "每轮几个", "a",
         [("主", "主会话"), ("Claude", "决定下一步"), ("worker", "返回摘要")]),
        ("Agent Teams", "lead agent 逐轮决定", "共享任务列表", "几个长跑同伴", "w",
         [("lead", "lead"), ("mate", "mate"), ("mate", "mate")]),
        ("Workflows", "脚本决定", "脚本变量", "几十到几百个", "o",
         [("script", "workflow.js"), ("agent", "agent × N"), ("out", "最终答案")]),
        ("跨会话消息", "你 + 多个会话", "对方的上下文", "同机 / 跨机器", "a",
         [("s1", "会话 A"), ("⇄", "消息"), ("s2", "会话 B")]),
    ]
    pw, gap = 214, 22
    for i, (name, who, where, scale, kind, nodes) in enumerate(panels):
        x = 30 + i * (pw + gap)
        cls = {"a": "panel-a", "w": "panel-w", "o": "panel-o"}[kind]
        b.append(rect(x, 70, pw, 350, 14, cls, ' opacity="0.4"'))
        b.append(rect(x, 70, pw, 46, 14, cls))
        b.append(txt(x + pw/2, 100, name, "t-h", "middle"))
        b.append(txt(x + 16, 142, "谁决定下一步", "t-small"))
        b.append(txt(x + 16, 162, who, "t-body"))
        b.append(txt(x + 16, 190, "中间结果在哪", "t-small"))
        b.append(txt(x + 16, 210, where, "t-body"))
        b.append(txt(x + 16, 238, "规模", "t-small"))
        b.append(txt(x + 16, 258, scale, "t-body"))
        # 节点示意
        ny = 290
        for j, (tag, label) in enumerate(nodes):
            yy = ny + j * 40
            b.append(rect(x + 16, yy, pw - 32, 32, 8, "panel"))
            b.append(txt(x + pw/2, yy + 21, label, "t-small", "middle"))
            if j < len(nodes) - 1:
                b.append(path(f"M{x+pw/2},{yy+32} L{x+pw/2},{yy+40}", "edge-a flow"))

    b.append(rect(30, 434, 900, 1.2, 0, "panel", ' fill="var(--line)" stroke="none"'))
    b.append(txt(W/2, 456, "一句话：需要结果 → Subagent；需要讨论 → Agent Teams；需要可重跑、可审计 → Workflows；需要跨终端交接 → 跨会话消息。",
                 "t-small", "middle"))
    return svg(W, H, "四种并行编排方式对比",
               "四栏对比 Subagents、Agent Teams、Workflows、跨会话消息，分别标注谁决定下一步、中间结果放在哪里、规模上限。",
               "\n".join(b))


# ==========================================================================
# 图 6-1 · 插件目录结构
# ==========================================================================
def fig_plugin_layout():
    W, H = 960, 470
    b = [f'  <rect width="{W}" height="{H}" fill="none"/>']
    b.append(txt(W/2, 34, "插件包的标准骨架", "t-title", "middle"))

    tree = [
        ("plugins/<plugin-name>/", 0, True),
        (".claude-plugin/plugin.json", 1, False),
        ("README.md", 1, False),
        ("agents/*.md", 1, False),
        ("skills/<skill-name>/SKILL.md", 1, False),
        ("commands/*.md", 1, False),
        ("templates/*.md", 1, False),
        ("tools/.mcp.json", 1, False),
    ]
    y = 74
    for label, depth, isroot in tree:
        x = 60 + depth * 34
        if isroot:
            b.append(rect(x - 14, y - 20, 340, 34, 8, "panel-a"))
            b.append(txt(x, y + 4, label, "t-mono ink-a"))
            b.append(badge(x + 250, y - 22, "插件根", "a", 66))
        elif label.startswith(".claude-plugin"):
            b.append(rect(x - 14, y - 20, 400, 34, 8, "panel-d"))
            b.append(txt(x, y + 4, label, "t-mono ink-d"))
            b.append(badge(x + 320, y - 22, "必需 · 官方位置", "d", 130))
        elif label.startswith("skills/"):
            b.append(rect(x - 14, y - 20, 400, 34, 8, "panel-w"))
            b.append(txt(x, y + 4, label, "t-mono ink-w"))
            b.append(badge(x + 320, y - 22, "必须是目录", "w", 110))
        else:
            b.append(txt(x, y + 4, label, "t-mono ink-m"))
        y += 46

    # 右栏：manifest 字段语义
    bx = 560
    b.append(rect(bx, 74, 370, 300, 14, "panel", ' filter="url(#sh)"'))
    b.append(txt(bx + 20, 106, "manifest 字段语义", "t-h"))
    b.append(txt(bx + 20, 134, '"skills"   → 指向目录', "t-mono"))
    b.append(txt(bx + 34, 152, "替换默认扫描", "t-small"))
    b.append(txt(bx + 20, 180, '"commands" → 指向文件', "t-mono"))
    b.append(txt(bx + 34, 198, "平铺的 .md", "t-small"))
    b.append(txt(bx + 20, 226, '"hooks" / "mcpServers" → 合并', "t-mono"))
    b.append(txt(bx + 34, 244, "与用户设置叠加", "t-small"))
    b.append(txt(bx + 20, 272, '"agents" → 指向文件', "t-mono"))
    b.append(txt(bx + 34, 290, "agent 文件", "t-small"))
    b.append(txt(bx + 20, 318, '"outputStyles" / "workflows"', "t-mono"))
    b.append(txt(bx + 34, 336, "替换默认扫描", "t-small"))

    b.append(rect(bx, 388, 370, 56, 10, "panel-d"))
    b.append(txt(bx + 20, 412, "写错是 error，不是 warning", "t-h ink-d"))
    b.append(txt(bx + 20, 432, "claude plugin validate 会当场判死", "t-small"))
    return svg(W, H, "插件目录结构与 manifest 字段语义",
               "左侧是插件包的标准目录骨架，标出 .claude-plugin/plugin.json 与 skills 子目录为关键项；右侧列出 manifest 各字段指向目录还是文件。",
               "\n".join(b))


# ==========================================================================
# 图 7-1 · 排错三段式
# ==========================================================================
def fig_triage():
    W, H = 960, 460
    b = [f'  <rect width="{W}" height="{H}" fill="none"/>']
    b.append(txt(W/2, 34, "排错三段式：症状 → 定位 → 根因", "t-title", "middle"))

    steps = [
        ("1 症状", ["先分清「没加载」还是「加载了但没生效」",
                    "看 /context：到底加载了哪些文件",
                    "看启动告警（无提示 ≠ 没报错）"], "a"),
        ("2 定位", ["claude --debug 读 ~/.claude/debug/<id>.txt",
                    "搜 \"does not recognize or apply\"",
                    "claude plugin validate <目录>"], "w"),
        ("3 根因", ["frontmatter 拼写错 → 字段被静默忽略",
                    "YAML 解析失败 → 整个文件被跳过",
                    "路径写错 → 组件根本没注册"], "d"),
    ]
    pw, gap = 280, 30
    for i, (name, items, kind) in enumerate(steps):
        x = 35 + i * (pw + gap)
        cls = {"a": "panel-a", "w": "panel-w", "d": "panel-d"}[kind]
        b.append(rect(x, 80, pw, 280, 14, cls, ' opacity="0.45"'))
        b.append(rect(x, 80, pw, 46, 14, cls))
        b.append(txt(x + pw/2, 110, name, "t-h", "middle"))
        for j, it in enumerate(items):
            yy = 156 + j * 62
            b.append(txt(x + 18, yy, "· " + it, "t-small"))
        if i < 2:
            b.append(path(f"M{x+pw+5},220 L{x+pw+gap-5},220", "edge-a flow", ' marker-end="url(#ah-a)"'))

    b.append(rect(35, 380, 890, 1.2, 0, "panel", ' fill="var(--line)" stroke="none"'))
    b.append(txt(W/2, 404, "最容易漏的一步：Claude Code 对「认识不了的文件」是静默跳过的 —— 不报错，只写 debug log。",
                 "t-body ink-w", "middle"))
    b.append(txt(W/2, 430, "所以「插件装了但命令没出现」的第一嫌疑永远是 frontmatter 或路径，不是模型不听话。",
                 "t-small", "middle"))
    return svg(W, H, "排错三段式流程",
               "三步：先看症状分清未加载还是未生效，再用 debug 日志与 plugin validate 定位，最后对照三类典型根因：frontmatter 字段拼错、YAML 解析失败、路径写错。",
               "\n".join(b))


# ==========================================================================
# 图 8-1 · 八条演进主线（时间轴 + 强度）
#
# 数据来源：
#   anthropics/claude-code 的 CHANGELOG.md —— 433 个版本 / 8,442 条变更条目。
#   每个版本在 npm registry 上的发布日期（2025-03 ~ 2026-10，共 20 个月）。
#   强度 = 该主线关键词在当月 CHANGELOG 条目中的命中条数（按各主线自身最大值归一）。
# ==========================================================================
EVO_MONTHS = [
    "2025-03", "2025-04", "2025-05", "2025-06", "2025-07", "2025-08",
    "2025-09", "2025-10", "2025-11", "2025-12", "2026-01", "2026-02",
    "2026-03", "2026-04", "2026-05", "2026-06", "2026-07", "2026-08",
    "2026-09", "2026-10",
]

# (序号, 名称, 语义组, 锚点版本, 锚点日期, 每月命中条目数, 关键词)
EVO_THREADS = [
    ("1", "权限判权", "d", "v2.1.302", "2026-10-16",
     [0, 1, 0, 0, 0, 0, 1, 0, 1, 4, 5, 7, 19, 32, 20, 21, 25, 44, 99, 83],
     "auto mode / classifier / managed settings"),
    ("2", "护栏下沉", "d", "v2.0.24", "2025-10-20",
     [0, 0, 0, 0, 1, 0, 1, 3, 2, 0, 4, 6, 20, 19, 9, 13, 7, 30, 52, 62],
     "sandbox / permissionDecision / PreToolUse"),
    ("3", "可编程性", "a", "v2.0.12", "2025-10-09",
     [0, 0, 0, 1, 13, 3, 4, 23, 14, 9, 51, 41, 107, 107, 127, 82, 91, 109, 337, 416],
     "skill / subagent / plugin / workflow / mods"),
    ("4", "并行实体", "w", "v2.1.32", "2026-02-05",
     [0, 0, 0, 0, 2, 2, 2, 6, 5, 4, 22, 34, 54, 49, 53, 66, 99, 77, 123, 116],
     "agent teams / teammate / cross-session / fork"),
    ("5", "上下文预算", "w", "v0.2.47", "2025-03-18",
     [1, 1, 1, 4, 4, 3, 3, 4, 1, 7, 32, 24, 45, 44, 35, 18, 23, 51, 97, 97],
     "compaction / context window / prompt cache"),
    ("6", "插件生态", "a", "v2.1.269", "2026-09-11",
     [0, 0, 0, 0, 0, 0, 0, 7, 0, 3, 5, 2, 28, 25, 31, 14, 2, 28, 83, 35],
     "marketplace / plugin eval / relevance / dependencies"),
    ("7", "客户端平台", "o", "v2.0.0", "2025-09-29",
     [1, 0, 2, 1, 9, 0, 6, 13, 4, 17, 32, 35, 109, 84, 84, 61, 66, 166, 566, 326],
     "VS Code / JetBrains / desktop / web / claude.ai"),
    ("8", "质量可观测", "o", "v1.0.39", "2025-07-01",
     [1, 0, 2, 1, 2, 2, 2, 1, 1, 2, 6, 6, 7, 21, 21, 6, 18, 24, 50, 56],
     "/doctor / OpenTelemetry / --debug"),
]

EVO_GROUPS = [
    ("d", "安全边界"),
    ("a", "扩展机制"),
    ("w", "运行时"),
    ("o", "交付形态"),
]


def _evo_date_x(date_str: str, x0: float, mw: float) -> float:
    """发布日期 → 时间轴 x 坐标（按天插值到月格内）。"""
    y, m, d = (int(x) for x in date_str.split("-"))
    idx = (y - 2025) * 12 + (m - 3)
    days = [31, 29 if y % 4 == 0 and (y % 100 != 0 or y % 400 == 0) else 28,
            31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    frac = (d - 1) / days[m - 1]
    return x0 + (idx + frac) * mw


def fig_evolution():
    W, H = 960, 420
    X0, MW, NM = 178.0, 35.0, len(EVO_MONTHS)
    PLOT = X0 + MW * NM                       # 878
    ROW_H, TOP = 34, 72

    b = [f'  <rect width="{W}" height="{H}" fill="none"/>']
    b.append(txt(W / 2, 30, "八条演进主线：一条比一条陡", "t-title", "middle"))
    b.append(txt(W / 2, 52,
                 "433 个版本 · 8,442 条变更 · 横轴=版本发布日期（2025-03 → 2026-10）· "
                 "柱高=当月该主线关键词命中条目数",
                 "t-small", "middle"))

    # 竖向季度网格
    for i in range(NM):
        if i % 3 == 0:
            gx = X0 + i * MW
            b.append(path(f"M{gx:.1f},66 L{gx:.1f},344", "edge",
                          ' stroke="var(--line)" stroke-width="1" opacity="0.5"'))

    for i, (num, name, kind, anchor, adate, counts, _kw) in enumerate(EVO_THREADS):
        top = TOP + i * ROW_H
        track = top + 28
        fg = {"a": "var(--accent)", "d": "var(--danger)",
              "w": "var(--warn)", "o": "var(--ok)"}[kind]
        bg = {"a": "var(--accent-bg)", "d": "var(--danger-bg)",
              "w": "var(--warn-bg)", "o": "var(--ok-bg)"}[kind]

        # 左栏：序号圆点 + 名称 + 锚点版本
        b.append(f'  <circle cx="32" cy="{top + 13}" r="11" fill="{bg}" stroke="{fg}" stroke-width="1.2"/>')
        b.append(txt(32, top + 17, num, "t-badge", "middle", f' fill="{fg}"'))
        b.append(txt(50, top + 17, name, "t-h"))
        b.append(txt(50, top + 30, anchor, "t-mono", "start", ' fill="var(--muted)"'))

        # 轨道
        b.append(path(f"M{X0},{track} L{PLOT:.1f},{track}", "edge",
                      ' stroke="var(--line)" stroke-width="1" opacity="0.55"'))

        # 月度强度柱
        mx = max(counts) or 1
        for j, n in enumerate(counts):
            if n <= 0:
                continue
            h = max(1.6, 19.0 * (n / mx) ** 0.62)
            bx = X0 + j * MW + 3
            b.append(f'  <rect x="{bx:.1f}" y="{track - h:.1f}" width="29" '
                     f'height="{h:.1f}" rx="2.5" fill="{fg}" opacity="{0.45 + 0.55 * n / mx:.2f}"/>')

        # 锚点：关键版本
        ax = _evo_date_x(adate, X0, MW)
        b.append(f'  <circle cx="{ax:.1f}" cy="{track}" r="4.6" fill="{fg}" '
                 f'stroke="var(--panel)" stroke-width="1.6"/>')

        # 右栏：累计命中条目数
        b.append(txt(942, track + 4, f"{sum(counts):,}", "t-mono", "end"))

    # 时间轴刻度（季度）
    for i in range(NM):
        if i % 3 == 0:
            lx = X0 + i * MW + 1
            b.append(txt(lx, 360, EVO_MONTHS[i][2:].replace("-", "/"), "t-small"))
    b.append(txt(PLOT, 360, "26/10", "t-small", "end"))
    b.append(txt(942, 360, "累计条目", "t-small", "end"))

    # 图例
    lx = 22
    for kind, gname in EVO_GROUPS:
        fg = {"a": "var(--accent)", "d": "var(--danger)",
              "w": "var(--warn)", "o": "var(--ok)"}[kind]
        b.append(f'  <rect x="{lx}" y="379" width="11" height="11" rx="2.5" fill="{fg}"/>')
        b.append(txt(lx + 16, 389, gname, "t-small"))
        lx += 26 + len(gname) * 12
    b.append(f'  <circle cx="{lx + 5}" cy="384" r="4.4" fill="var(--muted)" '
             f'stroke="var(--panel)" stroke-width="1.4"/>')
    b.append(txt(lx + 15, 389, "该主线标志性能力落地的版本", "t-small"))

    b.append(txt(W / 2, 409,
                 "共同指向一件事：Claude Code 正从一个「会写代码的 CLI」变成一个「可编程的工作流平台」。",
                 "t-small", "middle"))
    return svg(W, H, "Claude Code 八条演进主线的时间轴与强度",
               "横向时间轴从 2025-03 到 2026-10 共 20 个月，纵向八条主线：权限判权、护栏下沉、"
               "可编程性、并行实体、上下文预算、插件生态、客户端平台、质量可观测。每条主线上方的柱形"
               "高度代表该月 CHANGELOG 中命中该主线关键词的条目数，圆点标出标志性能力落地的版本，"
               "右栏为累计命中条目数。颜色分四组：安全边界、扩展机制、运行时、交付形态。",
               "\n".join(b))


FIGURES = {
    "fig-determinism.svg": fig_determinism,
    "fig-decision.svg": fig_decision,
    "fig-context-budget.svg": fig_context_budget,
    "fig-agentic-loop.svg": fig_agentic_loop,
    "fig-defense-layers.svg": fig_defense_layers,
    "fig-orchestration.svg": fig_orchestration,
    "fig-plugin-layout.svg": fig_plugin_layout,
    "fig-triage.svg": fig_triage,
    "fig-evolution.svg": fig_evolution,
}


def main() -> None:
    global _MODE
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, fn in FIGURES.items():
        stem = name[: -len(".svg")]
        for mode, suffix in (("light", ""), ("dark", ".dark")):
            _MODE = mode
            svg_text = fn()
            # 自检：标题/描述存在、无未闭合标签
            assert "<title" in svg_text and "<desc" in svg_text, name
            assert svg_text.count("<svg") == 1 and svg_text.rstrip().endswith("</svg>"), name
            out = OUT_DIR / f"{stem}{suffix}.svg"
            out.write_text(svg_text, encoding="utf-8")
            print(f"  ✔ {out.name}  ({len(svg_text):,} bytes)")


if __name__ == "__main__":
    main()
