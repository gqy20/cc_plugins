---
name: design-scout
description: Awwwards 设计灵感侦察 — 按奖项/分类/技术栈/UI元素/配色采集前端设计参考
user-invocable: true
version: 0.1.0
tags: [design, frontend, inspiration, ui, ux, awwwards]
argument-hint: <查询内容> [模式] [数量]
---

# Design Scout — Awwwards 设计灵感侦察

**目标**：`$1` | **模式**：`${2:-auto}` | **数量**：`${3:-5}`

---

## 快速入口

| 用户意图 | 模式 | 执行流程 |
|----------|------|----------|
| "找电商网站灵感" | `category` | → [按业务分类查找](#按业务分类-category) |
| "Webflow 能做出什么效果" | `technology` | → [按技术栈查找](#按技术栈-technology) |
| "Footer 怎么设计" | `element` | → [按 UI 元素查找](#按-ui-元素-element) |
| "暗色系网站参考" | `color` / `search` | → [按关键词/配色搜索](#搜索与筛选) |
| "分析这个获奖站" | `analyze` | → [单作品深度分析](#单作品深度分析-analyze) |
| "最近 10 个 SOTD" | `awards` | → [按奖项级别浏览](#按奖项级别-awards) |
| "收集 Pastel 配色参考" | `collection` | → [策展合集浏览](#策展合集-collection) |

自动识别：若 `$2` 未指定，根据 `$1` 关键词自动匹配模式。

---

## 前置准备

每次使用前执行：

```bash
# 确保浏览器可用
playwright-cli open --browser=chrome 2>&1 | head -3

# 如果已有会话则跳过（检查 playwright-cli list）
```

结束时关闭：

```bash
playwright-cli close
```

---

## 通用操作原语

以下命令在所有流程中复用：

```bash
# 导航到页面
playwright-cli goto <URL>

# 截图保存（用于分析）
playwright-cli screenshot --filename=/tmp/design-scout/<场景>.png

# 点击元素（通过 ref 或文本）
playwright-cli click e<ref>
playwright-cli click "<可见文本>"

# 填写搜索框
playwright-cli fill e<ref> "<关键词>"
playwright-cli press Enter

# 获取页面快照（提取结构化数据）
playwright-cli snapshot --filename=/tmp/design-scout/snapshot.yml

# 滚动页面
playwright-cli eval "window.scrollTo(0, document.body.scrollHeight)"
```

---

## 按业务分类 (category)

**适用**："找 XX 类型的网站设计"（电商、代理、企业、建筑、时尚…）

### URL 映射表

| 分类 | URL slug | 数量 |
|------|----------|------|
| E-commerce | `/websites/e-commerce/` | 6281 |
| Design Agencies | `/websites/design-agencies/` | 11081 |
| Business & Corporate | `/websites/business-corporate/` | 11075 |
| Architecture | `/websites/architecture/` | 3081 |
| Restaurant & Hotel | `/websites/hotel-restaurant/` | 2409 |
| Fashion | `/websites/fashion/` | 3753 |
| Mobile & Apps | `/websites/mobile-apps/` | 3177 |
| Interaction Design | `/websites/interaction-design/` | 3297 |
| Illustration | `/websites/illustration/` | 4137 |
| Header Design | `/websites/header-design/` | 1641 |

### 执行流程

```
1. playwright-cli goto https://www.awwwards.com/websites/{slug}/
2. playwright-cli screenshot --filename=/tmp/design-scout/category-{name}.png
3. 从 snapshot 中提取前 $3 个作品的：
   - 标题 (heading)
   - 作者/工作室 (strong)
   - 链接 (/sites/{slug})
4. 对每个作品执行 [单作品深度分析](#单作品深度分析-analyze) 的简化版（仅截图+标签）
5. 输出结构化结果
```

---

## 按技术栈 (technology)

**适用**："用 XX 技术做的好的站"（React、Webflow、GSAP、Three.js…）

### URL 映射表

| 技术 | URL slug |
|------|----------|
| React | `/websites/react/` |
| WordPress | `/websites/wordpress/` |
| Webflow | `/websites/webflow/` |
| Framer | `/websites/framer/` |
| Next.js | `/websites/next-js/` |
| GSAP | `/websites/gsap/` |
| Three.js | `/websites/three-js/` |
| WebGL | `/websites/webgl/` |
| WebGL + Three.js | `/websites/webgl-three-js/` |
| Vue.js | `/websites/vue-js/` |

### 执行流程

同 [按业务分类](#按业务分类-category)，替换 URL 即可。

---

## 按 UI 元素 (element)

**适用**："XX 组件怎么设计"（Header、Footer、CTA、动画、导航…）

### 入口

```
https://www.awwwards.com/elements/
搜索框占位符: "Search by Elements"
```

### Category 完整列表（40+）

**布局类**: Header, Hero Image, Footer, Layout, Sidebar, Desktop thumbnail, Mobile thumbnail

**导航类**: Navigation, Menu, Breadcrumb

**交互类**: CTA, Forms, Contact, Login/Sign up, Modal/Popup, Search, Shopping cart

**动效类**: Animation, Transition, Scroll, Loading, Mouse Interaction, Interaction

**内容类**: Gallery, Slider, Blog, Content, Pricing page, Products, Team, About Us, FAQ, 404 pages

**反馈类**: Notification (alerts, toast/flash messages), Cookie

**视觉类**: Icons, Illustration, Photo, Branding (Logo, Design Systems), Microcopy and UX writing

**其他**: Maps, Newsletter, Social Share, Stats, Other Element

### URL 格式

```
https://www.awwwards.com/elements/{category-slug}/
```

常见 slug 映射：

| 元素 | slug |
|------|------|
| Header | `header` |
| Footer | `footer` |
| CTA | `CTA` |
| Navigation | `navigation` |
| Menu | `menu` |
| Modal/Popup | `modal` |
| Animation | `animation` |
| Transition | （在列表中标记为 Transition） |
| Forms | `forms` |
| Contact | `contact` |
| Gallery | `gallery` |
| Hero Image | `hero_image` |
| Loading | `loading` |
| Mouse Interaction | `mouse_interaction` |
| Scroll | `scroll` |
| Interaction | `interaction` |

### Color 筛选

Elements 页面支持按 **hex 色值** 筛选：

```
URL 格式: https://www.awwwards.com/elements/%23{HEX}/
示例: https://www.awwwards.com/elements/%23404040/  (暗色)
      https://www.awwwards.com/elements/%231981C8/  (蓝色)
```

色板为网格选择器，约 20+ 预设色值。

### 执行流程

```
1. playwright-cli goto https://www.awwwards.com/elements/{slug}/
2. 可选：点击 Color 筛选，选目标色值
3. playwright-cli screenshot --filename=/tmp/design-scout/element-{name}.png
4. 从 snapshot 提取前 $3 个元素实例：
   - 元素类型标签 (Transition/Footer/CTA/...)
   - 标题
   - 来源工作室
   - 链接 (/inspiration/{slug})
5. 对有代表性的 1-2 个进入详情页:
   playwright-cli goto https://www.awwwards.com/inspiration/{slug}
   - 截取视频/图片演示效果
6. 输出：每个元素的设计特点描述 + 截图 + 来源站链接
```

---

## 搜索与筛选 (search)

### 全站搜索

**Websites 搜索**：
```
URL: https://www.awwwards.com/websites/?text={keyword}
搜索框: "Search by Websites"
```

**Elements 搜索**：
```
URL: https://www.awwwards.com/elements/?text={keyword}
搜索框: "Search by Elements"
```

**Collections 搜索**：
```
URL: https://www.awwwards.com/collections/search/
```

### 组合筛选

Elements 页面支持 **Category + Color** 同时筛选：
```
先选 Category → 再叠加 Color → 结果为交集
```

### 执行流程

```
1. playwright-cli goto https://www.awwwards.com/websites/?text={encoded-keyword}
2. playwright-cli screenshot --filename=/tmp/design-scout/search-{keyword}.png
3. 从 snapshot 提取搜索结果列表
4. 输出匹配度排序的结果
```

---

## 单作品深度分析 (analyze)

**适用**："分析这个站的设计"、"看看这个 SOTD 的评分"

### 入口

```
https://www.awwwards.com/sites/{site-slug}
```

### 详情页完整数据提取清单

```
┌─────────────────────────────────────────────┐
│  基本信息                                     │
│  - 标题 (h1)                                 │
│  - 作者/工作室 (link + PRO 标识)              │
│  - 获奖等级 (SOTD/SOTM/SOTY/Honorable)       │
│  - 总分 (X.XX/10)                            │
│  - 外链 (Visit Site → 实际网站 URL)           │
├─────────────────────────────────────────────┤
│  Technologies & Tools (标签云)                │
│  - 业务分类标签: Design Agencies, E-commerce.. │
│  - 风格标签: Clean, Minimal, Bold...          │
│  - 功能标签: Portfolio, Promotional...        │
│  - 技术标签: React, Webflow, GSAP...         │
├─────────────────────────────────────────────┤
│  Description (一句话简介)                     │
├─────────────────────────────────────────────┤
│  DESIGN SCORE (设计分)                       │
│  总分 + 四维度:                              │
│    Design 40% | Usability 30%               │
│    Creativity 20% | Content 10%             │
│  Jury 投票明细 (每人每项打分)                 │
│  Community 投票明细                           │
├─────────────────────────────────────────────┤
│  DEV SCORE (开发分)                          │
│  总分 + 六维度:                              │
│    Semantics·SEO | Animations·Transitions   │
│    Accessibility | WPO                       │
│    Responsive Design | Markup·Meta-data      │
│  Jury + Community DEV 投票明细               │
├─────────────────────────────────────────────┤
│  Collections (包含此站的策展合集)              │
└─────────────────────────────────────────────┘
```

### Tab 切换栏

详情页中部有固定 Tab 栏（约 10 个 tab）：
- **Creator** — 创作者信息
- **Font & Color** — 字体和配色方案
- **Details** — 详细信息
- **Score** — 评分详情（锚点跳转到评分区）

### 执行流程

```
1. playwright-cli goto https://www.awwwards.com/sites/{slug}
2. playwright-cli screenshot --filename=/tmp/design-scout/site-{slug}.png
3. 提取基本信息（标题、作者、获奖等级、总分）
4. 提取 Technologies & Tools 标签
5. 提取 Description
6. 提取 DESIGN SCORE（四维分数 + Jury/Community 投票）
7. 提取 DEV SCORE（六维分数 + Jury/Community 投票）
8. 提取关联 Collections
9. 输出结构化分析报告
```

---

## 按奖项级别 (awards)

**适用**："最近获奖的站有哪些"

### 入口路径

Explore > Awards 下拉菜单：

| 奖项 | URL | 数量 | 含义 |
|------|-----|------|------|
| Honor Mentions | `/websites/` | 25K | 入围提名 |
| Nominees | `/websites/nominees/` | 48K | 当期提名 |
| Sites of the Day | `/websites/sites_of_the_day/` | 6,335 | 每日最佳 |
| Sites of the Month | `/websites/sites_of_the_month/` | 192 | 月度最佳 |
| Sites of the Year | `/websites/sites_of_the_year/` | 64 | 年度最佳 |
| Honors | `/honors/winners` | - | 新荣誉体系 |
| Most Awarded Profiles | `/winner-list/` | - | 最获奖创作者 |
| Jury | `/jury/2026/` | - | 2026 评委 |

### 质量层级

```
Sites of the Year > Sites of the Month > Sites of the Day > Nominees > Honor Mentions
     (最高质量)                                              (最大量)
```

### 执行流程

```
1. playwright-cli goto https://www.awwwards.com/websites/sites_of_the_day/
2. playwright-cli screenshot --filename=/tmp/design-scout/awards-sotd.png
3. 提取前 $3 个获奖作品的基本信息
4. 可选：对每个作品执行 [单件分析](#单作品深度分析-analyze) 简化版
5. 输出：获奖作品列表 + 各自亮点摘要
```

---

## 策展合集 (collection)

**适用**："找 XX 主题的精选集合"

### 入口

```
列表页: https://www.awwwards.com/collections/
搜索: https://www.awwwards.com/collections/search/
总数: 132+ 官方/用户策展
```

### 详情页结构

```
https://www.awwwards.com/{user}/collections/{collection-slug}/

字段:
  - Curator (策展人)
  - Followers (关注数)
  - Items count (收录数量)
  - 网站卡片列表 (每个含来源工作室)
```

### 热门 Collection 类型

| 类型 | 示例 |
|------|------|
| 配色主题 | Pastel colors, Dark mode, Trendy Gradients |
| 动效主题 | CSS Animations, WebGL Animations, Text Marquee |
| 组件主题 | Team & About Pages, Footers, Headers |
| 行业主题 | Photography Portfolio, Games, E-commerce |
| 工具类 | Handy Tools and Apps for Designers |

Collection 可用作 moodboard，支持公开/私有、团队共享。

### 执行流程

```
1. playwright-cli goto https://www.awwwards.com/collections/
2. 搜索或浏览找到目标 collection
3. 进入 collection 详情页
4. 提取策展人、收录数量、网站列表
5. 输出：集合概览 + 代表性网站推荐
```

---

## 输出格式

### 标准输出模板

```markdown
## Design Scout: {查询主题}

**模式**: {category|technology|element|search|analyze|awards|collection}
**来源**: Awwwards (www.awwwards.com)
**采集时间**: {timestamp}

### 发现 ({n} 条结果)

#### 1. {站点/元素名称}
- **链接**: https://www.awwwards.com/sites/{slug}
- **作者**: {工作室名} {PRO?}
- **评分**: X.XX/10 (Design) / X.XX/10 (DEV)
- **标签**: {tag1}, {tag2}, {tag3}
- **亮点**: {一句话设计点评}
- **截图**: ![截图](/tmp/design-scout/xxx.png)

#### 2. ...

### 设计趋势总结
{基于采集结果的 2-3 句趋势洞察}
```

### 批量采集输出（$3 > 5 时）

```json
[
  {
    "title": "...",
    "url": "https://www.awwwards.com/sites/...",
    "author": "...",
    "score_design": 7.25,
    "score_dev": 6.79,
    "tags": ["Webflow", "Clean", "Portfolio"],
    "award_level": "SOTD",
    "date": "2026-05-09",
    "screenshot": "/tmp/design-scout/..."
  }
]
```

---

## 示例用法

```bash
# 按分类查找
/design-scout 电商网站设计 category
/design-scout architecture 5                    # 指定 5 个结果

# 按技术栈查找
/design-scout Webflow 优秀案例 technology
/design-scout Three.js 3                         # 只要 3 个

# 按 UI 元素查找
/design-scout Footer 设计方案 element
/design-scout CTA 暗色系 element                  # 后续会叠加 color 筛选
/design-scout 页面转场动画 element

# 搜索
/design-scout dark mode 网站 search
/design-scout minimal portfolio search

# 单作品分析
/design-scout https://www.awwwards.com/sites/simonholm-studio analyze

# 按奖项浏览
/design-scout 最近 SOTD awards
/design-scout 本月获奖者 10 awards

# 策展合集
/design-scout pastel 配色 collection
/design-scout CSS 动画 collection
```

---

## 注意事项

1. **必须使用 Playwright CLI** — Awwwards 是 SPA，纯 HTTP 请求拿不到动态内容
2. **Cookie 弹窗** — 首次访问会出现 cookie 同意弹窗，点 "GOT IT" 关闭
3. **截图保存** — 所有截图统一存 `/tmp/design-scout/`，便于后续分析
4. **速率控制** — 连续请求间隔 ≥ 2 秒，避免被限流
5. **无公开 API** — 所有数据通过页面 DOM 提取，页面结构变更时需更新提取逻辑
6. **搜索需编码** — URL 中的空格需编码为 `%20`，中文需 URI 编码
