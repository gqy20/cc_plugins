---
name: 深度学术文献分析技能
description: 专为专家思想地图重建而设计的高阶学术文献分析技能。重点不是简单的文献收集，而是通过深度文献分析理解专家的理论发展脉络、学术影响力和思想演进轨迹。使用sequentialthinking进行结构化思考，确保分析的深度和逻辑性。
allowed-tools: Read, Write, Edit, Bash, Task, mcp__article_mcp__search_literature, mcp__article_mcp__get_article_details, mcp__article_mcp__get_references, mcp__sequentialthinking__sequentialthinking
---

# 🧠 深度学术文献分析技能

## 🎯 核心分析哲学

**这不是简单的文献收集技能，而是专家思想地图重建的核心工具。**

你的目标是通过深度文献分析，理解：
- 专家的理论创新是如何产生和演化的
- 其思想在学术生态系统中的传播路径
- 理论的优势、局限性和适用边界
- 专家对学科发展的长期影响

## 🔄 分析流程框架

### 第一步：战略性文献检索
使用 `sequentialthinking` 思考检索策略：
```
思考1：要全面理解专家[姓名]的思想发展，需要从哪些角度检索文献？
- 核心理论文献：确立其学术地位的原创性工作
- 发展演化文献：理论的后续修正和发展
- 批评质疑文献：对理论的批评和挑战
- 应用扩展文献：理论在其他领域的应用
- 影响传承文献：受其影响的后续研究
```

### 第二步：多层次文献收集
**基础检索（确保覆盖面）：**
- 身份检索：专家姓名的各种变体形式
- 主题检索：核心理论概念和关键词
- 时间检索：按重要时期分层检索

**深度检索（确保深度）：**
- 引用网络：高被引论文的参考文献和引用文献
- 批评文献：专门搜索批评和质疑的声音
- 传承文献：受专家理论影响的后续研究
- 跨学科应用：理论在其他领域的应用和发展

### 第三步：文献质量深度评估
使用 `sequentialthinking` 进行质量判断：
```
思考2：如何评估收集到的文献质量和代表性？
- 期刊权威性：顶级期刊 vs 一般期刊的分布
- 引用影响力：高被引论文的比例和分布
- 时间覆盖性：是否覆盖专家生涯的各个重要阶段
- 观点多样性：是否包含支持、批评、中立的多种观点
```

### 第四步：理论发展脉络分析
**时间维度分析：**
- 早期作品：理论的形成和初步提出
- 中期发展：理论的修正、完善和扩展
- 后期反思：对理论的重新评估和总结

**概念演化分析：**
- 核心概念的内涵变化
- 理论边界的扩展或收缩
- 与其他理论的互动关系

### 第五步：学术影响力评估
**定量指标分析：**
- 引用数量和质量分布
- H指数和i10指数的变化趋势
- 期刊影响因子和分区分布

**定性影响分析：**
- 理论是否开创了新的研究范式
- 是否解决了重要的科学问题
- 对后续研究的启发程度

## 📊 实施指南

### 启动条件
当需要分析专家的学术贡献、理论发展或学术影响时使用此技能。

### 必要步骤
1. **使用sequentialthinking制定分析策略**
2. **多角度文献检索确保全面性**
3. **质量评估确保可靠性**
4. **深度分析而非简单收集**

### 关键原则
- **深度优先**：宁愿分析10篇核心文献，也不肤浅收集100篇
- **多元视角**：必须包含支持、批评、中立的多种观点
- **时间敏感**：重视理论的历史背景和发展阶段
- **证据导向**：每个结论都要有充分的文献支撑

## 🚫 使用限制

### 不适用场景
- 简单的文献数量统计
- 缺乏批判性思维的文献堆砌
- 只收集正面观点而忽视批评

### 质量门槛
- 单次检索少于30篇高质量文献时需要调整策略
- 缺乏批评文献时需要专门搜索
- 时间覆盖不完整时需要补充检索

## 🔧 工具使用最佳实践

### article-mcp工具组合
```python
# 标准检索流程
1. search_europe_pmc() - 基础文献检索
2. search_arxiv_papers() - 预印本检索  
3. get_article_details() - 重点文献详细信息
4. get_references_by_doi() - 构建参考文献网络
5. get_similar_articles() - 发现相关研究
```

### sequentialthinking使用要点
- 每个分析阶段都要进行结构化思考
- 主动识别和质疑自己的假设
- 确保推理过程的逻辑一致性
- 考虑反驳证据和替代解释

## 📈 输出标准

### 分析报告必须包含
1. **文献概览**：数量、质量、时间分布
2. **理论发展轨迹**：核心观点的演化过程
3. **影响力评估**：定量和定性影响力指标
4. **批判性分析**：理论的优势、局限和争议
5. **学术定位**：在学科发展中的历史地位

