# Claude Code Research Plugins

专业的专家顾问插件集合，为科学研究提供领域专家分析，以及实用的开发工具。
同时它是一套 **Claude Code 扩展工程参考**：文档、hooks 参考实现与策略引擎可被其他项目直接复用。

> 📖 **Claude Code 使用指南**：[`docs/cc-guide/`](./docs/cc-guide/README.md) —— 9 章实操文档，
> 结论全部来自**本机实测 + 二进制逆向 + 官方文档**（含 2 处已确认的官方文档过时）。
> 覆盖扩展层选型、上下文成本、权限与沙箱、插件 manifest 规范、快捷键、启动失败诊断。
> 在线版由 `.github/workflows/docs.yml` 发布到 GitHub Pages。
>
> 🧭 **项目定位与优先级**：[`docs/ROADMAP.md`](./docs/ROADMAP.md) —— 三层结构、当前优先级、明确不做什么。

## 📦 插件概览

### 研究专家插件

| 插件名称 | 版本 | 描述 | 技能数 | 智能体数 |
|---------|------|------|--------|----------|
| [evolutionary-biology-expert](./plugins/evolutionary-biology-expert/) | 0.1.3 | 进化生物学专家分析系统，提供思维图谱重构和学术网络分析 | 4 | 1 |
| [hybrid-speciation-expert](./plugins/hybrid-speciation-expert/) | 0.1.2 | 杂交物种形成专家咨询，专注于基因组渐渗和生殖隔离分析 | 3 | 1 |
| [crop-breeding-expert](./plugins/crop-breeding-expert/) | 0.1.2 | 作物育种专家顾问，提供分子育种和品种改良策略指导 | 3 | 1 |
| [evolutionary-ecology-expert](./plugins/evolutionary-ecology-expert/) | 0.1.3 | 进化生态学专家，专注于自然选择机制和生态相互作用分析 | 3 | 1 |

### 实用工具插件

| 插件名称 | 版本 | 描述 |
|---------|------|------|
| [slidev-generator](./plugins/slidev-generator/) | 0.1.1 | Markdown 转 Slidev 演示文稿，支持 PDF/HTML 导出 |
| [infographic-viz](./plugins/infographic-viz/) | 0.1.0 | AntV 信息图表可视化，支持时间线、图表、对比图等 |
| [agent-policy](./plugins/agent-policy/) | 0.1.0 | 策略即代码：单入口钩子 + TOML 规则，确定性 deny/ask/run |

## ✨ 核心特性

### 研究插件特性
- **🎯 专家级分析** - 每个插件都提供深度的专业领域分析
- **🔍 质量控制** - 基于严格标准的文献质量和相关性控制
- **🧠 结构化思考** - 使用 sequential thinking 确保分析逻辑性
- **📊 多维评估** - 时间、背景、网络、批判性思维等多维度分析
- **🔗 网络分析** - 学术合作网络和知识传播路径分析
- **📝 标准化输出** - Nature 格式的参考文献和标准化报告

### 实用工具特性
- **📄 演示文稿** - 一键将 Markdown 转换为精美的 Slidev 演示
- **📊 数据可视化** - 快速创建专业级信息图表

## 🚀 快速开始

### 1. 安装 Claude Code CLI

```bash
# 安装 Claude Code
curl -fsSL https://claude.ai/install.sh | sh
```

### 2. 安装 MCP 依赖

```bash
# 学术文献检索 (研究插件必需)
claude mcp add article-mcp uvx article-mcp server

# 结构化思考分析 (研究插件必需)
claude mcp add sequentialthinking npx -y @modelcontextprotocol/server-sequential-thinking@latest

# 可选依赖
claude mcp add mediawiki-mcp-server npx @professional-wiki/mediawiki-mcp-server@latest
claude mcp add playwright npx @playwright/mcp@latest --browser chrome --headless
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

# 运行验证脚本
python3 .github/scripts/check_references.py
python3 .github/scripts/check_mcp_dependencies.py
```

## 🛠️ 开发指南

### 验证命令

```bash
# 验证 marketplace 配置
claude plugin validate .claude-plugin/marketplace.json

# 文件引用检查
python3 .github/scripts/check_references.py

# MCP 依赖检查
python3 .github/scripts/check_mcp_dependencies.py

# 内容质量检查
python3 .github/scripts/validate_content.py <plugin-name>
```

### 提交规范

遵循 `.gitmessage` 定义的 Conventional Commits 格式：

