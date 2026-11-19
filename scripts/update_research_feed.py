#!/usr/bin/env python3
"""Refresh ARK's rolling research feed from arXiv, OpenAlex, and Crossref."""
from __future__ import annotations

import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_JSON = ROOT / "data" / "research_feed.json"
OUTPUT_MD = ROOT / "docs" / "research-feed.md"
ATOM = "{http://www.w3.org/2005/Atom}"
MAX_PER_CATEGORY = int(os.environ.get("ARK_RESEARCH_MAX_PER_CATEGORY", "15"))
MAILTO = os.environ.get("CROSSREF_MAILTO", "")
USER_AGENT = "ARK-ResearchFeed/1.1 (https://github.com/Gitcoder12/ARK)"
CATEGORIES = {
    "AI alignment and goal integrity": ["AI alignment", "goal misgeneralization", "value alignment"],
    "Reward hacking and specification gaming": ["reward hacking", "reward gaming", "specification gaming"],
    "Self-improvement and optimization": ["recursive self improvement", "self-refinement", "prompt optimization"],
    "Memory integrity and agent security": ["LLM agent memory poisoning", "agent memory security"],
    "Prompt injection and adversarial instructions": ["indirect prompt injection", "LLM agent prompt injection"],
    "Corrigibility and runtime safeguards": ["corrigibility", "AI oversight", "runtime safety monitoring"],
    "Autonomous agents and robotics": ["autonomous agent benchmark", "embodied agent safety", "robotics safety"],
}


def category_query(terms: list[str]) -> str:
    return " OR ".join(f'"{term}"' for term in terms)


def request_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    })
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def request_xml(url: str) -> ET.Element:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return ET.fromstring(response.read())


def node_text(parent: ET.Element, tag: str) -> str:
    node = parent.find(tag)
    return (node.text or "").strip() if node is not None else ""


def normalize_doi(value: str) -> str:
    value = value.strip()
    value = re.sub(r"^https?://(dx\.)?doi\.org/", "", value, flags=re.I)
    return value.lower()


def reconstruct_abstract(inverted_index: dict | None) -> str:
    if not inverted_index:
        return ""
    positions = {}
    for word, offsets in inverted_index.items():
        for offset in offsets:
            positions[offset] = word
    return " ".join(positions[index] for index in sorted(positions))


def date_from_parts(value: dict | None) -> str:
    parts = (value or {}).get("date-parts", [[]])[0]
    if not parts:
        return ""
    parts = list(parts) + [1] * (3 - len(parts))
    return f"{int(parts[0]):04d}-{int(parts[1]):02d}-{int(parts[2]):02d}"


def make_paper(*, title: str, authors: list[str], abstract: str, published: str,
               url: str, source: str, category: str, doi: str = "",
               arxiv_id: str = "", categories: list[str] | None = None) -> dict:
    stable_id = normalize_doi(doi) or arxiv_id.lower() or url.rstrip("/").lower()
    return {
        "id": stable_id,
        "title": re.sub(r"\s+", " ", html.unescape(title)).strip(),
        "authors": authors,
        "abstract": re.sub(r"\s+", " ", html.unescape(abstract)).strip(),
        "published": published,
        "url": url,
        "doi": normalize_doi(doi),
        "arxiv_id": arxiv_id,
        "categories": categories or [],
        "ark_category": category,
        "source": source,
    }