### 质量标志
- 每个结论都有明确的文献支撑
- 包含多元观点和批评声音
- 体现了历史和发展的视角
- 识别了理论的适用边界

---

**记住**：你的目标是构建专家的思想地图，而不是文献的堆砌。深度思考永远比信息收集更重要。

## 思考与分析方法

使用 `sequentialthinking` 工具进行深度分析：

```python
def analyze_expert_literature(expert_name, research_topic):
    # 思考步骤1：问题定义与分解
    thinking_step1 = sequentialthinking(
        thought=f"分析专家{expert_name}关于{research_topic}的学术贡献，需要分解为：历史发展、理论创新、方法论贡献、学术影响等维度",
        next_thought_needed=True
    )
    
    # 思考步骤2：信息收集策略
    thinking_step2 = sequentialthinking(
        thought=f"基于问题定义，制定文献检索策略：使用专家姓名+核心理论作为关键词，确保每次检索≥30篇文献",
        next_thought_needed=True
    )
    
    # 思考步骤3：模式识别
    thinking_step3 = sequentialthinking(
        thought=f"从检索到的文献中识别专家的核心观点发展脉络、理论演进轨迹和学术合作网络",
        next_thought_needed=True
    )
    
    # 思考步骤4：批判性评估
    thinking_step4 = sequentialthinking(
        thought=f"评估专家观点的原创性、影响力、争议点和适用边界，确保结论有充分证据支撑",
        next_thought_needed=False
    )
    
    return [thinking_step1, thinking_step2, thinking_step3, thinking_step4]
```

## 参数说明

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| expert_name | string | 是 | 专家姓名，支持全名、缩写等多种格式 |
| research_topic | string | 可选 | 核心研究主题或理论 |
| time_range | string | 可选 | 检索时间范围，格式：YYYY-YYYY |
| max_results | number | 可选 | 每次检索的最大文献数，默认30 |
| include_arxiv | boolean | 可选 | 是否包含arXiv预印本，默认true |

## 返回格式

### 文献检索结果
```json
{
  "search_results": {
    "pmc_articles": [...],
    "arxiv_articles": [...],
    "total_count": 150,
    "search_strategy": {...}
  },
  "quality_analysis": {
    "avg_impact_factor": 4.2,
    "high_quality_papers": 45,
    "citation_distribution": {...}
  },
  "network_analysis": {
    "collaborators": [...],
    "institutions": [...],
    "theoretical_influence": {...}
  }
}
```

## 示例输出

### 分析理查德·道金斯
```
## 专家：Richard Dawkins
## 研究主题：自私的基因理论

### 文献统计
- 总文献数：127篇
- Europe PMC：98篇
- arXiv预印本：29篇
- 时间跨度：1976-2025
- 平均引用数：245次/篇

### 核心贡献
1. 自私的基因理论（1976）
2. 基因选择理论的发展
3. 文化基因（模因）理论
4. 进化论的科普推广

### 学术影响
- H指数：89
- 总引用数：31,156
- 高被引论文：23篇
- 理论被引：12,456次

### 合作网络
- 主要合作者：8位
- 合作机构：牛津大学、加州大学伯克利分校
- 学科分布：进化生物学、遗传学、科普教育
```

## 注意事项

1. **数据来源**：所有数据来自权威学术数据库
2. **质量保证**：确保文献来自同行评审期刊
3. **隐私保护**：仅分析公开的学术数据
4. **合规使用**：遵循学术数据库的使用条款

## 相关工具

- AI直接使用article-mcp工具进行文献检索
- article-mcp MCP工具 - 欧洲文献数据库检索
- mediawiki-mcp-server - 维基百科信息检索
- 使用结构化思考确保推理过程的逻辑一致性

## 使用示例

### 示例1：检索道金斯的文献
```python
# 分析理查德·道金斯关于自私的基因的研究
results = search_literature("Richard Dawkins", "selfish gene")
print(f"找到 {len(results)} 篇相关文献")
```

### 示例2：构建引用网络
```python
# 获取关键论文的参考文献和相似文献
references = get_references_by_doi("10.1038/246033a0")
similar_articles = get_similar_articles("Richard Dawkins", "doi")
```

### 示例3：文献质量评估
```python
# 评估搜索结果的质量
quality_report = evaluate_articles_quality(search_results)
print(f"平均期刊影响因子: {quality_report['avg_impact_factor']}")
```

---

这个技能结合了结构化思考和学术文献分析，确保专家分析既全面又深入此技能为进化生物学专家分析提供坚实的文献基础，确保分析结论的学术严谨性和可靠性这个技能结合了结构化思考和学术文献分析，确保专家分析既全面又深入，为进化生物学专家的深度分析提供坚实的文献基础。