# 🌾 作物育种专家插件 v0.1.0

## 🎯 插件定位

专业的作物育种咨询系统，为育种工作者提供分子育种、基因组选择和杂交育种策略的专业指导。

## ⭐ 核心功能

- **育种程序设计** - 制定完整的育种方案和技术路线
- **分子育种咨询** - 提供分子标记辅助育种和基因编辑技术指导
- **品种改良策略** - 针对不同作物和目标的品种优化方案

## 📋 依赖要求

### 必需的MCP服务器

```bash
# 农业科学文献检索
claude mcp add article-mcp uvx article-mcp server

# 作物基因组数据分析
claude mcp add genome-mcp npx genome-mcp-server
```

## 🚀 使用方法

该插件通过以下智能体提供服务：

- **crop-breeding-genomics-analyst** - 作物育种基因组分析专家

## 📁 插件结构

- `agents/` - 智能体定义
- `skills/` - 专业技能模块
- `templates/` - 分析报告模板
- `standards/` - 数据接口标准

## 📄 许可证

MIT License