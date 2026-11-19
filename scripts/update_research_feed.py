#!/usr/bin/env python3
"""Refresh ARK's rolling research feed from the public arXiv Atom API."""
from __future__ import annotations
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
CATEGORIES = {
    "AI alignment and goal integrity": ["AI alignment", "goal misgeneralization", "value alignment"],
    "Reward hacking and specification gaming": ["reward hacking", "reward gaming", "specification gaming"],
    "Self-improvement and optimization": ["recursive self improvement", "self-refinement", "prompt optimization"],
    "Memory integrity and agent security": ["LLM agent memory poisoning", "agent memory security"],
    "Prompt injection and adversarial instructions": ["indirect prompt injection", "LLM agent prompt injection"],
    "Corrigibility and runtime safeguards": ["corrigibility", "AI oversight", "runtime safety monitoring"],
    "Autonomous agents and robotics": ["autonomous agent benchmark", "embodied agent safety", "robotics safety"],
}

def node_text(parent: ET.Element, tag: str) -> str:
    node = parent.find(tag)
    return (node.text or "").strip() if node is not None else ""

def category_query(terms: list[str]) -> str:
    return " OR ".join(f'all:"{term}"' for term in terms)

def fetch_category(category: str, terms: list[str]) -> list[dict]:
    params = {"search_query": category_query(terms), "start": "0",
              "max_results": str(MAX_PER_CATEGORY), "sortBy": "submittedDate",
              "sortOrder": "descending"}
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": "ARK-ResearchFeed/1.0"})
    with urllib.request.urlopen(request, timeout=25) as response:
        root = ET.fromstring(response.read())
    papers = []
    for entry in root.findall(f"{ATOM}entry"):
        raw_id = node_text(entry, f"{ATOM}id")
        match = re.search(r"/abs/([^/?#]+)", raw_id)
        if not match:
            continue
        authors = [node_text(a, f"{ATOM}name") for a in entry.findall(f"{ATOM}author")]
        published = node_text(entry, f"{ATOM}published")
        papers.append({
            "id": match.group(1),
            "title": re.sub(r"\s+", " ", node_text(entry, f"{ATOM}title")),
            "authors": authors,
            "abstract": re.sub(r"\s+", " ", node_text(entry, f"{ATOM}summary")),
            "published": published,
            "updated": node_text(entry, f"{ATOM}updated"),
            "url": f"https://arxiv.org/abs/{match.group(1)}",
            "pdf_url": f"https://arxiv.org/pdf/{match.group(1)}",
            "categories": [c.attrib.get("term", "") for c in entry.findall(f"{ATOM}category")],
            "ark_category": category,
            "source": "arXiv",
        })
    return papers

def render_markdown(payload: dict) -> str:
    lines = [
        "# ARK Live Research Feed", "",
        "Automatically refreshed from the public arXiv Atom API by GitHub Actions.", "",
        f"**Last successful update:** {payload['generated_at']}", "",
        f"**Records:** {len(payload['papers'])} · **Source:** arXiv", "",
        "> Automatically discovered research is not quality-ranked or necessarily peer-reviewed. Verify relevance, venue, and claims before citing. Categories reflect the search that discovered each paper.", "",
    ]
    for category in CATEGORIES:
        papers = [p for p in payload["papers"] if category in p["ark_category"]]
        lines += [f"## {category}", ""]
        if not papers:
            lines += ["_No matching papers in the latest sync._", ""]
            continue
        for p in papers:
            authors = ", ".join(p["authors"][:5]) or "Not listed"
            if len(p["authors"]) > 5:
                authors += ", et al."
            abstract = p["abstract"][:700] + ("…" if len(p["abstract"]) > 700 else "")
            lines += [
                f"### [{p['title']}]({p['url']})", "",
                f"- **Authors:** {authors}",
                f"- **Submitted:** {p['published'][:10] or 'Unknown'}",
                f"- **arXiv categories:** {', '.join(p['categories']) or 'Not listed'}",
                f"- **Abstract:** {abstract}", "",
            ]
    lines += [
        "## Freshness and limitations", "",
        "- The workflow runs daily and can be started manually from GitHub Actions.",
        "- Successful runs update this page and data/research_feed.json.",
        "- If every category query fails, the previous feed is preserved.",
        "- arXiv records are preprints unless a peer-reviewed venue is independently verified.",
        "- Coverage is limited to configured search terms; this is not an exhaustive survey.", "",
        "See [the curated research library](research-papers.md) for foundational references and ARK publications.", "",
    ]
    return "\n".join(lines)

def main() -> int:
    collected: dict[str, dict] = {}
    errors = []
    for index, (category, terms) in enumerate(CATEGORIES.items()):
        try:
            for paper in fetch_category(category, terms):
                key = paper["id"].lower()
                if key not in collected:
                    collected[key] = paper
                elif category not in collected[key]["ark_category"]:
                    collected[key]["ark_category"] += "; " + category
        except (urllib.error.URLError, TimeoutError, ET.ParseError, OSError, ValueError) as exc:
            errors.append(f"{category}: {exc}")
        if index < len(CATEGORIES) - 1:
            time.sleep(3)
    if not collected:
        print("Feed unchanged: all queries failed or returned no records.", file=sys.stderr)
        for error in errors:
            print("- " + error, file=sys.stderr)
        return 1
    papers = sorted(collected.values(), key=lambda p: (p["published"], p["title"]), reverse=True)
    payload = {"generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "source": "arXiv public Atom API", "categories": list(CATEGORIES),
               "papers": papers, "errors": errors}
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(payload), encoding="utf-8")
    print(f"Updated feed with {len(papers)} unique papers.")
    if errors:
        print(f"{len(errors)} category query(s) failed; partial feed saved with errors recorded.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
