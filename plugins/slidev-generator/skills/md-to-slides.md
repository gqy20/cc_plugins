# MD to Slides Skill

将 Markdown 内容转换为 Slidev 格式的 slides.md。

## 输入

- 原始 Markdown 内容（字符串）
- 选择的主题名称

## 输出

Slidev 格式的 slides.md 内容

## 转换规则

### 1. Frontmatter

在文件开头添加：

```yaml
---
theme: seriph
highlighter: shiki
lineNumbers: false
info: false
transition: slide-left
---
```

### 2. 标题转换

| 原始 | 转换后 |
|------|--------|
| `# Title` | `layout: cover` + `# Title` |
| `## Section` | `---` + `# Section` |
| `### Sub` | `## Sub`（保持） |

### 3. 内容分隔

每个主要段落之间添加 `---` 分隔符。

### 4. 布局优化

- 包含图片：使用 `layout: image-right` 或 `layout: image-left`
- 代码块 + 文本：使用 `layout: two-cols`
- 长列表（>5项）：考虑拆分或使用 `layout: two-cols`

## 示例

### 输入

```markdown
# 研究报告

## 方法

我们使用了以下方法：

1. 数据收集
2. 统计分析
3. 结果验证
```

### 输出

```markdown
---
theme: seriph
highlighter: shiki
lineNumbers: false
info: false
transition: slide-left
---

# 研究报告

---
# 方法

我们使用了以下方法：

1. 数据收集
2. 统计分析
3. 结果验证

---
```

## 注意事项

- 保持原有内容的 Markdown 格式
- 代码块的语言标记保持不变
- 图片路径保持不变
- 不要修改正文内容，只调整结构
