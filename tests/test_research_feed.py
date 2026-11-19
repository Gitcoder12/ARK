from scripts.update_research_feed import (
    category_query,
    date_from_parts,
    merge_paper,
    reconstruct_abstract,
    render_markdown,
)


def test_category_query_builds_arxiv_or_query():
    assert category_query(["AI alignment", "goal drift"]) == '"AI alignment" OR "goal drift"'


def test_reconstruct_abstract_restores_word_order():
    inverted = {"A": [0], "small": [1], "abstract": [2], "test.": [3]}
    assert reconstruct_abstract(inverted) == "A small abstract test."


def test_date_from_parts_handles_year_month_and_day():
    assert date_from_parts({"date-parts": [[2026, 11, 19]]}) == "2026-11-19"
    assert date_from_parts({"date-parts": [[2026, 11]]}) == "2026-11-01"
    assert date_from_parts(None) == ""


def test_merge_paper_deduplicates_doi_across_providers():
    records = {}
    first = {
        "id": "10.1234/example", "doi": "10.1234/example", "arxiv_id": "",
        "title": "Example", "authors": ["A. Author"], "abstract": "",
        "published": "2026-11-18", "url": "https://doi.org/10.1234/example",
        "categories": [], "ark_category": "AI alignment and goal integrity",
        "source": "OpenAlex",
    }
    second = {**first, "source": "Crossref", "abstract": "An abstract.",
              "ark_category": "Corrigibility and runtime safeguards"}
    merge_paper(records, first)
    merge_paper(records, second)
    assert len(records) == 1
    merged = next(iter(records.values()))
    assert merged["sources"] == ["OpenAlex", "Crossref"]
    assert merged["abstract"] == "An abstract."
    assert "Corrigibility and runtime safeguards" in merged["ark_category"]


def test_render_markdown_includes_timestamp_sources_and_warning():
    paper = {
        "title": "Example paper", "url": "https://doi.org/10.1234/example",
        "authors": ["A. Author"], "published": "2026-11-18",
        "categories": ["journal-article"],
        "ark_category": "AI alignment and goal integrity",
        "abstract": "An abstract.", "doi": "10.1234/example",
        "source": "OpenAlex", "sources": ["OpenAlex", "Crossref"],
    }
    rendered = render_markdown({
        "generated_at": "2026-11-19T00:00:00+00:00",
        "sources": ["Crossref", "OpenAlex"],
        "papers": [paper],
    })
    assert "2026-11-19T00:00:00+00:00" in rendered
    assert "Example paper" in rendered
    assert "OpenAlex, Crossref" in rendered
    assert "not a quality ranking" in rendered
    assert "## Reward hacking and specification gaming" in rendered