def fetch_arxiv(category: str, terms: list[str]) -> list[dict]:
    params = {
        "search_query": " OR ".join(f'all:"{term}"' for term in terms),
        "start": "0", "max_results": str(MAX_PER_CATEGORY),
        "sortBy": "submittedDate", "sortOrder": "descending",
    }
    root = request_xml("https://export.arxiv.org/api/query?" + urllib.parse.urlencode(params))
    papers = []
    for entry in root.findall(f"{ATOM}entry"):
        raw_id = node_text(entry, f"{ATOM}id")
        match = re.search(r"/abs/([^/?#]+)", raw_id)
        if not match:
            continue
        arxiv_id = match.group(1)
        authors = [node_text(a, f"{ATOM}name") for a in entry.findall(f"{ATOM}author")]
        papers.append(make_paper(
            title=node_text(entry, f"{ATOM}title"), authors=authors,
            abstract=node_text(entry, f"{ATOM}summary"),
            published=node_text(entry, f"{ATOM}published")[:10],
            url=f"https://arxiv.org/abs/{arxiv_id}", source="arXiv",
            category=category, arxiv_id=arxiv_id,
            categories=[c.attrib.get("term", "") for c in entry.findall(f"{ATOM}category")],
        ))
    return papers


def fetch_openalex(category: str, terms: list[str]) -> list[dict]:
    params = {
        "search": " OR ".join(terms),
        "per-page": str(MAX_PER_CATEGORY),
        "sort": "publication_date:desc",
        "select": "id,doi,title,authorships,publication_date,primary_location,abstract_inverted_index,type",
    }
    data = request_json("https://api.openalex.org/works?" + urllib.parse.urlencode(params))
    papers = []
    for item in data.get("results", []):
        authors = [
            a.get("author", {}).get("display_name", "")
            for a in item.get("authorships", [])
            if a.get("author", {}).get("display_name")
        ]
        doi = normalize_doi(item.get("doi") or "")
        location = item.get("primary_location") or {}
        landing = location.get("landing_page_url") or (f"https://doi.org/{doi}" if doi else item.get("id", ""))
        papers.append(make_paper(
            title=item.get("title") or "", authors=authors,
            abstract=reconstruct_abstract(item.get("abstract_inverted_index")),
            published=item.get("publication_date") or "", url=landing,
            source="OpenAlex", category=category, doi=doi,
            categories=[item.get("type", "")] if item.get("type") else [],
        ))
    return papers


def fetch_crossref(category: str, terms: list[str]) -> list[dict]:
    params = {
        "query.bibliographic": " ".join(terms),
        "rows": str(MAX_PER_CATEGORY),
        "sort": "published",
        "order": "desc",
    }
    if MAILTO:
        params["mailto"] = MAILTO
    data = request_json("https://api.crossref.org/works?" + urllib.parse.urlencode(params))
    papers = []
    for item in data.get("message", {}).get("items", []):
        doi = normalize_doi(item.get("DOI") or "")
        if not doi:
            continue
        title = (item.get("title") or [""])[0]
        authors = [
            " ".join(part for part in (a.get("given", ""), a.get("family", "")) if part)
            for a in item.get("author", [])
        ]
        abstract = re.sub(r"<[^>]+>", " ", item.get("abstract") or "")
        published = date_from_parts(
            item.get("published-online") or item.get("published-print")
            or item.get("published") or item.get("created")
        )
        papers.append(make_paper(
            title=title, authors=authors, abstract=abstract, published=published,
            url=f"https://doi.org/{doi}", source="Crossref", category=category, doi=doi,
            categories=[item.get("type", "")] if item.get("type") else [],
        ))
    return papers


def merge_paper(collected: dict[str, dict], paper: dict) -> None:
    key = normalize_doi(paper.get("doi") or "") or (
        paper.get("arxiv_id") or paper.get("id", "")
    ).lower()
    if not key:
        key = re.sub(r"\W+", "", paper.get("title", "").lower())
    if key not in collected:
        paper["sources"] = [paper["source"]]
        collected[key] = paper
        return
    existing = collected[key]
    if paper["source"] not in existing["sources"]:
        existing["sources"].append(paper["source"])
    if not existing.get("abstract") and paper.get("abstract"):
        existing["abstract"] = paper["abstract"]
    if not existing.get("authors") and paper.get("authors"):
        existing["authors"] = paper["authors"]
    if not existing.get("doi") and paper.get("doi"):
        existing["doi"] = paper["doi"]
    if not existing.get("arxiv_id") and paper.get("arxiv_id"):
        existing["arxiv_id"] = paper["arxiv_id"]
    categories = set(existing.get("categories", [])) | set(paper.get("categories", []))
    existing["categories"] = sorted(categories - {""})
    if paper["ark_category"] not in existing["ark_category"]:
        existing["ark_category"] += "; " + paper["ark_category"]


