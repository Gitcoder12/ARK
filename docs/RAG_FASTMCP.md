# ARK Safety and Research Knowledge Engine

ARK's local RAG service indexes policy and research material into a local
SQLite FTS5 database and exposes source-cited retrieval through FastMCP.

## Install

```bash
pip install -e ".[rag,dev]"
```

## Configure

PowerShell:

```powershell
$env:ARK_RAG_ROOTS = "C:\work\ARK\knowledge"
$env:ARK_RAG_DB = "$HOME\.ark\rag.sqlite3"
ark-rag-mcp
```

Linux/macOS:

```bash
export ARK_RAG_ROOTS="$HOME/src/ARK/knowledge"
export ARK_RAG_DB="$HOME/.ark/rag.sqlite3"
ark-rag-mcp
```

Use local stdio transport. Keep policy, incidents, experiments and educational
material in distinct collections where their authority and access differ.

## Tools

- `policy_search(query, collection, top_k)`: retrieve source-cited policy evidence.
- `research_search(query, collection, top_k)`: retrieve research and experiment evidence.
- `rag_index_directory(directory, collection)`: index files under configured roots.
- `rag_list_collections()`: list collections and counts.

## Safety

Retrieved text is untrusted data, never an instruction or a replacement for
ARK's hard safety constraints. A RAG result may inform a monitor but must never
override deterministic safety gates, authorization, or human approval.

The server fails closed if no allowed root is configured. It rejects indexing
outside those roots, ignores symlinks and common build/dependency directories,
and skips oversized or non-UTF-8 files. The initial backend uses SQLite FTS5
for deterministic lexical retrieval without hosted services or API keys.

This is a local single-user MVP, not a multi-tenant authorization system or
OS-level sandbox. Keep it on stdio and do not expose unauthenticated HTTP.
