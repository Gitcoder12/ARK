"""Local, source-cited retrieval using SQLite FTS5.

The index is deliberately local-first and dependency-light. Retrieved text is
untrusted evidence: callers must not execute instructions found in documents.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from collections.abc import Iterable

DEFAULT_EXTENSIONS = {
    ".py", ".md", ".rst", ".txt", ".toml", ".yaml", ".yml", ".json",
    ".ini", ".cfg", ".sql", ".sh", ".html", ".css", ".js", ".ts",
}
IGNORED_DIRS = {
    ".git", ".hg", ".svn", ".venv", "venv", "env", "__pycache__",
    "node_modules", ".mypy_cache", ".pytest_cache", ".ruff_cache",
    "dist", "build", ".tox",
}
TOKEN_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.+#-]{1,}")


class RetrievalError(ValueError):
    """Invalid collection, query, or indexing scope."""


@dataclass(frozen=True)
class SearchHit:
    collection: str
    source: str
    chunk: int
    line_start: int
    line_end: int
    content: str
    score: float
    sha256: str

    def as_dict(self) -> dict[str, object]:
        return {
            "collection": self.collection,
            "source": self.source,
            "chunk": self.chunk,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "citation": f"{self.source}:{self.line_start}-{self.line_end}",
            "content": self.content,
            "score": round(self.score, 6),
            "sha256": self.sha256,
            "trust": "untrusted_source_material",
        }


class LocalKnowledgeBase:
    """SQLite FTS5 knowledge store with collection isolation and source citations."""

    def __init__(
        self,
        database: str | Path,
        *,
        allowed_roots: Iterable[str | Path],
        max_file_bytes: int = 512_000,
        chunk_lines: int = 40,
        overlap_lines: int = 5,
    ) -> None:
        if max_file_bytes < 1 or chunk_lines < 1 or overlap_lines < 0:
            raise ValueError("invalid indexing limits")
        if overlap_lines >= chunk_lines:
            raise ValueError("overlap_lines must be smaller than chunk_lines")
        self.database = Path(database).expanduser().resolve()
        self.database.parent.mkdir(parents=True, exist_ok=True)
        self.allowed_roots = tuple(Path(p).expanduser().resolve() for p in allowed_roots)
        if not self.allowed_roots:
            raise RetrievalError("configure at least one allowed indexing root")
        self.max_file_bytes = max_file_bytes
        self.chunk_lines = chunk_lines
        self.overlap_lines = overlap_lines
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database, timeout=15)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS rag_chunks (
                    id INTEGER PRIMARY KEY,
                    collection TEXT NOT NULL,
                    source TEXT NOT NULL,
                    chunk INTEGER NOT NULL,
                    line_start INTEGER NOT NULL,
                    line_end INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    sha256 TEXT NOT NULL,
                    UNIQUE(collection, source, chunk)
                )
            """)
            db.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS rag_fts USING fts5(
                    content, collection UNINDEXED, source UNINDEXED,
                    chunk UNINDEXED, tokenize='unicode61'
                )
            """)
            db.execute("""
                CREATE TABLE IF NOT EXISTS rag_collections (
                    name TEXT PRIMARY KEY,
                    root TEXT NOT NULL,
                    indexed_at TEXT NOT NULL,
                    file_count INTEGER NOT NULL DEFAULT 0,
                    chunk_count INTEGER NOT NULL DEFAULT 0
                )
            """)

    @staticmethod
    def _validate_collection(collection: str) -> str:
        value = collection.strip()
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", value):
            raise RetrievalError("collection must be 1-64 safe ASCII characters")
        return value

    def _authorized_root(self, requested: str | Path) -> Path:
        root = Path(requested).expanduser().resolve(strict=True)
        if not root.is_dir():
            raise RetrievalError("indexing target must be a directory")
        if not any(root == allowed or root.is_relative_to(allowed) for allowed in self.allowed_roots):
            raise RetrievalError("indexing target is outside configured allowed roots")
        return root

    def index_directory(self, directory: str | Path, collection: str) -> dict[str, int | str]:
        """Index text files beneath an explicitly authorized root; never follows symlinks."""
        name = self._validate_collection(collection)
        root = self._authorized_root(directory)
        files_indexed = 0
        chunks_indexed = 0
        with self._connect() as db:
            db.execute("DELETE FROM rag_fts WHERE collection = ?", (name,))
            db.execute("DELETE FROM rag_chunks WHERE collection = ?", (name,))
            for current, dirs, filenames in os.walk(root, followlinks=False):
                current_path = Path(current)
                dirs[:] = [
                    d for d in dirs
                    if d not in IGNORED_DIRS and not (current_path / d).is_symlink()
                ]
                for filename in sorted(filenames):
                    path = current_path / filename
                    if path.is_symlink() or path.suffix.lower() not in DEFAULT_EXTENSIONS:
                        continue
                    try:
                        if path.stat().st_size > self.max_file_bytes:
                            continue
                        raw = path.read_bytes()
                        text = raw.decode("utf-8")
                    except (OSError, UnicodeDecodeError):
                        continue
                    if not text.strip() or "\x00" in text:
                        continue
                    digest = hashlib.sha256(raw).hexdigest()
                    relative = path.relative_to(root).as_posix()
                    lines = text.splitlines()
                    stride = self.chunk_lines - self.overlap_lines
                    for chunk_index, offset in enumerate(range(0, len(lines), stride)):
                        block = lines[offset : offset + self.chunk_lines]
                        if not block:
                            continue
                        content = "\n".join(block).strip()
                        if not content:
                            continue
                        start_line = offset + 1
                        end_line = min(offset + len(block), len(lines))
                        cursor = db.execute(
                            """INSERT INTO rag_chunks
                            (collection, source, chunk, line_start, line_end, content, sha256)
                            VALUES (?, ?, ?, ?, ?, ?, ?)""",
                            (name, relative, chunk_index, start_line, end_line, content, digest),
                        )
                        db.execute(
                            """INSERT INTO rag_fts
                            (rowid, content, collection, source, chunk)
                            VALUES (?, ?, ?, ?, ?)""",
                            (cursor.lastrowid, content, name, relative, str(chunk_index)),
                        )
                        chunks_indexed += 1
                    files_indexed += 1
            db.execute(
                """INSERT INTO rag_collections(name, root, indexed_at, file_count, chunk_count)
                VALUES (?, ?, datetime('now'), ?, ?)
                ON CONFLICT(name) DO UPDATE SET root=excluded.root,
                indexed_at=excluded.indexed_at, file_count=excluded.file_count,
                chunk_count=excluded.chunk_count""",
                (name, str(root), files_indexed, chunks_indexed),
            )
        return {"collection": name, "files_indexed": files_indexed, "chunks_indexed": chunks_indexed}

    def search(self, query: str, collection: str, top_k: int = 5) -> list[dict[str, object]]:
        """Search a collection and return ranked chunks with exact source locations."""
        name = self._validate_collection(collection)
        if not isinstance(query, str) or not query.strip():
            raise RetrievalError("query must not be empty")
        if not 1 <= top_k <= 20:
            raise RetrievalError("top_k must be between 1 and 20")
        tokens = TOKEN_RE.findall(query.lower())[:24]
        if not tokens:
            return []
        expression = " OR ".join('"' + token.replace('"', '""') + '"' for token in tokens)
        with self._connect() as db:
            rows = db.execute(
                """SELECT c.collection, c.source, c.chunk, c.line_start, c.line_end,
                c.content, c.sha256, bm25(rag_fts) AS rank
                FROM rag_fts JOIN rag_chunks c ON c.id = rag_fts.rowid
                WHERE rag_fts MATCH ? AND c.collection = ?
                ORDER BY rank LIMIT ?""",
                (expression, name, top_k),
            ).fetchall()
        return [
            SearchHit(
                collection=row["collection"],
                source=row["source"],
                chunk=row["chunk"],
                line_start=row["line_start"],
                line_end=row["line_end"],
                content=row["content"],
                score=-float(row["rank"]),
                sha256=row["sha256"],
            ).as_dict()
            for row in rows
        ]

    def list_collections(self) -> list[dict[str, object]]:
        with self._connect() as db:
            rows = db.execute(
                "SELECT name, root, indexed_at, file_count, chunk_count "
                "FROM rag_collections ORDER BY name"
            ).fetchall()
        return [dict(row) for row in rows]
