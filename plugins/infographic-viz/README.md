# 🎨 Infographic 信息图表插件 v0.1.0

## 🎯 插件定位

把文字信息转成**可感知的视觉语言**。基于 [AntV Infographic](https://infographic.antv.vision/) 的类 Mermaid DSL，
用缩进描述信息结构，由 AI 流式输出渲染成信息图表。

**公式**：`Infographic = Information Structure + Visual Expression`

## ⭐ 核心功能

- **多模板支持** — 时间线、对比图、层级结构、流程图、关系图等模板
- **DSL 语法** — 缩进式结构，容错性强，适合 AI 流式生成
- **图标体系** — 通过 `@iconify/json` 按需拉取图标集合
- **主题定制** — 调色板、字体等样式项可配置

## 📋 安装前准备

本插件**不依赖 MCP 服务器**，开箱即用。

```bash
# 确认 Claude Code 已安装
claude --version
```

## 🚀 使用方法

### 通过命令调用

```
/infographic "创建一张展示大语言模型发展历程的时间线信息图"
```

命令参数：

| 参数 | 说明 |
|------|------|
| 内容描述 | 自然语言描述希望可视化的内容，可包含要点、时间范围、对比关系 |

### 通过技能调用

技能 `infographic-creation` 会在描述中出现「生成信息图」「可视化结构」「infographic」等意图时自动触发，
也可显式调用：

```
用 infographic-creation 技能把这段内容做成层级结构图
```

## 🧩 插件结构

```
infographic-viz/
├── .claude-plugin/
│   └── plugin.json          # 插件元数据
├── commands/
│   └── infographic.md       # /infographic 命令
├── skills/
│   └── infographic-creation/
│       └── SKILL.md         # AntV Infographic DSL 与模板规范
└── README.md
```

## 📝 DSL 速查

```yaml
infographic <template-name>
data
title <title>
desc <description>
items
- label <label>
  value <numeric-value>
  desc <explanation>
  icon <icon-name>
theme
palette <color1> <color2> <color3>
```

## ⚙️ 环境变量

| 变量 | 必需 | 说明 |
|------|------|------|
| `ZHIPU_API_KEY` | 否 | 若启用 `crawl-mcp` 做素材抓取时需要 |

## 📄 许可证

MIT
