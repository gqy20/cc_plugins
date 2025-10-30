# Claude Code Research Plugins

专业的专家顾问插件集合，专为进化生物学、作物育种和生态学研究提供领域专家级别的咨询和分析能力。

## 📦 插件概览

| 插件名称 | 版本 | 描述 | 技能数 | 智能体数 |
|---------|------|------|--------|----------|
| [evolutionary-biology-expert](./plugins/evolutionary-biology-expert/) | 0.1.1 | 进化生物学专家分析系统，提供思维图谱重构和学术网络分析 | 4 | 1 |
| [hybrid-speciation-expert](./plugins/hybrid-speciation-expert/) | 0.1.0 | 杂交物种形成专家咨询，专注于基因组渐渗和生殖隔离分析 | 3 | 1 |
| [crop-breeding-expert](./plugins/crop-breeding-expert/) | 0.1.0 | 作物育种专家顾问，提供分子育种和品种改良策略指导 | 3 | 1 |
| [evolutionary-ecology-expert](./plugins/evolutionary-ecology-expert/) | 0.1.1 | 进化生态学专家，专注于自然选择机制和生态相互作用分析 | 3 | 1 |

## ✨ 核心特性

- **🎯 专家级分析** - 每个插件都提供深度的专业领域分析
- **🔍 质量控制** - 基于严格标准的文献质量和相关性控制
- **🧠 结构化思考** - 使用 sequential thinking 确保分析逻辑性
- **📊 多维评估** - 时间、背景、网络、批判性思维等多维度分析
- **🔗 网络分析** - 学术合作网络和知识传播路径分析
- **📝 标准化输出** - Nature 格式的参考文献和标准化报告

## 🚀 快速开始

### 1. 安装 Claude Code CLI

```bash
# 安装 Claude Code
curl -fsSL https://claude.ai/install.sh | sh
```

### 2. 安装 MCP 依赖

```bash
# 学术文献检索 (必需)
claude mcp add article-mcp uvx article-mcp server

# 结构化思考分析 (必需)
claude mcp add sequentialthinking npx -y @modelcontextprotocol/server-sequential-thinking@latest

# 可选依赖
claude mcp add mediawiki-mcp-server npx @professional-wiki/mediawiki-mcp-server@latest
claude mcp add playwright npx @playwright/mcp@latest --browser chrome --headless
claude mcp add genome-mcp npx genome-mcp-server
```

### 3. 配置环境变量 (可选)

```bash
# 提升期刊质量评估精度
export EASYSCHOLAR_SECRET_KEY="your_api_key_here"
```

### 4. 验证安装

```bash
# 验证 marketplace 配置
claude plugin validate .claude-plugin/marketplace.json

# 运行完整验证脚本
./scripts/pre-commit-validate.sh
```

## 🛠️ 开发指南

### 设置开发环境

```bash
# 克隆仓库
git clone https://github.com/gqy20/cc_plugins.git
cd cc_plugins

# 运行开发环境设置脚本
./scripts/setup-dev.sh
```

### 日常开发流程

1. **修改插件文件** - 编辑相应的 agents、skills 或配置文件
2. **暂存更改** - `git add .`
3. **提交代码** - `git commit -m "feat: 添加新功能"`
   - Pre-commit hook 会自动验证配置
   - 如果验证失败，请修复错误后重新提交
4. **推送代码** - `git push`

### 手动验证

```bash
# 验证 marketplace 配置
claude plugin validate .claude-plugin/marketplace.json

# 运行完整验证
./scripts/pre-commit-validate.sh

# 跳过验证 (不推荐)
git commit --no-verify
```

## 📁 项目结构

```
cc_plugins/
├── .claude-plugin/
│   └── marketplace.json          # 插件市场配置
├── plugins/                      # 插件目录
│   ├── evolutionary-biology-expert/
│   ├── hybrid-speciation-expert/
│   ├── crop-breeding-expert/
│   └── evolutionary-ecology-expert/
├── scripts/                      # 开发工具脚本
│   ├── pre-commit-validate.sh    # 预提交验证脚本
│   ├── setup-dev.sh             # 开发环境设置
│   └── validate-plugins.py      # 插件配置验证
├── .github/workflows/            # GitHub Actions
└── docs/                        # 文档目录
```

## 🔧 配置标准

本项目遵循严格的配置标准和质量控制：

- **插件配置** - 符合 Claude Code 官方 marketplace 格式
- **文件结构** - 标准化的目录结构和命名规范
- **质量控制** - 自动化验证和 CI/CD 检查
- **文档标准** - 完整的 README 和技能文档

详细配置说明请参考 [PLUGIN_CONFIGURATION.md](./PLUGIN_CONFIGURATION.md)

## 🤝 贡献指南

我们欢迎各种形式的贡献！

### 贡献类型

- 🐛 **Bug 报告** - 发现问题请提交 Issue
- 💡 **功能建议** - 提出新功能想法
- 📝 **文档改进** - 完善文档和示例
- 🔧 **代码贡献** - 修复 bug 或开发新功能

### 开发流程

1. Fork 项目仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: 添加某个功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 代码规范

- 遵循 Conventional Commits 规范
- 确保所有验证通过
- 更新相关文档
- 保持代码简洁和可维护性

## 📋 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 👤 作者

**qingyu_ge** - 科研工具开发者

- 📧 Email: qingyu.ge@example.com
- 🔗 GitHub: [@gqy20](https://github.com/gqy20)

## 🙏 致谢

- Claude Code 团队提供的优秀开发平台
- 所有贡献者和用户的支持
- 开源社区的灵感和工具

## 📞 支持

如有问题或建议，请通过以下方式联系：

- 🐛 [GitHub Issues](https://github.com/gqy20/cc_plugins/issues)
- 💬 [GitHub Discussions](https://github.com/gqy20/cc_plugins/discussions)
- 📧 Email: qingyu.ge@example.com

---

⭐ 如果这个项目对你有帮助，请给我们一个 Star！## Workflow Update
