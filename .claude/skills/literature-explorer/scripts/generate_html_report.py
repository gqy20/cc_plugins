#!/usr/bin/env python3
"""
Generate HTML report from literature JSON data.

Supports multiple color themes (modern, academic, dark).
Uses HTML template files for easier maintenance.

Usage:
    python scripts/generate_html_report.py --json links.json --output literature_report.html --theme modern
"""

import json
import argparse
import re
from datetime import datetime
from pathlib import Path
from string import Template


def generate_current_year():
    """Get current year dynamically."""
    return datetime.now().year


def generate_report_title(data, user_title=None):
    """
    Generate report title from user input or query keywords.

    Args:
        data: Original JSON data (may contain query field)
        user_title: User-provided title (takes priority)

    Returns:
        str: Generated report title
    """
    # If user provided a title, use it directly
    if user_title:
        return user_title

    # Extract keywords from query as fallback
    query = data.get('query', '') if isinstance(data, dict) else ''

    if not query:
        return '文献检索报告'

    # Extract quoted terms from query (both MeSH and regular keywords)
    all_terms = re.findall(r'"([^"]+)"', query)

    # Filter out non-content terms
    skip = {'AND', 'OR', 'NOT', 'pubmed', 'pmc[sb]', 'conference', 'proceedings',
            'hasPmc', '[pd]', '[sb]'}

    # Clean terms: remove field tags and short words
    terms = []
    for term in all_terms:
        term_clean = term.strip()
        # Remove field suffixes like [MeSH], [pd], [sb]
        term_clean = re.sub(r'\s*\[.*?\]\s*$', '', term_clean)
        if (len(term_clean) > 2 and
            term_clean.lower() not in skip and
            term_clean not in terms):
            terms.append(term_clean)

    # Build title from extracted terms
    if not terms:
        return '文献检索报告'

    # Use up to 3 main terms
    main_terms = terms[:3]
    if len(main_terms) == 1:
        return f'{main_terms[0]}相关文献'
    elif len(main_terms) == 2:
        return f'{main_terms[0]}与{main_terms[1]}相关文献'
    else:
        return f'{main_terms[0]}、{main_terms[1]}等主题文献'