def render_markdown(payload: dict) -> str:
    sources = ", ".join(payload.get("sources", []))
    lines = [
        "# ARK Live Research Feed", "",
        "Automatically refreshed from arXiv, OpenAlex, and Crossref by GitHub Actions.", "",
        f"**Last successful update:** {payload['generated_at']}", "",
        f"**Unique records:** {len(payload['papers'])} · **Sources:** {sources}", "",
        "> This is an automatically discovered feed, not a quality ranking. Records may include preprints, articles, or incomplete metadata. Verify the publication venue, version, and claims before citing. Categories reflect discovery queries.", "",
    ]
    for category in CATEGORIES:
        papers = [p for p in payload["papers"] if category in p["ark_category"]]
        lines += [f"## {category}", ""]
        if not papers:
            lines += ["_No matching papers in the latest sync._", ""]
            continue
        for paper in papers:
            authors = ", ".join(paper["authors"][:5]) or "Not listed"
            if len(paper["authors"]) > 5:
                authors += ", et al."
            abstract = paper["abstract"][:700] + ("…" if len(paper["abstract"]) > 700 else "")
            lines += [
                f"### [{paper['title']}]({paper['url']})", "",
                f"- **Authors:** {authors}",
                f"- **Date:** {paper['published'] or 'Unknown'}",
                f"- **Source(s):** {', '.join(paper.get('sources', [paper['source']]))}",
                f"- **DOI:** {paper['doi'] or 'Not listed'}",
                f"- **Abstract:** {abstract or 'Abstract not available.'}", "",
            ]
    lines += [
        "## Freshness and limitations", "",
        "- The workflow runs daily and can be started manually from GitHub Actions.",
        "- Successful runs update this page and data/research_feed.json.",
        "- If every source query fails or returns no records, the previous feed is preserved.",
        "- Metadata and abstracts vary by provider; a missing abstract does not mean a paper is invalid.",
        "- Search coverage is limited to the configured terms and provider indexing; this is not exhaustive.",
        "- Check publisher records before treating a Crossref or OpenAlex record as peer-reviewed.", "",
        "See [the curated research library](research-papers.md) for foundational references and ARK publications.", "",
    ]
    return "\n".join(lines)


def main() -> int:
    collected: dict[str, dict] = {}
    errors: list[str] = []
    providers = [
        ("arXiv", fetch_arxiv),
        ("OpenAlex", fetch_openalex),
        ("Crossref", fetch_crossref),
    ]
    successful_sources = set()
    for category, terms in CATEGORIES.items():
        for source, fetcher in providers:
            try:
                papers = fetcher(category, terms)
                successful_sources.add(source)
                for paper in papers:
                    merge_paper(collected, paper)
            except (urllib.error.URLError, TimeoutError, ET.ParseError, OSError,
                    ValueError, KeyError, TypeError, ET.ParseError) as exc:
                errors.append(f"{source} / {category}: {exc}")
            time.sleep(1)
    if not collected:
        print("Feed unchanged: all provider queries failed or returned no records.", file=sys.stderr)
        for error in errors:
            print("- " + error, file=sys.stderr)
        return 1
    papers = sorted(
        collected.values(),
        key=lambda paper: (paper.get("published") or "", paper.get("title") or ""),
        reverse=True,
    )
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sources": sorted(successful_sources),
        "categories": list(CATEGORIES),
        "papers": papers,
        "errors": errors,
    }
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(payload), encoding="utf-8")
    print(f"Updated feed with {len(papers)} unique records from {', '.join(sorted(successful_sources))}.")
    if errors:
        print(f"{len(errors)} provider/category query(s) failed; partial feed saved with errors recorded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
