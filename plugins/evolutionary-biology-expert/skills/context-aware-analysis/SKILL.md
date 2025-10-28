---
name: Context感知分析技能
description: 专门用于深度背景感知的专家分析技能。通过重建专家工作的历史、学术、社会、文化背景，理解其思想产生的环境和条件。使用sequentialthinking进行背景深度分析，揭示专家思想的时空嵌入性和历史必然性。
allowed-tools: Read, Write, Edit, Bash, Task, mcp__article_mcp__search_europe_pmc, mcp__article_mcp__search_arxiv_papers, mcp__article_mcp__get_article_details, mcp__article_mcp__get_references_by_doi, mcp__article_mcp__get_similar_articles, mcp__bl_aritcle_mcp__search_europe_pmc, mcp__bl_aritcle_mcp__search_arxiv_papers, mcp__bl_aritcle_mcp__get_article_details, mcp__bl_aritcle_mcp__get_references_by_doi, mcp__bl_aritcle_mcp__get_similar_articles, mcp__sequentialthinking__sequentialthinking
---

# 🌍 Context感知分析技能

## 🎯 核心分析哲学

**任何专家的思想都不是凭空产生的，而是深深嵌入在特定的时空背景中。**

Context感知分析的目标是：
- 重建专家工作的历史环境和科学条件
- 理解时代特征对研究主题选择的影响
- 分析学术传统和谱系对专家思维的塑造
- 识别文化背景和社会环境对理论构建的影响
- 把握专家在学术生态系统中的精确定位

## 🧠 Context分析思维框架

### 维度一：历史科学环境重建
使用 `sequentialthinking` 进行历史背景分析：
```
思考1：专家[姓名]工作时，科学界处于什么状态？
- 当时该领域的核心问题和争议是什么？
- 主导的研究范式和方法论是什么？
- 重大科学发现和技术进步有哪些？
- 科学界的社会结构和组织方式如何？
- 科学经费和资助环境怎样？
```

### 维度二：学术谱系定位
```
思考2：专家在学术谱系中处于什么位置？
- 师承关系：导师是谁，从谁那里继承了什么？
- 学派归属：属于哪个学术传统或学派？
- 学术网络：与同时代学者的关系如何？
- 机构背景：在哪些机构工作，机构文化如何？
- 学术传承：培养了哪些学生，影响了哪些后辈？
```

### 维度三：同时代学者对比
```
思考3：与同时代其他学者相比，专家有何独特之处？
- 同领域的主要竞争者和合作者是谁？
- 其他学者对相同问题有什么不同观点？
- 专家的观点在同期学界是主流还是边缘？
- 与同代学者相比，专家的方法有何特色？
- 在学术争论中，专家通常持什么立场？
```

### 维度四：社会经济背景分析
```
思考4：当时的社会经济环境如何影响专家研究？
- 经济条件：科研经费充足还是匮乏？
- 社会需求：社会对该领域有什么期待？
- 政治环境：政治气候对学术研究的影响？
- 技术条件：当时的实验技术和计算能力如何？
- 文化氛围：社会对科学的态度如何？
```

### 维度五：文化认知框架
```
思考5：文化背景如何塑造专家的思维模式？
- 教育背景：受教育的国家和体系特点？
- 语言文化：母语和文化传统的认知影响？
- 价值观：深层的文化价值观如何影响研究？
- 世界观：对自然和社会的基本看法？
- 思维习惯：分析问题的思维倾向？
```

### 维度六：地理空间因素
```
思考6：地理因素如何影响专家的学术发展？
- 机构位置：在不同地理环境中的学术机会？
- 学术交流：地理位置对国际交流的影响？
- 资源获取：不同地区的学术资源差异？
- 合作网络：地理因素对合作模式的影响？
- 思想传播：地理位置对思想传播的影响？
```

## 📊 Context分析实施指南

### 第一步：历史背景数据收集
**科学史信息检索：**
```python
# 搜索相关时期的科学史信息
historical_search_terms = [
    "history of [field] [decade]",
    "scientific paradigm [time_period]",
    "[field] major discoveries [year_range]",
    "scientific revolution [time_period]",
    "research methods [field] [decade]"
]

# 收集重大科学事件
major_events = []
for term in historical_search_terms:
    results = search_academic_database(term)
    major_events.extend(results)
```

**时代特征分析：**
- **技术发展水平**：当时的实验技术和计算能力
- **理论基础**：该领域的理论发展状况
- **方法论特点**：主流的研究方法和分析技术
- **学术组织**：学术期刊、学会、会议的组织状况
- **科学政策**：政府对科学的支持和管理政策

### 第二步：学术谱系重建
**师承关系追踪：**
```python
academic_lineage = {
    "intellectual_ancestors": [],    # 思想祖先
    "direct_mentors": [],            # 直接导师
    "academic_collaborators": [],    # 学术合作者
    "intellectual_descendants": [],  # 思想后代
    "institutional_affiliations": [] # 机构隶属
}

# 构建学术谱系图
for mentor in expert_data.get("mentors", []):
    academic_lineage["direct_mentors"].append({
        "name": mentor["name"],
        "institution": mentor["institution"],
        "field": mentor["field"],
        "influence": analyze_mentor_influence(mentor, expert)
    })
```

**学派识别：**
- **理论传统**：属于哪个理论传统或学派
- **方法论传承**：继承了哪些研究方法
- **问题意识**：关注哪些核心科学问题
- **价值取向**：学术价值观的传承
- **国际网络**：与国际学术界的联系

