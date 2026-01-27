---
name: literature-explorer
description: 生命科学领域学术文献探索与可视化；基于 Europe PMC 数据源；支持高级检索、PMC过滤、并行多检索；支持 PMCID/PMID/DOI 混合批量提取；生成美化的 HTML 可视化报告
dependency:
  python:
    - requests>=2.31.0
---

# 生命科学文献探索与可视化

## 任务目标
- 本 Skill 用于：从 **Europe PMC** 数据库搜索**生命科学领域**的开放获取学术文献，并提取 PDF 下载链接
- 能力包含：高级检索、PMC 过滤（确保 100% 可下载）、并行多检索、链接提取、生成美化的 HTML 报告
- 适用领域：生物医学、临床医学、药学、生物学、公共卫生等生命科学相关学科
- 触发条件：用户需要搜索**生命科学领域**的学术文献，获取 PDF 下载链接，并生成可视化报告时

## 默认规范
- **全文链接过滤（重要）**：**默认只返回有全文下载链接的文献**，确保所有结果可直接下载
  - **默认行为**：自动过滤掉没有 PDF/TGZ 下载链接的文献
  - **包含无全文**：如需包含无全文链接的文献，使用 `--include-no-fulltext` 参数
  - **过滤提示**：脚本会显示过滤掉的文献数量，便于了解检索情况
- **MeSH 检索（推荐）**：**优先使用 MeSH（Medical Subject Headings）主题词检索**，提升检索精度和全面性
  - **MeSH 优势**：专业术语标准化、自动扩展同义词、精确匹配医学概念、避免关键词歧义
  - **MeSH 语法**：`"Neoplasms"[MeSH]`（主题词）、`"Neoplasms/drug therapy"[MeSH]`（副主题词）
  - **查找 MeSH**：使用 MeSH Browser（https://www.ncbi.nlm.nih.gov/mesh/）查询标准术语
- **时间范围**：默认搜索**近 10 年**内的文献（从当前年份向前推算），确保文献的新颖性和相关性
- **检索模式**：默认使用**较为宽泛的检索模式**，**多用 OR 连接关键词**，获取更广的结果范围；避免过度使用 AND，提高检索覆盖面
- **文献类型过滤**：**默认排除会议论文**（conference proceedings），专注于期刊论文；使用 `NOT conference NOT proceedings` 过滤
- **筛选策略**：先宽泛检索获取更多结果，后续在 HTML 报告中使用筛选功能缩小范围
- **PMC 过滤**：默认使用 `pubmed pmc[sb]` 过滤器，确保 100% 可下载
- **检索数量**：单次检索默认返回 100 篇文献，多检索式合并后不超过 300 篇

## 前置准备
- 依赖说明：本 Skill 使用以下 Python 包，请使用虚拟环境安装
  ```bash
  # 创建并激活虚拟环境
  python -m venv venv
  source venv/bin/activate  # Linux/macOS
  # 或 venv\Scripts\activate  # Windows

  # 安装依赖
  pip install requests>=2.31.0
  ```
- 输出说明：
  - `links.json`：包含文献信息和 PDF 链接的 JSON 文件
  - `pdf_links.txt`：纯文本格式的 PDF 下载链接列表
  - `literature_report.html`：美化的 HTML 报告，展示文献列表和链接
- 可选配置：
  - NCBI API 邮箱和密钥（提升请求速率限制）：访问 https://www.ncbi.nlm.nih.gov/account/settings/ 获取

