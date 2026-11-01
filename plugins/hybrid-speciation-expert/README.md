# 🧬 杂交物种形成专家插件 v0.1.0

## 🎯 插件定位

专业的杂交物种形成咨询系统，为物种形成理论研究提供基因组渐渗分析、生殖隔离演化和物种形成机制的专业指导。

## ⭐ 核心功能

- **杂交起源分析** - 分析杂交物种的起源历史和基因组特征
- **基因流映射** - 追踪物种间的基因流和渐渗模式
- **物种形成机制咨询** - 探讨不同物种形成路径和机制

## 📋 依赖要求

### 必需的 MCP 服务器（插件已声明，启用后自动拉起）

```bash
# 学术文献检索
claude mcp add article-mcp uvx article-mcp server

# 结构化推理
claude mcp add sequentialthinking npx -y @modelcontextprotocol/server-sequential-thinking@latest
```

### 可选的 MCP 服务器

- **genome-mcp**：基因组数据读取与基因进化分析。目前 **npm 上没有公开包**（`genome-mcp-server` 返回 404），
  需要自备服务端：`claude mcp add genome-mcp <你的启动命令>`。
  未安装时，智能体会跳过基因组数据验证，只用文献证据与用户提供的结果，
  并在结论中标注「未做基因组验证」。

## 🚀 使用方法

该插件通过以下智能体提供服务：

- **hybrid-speciation-analyst** - 杂交物种形成分析专家

## 📁 插件结构

- `agents/` - 智能体定义
- `skills/` - 专业技能模块
- `templates/` - 分析报告模板
- `standards/` - 数据接口标准

## 📄 许可证

MIT License