#!/usr/bin/env python3
"""
文献 PDF 链接获取器
基于 PubMed E-utilities API 搜索文献，使用 PMC OA Service 获取 PDF 下载链接
"""

import argparse
import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests
import xml.etree.ElementTree as ET

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class LiteratureSearcher:
    """文献搜索器"""

    def __init__(self, email: str = "", api_key: str = ""):
        """
        初始化搜索器

        Args:
            email: NCBI API 邮箱
            api_key: NCBI API 密钥
        """
        self.session = requests.Session()
        self.email = email or os.getenv("NCBI_EMAIL", "")
        self.api_key = api_key or os.getenv("NCBI_API_KEY", "")
        self.europe_pmc_url = "https://www.ebi.ac.uk/europepmc/webservices/rest"
        self.pubmed_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def search_europepmc(
        self, query: str, limit: int = 50, require_pmcid: bool = False
    ) -> list[dict[str, Any]]:
        """
        通过 Europe PMC 搜索文献

        Args:
            query: 检索词
            limit: 返回结果数量限制
            require_pmcid: 是否只返回有 PMCID 的结果

        Returns:
            文献列表
        """
        logger.info(f"搜索文献 (Europe PMC): {query}")

        params = {
            "query": query,
            "format": "json",
            "pageSize": min(limit, 1000),
            "resultType": "core",
        }

        if require_pmcid:
            params["hasPmc"] = "Y"

        try:
            response = self.session.get(
                f"{self.europe_pmc_url}/search",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            papers = []
            for result in data.get("resultList", {}).get("result", []):
                # Extract journal title from journalInfo
                journal_info = result.get("journalInfo", {})
                journal_obj = journal_info.get("journal", {})
                journal_title = journal_obj.get("title", "") if isinstance(journal_obj, dict) else ""

                # Extract authors
                author_list = result.get("authorList", {}).get("author", [])
                authors = [a.get("fullName", "") for a in author_list] if author_list else []

                paper = {
                    "pmcid": result.get("pmcid", ""),
                    "pmid": result.get("pmid", ""),
                    "doi": result.get("doi", ""),
                    "title": result.get("title", ""),
                    "authors": authors,
                    "journal": journal_title,
                    "year": result.get("pubYear", ""),
                    "abstract": result.get("abstractText", ""),
                    "source": "europe_pmc",
                    "inPMC": bool(result.get("pmcid", "")),
                }
                papers.append(paper)

            result = papers[:limit]

            pmcid_count = sum(1 for p in result if p.get("pmcid"))
            pmcid_rate = (pmcid_count / len(result) * 100) if result else 0

            if require_pmcid:
                logger.info(
                    f"Europe PMC (HAS_PMCID过滤) 搜索返回 {len(result)} 条结果，其中 {pmcid_count} 条有 PMCID ({pmcid_rate:.1f}%)"
                )
            else:
                logger.info(
                    f"Europe PMC 搜索返回 {len(result)} 条结果，其中 {pmcid_count} 条有 PMCID ({pmcid_rate:.1f}%)"
                )

            return result

        except requests.exceptions.Timeout:
            logger.error("Europe PMC 搜索超时")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Europe PMC 搜索请求失败: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Europe PMC 搜索出错: {str(e)}")
            return []

    def search_pubmed(
        self, query: str, limit: int = 50, require_pmcid: bool = False
    ) -> list[dict[str, Any]]:
        """
        通过 PubMed E-utilities API 搜索文献（推荐用于进化生物学等非临床医学领域）

        Args:
            query: 检索词（支持 PubMed 语法）
            limit: 返回结果数量限制
            require_pmcid: 是否只返回有 PMCID 的结果

        Returns:
            文献列表
        """
        logger.info(f"搜索文献 (PubMed): {query}")

        # 构建 E-utilities API 请求
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": min(limit, 10000),
            "retmode": "xml",
            "tool": "literature_explorer",
        }

        # 添加认证信息（提高请求限制）
        if self.email:
            params["email"] = self.email
        if self.api_key:
            params["api_key"] = self.api_key

        try:
            # 第一步：搜索获取 PMIDs
            response = self.session.get(
                f"{self.pubmed_url}/esearch.fcgi",
                params=params,
                timeout=30
            )
            response.raise_for_status()

            # 解析 XML 获取 PMIDs
            root = ET.fromstring(response.content)
            pmids = [id_elem.text for id_elem in root.findall(".//Id")]

            if not pmids:
                logger.info("PubMed 搜索返回 0 条结果")
                return []

            pmids = pmids[:limit]
            logger.info(f"PubMed 搜索返回 {len(pmids)} 条结果")

            # 第二步：批量获取摘要信息
            papers = []
            batch_size = 200  # PubMed 允许每批最多 200 个 PMIDs

            for i in range(0, len(pmids), batch_size):
                batch_pmids = pmids[i:i + batch_size]

                summary_params = {
                    "db": "pubmed",
                    "id": ",".join(batch_pmids),
                    "retmode": "xml",
                }

                if self.email:
                    summary_params["email"] = self.email
                if self.api_key:
                    summary_params["api_key"] = self.api_key

                summary_response = self.session.get(
                    f"{self.pubmed_url}/efetch.fcgi",
                    params=summary_params,
                    timeout=60
                )
                summary_response.raise_for_status()

                # 解析 PubmedData 获取详细信息
                summary_root = ET.fromstring(summary_response.content)

                for article in summary_root.findall(".//PubmedArticle"):
                    pmid_elem = article.find(".//PMID")
                    pmid = pmid_elem.text if pmid_elem is not None else ""

                    # 获取期刊信息
                    journal_elem = article.find(".//Journal")
                    journal_title = ""
                    pub_year = ""
                    if journal_elem is not None:
                        title_elem = journal_elem.find(".//Title")
                        journal_title = title_elem.text if title_elem is not None else ""

                        year_elem = journal_elem.find(".//JournalArticle/PubDate/Year")
                        if year_elem is None:
                            year_elem = journal_elem.find(".//PubDate/Year")
                        pub_year = year_elem.text if year_elem is not None else ""

                    # 获取标题
                    title_elem = article.find(".//ArticleTitle")
                    title = ""
                    if title_elem is not None:
                        # 合并所有文本内容
                        title_parts = []
                        for elem in title_elem.iter():
                            if elem.text:
                                title_parts.append(elem.text)
                        title = "".join(title_parts).strip()

                    # 获取作者
                    authors = []
                    author_list = article.find(".//AuthorList")
                    if author_list is not None:
                        for author in author_list.findall("Author"):
                            last_name = author.find("LastName")
                            first_name = author.find("ForeName")
                            if last_name is not None:
                                name = f"{last_name.text}"
                                if first_name is not None:
                                    name += f" {first_name.text[0] if first_name.text else ''}"
                                authors.append(name)

                    # 获取摘要
                    abstract_elem = article.find(".//Abstract/AbstractText")
                    abstract = ""
                    if abstract_elem is not None:
                        abstract = abstract_elem.text

                    # 获取 PMCID
                    pmcid_elem = article.find(".//ArticleId[@IdType='pmc']")
                    pmcid = pmcid_elem.text if pmcid_elem is not None else ""

                    # 获取 DOI
                    doi_elem = article.find(".//ArticleId[@IdType='doi']")
                    doi = doi_elem.text if doi_elem is not None else ""

                    paper = {
                        "pmcid": pmcid,
                        "pmid": pmid,
                        "doi": doi,
                        "title": title,
                        "authors": authors,
                        "journal": journal_title,
                        "year": pub_year,
                        "abstract": abstract,
                        "source": "pubmed",
                        "inPMC": bool(pmcid),
                    }
                    papers.append(paper)

                # 速率限制：每秒最多 3 个请求（无 API Key）或 10 个（有 API Key）
                time.sleep(0.34 if not self.api_key else 0.1)

            pmcid_count = sum(1 for p in papers if p.get("pmcid"))
            pmcid_rate = (pmcid_count / len(papers) * 100) if papers else 0

            if require_pmcid:
                # 如果要求必须有 PMCID，过滤掉没有的
                filtered_papers = [p for p in papers if p.get("pmcid")]
                logger.info(
                    f"PubMed (HAS_PMCID过滤) 搜索返回 {len(filtered_papers)} 条结果，"
                    f"原始 {len(papers)} 条中 {pmcid_count} 条有 PMCID ({pmcid_rate:.1f}%)"
                )
                return filtered_papers
            else:
                logger.info(
                    f"PubMed 搜索返回 {len(papers)} 条结果，其中 {pmcid_count} 条有 PMCID ({pmcid_rate:.1f}%)"
                )

            return papers

        except requests.exceptions.Timeout:
            logger.error("PubMed 搜索超时")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"PubMed 搜索请求失败: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"PubMed 搜索出错: {str(e)}")
            return []

    def search_multiple_pubmed(
        self, queries: list[str], limit: int = 50, require_pmcid: bool = False, max_workers: int = 3
    ) -> list[dict[str, Any]]:
        """
        并行执行多个 PubMed 检索

        Args:
            queries: 检索词列表
            limit: 每个检索的结果数量限制
            require_pmcid: 是否只返回有 PMCID 的结果
            max_workers: 最大并发检索线程数

        Returns:
            合并后的文献列表
        """
        logger.info(f"并行执行 {len(queries)} 个 PubMed 检索，使用 {max_workers} 个并发线程")

        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            for i, query in enumerate(queries):
                future = executor.submit(
                    self.search_pubmed,
                    query,
                    limit,
                    require_pmcid
                )
                futures[future] = (i, query)

            for future in as_completed(futures, timeout=600):
                i, query = futures[future]
                try:
                    papers = future.result()
                    results.extend(papers)
                except Exception as e:
                    logger.error(f"PubMed 检索 '{query}' 失败: {str(e)}")

        # 去重（基于 PMCID）
        seen_pmcids = set()
        unique_papers = []
        for paper in results:
            pmcid = paper.get("pmcid", "")
            if pmcid and pmcid not in seen_pmcids:
                seen_pmcids.add(pmcid)
                unique_papers.append(paper)
            elif not pmcid:
                unique_papers.append(paper)

        pmcid_count = sum(1 for p in unique_papers if p.get("pmcid"))
        logger.info(
            f"PubMed 并行检索完成: {len(queries)} 个检索返回 {len(unique_papers)} 篇文献，"
            f"其中 {pmcid_count} 条有 PMCID (去重后)"
        )

        return unique_papers

    def search_multiple_europepmc(
        self, queries: list[str], limit: int = 50, require_pmcid: bool = False, max_workers: int = 3
    ) -> list[dict[str, Any]]:
        """
        并行执行多个 Europe PMC 检索

        Args:
            queries: 检索词列表
            limit: 每个检索的结果数量限制
            require_pmcid: 是否只返回有 PMCID 的结果
            max_workers: 最大并发检索线程数

        Returns:
            合并后的文献列表
        """
        logger.info(f"并行执行 {len(queries)} 个检索，使用 {max_workers} 个并发线程")

        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            for i, query in enumerate(queries):
                future = executor.submit(
                    self.search_europepmc,
                    query,
                    limit,
                    require_pmcid
                )
                futures[future] = (i, query)

            for future in as_completed(futures, timeout=300):
                i, query = futures[future]
                try:
                    papers = future.result()
                    results.extend(papers)
                except Exception as e:
                    logger.error(f"检索 '{query}' 失败: {str(e)}")

        # 去重（基于 PMCID）
        seen_pmcids = set()
        unique_papers = []
        for paper in results:
            pmcid = paper.get("pmcid", "")
            if pmcid and pmcid not in seen_pmcids:
                seen_pmcids.add(pmcid)
                unique_papers.append(paper)
            elif not pmcid:
                unique_papers.append(paper)

        pmcid_count = sum(1 for p in unique_papers if p.get("pmcid"))
        logger.info(
            f"并行检索完成: {len(queries)} 个检索返回 {len(unique_papers)} 篇文献，"
            f"其中 {pmcid_count} 条有 PMCID (去重后)"
        )

        return unique_papers