## 操作步骤
- 标准流程：

  1. **理解需求并整理关键词**
     - **优先使用 MeSH 术语**：查询 MeSH Browser（https://www.ncbi.nlm.nih.gov/mesh/）获取标准医学主题词
     - 分析用户的输入（可能是中文、英文或混合）
     - 将中文关键词翻译为规范的英文检索词（PubMed 标准术语）
     - 识别关键概念：疾病名称、药物、治疗方式、生物标志物、技术方法等
     - 扩展相关词汇：同义词、缩写、变体、专业术语
     - **MeSH 术语示例**：
       - 癌症 → `Neoplasms[MeSH]`
       - 糖尿病 → `Diabetes Mellitus[MeSH]`
       - 阿尔茨海默病 → `Alzheimer Disease[MeSH]`
       - 药物治疗 → `Drug Therapy[MeSH]` 或 `Therapeutics[MeSH]`
       - 诊断 → `Diagnosis[MeSH]`

  2. **构建多组检索式**
     - **重要**：构建检索式时必须遵循默认规范
       - 动态获取当前年份（使用 `datetime.now().year` 获取系统时间）
       - 计算近 10 年范围（如当前 2026 年，则默认为 `2016:2026[pd]`）
       - 所有检索式默认添加年份限制，除非用户明确要求其他时间范围
       - **优先使用 MeSH 术语**，提升检索精度（参见 MeSH 检索说明）
       - **使用 OR 连接关键词，获取更广的结果**（后续可在 HTML 报告中筛选）
       - **默认排除会议论文**，使用 `NOT conference NOT proceedings` 专注于期刊论文
       - 避免过度使用 AND，提高检索覆盖面
     - 基于整理的关键词，构建 2-4 组不同的检索式
     - **检索式 A（默认宽泛检索 - 推荐 MeSH 模式）**：使用 MeSH 术语 + PMC 过滤 + 排除会议 + 近 10 年
       - 示例（当前年份 2026）：`"Neoplasms/drug therapy"[MeSH] AND pubmed pmc[sb] NOT conference NOT proceedings 2016:2026[pd]`
       - 检索内容：所有癌症药物治疗的期刊论文（MeSH 自动扩展同义词）
     - **检索式 B（多概念宽泛检索）**：使用 OR 连接多个 MeSH 术语 + PMC 过滤 + 排除会议 + 近 10 年
       - 示例：`("Neoplasms"[MeSH] OR "Diabetes Mellitus"[MeSH]) AND pubmed pmc[sb] NOT conference NOT proceedings 2016:2026[pd]`
       - 检索内容：癌症或糖尿病相关文献
     - **检索式 C（普通关键词宽泛检索）**：使用 OR 连接普通关键词 + PMC 过滤 + 排除会议 + 近 10 年
       - 示例：`("cancer OR tumor OR neoplasm") AND pubmed pmc[sb] NOT conference NOT proceedings 2016:2026[pd]`
       - 检索内容：使用同义词检索，但不如 MeSH 精确
     - **检索式 D（可选精确检索）**：仅在用户明确要求精确检索时使用 AND 连接（如 `title:` 字段限定）
       - 示例：`title:"specific term" AND pubmed pmc[sb] 2016:2026[pd]`
     - **检索式 E（可选排除检索）**：排除无关文献 + PMC 过滤 + 排除会议 + 近 10 年（仅在用户需要排除某些类型时使用）
       - 示例：`("topic1"[MeSH] OR "topic2"[MeSH]) AND pubmed pmc[sb] NOT conference NOT proceedings NOT review 2016:2026[pd]`

  3. **获取 PDF 链接**
     - 使用 `get_pdf_links.py` 搜索文献并获取 PDF 下载链接
     - **重要**：执行搜索前确认检索式已包含：
       - 近 10 年的年份限制
       - `NOT conference NOT proceedings` 排除会议论文
       - PMC 过滤器 `pubmed pmc[sb]`
     - 单次检索模式：
       ```bash
       python scripts/get_pdf_links.py --search "(cancer OR tumor) AND pubmed pmc[sb] NOT conference NOT proceedings 2016:2026[pd]" --limit 100 --output links.json
       ```
     - 并行多检索模式：
       ```bash
       python scripts/get_pdf_links.py --search-multi "(cancer OR tumor) AND pubmed pmc[sb] NOT conference NOT proceedings 2016:2026[pd]","(Alzheimer OR dementia) AND pubmed pmc[sb] NOT conference NOT proceedings 2016:2026[pd]" --limit 50 --max-workers 3 --output links.json
       ```
     - 输出结果：`links.json` 包含文献信息和 PDF 链接

  4. **提取 PDF 下载链接**
     - 使用 `extract_pdf_links.py` 提取 PDF 下载链接
     ```bash
     python scripts/extract_pdf_links.py --json links.json --output pdf_links.txt
     ```
     输出：`pdf_links.txt` 包含所有可用的 HTTP 下载链接，用户可以自行选择下载方式（如 wget、IDM 等）

  5. **生成美化的 HTML 报告**
     - 使用 `generate_html_report.py` 脚本直接从 `links.json` 生成 HTML 报告
     - 脚本会自动：
       - 获取当前年份（动态获取，无需手动指定）
       - 根据全文和摘要可用性对文献进行四级分类和排序
       - 生成包含分组展示、统计信息、响应式设计的完整 HTML 页面
     - 执行命令：
       ```bash
       python scripts/generate_html_report.py --json links.json --output literature_report.html
       ```
     - 报告包含：文献标题、作者、发表信息、摘要、PDF 下载链接
     - **排序规则**：优先展示有全文和摘要的文献，将无全文/无摘要的文献放在最下面
       - 第一优先级：有全文 + 有摘要（高亮展示，绿色边框）
       - 第二优先级：有全文 + 无摘要（正常展示，蓝色边框）
       - 第二优先级：有全文 + 无摘要（正常展示，蓝色边框）
       - 第三优先级：无全文 + 有摘要（次要展示，浅色样式）
       - 第四优先级：无全文 + 无摘要（置底，灰色显示）
     - 报告样式：卡片式布局、响应式设计、分组标题显示各优先级文献数量
     - **智能体使用场景**：当需要自定义 HTML 样式或添加额外功能时，智能体可以基于模板生成定制化 HTML

  6. **验证结果**
     - 检查生成的 HTML 报告是否正确展示文献信息
     - 确认 PDF 链接是否有效
     - 查看链接提取统计和成功率
     - 验证年份显示是否为当前年份（动态获取）

