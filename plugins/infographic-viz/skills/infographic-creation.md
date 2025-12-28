---
name: infographic-creation
description: Create beautiful infographics based on the given text content using AntV Infographic framework.
---

# Infographic Creation Skill

## Overview

Infographic transforms data, information, and knowledge into perceivable visual language. It combines visual design with data visualization, using intuitive symbols to compress complex information and help audiences quickly understand and remember key points.

**Formula**: `Infographic = Information Structure + Visual Expression`

This skill utilizes [AntV Infographic](https://infographic.antv.vision/) to create visual infographics through a Mermaid-like DSL syntax.

## AntV Infographic Syntax

The syntax uses indentation to describe information, has strong robustness, and makes it easy to render infographics through AI streaming output.

### Basic Structure

```
infographic <template-name>
data
title <title>
desc <description>
items
- label <label>
value <numeric-value>
desc <explanation>
icon <icon-name>
theme
palette <color1> <color2> <color3>
```

### Key Components

1. **template**: Template name from the available templates list
2. **data**: Contains title, desc, items (label, value, desc, icon, children)
3. **theme**: Palette, font, and other styling options

### Data Structure

```typescript
interface Data {
  title?: string;
  desc?: string;
  items: ItemDatum[];
  [key: string]: any;
}

interface ItemDatum {
  icon?: string;
  label?: string;
  desc?: string;
  value?: number;
  illus?: string;
  children?: ItemDatum[];
  [key: string]: any;
}
```

### Syntax Rules

- First line: `infographic <template-name>`
- Use blocks for `data` / `theme` with two-space indentation
- Key-value pairs: `"key value"`
- Arrays: `"-"` items
- Icon format: `mdi/chart-line` (from Iconify)
- Illustration format: filename without extension (from unDraw)

## Icon and Illustration Resources

### Icons (from Iconify)

- Format: `<collection>/<name>`, e.g., `mdi/rocket-launch`
- Popular collections:
  - `mdi/*` - Material Design Icons (most common)
  - `fa/*` - Font Awesome
  - `bi/*` - Bootstrap Icons
  - `heroicons/*` - Heroicons
- Browse: https://icon-sets.iconify.design/

Common icons:
- Tech: `mdi/code-tags`, `mdi/database`, `mdi/api`, `mdi/cloud`
- Business: `mdi/chart-line`, `mdi/briefcase`, `mdi/currency-usd`
- Process: `mdi/check-circle`, `mdi/arrow-right`, `mdi/cog`
- People: `mdi/account`, `mdi/account-group`, `mdi/shield-account`

### Illustrations (from unDraw)

- Format: illustration filename (without .svg), e.g., `coding`
- Browse: https://undraw.co/illustrations
- Use sparingly (larger than icons)

## Available Templates

### Sequence / Timeline (顺序/时间线)
- `sequence-timeline-simple` - Simple timeline
- `sequence-timeline-rounded-rect-node` - Timeline with rounded nodes
- `sequence-zigzag-steps-underline-text` - Zigzag steps
- `sequence-roadmap-vertical-simple` - Vertical roadmap
- `sequence-horizontal-zigzag-simple-illus` - Zigzag with illustrations
- `sequence-circular-simple` - Circular progress
- `sequence-snake-steps-compact-card` - Snake steps compact
- `sequence-stairs-front-compact-card` - Staircase diagram

### Compare (对比分析)
- `compare-binary-horizontal-simple-fold` - Binary comparison
- `compare-binary-horizontal-underline-text-vs` - VS style comparison
- `compare-swot` - SWOT analysis

### Hierarchy (层级结构)
- `hierarchy-tree-tech-style-capsule-item` - Tech style tree
- `hierarchy-tree-curved-line-rounded-rect-node` - Curved line tree

### Chart (图表)
- `chart-column-simple` - Column chart
- `chart-bar-plain-text` - Bar chart
- `chart-line-plain-text` - Line chart
- `chart-pie-plain-text` - Pie chart
- `chart-pie-donut-plain-text` - Donut chart
- `chart-wordcloud` - Word cloud

### List (列表)
- `list-grid-badge-card` - Grid with badges
- `list-row-horizontal-icon-arrow` - Horizontal row with icons
- `list-column-vertical-icon-arrow` - Vertical column with icons
- `list-column-done-list` - Done list

### Quadrant (象限分析)
- `quadrant-quarter-simple-card` - Quarter quadrant
- `quadrant-quarter-circular` - Circular quadrant

### Relation (关系展示)
- `relation-circle-icon-badge` - Circle relation
- `relation-circle-circular-progress` - Circular progress

### Template Selection Guidelines

- **Sequential processes/trends**: `sequence-*` series
- **Comparative analysis**: `compare-binary-*` or `compare-swot`
- **Hierarchical structure**: `hierarchy-tree-*`
- **Data charts**: `chart-*` series
- **Bullet points**: `list-grid-*` or `list-row-*` / `list-column-*`

## Theme Customization

### Dark Theme with Custom Palette

```
infographic list-row-simple-horizontal-arrow
theme dark
palette
- #61DDAA
- #F6BD16
- #F08BB4
data
items
- label Step 1
desc Start
- label Step 2
desc In Progress
- label Step 3
desc Complete
```

### Hand-drawn Style (rough)

```
infographic list-row-simple-horizontal-arrow
theme
stylize rough
base
text
font-family 851tegakizatsu
data
items
- label Step 1
desc Start
- label Step 2
desc In Progress
- label Step 3
desc Complete
```

## Examples

### Example 1: Timeline with Icons

```
infographic list-row-horizontal-icon-arrow
data
title Internet Technology Evolution
desc From Web 1.0 to AI era, key milestones
items
- time 1991
label Web 1.0
desc Tim Berners-Lee published the first website
icon mdi/web
- time 2004
label Web 2.0
desc Social media becomes mainstream
icon mdi/account-multiple
- time 2007
label Mobile
desc iPhone changes the world
icon mdi/cellphone
- time 2023
label AI Large Model
desc ChatGPT ignites AI revolution
icon mdi/brain
```

### Example 2: Process with Illustrations

```
infographic sequence-horizontal-zigzag-simple-illus
data
title Product Development Phases
desc Key stages in our development process
items
- label Research
desc Understanding user needs
illus user-research
- label Design
desc Creating user experience
illus design-thinking
- label Development
desc Building the product
illus coding
- label Launch
desc Going to market
illus launch-day
```

### Example 3: SWOT Analysis

```
infographic compare-swot
data
items
- label Strengths
children
- label Expert Team
desc 10+ years experience
- label Proprietary Tech
desc Patented algorithms
- label Weaknesses
children
- label Limited Budget
desc Startup constraints
- label Small Team
desc Resource constraints
- label Opportunities
children
- label Growing Market
desc 50% YoY growth
- label New Demand
desc Digital transformation
- label Threats
children
- label Competition
desc New entrants
- label Regulation
desc Policy changes
```

## Creation Process

### Step 1: Understand Requirements

Extract key information:
1. Title and description
2. Data items (labels, values, descriptions)
3. Appropriate icons/illustrations
4. Suitable template

**CRITICAL**: Respect the language of user input. If user provides Chinese content, the infographic text must be in Chinese.

### Step 2: Generate HTML

Create a complete HTML file with:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Infographic</title>
    <script src="https://unpkg.com/@antv/infographic@latest/dist/infographic.min.js"></script>
</head>
<body>
    <div id="container"></div>
    <script>
        // Resource loader for icons and illustrations
        const resourceLoader = {
            async loadIcon(name) {
                if (name.startsWith('http')) return name;
                const [collection, iconName] = name.split('/');
                return `https://cdn.jsdelivr.net/npm/@iconify/json@latest/jsons/${collection}.json`;
            },
            async loadIllustration(name) {
                return `https://unpkg.com/undraw-coordinates@0.1.0/illustrations/${name}.svg`;
            }
        };

        const infographic = new Infographic({
            container: 'container',
            width: '100%',
            height: '100%',
            loader: resourceLoader
        });

        infographic.render(`
{syntax}
        `);

        // Export functionality
        async function exportSVG() {
            const svgDataUrl = await infographic.toDataURL({ type: 'svg' });
            const link = document.createElement('a');
            link.href = svgDataUrl;
            link.download = '{title}.svg';
            link.click();
        }
    </script>
</body>
</html>
```

### Step 3: Output

1. Write HTML file named `{title}-infographic.html` using Write tool
2. Display to user:
   - File path with instruction: "Open in browser to view and save SVG"
   - Generated syntax with instruction: "Adjust template/colors/content as needed"
