#!/usr/bin/env python3
"""
PDF 链接提取器
从 JSON 文件读取文献信息并提取 PDF 下载链接
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PDFLinkExtractor:
    """PDF 链接提取器"""

    def __init__(self, output_dir: str):
        """
        初始化链接提取器

        Args:
            output_dir: 输出目录
        """
        self.logger = logging.getLogger(__name__)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _convert_ftp_to_http(self, url: str) -> str:
        """
        将 FTP URL 转换为 HTTP URL

        Args:
            url: 原始 URL

        Returns:
            转换后的 HTTP URL
        """
        if url.startswith("ftp://"):
            return url.replace("ftp://ftp.ncbi.nlm.nih.gov/", "https://ftp.ncbi.nlm.nih.gov/")
        return url

    def extract_links_from_json(self, json_path: str) -> list[dict[str, Any]]:
        """
        从 JSON 文件提取 PDF 下载链接

        Args:
            json_path: JSON 文件路径

        Returns:
            链接信息列表
        """
        logger.info(f"从 JSON 文件提取链接: {json_path}")

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        papers = data.get("results", [])

        results = []
        for paper in papers:
            pmcid = paper.get("pmcid", "")
            pdf_link = paper.get("pdf_link", "")
            doi = paper.get("doi", "")
            title = paper.get("title", "")

            if not pdf_link:
                results.append({
                    "pmcid": pmcid,
                    "doi": doi,
                    "title": title,
                    "pdf_link": "",
                    "http_url": "",
                    "error": "No PDF link available"
                })
                continue

            http_url = self._convert_ftp_to_http(pdf_link)

            results.append({
                "pmcid": pmcid,
                "doi": doi,
                "title": title,
                "pdf_link": pdf_link,
                "http_url": http_url,
                "error": ""
            })

            self.logger.info(f"提取链接: {pmcid} -> {http_url[:80]}...")

        return results

    def extract_links_from_identifiers(
        self,
        identifiers: list[str],
        max_workers: int = 3
    ) -> list[dict[str, Any]]:
        """
        从标识符列表提取链接

        Args:
            identifiers: 标识符列表
            max_workers: 并发线程数

        Returns:
            链接信息列表
        """
        logger.info(f"从标识符列表提取链接: {len(identifiers)} 个")

        # 简化处理：直接构造可能的 PDF URL
        results = []
        for identifier in identifiers:
            id_type, id_value = self.classify_identifier(identifier)

            if id_type == "pmcid":
                http_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{id_value}/pdf/"
                results.append({
                    "pmcid": id_value,
                    "doi": "",
                    "title": "",
                    "pdf_link": http_url,
                    "http_url": http_url,
                    "error": ""
                })
            elif id_type == "doi":
                http_url = f"https://doi.org/{id_value}"
                results.append({
                    "pmcid": "",
                    "doi": id_value,
                    "title": "",
                    "pdf_link": http_url,
                    "http_url": http_url,
                    "error": ""
                })
            else:
                results.append({
                    "pmcid": id_value if id_type == "pmcid" else "",
                    "doi": id_value if id_type == "doi" else "",
                    "title": "",
                    "pdf_link": "",
                    "http_url": "",
                    "error": f"无法识别的标识符类型: {identifier}"
                })

        return results

    @staticmethod
    def classify_identifier(identifier: str) -> tuple[str, str]:
        """
        分类标识符

        Args:
            identifier: 标识符字符串

        Returns:
            (类型, 值) 类型: "pmcid" | "pmid" | "doi" | "unknown"
        """
        import re

        identifier = identifier.strip()

        if re.match(r"^PMC\d+$", identifier, re.IGNORECASE):
            return "pmcid", identifier.upper()
        if re.match(r"^\d+$", identifier):
            return "pmid", identifier
        if re.match(r"^10\.\d+/", identifier):
            return "doi", identifier

        return "unknown", identifier


class CSVInputParser:
    """CSV 输入解析器"""

    @staticmethod
    def parse_csv(csv_path: str, column: str | None = None) -> list[dict[str, str]]:
        """
        解析 CSV 文件

        Args:
            csv_path: CSV 文件路径
            column: 列名（可选）

        Returns:
            标识符列表 [{"id": "xxx"}]
        """
        try:
            import csv

            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                if column and column in reader.fieldnames:
                    return [{"id": row[column]} for row in reader if row.get(column)]
                elif reader.fieldnames:
                    first_column = reader.fieldnames[0]
                    return [{"id": row[first_column]} for row in reader if row.get(first_column)]

            return []

        except Exception as e:
            logger.error(f"CSV 解析失败: {str(e)}")
            return []


def main():
    parser = argparse.ArgumentParser(
        description="PDF 链接提取器 - 从 JSON 或 CSV 文件提取 PDF 下载链接",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 从 JSON 文件提取链接
  python extract_pdf_links.py --json links.json --output links.txt

  # 从标识符列表提取链接
  python extract_pdf_links.py --identifiers "PMC123456,38238491,10.1186/xxx" --output links.txt

  # 从 CSV 文件提取链接
  python extract_pdf_links.py --csv identifiers.csv --column pmcid --output links.txt
        """
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--json", "-j", type=str, help="JSON 文件路径（包含文献信息和链接）")
    group.add_argument("--identifiers", "-i", type=str, help="批量标识符（PMCID/PMID/DOI，逗号分隔）")
    group.add_argument("--csv", "-c", type=str, help="CSV 文件路径")

    parser.add_argument("--column", type=str, help="CSV 列名")
    parser.add_argument("--output", "-o", type=str, default="pdf_links.txt", help="输出文件路径")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    extractor = PDFLinkExtractor(output_dir=".")

    results = []

    if args.json:
        results = extractor.extract_links_from_json(args.json)

    elif args.identifiers:
        identifiers = [id_str.strip() for id_str in args.identifiers.split(",")]
        identifiers = [id_str for id_str in identifiers if id_str]
        results = extractor.extract_links_from_identifiers(identifiers)

    elif args.csv:
        identifiers = CSVInputParser.parse_csv(args.csv, args.column)

        id_list = [identifier["id"] for identifier in identifiers]
        results = extractor.extract_links_from_identifiers(id_list)

    # 输出结果
    with open(args.output, "w", encoding="utf-8") as f:
        f.write("# PDF 下载链接\n")
        f.write(f"# 生成时间: {__import__('time').ctime()}\n\n")

        success_count = 0
        for result in results:
            if result.get("http_url"):
                f.write(f"PMCID: {result.get('pmcid', 'N/A')}\n")
                f.write(f"DOI: {result.get('doi', 'N/A')}\n")
                f.write(f"标题: {result.get('title', 'N/A')[:80]}\n")
                f.write(f"PDF URL (HTTP): {result['http_url']}\n")
                f.write("-" * 80 + "\n\n")
                success_count += 1

        f.write(f"\n总计: {len(results)} 篇文献，{success_count} 篇可用\n")

    logger.info(f"\n链接已提取完成: {success_count}/{len(results)} 篇可用")
    logger.info(f"结果已保存到: {args.output}")


if __name__ == "__main__":
    main()