class PMCOAService:
    """PMC OA Web Service 客户端"""

    def __init__(self, session: requests.Session):
        """
        初始化 PMC OA Service

        Args:
            session: requests.Session 实例
        """
        self.logger = logging.getLogger(__name__)
        self.session = session
        self.oa_service_url = "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi"

    def _query_oa_service(self, pmcid: str) -> ET.Element | None:
        """
        查询 PMC OA Web Service

        Args:
            pmcid: PMCID (带 PMC 前缀)

        Returns:
            XML 根元素，失败返回 None
        """
        try:
            params = {"id": pmcid}
            response = self.session.get(
                self.oa_service_url, params=params, timeout=30
            )
            response.raise_for_status()
            return ET.fromstring(response.content)
        except requests.exceptions.Timeout:
            self.logger.error(f"PMC OA Service 查询超时: {pmcid}")
            return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"PMC OA Service 查询失败: {pmcid}, {str(e)}")
            return None
        except ET.ParseError as e:
            self.logger.error(f"PMC OA Service XML 解析失败: {pmcid}, {str(e)}")
            return None

    def get_pdf_link(self, pmcid: str) -> dict[str, Any]:
        """
        获取 PDF 下载链接

        Args:
            pmcid: PMCID (带 PMC 前缀)

        Returns:
            {"success": bool, "pdf_url": str, "tgz_url": str, "error": str}
        """
        result = {
            "success": False,
            "pdf_url": "",
            "tgz_url": "",
            "error": "",
        }

        xml_root = self._query_oa_service(pmcid)
        if xml_root is None:
            result["error"] = "OA Service 查询失败"
            return result

        records = xml_root.findall(".//record")

        if not records:
            result["error"] = "未找到 OA 记录"
            return result

        for record in records:
            pdf_links = record.findall(".//link[@format='pdf']")
            tgz_links = record.findall(".//link[@format='tgz']")

            for pdf_link in pdf_links:
                result["success"] = True
                result["pdf_url"] = pdf_link.get("href", "")
                self.logger.info(f"找到 PDF 链接: {pmcid}")
                return result

            for tgz_link in tgz_links:
                result["success"] = True
                result["tgz_url"] = tgz_link.get("href", "")
                self.logger.info(f"找到 TGZ 链接: {pmcid}")
                return result

        result["error"] = "未找到 PDF 链接"
        return result

    def get_pdf_links_batch(
        self, papers: list[dict[str, Any]], max_workers: int = 5
    ) -> list[dict[str, Any]]:
        """
        批量获取 PDF 链接

        Args:
            papers: 文献列表
            max_workers: 最大并发线程数

        Returns:
            文献列表（增加 pdf_link 字段）
        """
        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}

            for paper in papers:
                if not paper.get("pmcid"):
                    paper["pdf_link"] = ""
                    paper["download_success"] = False
                    results.append(paper)
                    continue

                future = executor.submit(self.get_pdf_link, paper["pmcid"])
                futures[future] = paper

            for future in as_completed(futures):
                paper = futures[future]
                try:
                    link_result = future.result()
                    paper["pdf_link"] = (
                        link_result.get("pdf_url") or link_result.get("tgz_url") or ""
                    )
                    paper["download_success"] = link_result["success"]
                    paper["download_error"] = link_result.get("error", "")
                    results.append(paper)
                except Exception as e:
                    paper["pdf_link"] = ""
                    paper["download_success"] = False
                    paper["download_error"] = str(e)
                    results.append(paper)

        success_count = sum(1 for r in results if r.get("download_success"))
        self.logger.info(f"获取链接完成: {success_count}/{len(results)} 成功")

        return results