- 可选分支：
  - 当用户明确要求其他时间范围：按用户指定的时间范围检索，否则默认使用近 10 年
  - 当用户需要更精确的检索：使用字段限定（如 title:、author:）缩小范围
  - 当用户需要排除某些类型：使用 NOT 操作符排除无关文献
  - 当检索结果过多：进一步增加年份限制或添加更多关键词限定
  - 当 API 请求受限：配置 NCBI API 邮箱和密钥
  - 当需要快速浏览文献列表：生成 HTML 报告并使用搜索/筛选功能

## 资源索引
- 必要脚本：
  - [scripts/get_pdf_links.py](scripts/get_pdf_links.py)（用途：搜索文献并获取 PDF 链接；参数：--search/--search-multi/--limit/--max-workers/--output）
  - [scripts/extract_pdf_links.py](scripts/extract_pdf_links.py)（用途：从 JSON/CSV/标识符提取 PDF 下载链接；参数：--json/--identifiers/--csv/--column/--output）
  - [scripts/generate_html_report.py](scripts/generate_html_report.py)（用途：从 JSON 生成美化的 HTML 报告；参数：--json/--output/--theme；功能：自动获取当前年份、智能分类排序、响应式设计、多主题支持）
- HTML 模板资产：
  - [assets/html-templates/modern.css](assets/html-templates/modern.css)（用途：现代主题样式，蓝绿色系，适合在线浏览）
  - [assets/html-templates/academic.css](assets/html-templates/academic.css)（用途：学术主题样式，黑白配色，适合打印）
  - [assets/html-templates/dark.css](assets/html-templates/dark.css)（用途：深色主题样式，护眼配色，适合夜间阅读）
- 领域参考：见 [references/literature-usage.md](references/literature-usage.md)（何时读取：需要了解高级检索语法、完整参数说明、PMC 过滤技巧、MeSH 检索指南时）
- 输出资产：`links.json`（文献元数据）、`pdf_links.txt`（下载链接）、`literature_report.html`（美化的 HTML 报告）