def load_json_data(json_file):
    """Load literature data from JSON file.

    Returns:
        tuple: (literature_list, original_data)
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 兼容两种格式：
    # 1. 直接是文献列表
    # 2. 包含在 'results' 字段中的包装格式
    if isinstance(data, dict) and 'results' in data:
        return data['results'], data
    elif isinstance(data, list):
        return data, {}
    else:
        raise ValueError(f"Invalid JSON format: expected list or dict with 'results' field")


def categorize_literature(literature_list):
    """
    Categorize literature based on fulltext and abstract availability.

    Returns:
        dict: Dictionary with 4 categories
    """
    categories = {
        'high_priority': [],      # 有全文 + 有摘要
        'medium_priority': [],    # 有全文 + 无摘要
        'low_priority': [],       # 无全文 + 有摘要
        'lowest_priority': []     # 无全文 + 无摘要
    }

    for item in literature_list:
        has_fulltext = bool(item.get('pdf_link'))
        has_abstract = bool(item.get('abstract'))

        if has_fulltext and has_abstract:
            categories['high_priority'].append(item)
        elif has_fulltext and not has_abstract:
            categories['medium_priority'].append(item)
        elif not has_fulltext and has_abstract:
            categories['low_priority'].append(item)
        else:
            categories['lowest_priority'].append(item)

    return categories


def extract_year_range(literature_list):
    """
    Extract year range from literature list.

    Returns:
        str: HTML option tags for year dropdown
    """
    years = set()
    for item in literature_list:
        year = item.get('year')
        if year and year.isdigit():
            years.add(int(year))

    if not years:
        return ''

    year_list = sorted(years)
    options = [f'<option value="{year}">{year}</option>' for year in year_list]
    return '\n                        '.join(options)


def load_css_template(theme):
    """Load CSS template from assets directory."""
    script_dir = Path(__file__).parent
    css_file = script_dir.parent / 'assets' / 'html-templates' / f'{theme}.css'

    if not css_file.exists():
        raise ValueError(f"CSS theme not found: {css_file}")

    with open(css_file, 'r', encoding='utf-8') as f:
        return f.read()


def load_template(template_name):
    """Load HTML template part from assets directory."""
    script_dir = Path(__file__).parent
    template_file = script_dir.parent / 'assets' / 'html-templates' / template_name

    if not template_file.exists():
        raise ValueError(f"Template not found: {template_file}")

    with open(template_file, 'r', encoding='utf-8') as f:
        return Template(f.read())


def generate_identifiers(item):
    """Generate HTML for identifiers."""
    identifiers = []
    if item.get('pmcid'):
        identifiers.append(f'<span class="identifier">PMCID: {item["pmcid"]}</span>')
    if item.get('pmid'):
        identifiers.append(f'<span class="identifier">PMID: {item["pmid"]}</span>')
    if item.get('doi'):
        identifiers.append(f'<span class="identifier">DOI: {item["doi"]}</span>')
    return ''.join(identifiers) if identifiers else ''


def generate_abstract(abstract):
    """Generate HTML for abstract section with expand/collapse button."""
    if not abstract:
        return ''
    return f"""
        <div class="abstract">
            <div class="abstract-content">{abstract}</div>
            <button class="abstract-toggle">▶ 展开摘要</button>
        </div>
    """


def generate_pdf_button(pdf_link):
    """Generate HTML for PDF download button."""
    if not pdf_link:
        return ''
    return f"""
        <a href="{pdf_link}" target="_blank" class="btn btn-primary">
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            下载 PDF
        </a>
    """


def generate_card(item, card_class):
    """Generate HTML card for a single literature item."""
    title = item.get('title', 'No Title')
    authors = item.get('authors', [])
    authors_str = ', '.join(authors[:5]) + ('...' if len(authors) > 5 else '')
    journal = item.get('journal', '')
    year = item.get('year', '')
    pdf_link = item.get('pdf_link', '')

    # Load card template
    card_template = load_template('parts/card.html')

    # Generate components
    identifiers = generate_identifiers(item)
    abstract = generate_abstract(item.get('abstract', ''))
    pdf_button = generate_pdf_button(pdf_link)

    # Fill template
    return card_template.substitute(
        card_class=card_class,
        title=title,
        authors=authors_str,
        journal=journal,
        year=year,
        identifiers=identifiers,
        abstract=abstract,
        pdf_button=pdf_button
    )


def generate_category_sections(categories):
    """Generate HTML sections for each category."""
    sections = []
    category_config = [
        ('high_priority', '高优先级 - 全文 + 摘要', 'high-priority', 'highlight'),
        ('medium_priority', '中优先级 - 仅全文', 'medium-priority', 'normal'),
        ('low_priority', '低优先级 - 仅摘要', 'low-priority', 'faded'),
        ('lowest_priority', '最低优先级 - 无全文无摘要', 'lowest-priority', 'gray')
    ]

    section_template = load_template('parts/section.html')

    for cat_key, cat_title, cat_id, card_class in category_config:
        items = categories[cat_key]
        if items:
            # Generate all cards for this category
            cards = [generate_card(item, card_class) for item in items]
            cards_html = '\n'.join(cards)

            # Fill section template
            section_html = section_template.substitute(
                id=cat_id,
                title=cat_title,
                count=len(items),
                cards=cards_html
            )
            sections.append(section_html)

    return '\n'.join(sections)


def generate_stats(categories):
    """Generate HTML for statistics section."""
    stats_template = load_template('parts/stats.html')

    total_count = sum(len(v) for v in categories.values())
    high_count = len(categories['high_priority'])
    medium_count = len(categories['medium_priority'])
    low_count = len(categories['low_priority'])

    return stats_template.substitute(
        total_count=total_count,
        high_count=high_count,
        medium_count=medium_count,
        low_count=low_count
    )


def generate_html_report(categories, output_file, theme='modern', literature_list=None, original_data=None, user_title=None):
    """Generate HTML report from categorized literature."""

    current_year = generate_current_year()

    # Generate title (user-specified or auto-generated from query)
    report_title = generate_report_title(original_data if original_data else {}, user_title)

    # Load templates
    main_template = load_template('template.html')
    css_template = load_css_template(theme)

    # Generate content
    sections_html = generate_category_sections(categories)
    stats_html = generate_stats(categories)

    # Extract year options from literature list
    year_options = extract_year_range(literature_list) if literature_list else ''

    # Fill main template
    html_content = main_template.substitute(
        title=report_title,
        year=current_year,
        date=datetime.now().strftime('%Y-%m-%d'),
        css=css_template,
        stats=stats_html,
        sections=sections_html,
        year_options=year_options
    )

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)


def main():
    parser = argparse.ArgumentParser(description='Generate HTML report from literature JSON data')
    parser.add_argument('--json', required=True, help='Path to input JSON file')
    parser.add_argument('--output', default='literature_report.html', help='Path to output HTML file')
    parser.add_argument('--theme', default='modern',
                       choices=['modern', 'academic', 'dark'],
                       help='Color theme for HTML report (default: modern)')
    parser.add_argument('--title', help='Custom report title (default: auto-generated from query)')
    args = parser.parse_args()

    # Load data
    literature_list, original_data = load_json_data(args.json)
    print(f"✓ Loaded {len(literature_list)} papers from {args.json}")

    # Categorize
    categories = categorize_literature(literature_list)
    print("✓ Categorized papers by priority")

    # Generate HTML
    print(f"✓ Using theme: {args.theme}")
    generate_html_report(categories, args.output, args.theme, literature_list, original_data, args.title)
    print(f"✓ HTML report generated: {args.output}")

    # Print statistics
    total_count = sum(len(v) for v in categories.values())
    print(f"✓ Total papers: {total_count}")
    print(f"  - High Priority (Fulltext + Abstract): {len(categories['high_priority'])}")
    print(f"  - Medium Priority (Fulltext Only): {len(categories['medium_priority'])}")
    print(f"  - Low Priority (Abstract Only): {len(categories['low_priority'])}")
    print(f"  - Lowest Priority (No Fulltext/Abstract): {len(categories['lowest_priority'])}")


if __name__ == '__main__':
    main()