class LinkFetcher:
    """文献链接获取器整合类"""

    def __init__(self, email: str = "", api_key: str = ""):
        """
        初始化链接获取器

        Args:
            email: NCBI API 邮箱
            api_key: NCBI API 密钥
        """
        self.session = requests.Session()
        self.email = email or os.getenv("NCBI_EMAIL", "")
        self.api_key = api_key or os.getenv("NCBI_API_KEY", "")
        self.searcher = LiteratureSearcher(email, api_key)
        self.oa_service = PMCOAService(self.session)

    def fetch_links_from_search(
        self,
        query: str,
        limit: int = 50,
        require_pmcid: bool = True,
        max_workers: int = 5,
        require_fulltext: bool = True
    ) -> list[dict[str, Any]]:
        """
        通过搜索获取 PDF 链接

        Args:
            query: 检索词
            limit: 返回结果数量限制
            require_pmcid: 是否只返回有 PMCID 的结果
            max_workers: 获取链接的并发线程数
            require_fulltext: 是否只返回有全文链接的结果（默认 True）

        Returns:
            文献列表（包含 pdf_link 字段）
        """
        logger.info(f"通过搜索获取链接: {query}")

        papers = self.searcher.search_europepmc(query, limit, require_pmcid)

        if not papers:
            logger.warning("未找到匹配的文献")
            return []

        papers_with_links = self.oa_service.get_pdf_links_batch(papers, max_workers)

        # 默认只返回有全文链接的文章
        if require_fulltext:
            filtered_papers = [p for p in papers_with_links if p.get("download_success")]
            filtered_count = len(papers_with_links) - len(filtered_papers)
            if filtered_count > 0:
                logger.info(f"已过滤 {filtered_count} 篇无全文链接的文献")
            logger.info(f"返回 {len(filtered_papers)} 篇有全文链接的文献")
            return filtered_papers

        return papers_with_links

    def fetch_links_from_search_multi(
        self,
        queries: list[str],
        limit: int = 50,
        require_pmcid: bool = True,
        max_search_workers: int = 3,
        max_link_workers: int = 5,
        require_fulltext: bool = True
    ) -> list[dict[str, Any]]:
        """
        通过并行搜索获取 PDF 链接

        Args:
            queries: 检索词列表
            limit: 每个检索的结果数量限制
            require_pmcid: 是否只返回有 PMCID 的结果
            max_search_workers: 检索的并发线程数
            max_link_workers: 获取链接的并发线程数
            require_fulltext: 是否只返回有全文链接的结果（默认 True）

        Returns:
            文献列表（包含 pdf_link 字段）
        """
        logger.info(f"通过并行搜索获取链接: {len(queries)} 个检索")

        papers = self.searcher.search_multiple_europepmc(
            queries, limit, require_pmcid, max_search_workers
        )

        if not papers:
            logger.warning("未找到匹配的文献")
            return []

        papers_with_links = self.oa_service.get_pdf_links_batch(papers, max_link_workers)

        # 默认只返回有全文链接的文章
        if require_fulltext:
            filtered_papers = [p for p in papers_with_links if p.get("download_success")]
            filtered_count = len(papers_with_links) - len(filtered_papers)
            if filtered_count > 0:
                logger.info(f"已过滤 {filtered_count} 篇无全文链接的文献")
            logger.info(f"返回 {len(filtered_papers)} 篇有全文链接的文献")
            return filtered_papers

        return papers_with_links