## 注意事项
- **虚拟环境使用**：强烈建议使用 Python 虚拟环境安装依赖，避免权限冲突和系统包污染
- **适用领域**：本 Skill 专门用于**生命科学领域**（生物医学、临床医学、药学、生物学、公共卫生等）的文献搜索
- **数据源说明**：PubMed 和 Europe PMC 主要收录生物医学和生命科学领域的文献，不适用于物理、数学、计算机等其他学科
- **PMC 过滤的重要性**：默认使用 `pubmed pmc[sb]` 过滤器可确保 100% 可下载
- **文献类型过滤的重要性**：默认使用 `NOT conference NOT proceedings` 过滤会议论文，专注于期刊论文；如需检索会议论文，可移除此过滤
- **时间范围默认规范**：默认搜索近 10 年的文献，确保文献新颖性；仅在用户明确要求其他时间范围时才调整
- **检索模式默认规范**：默认使用较为宽泛的检索模式，**多用 OR 连接关键词**，获取更广的结果范围；后续可在 HTML 报告中使用筛选功能缩小范围；仅在用户需要精确检索时才使用 AND 连接或添加字段限定
- **分步骤执行**：获取链接和下载是两个独立的步骤，可以先获取链接并审查结果，再决定是否下载
- **API 速率限制**：未配置 API 密钥时，NCBI 每秒最多 3 个请求；配置后可提升至 10 个请求
- **HTML 报告设计**：报告应美观、易用、功能完善，支持搜索和筛选，提升用户体验
- **链接有效性**：部分文献可能因权限或访问限制导致 PDF 链接失效，建议优先使用 PMC 过滤器
- **MeSH 检索的重要性**：优先使用 MeSH（Medical Subject Headings）主题词检索，提升检索精度和全面性；MeSH 检索自动扩展同义词、避免关键词歧义、精确匹配医学概念；参见 [references/literature-usage.md](references/literature-usage.md) 中的 MeSH 检索指南

## 使用示例

### 示例 1：搜索文献并获取链接（默认模式）
- **功能说明**：使用默认规范（近 10 年 + OR 宽泛检索 + PMC 过滤 + 排除会议）搜索文献并获取 PDF 下载链接
- **执行方式**：脚本执行
- **关键参数**：`--search "检索关键词"`（使用 OR 连接，排除会议，默认添加近 10 年限制）、`--limit 100`（默认数量）、`--output links.json`（输出文件）
- **示例代码**（当前年份 2026）：
  ```bash
  python scripts/get_pdf_links.py --search "(machine learning OR deep learning) AND pubmed pmc[sb] NOT conference NOT proceedings 2016:2026[pd]" --limit 100 --output links.json
  ```
  输出：`links.json` 包含 100 篇近 10 年内有全文下载链接的期刊论文（已排除会议论文和无全文文献）

### 示例 2：并行搜索多组关键词（默认模式）
- **功能说明**：同时执行多个检索式（均使用 OR 连接，排除会议，包含近 10 年限制），自动合并结果并获取链接
- **执行方式**：脚本执行
- **关键参数**：`--search-multi`（多个检索式，逗号分隔，均排除会议）、`--limit 50`（每个检索的数量）、`--max-workers 3`（检索并发数）、`--output links.json`（输出文件）
- **示例代码**（当前年份 2026）：
  ```bash
  python scripts/get_pdf_links.py --search-multi "(cancer OR tumor) AND pubmed pmc[sb] NOT conference NOT proceedings 2016:2026[pd]","(Alzheimer OR dementia) AND pubmed pmc[sb] NOT conference NOT proceedings 2016:2026[pd]","(diabetes OR hyperglycemia) AND pubmed pmc[sb] NOT conference NOT proceedings 2016:2026[pd]" --limit 50 --max-workers 3 --output links.json
  ```
  输出：`links.json` 包含合并并去重后有全文下载链接的期刊论文（已排除会议论文和无全文文献）

