---
hide:
  - navigation
  - toc
---

<div class="hero" markdown>

# Claude Code 使用指南

**基于 Anthropic 官方文档（141 页）与 CHANGELOG（433 个版本）整理的实战手册**

每章先讲**机制**，再给本仓库（`cc_plugins`）的**真实用法**，可直接对照落地。

</div>

<div class="badges" markdown>

[![Claude Code](https://img.shields.io/badge/Claude%20Code-2.1.314-4f46e5)](https://code.claude.com/docs)
[![文档](https://img.shields.io/badge/官方文档-141%20页-0a7d55)](https://code.claude.com/docs/llms.txt)
[![CC Plugins](https://img.shields.io/badge/cc_plugins-6%20个插件-8250df)](https://github.com/gqy20/cc_plugins)

</div>

---

## 🧭 从哪儿开始

<div class="grid cards" markdown>

- :material-compass-outline: **第一次用 Claude Code**

    → [01 能力选型矩阵](cc-guide/01-能力选型矩阵.md)

    12 个扩展层各自管什么，选错就是用错工具。
    先建立这张地图，后面所有配置才有归属。

    [:octicons-arrow-right-24: 开始阅读](cc-guide/01-能力选型矩阵.md)

- :material-chart-line: **会话变慢 / 变贵 / 丢信息**

    → [02 上下文经济学](cc-guide/02-上下文经济学.md)

    上下文窗口怎么被填满的，什么会被压缩掉。
    **本仓库实测：145 个 skill 的 description 合计 46,109 字符，超预算 7.6 倍。**

    [:octicons-arrow-right-24: 开始阅读](cc-guide/02-上下文经济学.md)

- :material-shield-lock-outline: **配置安全边界**

    → [04 权限与护栏](cc-guide/04-权限与护栏.md)

    6 种权限模式、不可绕过的 deny 规则、hooks 策略层。
    **权限规则不是安全边界，沙箱才是 —— 而原生 Windows 上没有沙箱。**

    [:octicons-arrow-right-24: 开始阅读](cc-guide/04-权限与护栏.md)

- :material-bug: **出问题了**

    → [07 排错手册](cc-guide/07-排错手册.md)

    从症状到根因的诊断路径。
    收录了本仓库真实踩过的 6 个坑：frontmatter 解析失败、插件缓存过期、
    `Write` vs `Edit` 规则失效、skill 清单超预算、官方文档自相矛盾、
    以及一条"文档说了但二进制不认"的坑。

    [:octicons-arrow-right-24: 开始阅读](cc-guide/07-排错手册.md)

</div>

---

## 📚 全部章节

| # | 章节 | 解决什么问题 | 何时读 |
|---|------|-------------|--------|
| 01 | [能力选型矩阵](cc-guide/01-能力选型矩阵.md) | 12 个扩展层各自管什么，选错就是"用错工具" | 设计扩展体系前必读 |
| 02 | [上下文经济学](cc-guide/02-上下文经济学.md) | 上下文窗口怎么填满的、什么会被压缩掉 | 会话变慢/变贵/丢信息时 |
| 03 | [提示词与交互技巧](cc-guide/03-提示词与交互技巧.md) | 怎么把意图变成可执行指令 | 每天都在用，但很少有人读完 |
| 04 | [权限与护栏](cc-guide/04-权限与护栏.md) | 6 种权限模式 + 不可绕过的 deny + hooks 策略层 | 配置安全边界时 |
| 05 | [多代理编排](cc-guide/05-多代理编排.md) | subagent / teams / workflows / 跨会话 怎么选 | 任务并行化时 |
| 06 | [插件与市场](cc-guide/06-插件与市场.md) | 插件目录规范、manifest 语义、发布与成本 | 写插件或装插件时 |
| 07 | [排错手册](cc-guide/07-排错手册.md) | 从症状到根因的诊断路径 | 出问题时先查这里 |
| 08 | [演进趋势](cc-guide/08-演进趋势.md) | 从 release 看 Claude Code 下一步往哪走 | 做技术选型时 |

---

## 🎯 三条阅读路径

**新人（1 天）**
[01 能力选型矩阵](cc-guide/01-能力选型矩阵.md) → [03 提示词与交互技巧](cc-guide/03-提示词与交互技巧.md) → [07 排错手册](cc-guide/07-排错手册.md)

**写插件（半天）**
[01 能力选型矩阵](cc-guide/01-能力选型矩阵.md) → [06 插件与市场](cc-guide/06-插件与市场.md) → [04 权限与护栏](cc-guide/04-权限与护栏.md)（hooks 章节）

**调优现有项目（1 小时）**
[02 上下文经济学](cc-guide/02-上下文经济学.md) → [04 权限与护栏](cc-guide/04-权限与护栏.md) → [05 多代理编排](cc-guide/05-多代理编排.md)

---

## 🔍 这套文档是怎么做出来的

**全部数字来自实测，不是估算。** 核心手段是 Claude Code 自己的 `--debug` 日志：

```bash
claude --debug -p "hi"          # 启动一次，读 ~/.claude/debug/<session-id>.txt
uv run --with pyyaml python scripts/measure_context.py   # 精确统计常驻成本
claude plugin details <name>    # 官方自己的插件成本估算
claude plugin validate <path>   # manifest 校验
```

把这套方法论固化成脚本的过程，见 [07 排错手册 · 诊断方法论](cc-guide/07-排错手册.md)。

---

<div class="grid cards" markdown>

- :material-github: **源码**

    [github.com/gqy20/cc_plugins](https://github.com/gqy20/cc_plugins)

    6 个研究专家插件 + 本指南 + 校验脚本

- :material-book-open-variant: **仓库内文档**

    [`docs/cc-guide/`](https://github.com/gqy20/cc_plugins/tree/main/docs/cc-guide)

    Markdown 原文，带 SVG 图，可直接提 PR 修改

</div>
