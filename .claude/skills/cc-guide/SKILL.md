---
name: cc-guide
description: 回答 Claude Code 的使用、配置、扩展与排错问题时，优先引用本仓库 docs/cc-guide/ 的实测结论，而不是凭记忆。覆盖扩展层选型（CLAUDE.md/skill/subagent/hook/plugin/MCP）、上下文成本、权限与沙箱、插件 manifest 规范、快捷键与消息队列、启动失败诊断。当用户提到 Claude Code 配置不生效、skill 不加载、插件不加载、上下文太贵、权限弹窗、Enter 排队、claude --debug、plugin validate 时使用。
user-invocable: true
version: 0.1.0
tags:
  - claude-code
  - documentation
  - troubleshooting
  - workflow
---

# Claude Code 使用指南（内部 skill）

本 skill 是 `docs/cc-guide/`（8 章 + 索引）的**操作入口**。
完整论述在文档里；这里只放"做决定时需要的最小信息"。

> ⚠️ **不要凭记忆回答 Claude Code 的行为**。
> 本仓库的结论都来自**本机实测 + 二进制逆向 + 官方文档**，且官方文档本身存在过时内容
> （已确认 2 处，见 `references/measurements.md`）。
> 回答前先查下面的路由表。

## 路由表：问题 → 去哪查

| 用户在问 | 去读 | 关键结论速记 |
|---------|------|------------|
| 该用哪个扩展层？CLAUDE.md 还是 skill 还是 hook？ | `docs/cc-guide/01-能力选型矩阵.md` | 12 层扩展；**确定性的只有权限/hook/沙箱**，其余都是建议性的 |
| 上下文为什么这么贵？什么被压缩掉了？ | `docs/cc-guide/02-上下文经济学.md` | 启动时 skill description 就超预算 7.6 倍；压缩会丢带 `paths:` 的规则 |
| 怎么写提示词？消息怎么排队？快捷键？ | `docs/cc-guide/03-提示词与交互技巧.md` | **排队 = `Ctrl+X Enter`**，`Enter` = 立即发送 |
| 权限怎么配？沙箱有没有？deny 怎么写才有效？ | `docs/cc-guide/04-权限与护栏.md` | deny 是唯一不可绕过的层；**`Write(...)` 规则不生效，要写 `Edit(...)`** |
| subagent / teams / worktree 怎么选？ | `docs/cc-guide/05-多代理编排.md` | 本仓库插件 skill 一个都没加载（缓存跟的是远端版本） |
| 插件怎么写？manifest 字段怎么填？ | `docs/cc-guide/06-插件与市场.md` | `skills` 指目录、`commands` 指文件；插件是**装到缓存**再加载的；**`$schema` 的官方地址已 404** |
| 出问题了怎么查？ | `docs/cc-guide/07-排错手册.md` | **先 `claude --debug`**，猜是没用的 |
| 下一步往哪走？ | `docs/cc-guide/08-演进趋势.md` | v2.1.284 起 **auto 模式是默认**；v2.1.314 起空闲即压缩 |

速查表：`references/extensions.md`（选型 + manifest 规范）
诊断手册：`references/diagnostics.md`（症状 → 命令 → 动作）
实测数据：`references/measurements.md`（数字、测量日期、复现命令、文档过时清单）

## 三条最容易踩的坑（先记住这个）

1. **`Write(.env*)` 这条 deny 规则根本不生效。**
   Claude Code 启动时会告警：只有 `Edit(path)` 规则会被文件权限检查匹配，
   而 `Edit` 规则覆盖所有文件编辑类工具。→ 写 `Edit(.env*)`。

2. **改了仓库里的插件源码，本机的插件不会自动更新。**
   插件是"安装到缓存再加载"的模型，而**缓存同步的是 git 远端的已发布版本** ——
   本地没 push 的改动永远进不去。改完先 `git push`，再 `claude plugin update --all`；
   调试时直接 `claude --plugin-dir ./plugins/<name>` 就地加载。

3. **`Enter` 不是排队键。**
   出厂绑定是 `enter → chat:submit`（立即发送）、`ctrl+x enter → chat:queueSubmit`（排队）。
   官方 [interactive-mode](https://code.claude.com/docs/en/interactive-mode) 那句
   "press Enter … queues the message" 是 v2.1.247 之前的旧行为，没更新。

## 排错的黄金路径

```bash
claude --debug -p "回复 OK 两个字即可"     # 1. 起最小会话，留启动日志
LOG=$(ls -t ~/.claude/debug/*.txt | head -1)  # 2. 找最新日志
grep -iE "skill|agent|plugin" "$LOG"        # 3. 按症状 grep
```

完整流程、关键字速查表、日志样本：`references/diagnostics.md`。

## 本仓库的常驻成本体检

```bash
uv run --with pyyaml python scripts/measure_context.py
```

会逐来源统计 skill / agent 的 description 字符数，并**标出 frontmatter 解析失败的文件**
和**缓存里还没跟上的旧平铺布局**。

## 改指南文档后

```bash
# 严格构建：链接写错、锚点失效直接让构建失败
PYTHONPATH=. uv run --with "mkdocs-material>=9.5" mkdocs build --strict --site-dir site

# 表格结构体检：列数不一致 / 分隔行错位 / 整列为空
# （Markdown 解析器会静默补齐，构建期抓不到，只有这个脚本能抓）
uv run python scripts/check_tables.py docs/cc-guide

# 插图改了就重新生成（明暗两套，共 18 个 SVG）
uv run python scripts/gen_guide_figures.py

# 本地预览（修正 Windows 上 .svg 的 MIME，否则图裂）
uv run python scripts/serve.py
```

## 改插件 manifest 后

```bash
# 按 manifest 自己声明的 $schema 校验（顺带确认那个地址还活着）
uv run --with jsonschema python scripts/validate_manifests.py
```

## 事实来源优先级

1. **本机实测**（`claude --debug` 日志、`scripts/measure_context.py`）
2. **二进制**（出厂键位、内嵌 CHANGELOG）—— `scripts/extract_keybindings.py`、`scripts/extract_changelog.py`
3. **[keybindings 文档](https://code.claude.com/docs/en/keybindings)**（比 interactive-mode 更新更勤）
4. 其他官方文档

官方文档会过时，**实测和二进制不会**。发现冲突时按这个顺序裁决，并在文档里记下来。
