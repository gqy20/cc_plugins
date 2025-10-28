---
name: 谷歌学术分析技能
description: 专门用于分析进化生物学专家谷歌学术个人主页的技能。当需要获取专家的学术影响力指标、H指数、引用数据、合作者网络、研究兴趣标签、学术声誉分析时使用。通过Playwright MCP工具自动访问和解析谷歌学术数据，提供权威的学术影响力评估。适用于专家学术评估、影响力分析、学术网络研究、声誉管理等场景。
allowed-tools: Read, Write, Edit, Bash, Task, mcp__playwright__playwright_navigate, mcp__playwright__playwright_get_visible_text, mcp__playwright__playwright_click, mcp__playwright__playwright_fill, mcp__playwright__playwright_evaluate, mcp__playwright__playwright_screenshot, mcp__playwright__playwright_get_visible_html
---

# 谷歌学术分析技能

## 功能描述

这是一个专门用于分析进化生物学专家谷歌学术个人主页的智能技能。它能够：
- 自动搜索和发现专家的谷歌学术个人主页
- 提取权威的学术影响力指标（H指数、i10指数、总引用数）
- 分析研究成果排序和引用趋势
- 识别核心合作者网络和研究兴趣标签
- 提供实时的学术声誉和发展趋势分析

## 使用场景

- **专家影响力评估**：获取权威的学术影响力指标
- **学术声誉分析**：分析专家的学术地位和声誉
- **研究动态追踪**：监控专家的最新研究动态
- **合作网络研究**：识别重要的学术合作关系
- **数据验证补充**：与其他数据源进行交叉验证

## 核心算法

### 1. 个人主页发现算法
- **智能搜索**：基于专家姓名和研究领域的智能匹配
- **身份验证**：多重验证确保找到正确的专家主页
- **消歧处理**：处理同名专家的身份识别问题

### 2. 数据提取算法
- **结构化解析**：使用JavaScript提取页面结构化数据
- **动态内容处理**：处理JavaScript渲染的动态内容
- **数据清洗**：自动清洗和标准化提取的数据

### 3. 影响力分析算法
- **指标计算**：计算多种学术影响力指标
- **趋势分析**：分析引用和发展趋势
- **比较评估**：与领域内其他专家进行比较

## 使用方法

### 基本用法
```
请分析理查德·道金斯的谷歌学术数据
```

### 高级用法
```
请对进化生物学专家[专家姓名]进行全面的谷歌学术分析，包括：
1. 搜索专家的谷歌学术个人主页
2. 提取所有可用的学术影响力指标
3. 分析研究成果排序和引用趋势
4. 识别合作者网络和研究兴趣
5. 评估学术声誉和发展动态
```

## 实现细节

### 个人主页发现流程
```python
async def find_scholar_profile(expert_name: str, research_field: str = None):
    # 1. 导航到谷歌学术作者搜索页面
    await playwright_navigate(
        "https://scholar.google.com/citations?view_op=search_authors",
        headless=True
    )
    
    # 2. 填写搜索关键词
    search_query = f"author:{expert_name}"
    if research_field:
        search_query += f" {research_field}"
    
    await playwright_fill(
        selector="input[name='mauthors']",
        value=search_query
    )
    
    # 3. 点击搜索按钮
    await playwright_click("button[type='submit']")
    
    # 4. 等待搜索结果加载
    await playwright_get_visible_text()
    
    # 5. 查找最佳匹配的专家
    return await playwright_evaluate("""
        const cards = document.querySelectorAll('.gsc_1usr');
        let bestMatch = null;
        let bestScore = 0;
        
        cards.forEach(card => {
            const nameElement = card.querySelector('.gsc_1usr_name a');
            if (nameElement) {
                const cardName = nameElement.textContent.trim();
                const score = calculateNameSimilarity(name, cardName);
                
                if (score > bestScore && score > 0.7) {
                    bestScore = score;
                    bestMatch = nameElement.href;
                }
            }
        });
        
        return bestMatch;
    """)
```

