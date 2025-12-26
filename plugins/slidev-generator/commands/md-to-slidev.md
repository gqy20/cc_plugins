# /md-to-slidev

将 Markdown 文件转换为 Slidev 演示文稿并导出。

## 用法

```
/md-to-slidev <input.md> [options]
```

## 参数

| 参数 | 说明 |
|------|------|
| `input.md` | 输入的 Markdown 文件路径（必需） |

## 选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--format` | 导出格式：`pdf`、`html` 或 `both` | `pdf` |
| `--output` | 输出目录 | 当前目录 |
| `--theme` | 指定主题（留空则自动选择） | 自动 |
| `--keep-temp` | 保留临时 `.slidev-temp` 目录 | 不保留 |

## 示例

```bash
# 基础用法 - 导出 PDF
/md-to-slidev research.md

# 导出 HTML
/md-to-slidev talk.md --format html

# 同时导出 PDF 和 HTML
/md-to-slidev doc.md --format both

# 指定主题
/md-to-slidev presentation.md --theme seriph

# 指定输出目录
/md-to-slidev slides.md --output ./dist
```

## 可用主题

- `default` - 默认主题
- `seriph` - 简洁主题（适合代码多）
- `apple-basic` - 简洁干净（适合学术）
- `dracula` - 深色主题

## 工作流程

1. 读取并分析 Markdown 文件
2. 根据内容智能选择主题
3. 生成 Slidev 格式的 slides.md
4. 创建临时项目并安装依赖
5. 导出 PDF/HTML
6. 清理临时文件（除非使用 `--keep-temp`）
