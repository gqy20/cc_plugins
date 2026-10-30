# 📽️ Slidev 演示文稿生成插件 v0.1.1

## 🎯 插件定位

把 Markdown 内容转成 [Slidev](https://sli.dev/) 演示文稿（`slides.md`），自动匹配主题，
并支持导出为 PDF 或 HTML。

## ⭐ 核心功能

- **结构化转换** — 标题层级自动映射到 Slidev 布局（`#` → `layout: cover`，`##` → 分节）
- **布局优化** — 含图片用 `image-right`/`image-left`，代码+文本用 `two-cols`，长列表提示拆分
- **主题匹配** — 按内容类型自动选择主题与高亮器
- **导出能力** — 一条命令导出 PDF 或 HTML

## 📋 安装前准备

本插件**不依赖 MCP 服务器**。导出功能需要本地已安装 Slidev：

```bash
# 使用 pnpm 安装 Slidev CLI（推荐）
pnpm add -g @slidev/cli

# 或使用 npm
npm install -g @slidev/cli
```

验证：

```bash
slidev --version
```

## 🚀 使用方法

### 通过命令调用

```
/md-to-slidev docs/report.md
```

命令参数：

| 参数 | 说明 |
|------|------|
| `input.md` | 输入的 Markdown 文件路径 |
| `options` | 可选，导出目标（如 `pdf` / `html`）与主题名 |

### 通过技能调用

技能 `md-to-slides` 负责「Markdown → Slidev 结构」的转换规则，
Agent `slidev-converter` 负责完整的读取、转换与导出流程。

## 🧩 插件结构

```
slidev-generator/
├── .claude-plugin/
│   └── plugin.json          # 插件元数据
├── agents/
│   └── slidev-converter.md  # 转换执行智能体
├── commands/
│   └── md-to-slidev.md      # /md-to-slidev 命令
├── skills/
│   └── md-to-slides/
│       └── SKILL.md         # 转换规则（frontmatter/标题/布局）
└── README.md
```

## 🔄 转换规则速览

| 原始 Markdown | 转换结果 |
|--------------|---------|
| `# Title` | `layout: cover` + `# Title` |
| `## Section` | `---` + `# Section` |
| `### Sub` | `## Sub`（保持） |
| 段落之间 | 插入 `---` 分隔符 |

生成的 `slides.md` 头部包含：

```yaml
---
theme: seriph
highlighter: shiki
lineNumbers: false
info: false
transition: slide-left
---
```

## 📄 许可证

MIT
