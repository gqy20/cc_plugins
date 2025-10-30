# 🌿 进化生态学专家插件 v0.1.1

## 🎯 插件定位

专业的进化生态学咨询系统，为生态学和进化生物学研究提供自然选择机制、适应过程和生态相互作用分析的专业指导。

## ⭐ 核心功能

- **自然选择分析** - 分析不同环境下的选择压力和进化响应
- **适应机制研究** - 探讨生物体对环境变化的适应策略和机制
- **生态相互作用研究** - 分析种间关系和生态网络结构
- **生态实验设计** - 设计进化生态学实验和研究方案

## 📋 依赖要求

### 必需的MCP服务器

```bash
# 生态学文献检索
claude mcp add article-mcp uvx article-mcp server

# 结构化生态分析思考
claude mcp add sequentialthinking npx -y @modelcontextprotocol/server-sequential-thinking@latest
```

## 🚀 使用方法

该插件通过以下智能体提供服务：

- **evolutionary-ecology-analyst** - 进化生态学分析专家

## 📁 插件结构

- `agents/` - 智能体定义
- `skills/` - 专业技能模块
- `templates/` - 分析报告模板
- `standards/` - 数据接口标准

## 📄 许可证

MIT License