### 学术指标提取流程
```python
async def extract_scholar_metrics(profile_url: str):
    # 1. 导航到专家主页
    await playwright_navigate(profile_url, headless=True)
    
    # 2. 使用JavaScript提取学术指标
    metrics = await playwright_evaluate("""
        const metrics = {};
        
        // 提取基本统计数据
        const statsTable = document.querySelector('.gsc_rsb_st tbody');
        if (statsTable) {
            const rows = statsTable.querySelectorAll('tr');
            
            // 总引用数
            if (rows[0]) {
                const citationsCell = rows[0].querySelector('td:nth-child(2)');
                metrics.total_citations = parseInt(citationsCell.textContent.replace(/[^0-9]/g, ''));
            }
            
            // H指数
            if (rows[1]) {
                const hIndexCell = rows[1].querySelector('td:nth-child(2)');
                metrics.h_index = parseInt(hIndexCell.textContent.replace(/[^0-9]/g, ''));
            }
            
            // i10指数
            if (rows[2]) {
                const i10IndexCell = rows[2].querySelector('td:nth-child(2)');
                metrics.i10_index = parseInt(i10IndexCell.textContent.replace(/[^0-9]/g, ''));
            }
        }
        
        // 提取研究兴趣
        const interestsSection = document.querySelector('.gsc_prf_int');
        if (interestsSection) {
            const interestLinks = interestsSection.querySelectorAll('a');
            metrics.research_interests = Array.from(interestLinks).map(link => link.textContent.trim());
        }
        
        return metrics;
    """)
    
    return metrics
```

### 论文列表分析流程
```python
async def analyze_publications(max_publications: int = 20):
    # 使用JavaScript提取论文数据
    publications_data = await playwright_evaluate(f"""
        const publications = [];
        const rows = document.querySelectorAll('.gsc_a_tr');
        
        for (let i = 0; i < Math.min(rows.length, {max_publications}); i++) {{
            const row = rows[i];
            const titleElement = row.querySelector('.gsc_a_at');
            const yearElement = row.querySelector('.gsc_a_h');
            const citesElement = row.querySelector('.gsc_a_ac');
            
            if (titleElement) {{
                publications.push({{
                    rank: i + 1,
                    title: titleElement.textContent.trim(),
                    year: yearElement ? parseInt(yearElement.textContent) : null,
                    citations: citesElement ? parseInt(citesElement.textContent) : 0
                }});
            }}
        }}
        
        return publications;
    """)
    
    return publications_data
```

## 返回格式

### 谷歌学术分析结果
```json
{
  "expert_profile": {
    "name": "Richard Dawkins",
    "profile_url": "https://scholar.google.com/citations?user=...",
    "verified": true,
    "affiliation": "University of Oxford"
  },
  "academic_metrics": {
    "h_index": 89,
    "i10_index": 156,
    "total_citations": 31156,
    "research_interests": [
      "Evolutionary Biology",
      "Genetics",
      "Natural Selection"
    ]
  },
  "publications_analysis": {
    "total_publications": 245,
    "top_cited_papers": [...],
    "recent_works": [...],
    "analysis": {
      "avg_citations_per_paper": 127,
      "high_cited_percentage": 85
    }
  },
  "analysis_report": {
    "summary": {...},
    "key_insights": [...],
    "recommendations": [...]
  }
}
```

## 使用示例

### 分析理查德·道金斯
```
请分析理查德·道金斯的谷歌学术数据
```

**分析过程：**
1. 自动搜索 "Richard Dawkins" 的谷歌学术主页
2. 导航到找到的个人主页
3. 提取 H指数、i10指数、总引用数等指标
4. 分析论文列表和引用趋势
5. 生成完整的分析报告

### 分析特定研究领域的专家
```
请分析进化生物学专家 "Stephen Jay Gould" 关于 "间断平衡理论" 的谷歌学术数据
```

## 注意事项

1. **合规使用**：仅在学术研究目的下使用
2. **访问频率**：避免过度频繁的请求
3. **数据准确性**：结合其他数据源进行验证
4. **隐私保护**：尊重专家的学术隐私

## 相关工具

- `playwright_navigate` - 页面导航
- `playwright_fill` - 表单填写
- `playwright_click` - 元素点击
- `playwright_evaluate` - JavaScript执行
- `playwright_get_visible_text` - 文本提取
- `playwright_screenshot` - 页面截图

---

此技能利用Playwright MCP工具提供专业、稳定的谷歌学术分析能力，为进化生物学专家分析提供权威的学术影响力数据。