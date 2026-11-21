#!/usr/bin/env python3
"""Safely organize loose, untracked files at the repository root.

Default mode is a preview. Use --apply to move files. Tracked files, staged
files, ignored files, directories, symlinks, and protected project files are
never moved.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

PROTECTED = {
    "readme.md", "readme.rst", "license", "license.md", "license.txt",
    "contributing.md", "code_of_conduct.md", "security.md",
    "changelog.md", "pyproject.toml", "setup.py", "setup.cfg",
    "requirements.txt", "makefile", "dockerfile",
}


def repo_name(root: Path) -> str:
    return root.name.lower()


def destination(path: Path, repo: str) -> Path | None:
    name = path.name.lower()
    suffix = path.suffix.lower()
    stem = path.stem.lower()

    if name in PROTECTED or name.startswith("."):
        return None

    if any(token in stem for token in ("example", "demo")):
        return Path("examples") / path.name

    if repo == "repoforge" and any(token in stem for token in ("sandbox", "bwrap", "fortress")):
        # RepoForge currently exposes fortress.py as a module. Keep new
        # experiments separate until that module is intentionally migrated.
        return Path("playground") / "fortress" / path.name

    if repo == "ark" and any(token in stem for token in ("safety", "gate")):
        return Path("src/ark/safety") / path.name

    if suffix in {".md", ".txt", ".pdf"}:
        return Path("ideas") / path.name

    if suffix == ".py":
        return Path("playground") / path.name

    return None


def untracked_root_files(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=root, check=True, capture_output=True, text=True,
    )
    files = []
    for entry in result.stdout.splitlines():
        candidate = Path(entry)
        if len(candidate.parts) != 1:
            continue
        source = root / candidate
        if source.is_file() and not source.is_symlink():
            files.append(source)
    return sorted(files, key=lambda item: item.name.lower())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="move eligible files")
    mode.add_argument("--check", action="store_true", help="fail if eligible loose files exist")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    repo = repo_name(root)
    planned = []
    skipped = []

    for source in untracked_root_files(root):
        relative = source.relative_to(root)
        target = destination(relative, repo)
        if target is None:
            skipped.append(relative.as_posix())
            continue
        target_path = root / target
        if target_path.exists():
            skipped.append(f"{relative} (destination exists: {target})")
            continue
        planned.append((source, target_path, relative, target))

    if args.check:
        if planned:
            print("Loose root files need organizing:")
            for _, _, source, target in planned:
                print(f"  {source} -> {target}")
            print("Run: python scripts/auto_organize.py --apply")
            return 1
        print("Organization check passed: no eligible loose root files.")
        return 0

    if not args.apply:
        print("DRY RUN — no files moved. Re-run with --apply to organize:")
        for _, _, source, target in planned:
            print(f"  {source} -> {target}")
    else:
        moved = 0
        for source, target_path, relative, target in planned:
            if target_path.exists():
                skipped.append(f"{relative} (destination appeared during run)")
                continue
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(target_path))
            print(f"MOVED {relative} -> {target}")
            moved += 1
        print(f"Organized {moved} file(s).")

    if skipped:
        print("Skipped:")
        for item in skipped:
            print(f"  {item}")
    if not planned and not skipped:
        print("Nothing to organize.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
