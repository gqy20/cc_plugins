---
name: 参考文献格式化技能
description: 专门用于将检索到的学术文献转换为标准Nature格式的参考文献技能。支持自动提取PubMed URL、格式化作者信息、期刊信息等，确保引用格式符合Nature期刊标准。适用于学术报告写作、文献综述、引用管理等场景。
allowed-tools: mcp__article_mcp__search_literature, mcp__article_mcp__get_article_details, Read, Write, Edit
---

# 参考文献格式化技能

## 功能描述

这个技能专门用于将检索到的学术文献数据转换为标准的Nature期刊参考文献格式，确保所有引用都包含完整的PubMed链接。

## 使用场景

- **学术报告写作**：生成符合Nature标准的参考文献列表
- **文献综述**：整理和分析相关文献
- **引用管理**：维护规范的引用格式
- **学术质量保证**：确保引用的准确性和可验证性

## 核心功能

### 1. Nature格式转换
- **期刊文章格式**：`[编号] 作者. 标题. 期刊 卷, 页码 (年份). URL`
- **书籍格式**：`[编号] 作者. 书名 (出版社, 年份).`
- **章节格式**：`[编号] 作者. in 书名 (编者) 页码 (出版社, 年份).`
- **预印本格式**：`[编号] 作者. 标题. arXiv [分类编号] (年份).`

### 2. PubMed URL生成
- 从PMID自动生成标准PubMed链接
- 格式：`https://pubmed.ncbi.nlm.nih.gov/PMID/`
- 确保所有引用都可在线访问
- 支持批量URL生成和验证

### 3. 作者信息规范化
- 姓氏首字母大写：`Dawkins, R.`
- 多作者处理：`Author1, A.B. & Author2, C.D. & Author3, E.F.`
- 作者数量限制：超过10位作者时显示"et al."
- 姓名变体处理：处理不同署名格式

### 4. 数据验证
- 验证PMID的有效性和可访问性
- 检查期刊信息的完整性（ISSN、影响因子）
- 确保年份和卷期信息准确
- 验证DOI链接的有效性

### 5. 批量处理能力
- **文献数量保证**：确保格式化文献不少于30篇
- **多轮处理**：支持分批处理和合并结果
- **去重处理**：自动识别并移除重复文献
- **质量筛选**：按期刊影响因子和引用次数筛选

### 6. 数据质量控制
- **相关性评分**：0-1分评分系统，要求≥0.6
- **期刊质量分类**：核心期刊（IF>5）、重要期刊（IF>2）、其他期刊
- **时间分布检查**：确保覆盖各个重要时期
- **文献类型平衡**：期刊文章、书籍、会议论文的合理比例

## 使用方法

### 基本用法
```
请将以下文献转换为Nature格式：
PMID: 37638481
标题: Did dawkins recant his selfish gene argument against group selection?
作者: Koen B Tanghe
期刊: Theoretical biology forum
年份: 2023
```

### 批量转换
```
请将以下30篇文献转换为Nature参考文献格式，确保：
1. 文献总数不少于30篇
2. 按发表年份排序（从最早到最新）
3. 包含完整的PubMed URL
4. 核心期刊文章占比不少于40%
5. 涵盖专家的主要贡献时期
[文献数据列表]
```

### 质量检查和补充
```
检查当前文献列表，如不足30篇，请：
1. 扩展检索关键词，增加同义词和相关术语
2. 延长时间范围，包含更多历史文献
3. 添加跨学科应用文献
4. 补充批评和反驳文献
5. 确保每个重要观点都有3篇以上支撑文献
```

## Nature格式标准

### 期刊文章
```
[1] Tanghe, K.B. Did dawkins recant his selfish gene argument against group selection? Theor. Biol. Forum 116, 35–48 (2023). https://pubmed.ncbi.nlm.nih.gov/37638481/
```

### 书籍
```
[2] Dawkins, R. The Selfish Gene (Oxford University Press, 1976).
```

### 会议论文
```
[3] Author, A.B. & Author, C.D. Title. in Proceedings of Conference Name (eds. Editor, E.F.) pages–pages (Publisher, Year).
```

## 质量控制

### 格式检查清单
- [ ] 编号连续且正确
- [ ] 作者姓名格式规范
- [ ] 期刊名称使用标准缩写
- [ ] 卷号、页码格式正确
- [ ] 年份在括号内
- [ ] PubMed链接有效

### 常见错误修正
- **错误**：`Richard Dawkins, The Selfish Gene`
- **正确**：`Dawkins, R. The Selfish Gene`

- **错误**：`Journal Name, vol. 123, pp. 45-67 (2023)`
- **正确**：`J. Name 123, 45–67 (2023)`

## 工具集成

### 使用的MCP工具
- `search_literature`: 检索文献
- `get_article_details`: 获取详细信息
- 自动提取PMID和期刊信息

### 数据来源
- Europe PMC数据库
- PubMed数据库
- 期刊官方网站

## 输出格式

### 结构化输出
```json
{
  "references": [
    {
      "number": 1,
      "citation": "格式化的引用字符串",
      "pmid": "12345678",
      "pubmed_url": "https://pubmed.ncbi.nlm.nih.gov/12345678/",
      "type": "journal_article"
    }
  ],
  "statistics": {
    "total_references": 15,
    "journal_articles": 12,
    "books": 2,
    "conference_papers": 1
  }
}
```

## 优化建议

1. **批量处理**：一次处理多篇文献，提高效率
2. **去重处理**：识别并移除重复引用
3. **排序选项**：支持按年份、作者、期刊排序
4. **质量控制**：自动检查格式错误并提供修正建议

这个技能确保您的学术引用始终符合Nature期刊的高标准要求。