### 示例 3：提取 PDF 下载链接
- **功能说明**：从 JSON 文件提取 PDF 下载链接，输出为文本文件
- **执行方式**：脚本执行
- **关键参数**：`--json links.json`（JSON 文件）、`--output pdf_links.txt`（输出文件）
- **示例代码**：
  ```bash
  python scripts/extract_pdf_links.py --json links.json --output pdf_links.txt
  ```
  输出：`pdf_links.txt` 包含所有可用的 HTTP 下载链接

### 示例 4：生成美化的 HTML 报告（推荐方式）
- **功能说明**：使用脚本直接从 JSON 文件生成美化的 HTML 报告，支持自动分类、智能排序、响应式设计、多主题选择
- **执行方式**：脚本执行（推荐）或智能体生成（定制化需求）
- **脚本执行**：
  ```bash
  # 默认主题：modern（蓝绿色系，适合在线浏览）
  python scripts/generate_html_report.py --json links.json --output literature_report.html --theme modern
  
  # 学术主题：academic（黑白配色，适合打印）
  python scripts/generate_html_report.py --json links.json --output literature_report.html --theme academic
  
  # 深色主题：dark（护眼配色，适合夜间阅读）
  python scripts/generate_html_report.py --json links.json --output literature_report.html --theme dark
  ```
- **功能特性**：
  - 自动获取当前年份（动态获取，无需手动指定）
  - 智能分类：根据全文和摘要可用性自动分组（4 个优先级）
  - 卡片式布局：每篇文献展示完整信息
  - 视觉区分：不同优先级使用不同卡片样式（高亮/正常/浅色/灰色）
  - 统计信息：显示总文献数和各组文献数量
  - 响应式设计：支持移动端和桌面端
  - 多主题支持：3 种配色方案（modern/academic/dark）
  - 分组统计：显示各组文献数量
- **输出**：`literature_report.html` 可直接在浏览器中打开
- **智能体使用场景**：当需要自定义 HTML 样式或添加额外功能（如搜索、筛选）时
  ```bash
  python scripts/generate_html_report.py --json links.json --output literature_report.html
  ```
- **功能特性**：
  - 自动获取当前年份（动态获取，无需手动指定）
  - 智能分类：根据全文和摘要可用性自动分组（4 个优先级）
  - 卡片式布局：每篇文献展示完整信息
  - 视觉区分：不同优先级使用不同卡片样式（高亮/正常/浅色/灰色）
  - 统计信息：显示总文献数和各组文献数量
  - 响应式设计：支持移动端和桌面端
  - 现代配色：蓝绿色系，符合生命科学领域
  - 分组统计：显示各组文献数量
- **输出**：`literature_report.html` 可直接在浏览器中打开
- **智能体使用场景**：当需要自定义 HTML 样式或添加额外功能（如搜索、筛选）时

### 示例 14：从标识符直接提取链接
- **功能说明**：直接使用 PMCID/PMID/DOI 标识符获取下载链接
- **执行方式**：脚本执行
- **关键参数**：`--identifiers`（标识符列表，逗号分隔）、`--output pdf_links.txt`（输出文件）
- **示例代码**：
  ```bash
  python scripts/extract_pdf_links.py --identifiers "PMC5764346,38238491,10.1186/s13059-020-02147-0" --output pdf_links.txt
  ```
  输出：`pdf_links.txt` 包含所有可用的 HTTP 下载链接

### 示例 15：检索自定义主题的文献
- **功能说明**：检索任意生命科学主题的文献
- **执行方式**：脚本执行
- **关键参数**：`--search "检索式"`（根据主题调整）、`--limit`（数量）、`--output`（输出文件）
- **示例代码**（当前年份 2026）：
  ```bash
  # 使用 MeSH 术语检索基因编辑相关文献
  python scripts/get_pdf_links.py --search "\"Gene Editing\"[MeSH] AND pubmed pmc[sb] NOT conference NOT proceedings 2016:2026[pd]" --limit 100 --output links.json
  ```
  输出：`links.json` 包含基因编辑相关期刊论文