### 第三步：同时代对比分析
**竞争者识别：**
```python
contemporary_analysis = {
    "main_competitors": [],      # 主要竞争者
    "close_collaborators": [],   # 紧密合作者
    "independent_discoverers": [], # 独立发现者
    "critical_opponents": [],    # 批评者
    "supportive_allies": []      # 支持者
}

# 分析同时代学者的观点
for contemporary in contemporaries:
    comparison = {
        "name": contemporary["name"],
        "approach": contemporary["approach"],
        "agreement_areas": [],
        "disagreement_areas": [],
        "methodological_differences": [],
        "philosophical_differences": []
    }
```

**观点对比矩阵：**
- **理论观点**：对核心问题的不同看法
- **方法论偏好**：研究方法的差异
- **哲学立场**：科学哲学观点的不同
- **应用倾向**：理论应用方向的差异
- **社会影响**：对社会影响的不同理解

### 第四步：社会经济环境分析
**环境因素分类：**
```python
socioeconomic_context = {
    "economic_factors": {
        "funding_availability": "经费可获得性",
        "research_costs": "研究成本",
        "commercial_potential": "商业化潜力",
        "economic_priorities": "经济优先级"
    },
    "political_factors": {
        "science_policy": "科学政策",
        "research_freedom": "研究自由度",
        "international_relations": "国际关系",
        "national_priorities": "国家优先方向"
    },
    "social_factors": {
        "public_attitude": "公众态度",
        "media_coverage": "媒体报道",
        "educational_system": "教育体系",
        "cultural_values": "文化价值观"
    }
}
```

**影响机制分析：**
- **资源约束**：经费、设备、人力限制
- **政策引导**：科学政策对研究方向的影响
- **社会期待**：社会对科学家的期待和压力
- **文化约束**：文化传统对思维的潜在限制

### 第五步：文化认知深度分析
**认知模式识别：**
```python
cognitive_framework = {
    "educational_influence": {
        "primary_education": "基础教育背景",
        "higher_education": "高等教育经历",
        "international_experience": "国际经验",
        "language_skills": "语言能力"
    },
    "cultural_dimensions": {
        "individualism_vs_collectivism": "个人主义vs集体主义",
        "power_distance": "权力距离",
        "uncertainty_avoidance": "不确定性回避",
        "long_term_orientation": "长期导向"
    },
    "thinking_patterns": {
        "analytical_vs_holistic": "分析vs整体思维",
        "linear_vs_circular": "线性vs循环思维",
        "abstract_vs_concrete": "抽象vs具体思维",
        "deductive_vs_inductive": "演绎vs归纳思维"
    }
}
```

**文化影响路径：**
- **教育传统**：不同教育体系的思维训练
- **语言习惯**：语言结构对思维的影响
- **价值观念**：深层文化价值对研究选择的影响
- **社会规范**：社会行为规范对学术表达的影响

### 第六步：地理空间分析
**空间因素建模：**
```python
spatial_analysis = {
    "institutional_mobility": {
        "education_locations": "教育地点",
        "work_institutions": "工作机构",
        "collaboration_network": "合作网络地理分布",
        "conference_attendance": "会议参与地理范围"
    },
    "resource_access": {
        "library_resources": "图书馆资源",
        "laboratory_facilities": "实验设施",
        "computing_resources": "计算资源",
        "field_sites": "野外或实地研究地点"
    },
    "knowledge_flow": {
        "information_channels": "信息渠道",
        "collaboration_patterns": "合作模式",
        "influence_dissemination": "影响传播路径",
        "regional_impact": "地区影响范围"
    }
}
```

## 📈 Context分析输出标准

### 必须包含的内容
1. **历史环境重建**
   - 科学发展阶段的特征描述
   - 重大科学事件和发现的影响
   - 技术条件对研究的限制和机遇

2. **学术谱系定位**
   - 师承关系和学术传承
   - 学派归属和理论传统
   - 在学术网络中的位置

3. **同时代对比**
   - 与同代学者的观点对比
   - 在学术争论中的立场
   - 独特贡献和创新之处

4. **社会经济背景**
   - 经济条件对研究的影响
   - 政策环境对学术的塑造
   - 社会文化对理论的影响

5. **文化认知框架**
   - 教育背景对思维的塑造
   - 文化价值观的影响
   - 认知模式和思维习惯

6. **地理空间因素**
   - 机构环境的学术影响
   - 地理位置对合作的影响
   - 空间因素对思想传播的影响

### 分析深度要求
**多层次分析：**
- **宏观层面**：时代背景和社会环境
- **中观层面**：学术机构和学科环境
- **微观层面**：个人经历和思维特征

**多角度审视：**
- **时间角度**：历史发展的脉络
- **空间角度**：地理环境的影响
- **社会角度**：社会结构的塑造
- **文化角度**：文化传统的约束

### 质量保证措施
**数据可靠性：**
- 多源信息交叉验证
- 历史事实的准确性检查
- 避免时代错置的分析

**分析深度：**
- 深入到具体的历史细节
- 考虑复杂的多重因果关系
- 避免简单化的因果解释

**客观公正：**
- 理解历史条件的局限性
- 避免用现代标准苛责历史
- 平衡考虑正面和负面因素

## 🚫 Context分析的注意事项

### 常见分析陷阱
- **时代错置**：用现代观点评价历史选择
- **单一因果**：忽视复杂的多重因果
- **文化偏见**：用自身文化标准评判其他文化
- **过度概括**：从个别案例推广到整体
- **事后诸葛亮**：忽视历史的不确定性

### 分析边界
- 专注于对专家思想有直接影响的背景因素
- 避免过度解读不相关的历史事件
- 承认背景分析的局限性和不确定性
- 区分直接影响和间接影响

---

**核心原则**：Context感知分析是为了理解专家思想的产生环境和条件，而不是为专家寻找借口或进行辩护。真正的理解来自于对复杂背景因素的全面把握和客观分析。