from scripts.update_research_feed import category_query, render_markdown

def test_category_query_builds_arxiv_or_query():
    assert category_query(["AI alignment", "goal drift"]) == 'all:"AI alignment" OR all:"goal drift"'

def test_render_markdown_includes_timestamp_and_warning():
    paper = {"title": "Example paper", "url": "https://arxiv.org/abs/1234.5678",
             "authors": ["A. Author"], "published": "2026-11-18T00:00:00Z",
             "categories": ["cs.AI"], "ark_category": "AI alignment and goal integrity",
             "abstract": "An abstract."}
    rendered = render_markdown({"generated_at": "2026-11-19T00:00:00+00:00",
                                "papers": [paper]})
    assert "2026-11-19T00:00:00+00:00" in rendered
    assert "Example paper" in rendered
    assert "not quality-ranked" in rendered
    assert "## Reward hacking and specification gaming" in rendered
