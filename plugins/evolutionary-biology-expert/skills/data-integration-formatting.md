---
name: 数据整合格式化技能
description: 专为专家分析报告生成而设计的数据整合与格式化技能。整合Google Scholar数据获取和Nature格式参考文献标准化，提供统一的数据处理流程，确保报告的数据完整性、格式规范性和可验证性。该技能避免了多个数据处理工具的切换，提供高效的一站式数据整合格式化服务。
allowed-tools: Read, Write, Edit, Bash, Task, mcp__playwright__playwright_navigate, mcp__playwright__playwright_get_visible_text, mcp__playwright__playwright_click, mcp__playwright__playwright_fill, mcp__playwright__playwright_evaluate, mcp__playwright__playwright_screenshot, mcp__playwright__playwright_get_visible_html, mcp__article_mcp__search_literature, mcp__article_mcp__get_article_details
---

# 🔧 数据整合格式化技能

## 🎯 核心功能定位

**高质量的分析报告需要高质量的数据支撑。**

数据整合格式化技能提供统一的数据处理流程，确保：
1. **Google Scholar数据** - 获取权威的学术影响力指标
2. **参考文献格式化** - 生成符合Nature期刊标准的引用
3. **数据完整性验证** - 确保所有数据的准确性和一致性
4. **格式标准化** - 提供统一的数据输出格式

## 🔄 统一数据处理流程

### 第一步：Google Scholar数据整合
```
思考1：如何高效获取专家的Google Scholar数据？
- 搜索策略：专家姓名 + 机构关键词
- 数据提取：H指数、i10指数、总引用数
- 作品分析：高被引论文排序和时间分布
- 合作网络：识别高频合作者和研究兴趣
```

#### 数据获取策略
- **搜索优化**：使用专家姓名+研究领域进行精确搜索
- **页面解析**：提取关键指标和作品列表
- **数据验证**：交叉验证引用数据和合作者信息
- **更新频率**：确保数据的时效性和准确性

#### 提取的数据项
- **基础指标**：H指数、i10指数、总引用数
- **作品分析**：高被引论文列表、引用趋势
- **合作网络**：主要合作者、合作关系强度
- **研究标签**：自动识别的研究兴趣关键词
- **时间分布**：发表论文的时间模式和趋势

### 第二步：参考文献标准化处理
```
思考2：如何将文献数据转换为标准Nature格式？
- 作者格式：姓氏全拼+名字首字母
- 期刊缩写：符合Nature期刊标准
- 年份位置：在作者后或期刊后
- DOI/PMID：确保可验证链接
- 格式一致性：所有引用保持统一格式
```

#### Nature格式标准
```
期刊文章格式：
[1] Author, A. B. Title of article. J. Abbrev. Volume, pages (Year).

书籍格式：
[2] Author, A. B. Title of Book (Publisher, Year).

DOI/PMID添加：
https://pubmed.ncbi.nlm.nih.gov/PMID/
```

#### 自动化处理流程
- **作者格式化**：自动转换为姓氏+首字母格式
- **期刊缩写**：使用标准期刊缩写数据库
- **年份定位**：根据文献类型确定年份位置
- **链接生成**：自动添加PubMed/DOI链接
- **格式检查**：验证所有引用的格式一致性

### 第三步：数据整合与验证
```
思考3：如何确保不同来源数据的一致性？
- 交叉验证：文献数据库与Google Scholar数据对比
- 缺失处理：处理缺失数据和异常值
- 质量评估：评估数据的可靠性和完整性
- 格式统一：确保所有数据符合模板要求
```

#### 数据质量控制
- **完整性检查**：确保所有必需数据项都有值
- **一致性验证**：交叉验证不同数据源的信息
- **异常值处理**：识别和处理明显错误的数据
- **格式标准化**：统一所有数据的输出格式

## 📋 标准化输出格式

### Google Scholar数据输出
```json
{
  "scholar_metrics": {
    "h_index": 数字,
    "i10_index": 数字,
    "total_citations": 数字,
    "citation_trend": "上升/稳定/下降"
  },
  "top_publications": [
    {
      "title": "论文标题",
      "citations": 数字,
      "year": 年份,
      "journal": "期刊名称"
    }
  ],
  "collaboration_network": [
    {
      "name": "合作者姓名",
      "collaboration_count": 数字,
      "institution": "机构名称"
    }
  ],
  "research_interests": ["兴趣标签1", "兴趣标签2"]
}
```

### 参考文献输出
```
[1] Dawkins, R. The Selfish Gene (Oxford University Press, 1976).
[2] Hamilton, W.D. The genetical evolution of social behaviour. J. Theor. Biol. 7, 1–16 (1964). https://pubmed.ncbi.nlm.nih.gov/14115693/
[3] Wilson, E.O. Sociobiology: The New Synthesis (Harvard University Press, 1975).
```

### 数据质量报告
```json
{
  "data_quality": {
    "completeness_score": 数字,
    "consistency_score": 数字,
    "reliability_assessment": "高/中/低",
    "missing_data_items": ["缺失项列表"],
    "data_sources": ["来源1", "来源2"]
  }
}
```

## 🎯 技术实现特点

### 高效性优势
- **一站式处理**：避免多个工具切换的开销
- **批量处理**：支持大量文献的批量格式化
- **缓存机制**：避免重复的网络请求
- **并行处理**：同时进行多个数据源的获取

### 可靠性保障
- **错误处理**：完善的异常处理和恢复机制
- **数据验证**：多层次的数据质量检查
- **备用方案**：Google Scholar无法访问时的替代策略
- **重试机制**：网络请求失败时的自动重试

### 可扩展性设计
- **模块化结构**：数据获取和处理功能分离
- **配置灵活**：支持不同的输出格式要求
- **接口标准**：统一的数据输入输出接口
- **插件机制**：支持新的数据源扩展

## 🔍 使用限制和注意事项

### 技术限制
- **网络依赖**：需要稳定的网络连接访问外部数据源
- **反爬虫机制**：Google Scholar可能有访问频率限制
- **数据时效性**：外部数据可能存在更新延迟
- **格式变化**：外部网站结构变化可能影响数据提取

### 使用建议
- **合理使用频率**：避免过于频繁的数据请求
- **数据验证**：重要数据需要人工验证
- **备用数据源**：准备多个数据源以应对服务中断
- **合规使用**：遵守相关网站的使用条款

---

*这个技能整合了数据获取和格式化的完整流程，为专家分析报告提供高质量、标准化的数据支撑。*