def main():
    parser = argparse.ArgumentParser(
        description="文献 PDF 链接获取器 - 搜索文献并获取 PDF 下载链接",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 单次检索并获取链接（使用 PubMed）
  python get_pdf_links.py --search "cancer AND pubmed pmc[sb]" --limit 50

  # 使用 Europe PMC 检索（适合临床医学）
  python get_pdf_links.py --search "cancer AND pubmed pmc[sb]" --limit 50 --use-europepmc

  # 并行多检索并获取链接（使用 PubMed，推荐用于进化生物学等领域）
  python get_pdf_links.py --search-multi "speciation;introgression;\"gene flow\"" --limit 50 --max-workers 3

  # 输出 JSON 文件
  python get_pdf_links.py --search "machine learning AND pubmed pmc[sb]" --limit 50 --output links.json
        """
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--search", "-s", type=str, help="搜索文献（单次）")
    group.add_argument("--search-multi", "-sm", type=str, help="并行执行多个检索，多个检索词用分号(;)分隔（MeSH 术语中可能包含逗号，请使用分号作为检索式分隔符）")

    parser.add_argument("--limit", "-l", type=int, default=200, help="数量限制（每个检索）")
    parser.add_argument("--max-workers", type=int, default=3, help="检索并发线程数（仅 --search-multi 有效）")
    parser.add_argument("--output", "-o", type=str, help="输出 JSON 文件路径（默认：控制台输出）")
    parser.add_argument("--use-europepmc", action="store_true", help="使用 Europe PMC API 搜索（默认使用 PubMed，适合临床医学领域；对于进化生物学等领域推荐使用 PubMed）")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--include-no-fulltext", action="store_true", help="包含没有全文链接的文章（默认只返回有全文的）")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    fetcher = LinkFetcher()

    # 默认只返回有全文链接的文章，用户指定 --include-no-fulltext 时才包含无全文的
    require_fulltext = not args.include_no_fulltext
    if args.include_no_fulltext:
        logger.info("包含没有全文链接的文章")

    if args.search:
        logger.info(f"搜索文献: {args.search}")

        # 选择搜索 API
        if args.use_europepmc:
            papers = fetcher.fetch_links_from_search(
                args.search,
                limit=args.limit,
                require_pmcid=True,
                max_workers=5,
                require_fulltext=require_fulltext
            )
        else:
            # 默认使用 PubMed（更适合非临床医学领域）
            searcher_results = fetcher.searcher.search_pubmed(
                args.search,
                limit=args.limit,
                require_pmcid=True
            )
            papers = fetcher.oa_service.get_pdf_links_batch(
                searcher_results,
                max_workers=5
            )

            if require_fulltext:
                filtered_papers = [p for p in papers if p.get("download_success")]
                filtered_count = len(papers) - len(filtered_papers)
                if filtered_count > 0:
                    logger.info(f"已过滤 {filtered_count} 篇无全文链接的文献")
                papers = filtered_papers

        if not papers:
            logger.error("未找到匹配的文献")
            sys.exit(1)

        query = args.search
    elif args.search_multi:
        # 使用分号(;)作为分隔符，因为 MeSH 术语中可能包含逗号
        queries = [q.strip() for q in args.search_multi.split(";")]
        queries = [q for q in queries if q]
        if not queries:
            logger.error("未提供有效的检索词")
            sys.exit(1)

        logger.info(f"并行执行 {len(queries)} 个检索")

        # 选择搜索 API
        if args.use_europepmc:
            papers = fetcher.fetch_links_from_search_multi(
                queries,
                limit=args.limit,
                require_pmcid=True,
                max_search_workers=args.max_workers,
                max_link_workers=5,
                require_fulltext=require_fulltext
            )
        else:
            # 默认使用 PubMed（更适合非临床医学领域）
            searcher_results = fetcher.searcher.search_multiple_pubmed(
                queries,
                limit=args.limit,
                require_pmcid=True,
                max_workers=args.max_workers
            )
            papers = fetcher.oa_service.get_pdf_links_batch(
                searcher_results,
                max_workers=5
            )

            if require_fulltext:
                filtered_papers = [p for p in papers if p.get("download_success")]
                filtered_count = len(papers) - len(filtered_papers)
                if filtered_count > 0:
                    logger.info(f"已过滤 {filtered_count} 篇无全文链接的文献")
                papers = filtered_papers

        if not papers:
            logger.error("未找到匹配的文献")
            sys.exit(1)

        query = args.search_multi

    logger.info(f"找到 {len(papers)} 篇文献")

    success_count = sum(1 for p in papers if p.get("download_success"))
    logger.info(f"成功获取链接: {success_count}/{len(papers)}")

    # 显示摘要信息
    for i, paper in enumerate(papers[:10], 1):
        logger.info(f"\n{i}. {paper['title']}")
        logger.info(f"   PMCID: {paper.get('pmcid', '无')}")
        logger.info(f"   链接: {'已获取' if paper.get('pdf_link') else '未获取'}")
        if paper.get('download_error'):
            logger.info(f"   错误: {paper['download_error']}")

    if len(papers) > 10:
        logger.info(f"\n... 还有 {len(papers) - 10} 篇文献")

    # 输出结果
    result_data = {
        "query": query,
        "timestamp": time.time(),
        "total": len(papers),
        "success": success_count,
        "results": papers,
    }

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)

        logger.info(f"结果已保存到: {output_path}")
    else:
        print("\n" + "=" * 60)
        print("JSON 结果：")
        print("=" * 60)
        print(json.dumps(result_data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    import sys
    main()