```
<type>(<scope>): <subject>

## Summary
<brief description>

## Changes Made
### <Component> Updates
<specific changes>

## Impact
<explanation>

Co-authored-by: Claude <noreply@anthropic.com>
```

**类型**: feat, fix, docs, style, refactor, test, chore
**作用域**: agent, skill, command, template, config, docs

## 📁 项目结构

```
cc_plugins/
├── .claude-plugin/
│   └── marketplace.json          # 插件市场配置
├── .claude/
│   ├── agents/                   # 本地开发智能体
│   └── commands/                 # 本地开发命令 (tdd, bdd, gh, sdr, docs, linus, elegant, squash, lint)
├── plugins/                      # 插件目录
│   ├── evolutionary-biology-expert/
│   ├── hybrid-speciation-expert/
│   ├── crop-breeding-expert/
│   ├── evolutionary-ecology-expert/
│   ├── slidev-generator/
│   └── infographic-viz/
├── .github/
│   ├── workflows/                # CI/CD 工作流
│   │   └── plugin-validation.yml
│   └── scripts/                  # 验证脚本
│       ├── check_references.py
│       ├── check_mcp_dependencies.py
│       └── validate_content.py
├── CLAUDE.md                     # Claude Code 项目指南
└── README.md
```

### 插件目录结构

```
plugins/<plugin-name>/
├── .claude-plugin/
│   └── plugin.json      # 插件元数据（官方规范位置）
├── README.md            # 插件说明文档
├── agents/              # Agent 文件 (MD 格式)
├── skills/              # 技能模块（每个技能一个目录）
│   └── <skill-name>/
│       └── SKILL.md
├── commands/            # 用户命令接口 (平铺 .md)
└── templates/           # 输出模板
```

## 🔧 配置标准

本项目遵循严格的配置标准和质量控制：

- **插件配置** - 符合 Claude Code 官方 marketplace 格式
- **文件结构** - 标准化的目录结构和命名规范
- **质量控制** - 自动化验证和 CI/CD 检查
- **文档标准** - 完整的 README 和技能文档
- **错误追踪** - 自动错误记录系统（Error Playbook）

### 自动错误记录

项目配置了 Error Playbook Hook，自动捕获并记录开发过程中的错误：

- **自动检测** - pytest/git/网络/配置等多种错误类型
- **智能分类** - 自动推断 domain（tool/network/config）和 severity（blocker/major/minor）
- **知识积累** - 错误记录到 `docs/error-playbook/`，形成可复用的问题解决库
- **查询复用** - 使用 `/err find <关键词>` 快速查找历史错误解决方案

配置文件：`.claude/settings.json` + `.claude/hooks/err-catcher.py`

详细配置说明请参考 [CLAUDE.md](./CLAUDE.md)

## 💻 本地开发命令

项目根目录的 `.claude/commands/` 提供开发工作流命令：

| 命令 | 用途 |
|------|------|
| `/tdd` | 测试驱动开发流程，增量测试策略 |
| `/bdd` | 行为驱动开发流程，可执行文档 |
| `/gh` | GitHub CLI 专家助手，场景化指导 |
| `/sdr` | 规格驱动开发流程，Git 工作流管理 |
| `/docs` | 活文档维护，文档健康检查 |
| `/linus` | 实用主义代码审查与重构 |
| `/elegant` | 优雅编码与重构规范 |
| `/squash` | Commit 历史整理与合并 |
| `/lint` | 代码质量检查工具集 |

**命令协同**：
- `/tdd` → `/squash`：TDD 产生小 commit → 功能完成后合并
- `/bdd` + `/tdd`：BDD (验收) + TDD (单元)，双层测试
- `/sdr` → `/gh`：规格驱动 → GitHub 操作
- `/docs` + 任何命令：代码变更后更新文档

详细使用说明请参考各命令文件。

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

- 📧 Email: qingyuge@foxmail.com
- 🔗 GitHub: [@gqy20](https://github.com/gqy20)

## 🙏 致谢

- Claude Code 团队提供的优秀开发平台
- 所有贡献者和用户的支持
- 开源社区的灵感和工具

## 📞 支持

如有问题或建议，请通过以下方式联系：

- 🐛 [GitHub Issues](https://github.com/gqy20/cc_plugins/issues)
- 💬 [GitHub Discussions](https://github.com/gqy20/cc_plugins/discussions)

---

⭐ 如果这个项目对你有帮助，请给我们一个 Star！
