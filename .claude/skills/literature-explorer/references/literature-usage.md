# 生命科学文献下载参考文档

## 目录
- [工具概述](#工具概述)
- [核心概念](#核心概念)
- [MeSH 检索指南](#mesh-检索指南)
- [高级检索语法](#高级检索语法)
- [完整参数说明](#完整参数说明)
- [PMC 过滤技巧](#pmc-过滤技巧)
- [批量下载方法](#批量下载方法)
- [API 配置](#api-配置)
- [常见问题](#常见问题)

## 工具概述

本工具专为**生命科学领域**的科研工作者设计，集成 PubMed 和 Europe PMC 等权威生物医学数据库。

### 适用领域
- 生物医学研究
- 临床医学
- 药物研发
- 生物学
- 公共卫生
- 神经科学
- 遗传学
- 其他生命科学相关学科

### 核心特性
- 🔍 **智能搜索** - 支持高级检索语法，精确查找文献
- 📥 **批量下载** - 自动下载开放获取 PDF，支持并发
- 📋 **混合输入** - 支持 CSV 文件（PMCID/PMID/DOI）批量下载
- 🎯 **PMC 过滤** - 使用 `pubmed pmc[sb]` 确保 100% 可下载
- 💾 **智能缓存** - 避免重复下载，提升效率

## 核心概念

### MeSH（Medical Subject Headings）主题词
**MeSH 是什么**：美国国家医学图书馆（NLM）的医学主题词表，是生物医学领域的标准术语系统

**MeSH 检索优势**：
- **精确匹配**：使用标准化医学术语，避免关键词歧义
- **自动扩展**：自动包含同义词、上位词、下位词，检索更全面
- **专业组织**：按疾病、治疗、诊断等维度组织，便于定位
- **国际通用**：PubMed、PMC、Europe PMC 等主流数据库都支持

**MeSH 检索语法**：
```bash
# 基本语法：主题词[MeSH]
"Neoplasms"[MeSH]  # 癌症

# 副主题词：主题词/副主题词[MeSH]
"Neoplasms/drug therapy"[MeSH]  # 癌症的药物治疗
"Diabetes Mellitus/diagnosis"[MeSH]  # 糖尿病的诊断

# 多个 MeSH 术语 OR 连接
("Neoplasms"[MeSH] OR "Diabetes Mellitus"[MeSH])

# 主要 MeSH 主题
"[MeSH Major Topic]"  # 限定为主要 MeSH 主题的文献
```

**查找 MeSH 术语**：
1. 访问 MeSH Browser：https://www.ncbi.nlm.nih.gov/mesh/
2. 在搜索框中输入概念（如 "cancer"、"diabetes"、"AI"）
3. 查看返回的 MeSH 术语及其定义
4. 浏览副主题词（如 `/drug therapy`、`/diagnosis`、`/epidemiology`）
5. 复制 MeSH 术语用于检索

**常用 MeSH 术语示例**：
| 中文概念 | MeSH 术语 | 说明 |
|---------|-----------|------|
| 癌症/肿瘤 | `Neoplasms[MeSH]` | 包含所有类型癌症 |
| 糖尿病 | `Diabetes Mellitus[MeSH]` | 糖尿病总称 |
| 阿尔茨海默病 | `Alzheimer Disease[MeSH]` | 阿尔茨海默病 |
| 药物治疗 | `Drug Therapy[MeSH]` | 药物治疗 |
| 诊断 | `Diagnosis[MeSH]` | 诊断方法 |
| 治疗/疗法 | `Therapeutics[MeSH]` | 治疗方法 |
| 基因编辑 | `Gene Editing[MeSH]` | 基因编辑技术 |
| 免疫疗法 | `Immunotherapy[MeSH]` | 免疫治疗 |

**MeSH vs 普通关键词对比**：
| 检索方式 | 示例 | 覆盖范围 | 精确度 | 推荐度 |
|---------|------|----------|--------|--------|
| **MeSH 检索** | `"Neoplasms"[MeSH]` | 自动扩展同义词、下位词 | 高 | ⭐⭐⭐⭐⭐ |
| **普通关键词** | `("cancer OR tumor OR neoplasm")` | 仅检索指定关键词 | 中 | ⭐⭐⭐ |
| **组合检索** | `("Neoplasms"[MeSH] OR "cancer")` | 结合两者优势 | 高 | ⭐⭐⭐⭐ |

### 数据源
- **Europe PMC**: 欧洲版本的 PMC 数据库，收录生物医学和生命科学文献（**默认，更稳定**）
- **PubMed**: 美国国家医学图书馆的文献检索系统，主要收录生物医学和生命科学文献（备选）
- **PMC (PubMed Central)**: PubMed 的全文存档系统，提供开放获取的全文 PDF

### 标识符类型
| 类型 | 示例 | 说明 |
|------|------|------|
| **PMCID** | PMC123456
        
        
        
        
        
        
        
        
        
         | PMC 内部标识符，可直接下载 |
| **PMID** | 38238491 | PubMed 标识符 |
| **DOI** | 10.1186/s12916-020-01690-4
        
        
        
        
        
        
        
        
        
         | 数字对象标识符 |

### 下载模式
- **统计模式**: 仅检索文献，显示统计信息，不下载 PDF
- **下载模式**: 检索文献并下载 PDF 文件

## MeSH 检索指南

### MeSH 检索入门

**基本检索示例**：
```bash
# 检索癌症相关文献（MeSH 自动扩展）
python scripts/get_pdf_links.py --search "\"Neoplasms\"[MeSH] AND pubmed pmc[sb] NOT conference NOT proceedings 2016:2026[pd]" --limit 100 --output links.json

# 检索糖尿病相关文献
python scripts/get_pdf_links.py --search "\"Diabetes Mellitus\"[MeSH] AND pubmed pmc[sb] NOT conference NOT proceedings 2016:2026[pd]" --limit 100 --output links.json
```

### MeSH 副主题词检索

**常用副主题词**：
| 副主题词 | 含义 | 示例 |
|---------|------|------|
| `/drug therapy` | 药物治疗 | `Neoplasms/drug therapy` |
| `/diagnosis` | 诊断 | `Diabetes Mellitus/diagnosis` |
| `/therapy` | 治疗 | `Alzheimer Disease/therapy` |
| `/epidemiology` | 流行病学 | `Neoplasms/epidemiology` |
| `/prevention and control` | 预防与控制 | `Diabetes Mellitus/prevention and control` |
| `/genetics` | 遗传学 | `Alzheimer Disease/genetics` |

**副主题词检索示例**：
```bash
# 检索癌症的药物治疗相关文献
python scripts/get_pdf_links.py --search "\"Neoplasms/drug therapy\"[MeSH] AND pubmed pmc[sb] NOT conference NOT proceedings 2016:2026[pd]" --limit 100 --output links.json

# 检索糖尿病的诊断相关文献
python scripts/get_pdf_links.py --search "\"Diabetes Mellitus/diagnosis\"[MeSH] AND pubmed pmc[sb] NOT conference NOT proceedings 2016:2026[pd]" --limit 100 --output links.json
```

### MeSH 组合检索

**多个 MeSH 术语 OR 连接**（宽泛检索）：
```bash
# 检索癌症或糖尿病相关文献
python scripts/get_pdf_links.py --search "(\"Neoplasms\"[MeSH] OR \"Diabetes Mellitus\"[MeSH]) AND pubmed pmc[sb] NOT conference NOT proceedings 2016:2026[pd]" --limit 100 --output links.json
```

**多个 MeSH 术语 AND 连接**（精确检索）：
```bash
# 检索癌症且涉及免疫疗法的文献
python scripts/get_pdf_links.py --search "\"Neoplasms\"[MeSH] AND \"Immunotherapy\"[MeSH] AND pubmed pmc[sb] NOT conference NOT proceedings 2016:2026[pd]" --limit 100 --output links.json
```

### MeSH 高级检索

**主要 MeSH 主题**：
```bash
# 检索主要 MeSH 主题为癌症的文献
python scripts/get_pdf_links.py --search "\"Neoplasms\"[MeSH Major Topic] AND pubmed pmc[sb] NOT conference NOT proceedings 2016:2026[pd]" --limit 100 --output links.json
```

**MeSH + 普通关键词组合**：
```bash
# MeSH 术语 + 特定关键词
python scripts/get_pdf_links.py --search "(\"Neoplasms\"[MeSH] AND \"CRISPR\") AND pubmed pmc[sb] NOT conference NOT proceedings 2016:2026[pd]" --limit 100 --output links.json
```

### 查找 MeSH 术语的方法

**方法一：使用 MeSH Browser**
1. 访问 https://www.ncbi.nlm.nih.gov/mesh/
2. 在搜索框输入概念（中文或英文）
3. 查看返回的 MeSH 术语
4. 点击术语查看详细信息
5. 浏览副主题词列表
6. 复制 MeSH 术语用于检索

**方法二：使用 PubMed 检索**
1. 访问 https://pubmed.ncbi.nlm.nih.gov/
2. 搜索概念（如 "cancer"）
3. 在右侧栏查看 "MeSH terms"
4. 点击 MeSH 术语查看详细信息

**方法三：使用智能体辅助**
- 让智能体帮助查找 MeSH 术语
- 例如："请帮我查找 '肺癌' 的 MeSH 术语"

## 高级检索语法

### 免费全文过滤

#### PMC 全文过滤（推荐，100% 可下载）

使用 `pubmed pmc[sb]` 过滤器只返回在 PubMed Central 中收录的文献，所有结果都可以下载：

```bash
# 搜索 PMC 收录的癌症文献（100% 可下载）
pdfget -s "cancer AND pubmed pmc[sb]" -l 100 -d

# 基因家族研究
pdfget -s '"gene family" AND pubmed pmc[sb]' -l 200

# 配合年份限制
pdfget -s '"machine learning" AND pubmed pmc[sb] 2020:2023[pd]' -l 100 -d
```

#### 免费全文过滤

使用 `filter[free full text]` 包含所有类型的免费全文：

```bash
# 搜索有免费全文的高血压文献
pdfget -s "hypertension filter[free full text]" -l 100

# 搜索特定领域的免费全文文献
pdfget -s "machine learning filter[free full text]" -l 50 -d
```

**重要说明**：

| 过滤器 | 可下载率 | 说明 |
|--------|----------|------|
| `pubmed pmc[sb]` | 100% | 只返回 PMC 收录文献，**推荐使用** |
| `filter[free full text]` | 30-40% | 包含所有免费全文，部分无法下载 |

### 布尔运算符

```bash
# AND: 同时包含多个关键词
pdfget -s "cancer AND immunotherapy" -l 30

# OR: 包含任意关键词
pdfget -s "machine OR deep learning" -l 20

# NOT: 排除特定词汇
pdfget -s "cancer AND immunotherapy NOT review" -l 30

# 复杂组合
pdfget -s "(cancer OR tumor) AND immunotherapy NOT mice" -l 25

# 下载模式（添加 -d）
pdfget -s "cancer AND immunotherapy" -l 30 -d
```

### 字段检索

```bash
# 标题检索
pdfget -s 'title:"deep learning"' -l 15

# 作者检索
pdfget -s 'author:hinton AND title:"neural networks"' -l 10

# 期刊检索
pdfget -s 'journal:Nature AND cancer' -l 20

# 标题 AND 作者
pdfget -s 'title:"transformer" AND author:vaswani' -l 10
```

### 日期范围过滤

```bash
# 按年份过滤
pdfget -s "machine learning AND pubmed pmc[sb] 2020:2023[pd]" -l 100

# 最近 3 年
pdfget -s "cancer AND pubmed pmc[sb] 2022:2025[pd]" -l 50

# 特定年份
pdfget -s "immunotherapy AND 2023[pd]" -l 30
```

## 完整参数说明

### 必需参数（二选一）

#### 搜索模式
```bash
-s QUERY, --search QUERY
```
搜索文献，支持高级检索语法。

**示例**:
```bash
pdfget -s "cancer AND pubmed pmc[sb]"
pdfget -s 'title:"deep learning" AND author:hinton'
```

#### 批量输入模式
```bash
-m INPUT, --mode INPUT
```
批量输入，支持：
- CSV 文件路径
- 单个标识符（PMCID/PMID/DOI）
- 多个标识符（逗号分隔）

**示例**:
```bash
# CSV 文件
pdfget -m identifiers.csv

# 单个标识符
pdfget -m "PMC5764346
        
        "

# 多个标识符
pdfget -m "PMC123456
        
        ,38238491,10.1186/s12916-020-01690-4"
```

### 常用参数

#### 下载模式
```bash
-d, --download
```
下载 PDF 文件。默认为统计模式（仅检索，不下载）。

#### 处理数量
```bash
-l NUM, --limit NUM
```
处理数量（默认 200）。

**示例**:
```bash
python download_literature.py -s "cancer" -l 50 -d
```

#### 并发线程数
```bash
-t NUM, --threads NUM
```
并发线程数（默认 5）。增加线程数可提升下载速度，但可能触发 API 限制。

**示例**:
```bash
python download_literature.py -s "cancer" -t 5 -d
```

#### 下载延迟
```bash
--delay SEC
```
下载延迟秒数（默认 1.0）。调整延迟避免触发 API 限制。

**示例**:
```bash
python download_literature.py -s "cancer" --delay 0.5 -d
```

#### 输出目录
```bash
-o DIR, --output DIR
```
输出目录（默认 `data/pdfs`）。

**示例**:
```bash
python download_literature.py -s "cancer" -d -o ~/papers
```

#### 详细输出
```bash
-v, --verbose
```
显示详细的执行信息。

### 数据源选择

```bash
-S {pubmed,europe_pmc,both}, --source {pubmed,europe_pmc,both}
```

| 选项 | 说明 |
|------|------|
| `europe_pmc` | Europe PMC（**默认，更稳定**） |
| `pubmed` | PubMed（备选） |
| `both` | 同时使用两个数据源 |

**示例**:
```bash
python download_literature.py -s "cancer" -S europe_pmc -d
python download_literature.py -s "cancer" -S pubmed -d
python download_literature.py -s "cancer" -S both -d
```

### CSV 相关参数

```bash
-c COLUMN, --column COLUMN
```
指定 CSV 文件中的列名。

**示例**:
```bash
# CSV 文件格式：
# pmcid
# PMC5764346
# PMC5761748

python download_literature.py -m identifiers.csv -c pmcid -d
```

### API 配置参数

#### NCBI API 邮箱
```bash
-e EMAIL, --email EMAIL
```
NCBI API 邮箱。提供邮箱可提升 API 请求速率限制。

**获取方式**: 访问 https://www.ncbi.nlm.nih.gov/account/settings/

#### NCBI API 密钥
```bash
-k KEY, --api-key KEY
```
NCBI API 密钥。提供密钥可进一步提升 API 请求速率限制。

**获取方式**: 访问 https://www.ncbi.nlm.nih.gov/account/settings/

**速率限制对比**:

| 配置 | 请求速率 |
|------|----------|
| 无配置 | 3 次/秒 |
| 仅邮箱 | 3 次/秒 |
| 邮箱 + 密钥 | 10 次/秒 |

## PMC 过滤技巧

### 为什么使用 PMC 过滤？

许多期刊提供免费的开放获取（Open Access），但这些文献：
1. 可能只存在于期刊官网
2. 可能需要 6-12 个月的延迟才被 PMC 收录
3. 有些期刊选择不在 PMC 存放全文
4. PDFGet 只能从 PMC 下载，无法处理其他来源

### 最佳实践

#### 1. 确保 100% 可下载
```bash
# 推荐方式
pdfget -s "your-topic AND pubmed pmc[sb]" -l 50 -d
```

#### 2. 结合年份过滤
```bash
# 限制年份提升 PMC 收录率
pdfget -s "machine learning AND pubmed pmc[sb] 2020:2023[pd]" -l 100 -d
```

#### 3. 避免使用 filter[free full text]
```bash
# 不推荐（可下载率低）
pdfget -s "cancer filter[free full text]" -l 100 -d

# 推荐（100% 可下载）
pdfget -s "cancer AND pubmed pmc[sb]" -l 100 -d
```

#### 4. 发现更多免费文献（统计用）
```bash
# 用于了解开放获取情况
pdfget -s "your-topic filter[free full text]" -l 1000
```

## 批量下载方法

### 方法 1：CSV 文件批量下载

**CSV 文件格式**:
```csv
pmcid
PMC5764346
PMC5761748
PMC1234567
PMC7654321
```

**执行下载**:
```bash
# 自动检测列名
pdfget -m identifiers.csv -d

# 指定列名
pdfget -m identifiers.csv -c pmcid -d

# 调整并发数和延迟
pdfget -m identifiers.csv -c pmcid -d -t 5 --delay 0.5
```

### 方法 2：混合标识符批量下载

```bash
# 单个标识符
pdfget -m "PMC123456" -d

# 多个标识符（逗号分隔）
pdfget -m "PMC123456,38238491,10.1186/s12916-020-01690-4" -d

# 使用环境变量（大批量）
export PMCID_LIST="PMC123456,PMC234567,PMC345678,..."
pdfget -m "$PMCID_LIST" -d
```

### 方法 3：从其他来源导入

**从 PubMed 导出 PMCID 列表**:
1. 在 PubMed 搜索文献
2. 使用 `pubmed pmc[sb]` 过滤
3. 选择 "Send to" → "File"
4. 格式选择 "PMID list" 或 "PMCID"
5. 保存为文本文件
6. 使用 pdfget 批量下载

**从文献管理软件导出**:
- EndNote/Mendeley/Zotero
- 导出包含 PMCID/PMID/DOI 的 CSV 文件
- 使用 pdfget 批量下载

## API 配置

### 获取 API 密钥

1. 访问 https://www.ncbi.nlm.nih.gov/account/settings/
2. 登录或创建 NCBI 账户
3. 进入 "API Key Management"
4. 创建 API 密钥

### 配置方式

#### 方式 1：命令行参数
```bash
pdfget -s "cancer" -d -e "your@email.com" -k "your_api_key"
```

#### 方式 2：环境变量（推荐）
```bash
# 设置环境变量
export NCBI_EMAIL="your@email.com"
export NCBI_API_KEY="your_api_key"

# 直接使用（无需每次指定）
pdfget -s "cancer" -l 100 -d
```

#### 方式 3：Shell 配置文件
```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export NCBI_EMAIL="your@email.com"
export NCBI_API_KEY="your_api_key"

# 重新加载配置
source ~/.bashrc
```

## 常见问题

### Q1: 下载速度慢怎么办？

**解决方案**:
1. 增加 API 密钥配置（提升到 10 次/秒）
2. 调整并发线程数：`-t 5`
3. 减少延迟：`--delay 0.5`

```bash
pdfget -s "cancer" -d -t 5 --delay 0.5
```

### Q2: 部分文献无法下载？

**原因**:
- 使用了 `filter[free full text]` 而非 `pubmed pmc[sb]`
- 较新的文献（<1 年）尚未被 PMC 收录
- 文献本身是付费的（非开放获取）

**解决方案**:
```bash
# 使用 PMC 过滤器确保 100% 可下载
pdfget -s "your-topic AND pubmed pmc[sb]" -l 100 -d

# 限制年份提升收录率
pdfget -s "your-topic AND pubmed pmc[sb] 2020:2023[pd]" -l 100 -d
```

### Q3: 如何处理大批量下载？

**解决方案**:
1. 将大批量拆分为多个小批次
2. 使用智能缓存功能（中断后可继续）
3. 增加并发数和调整延迟

```bash
# 分批下载
pdfget -m batch1.csv -d
pdfget -m batch2.csv -d
pdfget -m batch3.csv -d
```

### Q4: API 请求被限制？

**原因**: 未配置 API 密钥，触发了速率限制（3 次/秒）

**解决方案**:
```bash
# 配置 API 密钥
export NCBI_EMAIL="your@email.com"
export NCBI_API_KEY="your_api_key"

# 或增加延迟
pdfget -s "cancer" -d --delay 2.0
```

### Q5: 如何仅统计而不下载？

**解决方案**: 不使用 `-d` 参数

```bash
# 仅统计
pdfget -s "cancer immunotherapy" -l 1000

# 输出统计信息，不下载 PDF
```

### Q6: CSV 文件格式要求？

**要求**:
- CSV 格式（逗号分隔）
- 第一行为列名
- 至少包含一列标识符（pmcid/pmid/doi）

**示例格式**:
```csv
pmcid,title,author
PMC5764346,Study on cancer,Smith J
PMC5761748,Machine learning,Johnson A
PMC1234567,Deep learning,Brown R
```

```bash
# 使用 pmcid 列
pdfget -m data.csv -c pmcid -d
```

### Q7: 支持哪些数据库？

**当前支持**:
- PubMed（默认）
- Europe PMC（备选）

**计划支持**:
- Semantic Scholar
- arXiv（未来版本）

### Q8: 下载的 PDF 文件命名规则？

**命名格式**: `{pmcid}.pdf`

**示例**:
- `PMC5764346.pdf`
- `PMC5761748.pdf`

**存储位置**: 默认 `data/pdfs/` 目录，可通过 `-o` 参数修改。

## 高级技巧

### 技巧 1：构建高效检索式

```bash
# 核心关键词 + PMC 过滤 + 年份限制
pdfget -s "cancer immunotherapy AND pubmed pmc[sb] 2020:2025[pd]" -l 100 -d

# 字段检索提升准确性
pdfget -s 'title:"transformer" AND author:vaswani AND pubmed pmc[sb]' -l 20 -d

# 布尔组合
pdfget -s "(cancer OR tumor) AND immunotherapy NOT mice AND pubmed pmc[sb]" -l 50 -d
```

### 技巧 2：自动化工作流

```bash
#!/bin/bash
# 批量下载脚本

# 配置
TOPIC="machine learning"
YEARS="2020:2025"
LIMIT=100
OUTPUT_DIR="~/papers/ml_papers"

# 创建输出目录
mkdir -p $OUTPUT_DIR

# 下载
pdfget -s "$TOPIC AND pubmed pmc[sb] $YEARS[pd]" -l $LIMIT -d -o $OUTPUT_DIR

# 统计
echo "下载完成: $(ls $OUTPUT_DIR/*.pdf | wc -l) 个 PDF 文件"
```

### 技巧 3：与文献管理软件集成

```bash
# 下载后导入到文献管理软件
pdfget -s "cancer AND pubmed pmc[sb]" -l 50 -d -o ~/papers/zotero_import

# 在 Zotero 中使用 "File → Import Folder" 导入
```

### 技巧 4：定时更新文献

```bash
# 添加到 crontab，每周下载最新文献
# 每周一凌晨 2 点执行
0 2 * * 1 cd /path/to/project && pdfget -s "cancer AND pubmed pmc[sb] 2025[pd]" -l 100 -d
```