- **功能说明**：直接使用 PMCID/PMID/DOI 标识符获取下载链接
- **执行方式**：脚本执行
- **关键参数**：`--identifiers`（标识符列表，逗号分隔）、`--output pdf_links.txt`（输出文件）
- **示例代码**：
  ```bash
  python scripts/extract_pdf_links.py --identifiers "PMC5764346,38238491,10.1186/s13059-020-02147-0" --output pdf_links.txt
  ```
  输出：`pdf_links.txt` 包含所有可用的 HTTP 下载链接

### 示例 6：自定义时间范围检索（非默认场景）
- **功能说明**：当用户明确要求其他时间范围时，使用指定的年份限制而非默认的近 10 年
- **执行方式**：脚本执行
- **关键参数**：`--search`（包含自定义年份限制的检索式）、`--limit`（数量）、`--output`（输出文件）
- **示例代码**（用户要求近 5 年，当前年份 2026）：
  ```bash
  python scripts/get_pdf_links.py --search "(machine learning OR AI) AND pubmed pmc[sb] 2021:2026[pd]" --limit 100 --output links.json
  ```
- **注意**：仅在用户明确要求其他时间范围时才使用此模式，否则默认使用近 10 年

### 示例 7：使用 MeSH 术语检索（推荐模式）
- **功能说明**：使用 MeSH（Medical Subject Headings）主题词检索，提升检索精度和全面性
- **执行方式**：脚本执行
- **关键参数**：`--search "MeSH 术语"`（使用 [MeSH] 字段）、`--limit 100`、`--output links.json`
- **优势对比**：
  - **MeSH 检索**：`"Neoplasms/drug therapy"[MeSH]` 自动扩展为所有癌症药物治疗相关文献，包含同义词、下位词
  - **普通关键词**：`("cancer OR tumor" AND treatment)` 只检索包含特定关键词的文献，可能遗漏相关文献
- **示例代码**（当前年份 2026）：
  ```bash
  # 检索癌症药物治疗相关文献（MeSH 自动扩展）
  python scripts/get_pdf_links.py --search "\"Neoplasms/drug therapy\"[MeSH] AND pubmed pmc[sb] NOT conference NOT proceedings 2016:2026[pd]" --limit 100 --output links.json
  ```
  输出：`links.json` 包含所有癌症药物治疗的期刊论文（MeSH 自动扩展，覆盖全面）
- **查找 MeSH 术语**：
  - 使用 MeSH Browser：https://www.ncbi.nlm.nih.gov/mesh/
  - 输入概念（如 "cancer"、"diabetes"）查询标准 MeSH 术语
  - 查看副主题词（如 `/drug therapy`、`/diagnosis`）优化检索

### 示例 8：并行搜索多个 MeSH 术语（推荐模式）
- **功能说明**：同时检索多个 MeSH 主题词，获取更全面的文献覆盖
- **执行方式**：脚本执行
- **关键参数**：`--search-multi`（多个 MeSH 检索式）、`--limit 50`（每个检索的数量）、`--max-workers 3`（并发数）
- **示例代码**（当前年份 2026）：
  ```bash
  # 同时检索癌症、糖尿病、阿尔茨海默病的药物治疗文献
  python scripts/get_pdf_links.py --search-multi "\"Neoplasms/drug therapy\"[MeSH] AND pubmed pmc[sb] NOT conference NOT proceedings 2016:2026[pd]","\"Diabetes Mellitus/drug therapy\"[MeSH] AND pubmed pmc[sb] NOT conference NOT proceedings 2016:2026[pd]","\"Alzheimer Disease/drug therapy\"[MeSH] AND pubmed pmc[sb] NOT conference NOT proceedings 2016:2026[pd]" --limit 50 --max-workers 3 --output links.json
  ```
  输出：`links.json` 包含三种疾病的药物治疗期刊论文（MeSH 精确检索，自动合并去重）

