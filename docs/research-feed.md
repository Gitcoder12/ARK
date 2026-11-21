# ARK Live Research Feed

Automatically refreshed daily from three scholarly discovery services:

- **arXiv** — preprints and research manuscripts, including abstracts and arXiv identifiers.
- **OpenAlex** — scholarly works, authorship metadata, publication dates, DOI links, and abstracts when available.
- **Crossref** — registered scholarly metadata, DOI records, publication dates, and abstracts when deposited.

The collector searches ARK's configured research categories, normalizes metadata, and deduplicates records by DOI where possible. Provider records for the same DOI are combined into one entry with all contributing sources recorded.

_Not synced yet. Run `python scripts/update_research_feed.py` locally or trigger the **Refresh ARK Research Feed** GitHub Actions workflow._

## Important interpretation notes

- This is a discovery feed, not a ranking, endorsement, or peer-review certification.
- arXiv entries are generally preprints. OpenAlex and Crossref index a mixture of publication types and versions.
- Abstracts and author metadata are not consistently available from every provider.
- The feed is refreshed daily, not continuously. A failed provider query is recorded; the previous feed is retained if every query fails or no records are returned.
- Search coverage depends on the configured terms and provider indexing. Check the publisher's official page before citing a paper.

See [the curated research library](research-papers.md) for foundational references and ARK publications.
