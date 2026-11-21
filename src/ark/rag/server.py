"""FastMCP read-only retrieval tools for ARK policies and research."""

from __future__ import annotations

import os
from pathlib import Path

from ark.rag.store import LocalKnowledgeBase

try:
    from fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover - optional dependency
    raise RuntimeError(
        "FastMCP is optional. Install ARK with: pip install 'ark-alignment[rag]'"
    ) from exc

ROOTS = tuple(
    item for item in os.environ.get("ARK_RAG_ROOTS", "").split(os.pathsep) if item.strip()
)
if not ROOTS:
    raise RuntimeError(
        "Set ARK_RAG_ROOTS to one or more trusted policy/research directories before startup."
    )

DB_PATH = Path(os.environ.get("ARK_RAG_DB", "~/.ark/rag.sqlite3")).expanduser()
knowledge = LocalKnowledgeBase(DB_PATH, allowed_roots=ROOTS)
mcp = FastMCP("ARK Safety and Research Knowledge Engine")


@mcp.tool
def policy_search(query: str, collection: str = "ark-policies", top_k: int = 5) -> list[dict]:
    """Retrieve safety policies and return source-cited, untrusted evidence."""
    return knowledge.search(query, collection, top_k)


@mcp.tool
def research_search(query: str, collection: str = "ark-research", top_k: int = 5) -> list[dict]:
    """Retrieve research notes and experiment records with exact source locations."""
    return knowledge.search(query, collection, top_k)


@mcp.tool
def rag_list_collections() -> list[dict]:
    """List indexed ARK knowledge collections and their counts."""
    return knowledge.list_collections()


@mcp.tool
def rag_index_directory(directory: str, collection: str) -> dict:
    """Index files beneath an explicitly configured ARK knowledge root.

    This tool reads allowlisted text/code files only. It does not execute files.
    """
    return knowledge.index_directory(directory, collection)


def main() -> None:
    """Run the local MCP server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
