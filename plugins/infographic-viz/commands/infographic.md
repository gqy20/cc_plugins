# /infographic

使用 AntV Infographic 框架创建美观的信息图表。

## 用法

```
/infographic "描述你想要可视化的内容"
```

## 参数

输入一个自然语言描述，说明你想要创建的信息图表内容。可以包括：

- **标题和描述**：图表的主题和简要说明
- **数据项**：要展示的关键信息点
- **数据类型**：时间线、流程图、对比图、层级图、数据图表等
- **风格偏好**：（可选）深色/浅色主题、手绘风格、渐变色等

## 模板类型

| 类型 | 适用场景 | 模板示例 |
|------|----------|----------|
| **顺序/时间线** | 流程步骤、发展趋势 | `sequence-timeline-simple`, `sequence-roadmap-vertical-simple` |
| **对比分析** | 双方对比、优劣势 | `compare-binary-horizontal-simple-fold`, `compare-swot` |
| **层级结构** | 树形结构、组织架构 | `hierarchy-tree-tech-style-capsule-item` |
| **数据图表** | 柱状图、饼图、折线图 | `chart-column-simple`, `chart-pie-donut-plain-text` |
| **列表展示** | 要点列表、卡片网格 | `list-grid-badge-card`, `list-row-horizontal-icon-arrow` |
| **象限分析** | 四象限分析 | `quadrant-quarter-simple-card` |

## 示例

```bash
# 时间线图表
/infographic "创建一个展示互联网技术发展历程的时间线，从1991年Web 1.0到2023年AI大模型"

# SWOT分析
/infographic "为一家AI创业公司做SWOT分析，包括：优势-专家团队、专利技术；劣势-预算有限；机会-市场增长；威胁-竞争加剧"

# 流程图
/infographic "产品开发流程图：研究阶段-理解用户需求，设计阶段-创建用户体验，开发阶段-构建产品，发布阶段-推向市场"

# 数据对比
/infographic "对比两种编程语言：Python和JavaScript，从学习曲线、应用领域、性能等方面"
```

## 输出

命令将生成一个 HTML 文件，包含：
- 可交互的 SVG 信息图表
- 导出为 SVG 的按钮
- 响应式布局

在浏览器中打开即可查看和保存。

## 主题选项

- **深色主题**: `theme dark`
- **手绘风格**: `theme.stylize rough`
- **自定义配色**: `theme.palette #color1 #color2 #color3`
- **渐变效果**: `theme.stylize linear-gradient`

## 注意事项

- 支持中文和英文内容
- 图标来自 Iconify（支持 Material Design、Font Awesome 等）
- 插图来自 unDraw
- 生成的 HTML 文件可直接在浏览器中打开
