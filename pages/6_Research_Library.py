"""Searchable ARK research library with transparent paper-to-project relevance tiers."""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
LIBRARY_PATH = ROOT / "data" / "research_library.json"
TIER_ORDER = {"P1": 0, "P2": 1, "P3": 2}
TIER_LABELS = {
    "P1": "Core relevance",
    "P2": "Supporting relevance",
    "P3": "Exploratory relevance",
}

st.set_page_config(page_title="ARK — Research Library", page_icon="📚", layout="wide")
st.title("ARK Research Library")
st.caption(
    "A searchable, attributed reading map for alignment, agent reliability, "
    "memory integrity, interpretability, and embodied safety research."
)

try:
    library = json.loads(LIBRARY_PATH.read_text(encoding="utf-8"))
    papers = library["papers"]
except (OSError, json.JSONDecodeError, KeyError) as exc:
    st.error(f"Research library could not be loaded: {exc}")
    st.stop()

verified = [paper for paper in papers if paper.get("metadata_verified", False)]
pending = [paper for paper in papers if not paper.get("metadata_verified", False)]

st.info(
    "**How to interpret priority:** ARPI ranks how directly a paper relates to ARK's "
    "current roadmap. It does not assess scientific quality, rank authors, or measure "
    "the paper's value to the wider research community. P3 means less directly applicable "
    "to current ARK work—not useless."
)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Curated records", len(verified))
m2.metric("P1 · Core", sum(p.get("priority") == "P1" for p in verified))
m3.metric("P2 · Supporting", sum(p.get("priority") == "P2" for p in verified))
m4.metric("P3 · Exploratory", sum(p.get("priority") == "P3" for p in verified))

st.subheader("Find research")
query_col, tier_col, category_col = st.columns([2, 1, 1])
with query_col:
    query = st.text_input(
        "Search title or author",
        placeholder="e.g. reward gaming, Dylan Hadfield-Menell",
    )
with tier_col:
    selected_tiers = st.multiselect(
        "Priority",
        options=["P1", "P2", "P3"],
        default=["P1", "P2", "P3"],
        format_func=lambda value: f"{value} — {TIER_LABELS[value]}",
    )
with category_col:
    categories = sorted({paper["category"] for paper in verified})
    selected_categories = st.multiselect("Research area", categories, default=[])

show_pending = st.checkbox(
    f"Show candidate records with metadata/acceptance still to verify ({len(pending)})",
    value=False,
)

visible = verified + (pending if show_pending else [])
query_lower = query.strip().casefold()
filtered = []
for paper in visible:
    if paper.get("priority") not in selected_tiers:
        continue
    if selected_categories and paper.get("category") not in selected_categories:
        continue
    haystack = " ".join(
        [paper.get("title", ""), paper.get("category", "")]
        + paper.get("authors", [])
    ).casefold()
    if query_lower and query_lower not in haystack:
        continue
    filtered.append(paper)

filtered.sort(
    key=lambda paper: (
        TIER_ORDER.get(paper.get("priority", "P3"), 3),
        paper.get("title", "").casefold(),
    )
)

st.caption(f"Showing {len(filtered)} of {len(visible)} records.")
if not filtered:
    st.warning("No papers match these filters. Try clearing one of the filters.")
else:
    for paper in filtered:
        tier = paper.get("priority", "P3")
        title = paper.get("title", "Untitled")
        status = paper.get("publication_status", "Status not recorded")
        label = f"{tier} · {TIER_LABELS.get(tier, 'Unclassified')}"
        if not paper.get("metadata_verified", False):
            label += " · Verification pending"

        with st.expander(f"{title}  |  {label}", expanded=False):
            left, right = st.columns([3, 1])
            with left:
                st.markdown(f"**Research area:** {paper.get('category', 'Uncategorized')}")
                author_text = ", ".join(paper.get("authors") or [])
                if not author_text:
                    author_text = "Not published / not independently verified"
                st.markdown(f"**Authors (original order):** {author_text}")
                st.markdown(f"**Year:** {paper.get('year', 'Not recorded')}")
                st.markdown(f"**Venue:** {paper.get('venue', 'Not verified')}")
                st.markdown(f"**Publication status:** {status}")
            with right:
                st.metric("ARK priority", tier)
                st.caption(TIER_LABELS.get(tier, "Unclassified"))
            st.markdown("**Why it is relevant to ARK**")
            st.write(paper.get("rationale", "No relevance note recorded."))
            st.markdown(f"[Open original source]({paper['url']})")
            if paper.get("doi"):
                st.caption(f"DOI: {paper['doi']}")
            st.caption(f"Metadata source: {paper.get('metadata_source', 'Not recorded')}")
            if paper.get("metadata_note"):
                st.warning(paper["metadata_note"])
            if not paper.get("metadata_verified", False):
                st.warning(
                    "This is a candidate reading record only. Do not cite its venue, "
                    "acceptance, or author attribution as confirmed until the metadata "
                    "is reconciled against the final public record."
                )

st.divider()
st.subheader("How ARPI priority is assigned")
st.write(library["scoring"]["policy"])
weights = library["scoring"]["weights"]
weight_cols = st.columns(len(weights))
for column, item in zip(weight_cols, weights, strict=True):
    column.metric(item["criterion"], f'{item["weight"]}%')

tier_cols = st.columns(3)
for column, key in zip(tier_cols, ["P1", "P2", "P3"], strict=True):
    tier = library["scoring"]["tiers"][key]
    column.markdown(f"**{key} · {tier['label']}**")
    column.caption(tier["range"])
    column.write(tier["description"])

st.caption(
    "The displayed tiers are provisional editorial triage. Numeric scores are "
    "intentionally withheld until a reviewer records criterion-level evidence. "
    "The live discovery feed is separate from this curated library. Bibliographic "
    "metadata should be checked against the linked publisher or canonical preprint."
)