### 示例 12：生成不同主题的 HTML 报告
- **功能说明**：生成不同配色主题的 HTML 报告，满足不同场景需求
- **执行方式**：脚本执行
- **关键参数**：`--theme`（主题选择：modern/academic/dark）
- **主题说明**：
  - **modern**（默认）：蓝绿色系，卡片式布局，适合在线浏览
  - **academic**：黑白配色，简化布局，适合打印
  - **dark**：深色护眼，深紫色系，适合夜间阅读
- **示例代码**：
  ```bash
  # 生成现代主题报告（蓝绿色系，适合在线浏览）
  python scripts/generate_html_report.py --json links.json --output report_modern.html --theme modern
  
  # 生成学术主题报告（黑白配色，适合打印）
  python scripts/generate_html_report.py --json links.json --output report_academic.html --theme academic
  
  # 生成深色主题报告（护眼配色，适合夜间阅读）
  python scripts/generate_html_report.py --json links.json --output report_dark.html --theme dark
  ```
- **输出**：生成 3 个不同主题的 HTML 文件

### 示例 13：检索会议论文（非默认场景）
- **功能说明**：当用户需要检索会议论文时，移除 `NOT conference NOT proceedings` 过滤
- **执行方式**：脚本执行
- **关键参数**：`--search`（不包含会议排除的检索式）、`--limit`（数量）、`--output`（输出文件）
- **示例代码**（当前年份 2026）：
  ```bash
  python scripts/get_pdf_links.py --search "(machine learning OR AI) AND pubmed pmc[sb] 2016:2026[pd]" --limit 100 --output links.json
  ```
- **注意**：仅在用户明确需要会议论文时才移除此过滤，默认模式会排除会议论文

### 示例 14：从标识符直接提取链接

## 高级功能

### 文献智能分组和排序
根据全文和摘要的可用性自动分组排序，优先展示最有价值的文献：
- **高优先级组**（有全文 + 有摘要）：彩色边框，置顶展示
- **中优先级组**（有全文 + 无摘要）：正常样式，紧随其后
- **低优先级组**（无全文 + 有摘要）：浅色样式，次要位置
- **最低优先级组**（无全文 + 无摘要）：灰色样式，置于页面底部

### 自定义 HTML 报告样式
用户可以指定报告的配色方案和布局风格：
- **学术风格**：简洁黑白配色，适合打印
- **现代风格**：蓝绿色系，适合在线浏览
- **深色模式**：护眼配色，适合夜间阅读

### 批量处理标识符
支持从 CSV 文件批量提取下载链接：
```bash
python scripts/extract_pdf_links.py --csv identifiers.csv --column pmcid --output pdf_links.txt
```

### 包含没有全文链接的文献（非默认场景）
- **功能说明**：当用户需要包含没有全文下载链接的文献时，使用 `--include-no-fulltext` 参数
- **执行方式**：脚本执行
- **关键参数**：`--include-no-fulltext`（包含无全文文献）、`--search` 或 `--search-multi`（检索式）
- **示例代码**：
  ```bash
  # 单次检索，包含无全文文献
  python scripts/get_pdf_links.py --search "(machine learning OR deep learning) AND pubmed pmc[sb] NOT conference NOT proceedings 2016:2026[pd]" --limit 100 --include-no-fulltext --output all_links.json

  # 多检索，包含无全文文献
  python scripts/get_pdf_links.py --search-multi "(cancer OR tumor) AND pubmed pmc[sb] NOT conference NOT proceedings 2016:2026[pd]","(Alzheimer OR dementia) AND pubmed pmc[sb] NOT conference NOT proceedings 2016:2026[pd]" --limit 50 --max-workers 3 --include-no-fulltext --output all_links.json
  ```
  输出：`all_links.json` 包含所有检索到的文献（包括没有全文链接的）

### 检索结果排序
根据影响因子、引用次数、发表日期等维度对文献排序（需要在 HTML 报告中实现）
