---
name: 检索词优化技能
description: 专门用于优化进化生物学专家分析的学术文献检索词的技能。当需要提高文献检索的覆盖度和精确度、处理专家姓名变体、动态扩展关键词、评估检索质量时使用。通过多层次检索策略、智能关键词扩展、质量控制反馈等机制，确保文献检索既全面又精确。适用于学术文献检索、专家分析、文献综述等需要高质量检索结果的场景。
allowed-tools: Read, Write, Edit, Bash, Task, mcp__article_mcp__search_literature
---

# 检索词优化技能

## 功能描述

这是一个专门用于优化学术文献检索词的智能技能。它能够：
- 生成专家姓名的各种变体和组合
- 设计多层次递进的检索策略
- 动态扩展和优化关键词
- 评估和反馈检索质量
- 确保文献检索的全面性和精确性

## 使用场景

- **专家文献检索**：提高进化生物学专家文献检索的覆盖度
- **理论追踪分析**：全面检索特定理论的相关文献
- **跨学科搜索**：处理跨学科研究中的术语差异
- **检索质量提升**：优化检索策略，减少遗漏和噪音

## 核心算法

### 1. 多层检索架构
- **身份层**：专家姓名全组合 + 基础领域
- **理论层**：核心创新术语 + 时间演化
- **网络层**：重要合作者 + 交叉主题
- **影响层**：理论应用 + 后续发展

### 2. 智能关键词扩展
- **同义词扩展**：基于领域知识库的同义词替换
- **上下文学习**：从初始结果中学习新的关键词
- **术语映射**：处理不同时期的术语变化
- **跨学科适配**：适应不同领域的表达习惯

### 3. 质量控制机制
- **覆盖率评估**：确保检索结果的全面性
- **精确度评分**：过滤不相关的文献
- **重复检测**：去除重复的检索结果
- **迭代优化**：基于反馈调整检索策略

## 使用方法

### 基本用法
```
请优化"Richard Dawkins"关于"自私的基因"的文献检索词
```

### 高级用法
```
请为进化生物学专家[专家姓名]设计一个全面的检索词优化策略，包括：
1. 生成所有可能的姓名变体和署名组合
2. 设计四层递进的检索策略
3. 实现动态关键词扩展机制
4. 建立质量评估和反馈系统
5. 确保每次检索不少于30篇高质量文献
```

## 参数说明

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| expert_name | string | 是 | 专家姓名，支持全名、缩写等格式 |
| research_topic | string | 可选 | 核心研究主题或理论名称 |
| optimization_level | string | 可选 | 优化级别：basic/standard/comprehensive |
| target_languages | list | 可选 | 目标语言，默认['en', 'zh'] |
| time_sensitivity | boolean | 可选 | 是否考虑时间因素，默认true |

## 返回格式

### 检索策略优化结果
```json
{
  "optimization_summary": {
    "name_variants": 8,
    "search_layers": 4,
    "total_queries": 45,
    "estimated_coverage": 0.92
  },
  "search_strategy": {
    "identity_layer": {
      "queries": [...],
      "weight": 0.3
    },
    "theory_layer": {
      "queries": [...],
      "weight": 0.3
    },
    "network_layer": {
      "queries": [...],
      "weight": 0.2
    },
    "impact_layer": {
      "queries": [...],
      "weight": 0.2
    }
  },
  "quality_metrics": {
    "expected_results": 120,
    "relevance_threshold": 0.8,
    "duplicate_rate": 0.05
  },
  "optimization_recommendations": [...]
}
```

## 示例输出

### 优化理查德·道金斯的检索策略
```
## 专家：Richard Dawkins
## 检索优化策略

### 姓名变体生成（8个）
1. Richard Dawkins
2. R Dawkins  
3. R. Dawkins
4. Dawkins R
5. Dawkins Richard
6. Dawkins, Richard
7. Dawkins, R.
8. Richard C. Dawkins

### 四层检索策略

#### 第1层：身份检索（权重30%）
- "Richard Dawkins" AND evolution
- "R Dawkins" AND genetics  
- "Dawkins R" AND natural selection
- "Dawkins, Richard" AND molecular evolution
- ...（共12个查询）

#### 第2层：理论检索（权重30%）
- ("selfish gene" OR "selfish gene theory") AND evolution
- ("meme" OR "memetics") AND cultural evolution
- ("gene selection" OR "genetic determinism") AND adaptation
- ...（共15个查询）

#### 第3层：网络检索（权重20%）
- "Richard Dawkins" AND collaboration
- "Dawkins" AND Oxford University
- "Richard Dawkins" AND "John Maynard Smith"
- ...（共10个查询）

#### 第4层：影响检索（权重20%）
- ("selfish gene" OR "Richard Dawkins") AND influence
- ("Dawkins theory" OR "Dawkins paradigm") AND impact
- ("Dawkins contribution" OR "Dawkins legacy") AND evolution
- ...（共8个查询）

### 动态扩展机制
- **同义词扩展**：evolution ↔ evolutionary ↔ darwinian
- **术语映射**：selfish gene ↔ inclusive fitness ↔ gene selection
- **时间适配**：1970s: "sociobiology" → 1990s: "evolutionary psychology" → 2000s: "gene-culture coevolution"

### 质量控制标准
- **最小结果数**：每层检索 ≥30篇
- **相关性阈值**：≥0.8
- **重复率控制**：≤5%
- **时间覆盖**：1960-2025年
- **语言覆盖**：英语 + 中文译本

### 预期效果
- **总检索查询**：45个
- **预期文献数**：120-150篇
- **覆盖率估计**：92%
- **精确度目标**：85%
- **完整性保证**：95%+
```

## 优化级别说明

### Basic（基础优化）
- 生成基础姓名变体
- 简单的关键词组合
- 基本的质量控制
- 适合初步探索

### Standard（标准优化）
- 完整的姓名变体生成
- 四层检索策略
- 动态关键词扩展
- 中等质量保证

### Comprehensive（综合优化）
- 深度的姓名变体分析
- 多维检索策略组合
- 智能学习扩展机制
- 高级质量控制
- 迭代优化反馈

## 特殊处理机制

### 1. 姓名变体处理
- **学术署名习惯**：不同时期的署名格式
- **跨文化差异**：东西方姓名表达差异
- **婚姻变更**：女性学者婚后姓名变更
- **缩写规则**：各种标准的缩写格式

### 2. 术语适配机制
- **时间演化**：术语随时间的演变
- **地域差异**：不同地区的术语表达
- **学科交叉**：跨学科的术语转换
- **语言翻译**：多语言术语对应

### 3. 质量保证流程
- **预检索验证**：关键词有效性测试
- **结果评估**：检索结果质量评分
- **去重处理**：智能重复文献识别
- **反馈优化**：基于结果的策略调整

## 注意事项

1. **隐私保护**：仅使用公开的学术信息
2. **合规使用**：遵循数据库的使用条款
3. **质量平衡**：在覆盖度和精确度间找到平衡
4. **动态调整**：根据实际结果调整检索策略

## 相关工具

- AI智能构建检索策略并进行动态优化
- article-mcp MCP工具 - 检索结果验证和优化
- sequentialthinking MCP工具 - 检索策略结构化思考

---

此技能确保进化生物学专家分析的文献检索既全面又精确，为深度分析提供高质量的文献基础。