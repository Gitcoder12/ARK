# Repository organization

Keep permanent application code in the existing source packages. Use these
root-level areas for new, loose work:

- `playground/` — experiments and scratch Python files.
- `ideas/` — loose notes, text files, PDFs, and design thoughts.
- `examples/` — runnable demonstrations and sample programs.
- `scripts/` — maintained developer utilities (not scratch files).

## Safe auto-organizer

The organizer only considers regular, untracked, non-ignored files directly
inside the repository root. It never moves tracked or staged files, hidden
files, protected project files, nested files, directories, or symlinks.
Existing destinations are skipped rather than overwritten.

Preview first:

```bash
python scripts/auto_organize.py
```

Apply the preview:

```bash
python scripts/auto_organize.py --apply
git status --short
```

Then inspect the moves and stage only what you want:

```bash
git add <intended-paths>
```

Check mode (also used by the pre-commit hook):

```bash
python scripts/auto_organize.py --check
```

## Enable the version-controlled pre-commit hook

Run once after cloning:

```bash
git config core.hooksPath .githooks
```

On macOS/Linux, if Git reports that the hook is not executable:

```bash
chmod +x .githooks/pre-commit
```

The hook does not move files or stage changes. It only warns and blocks a
commit when eligible loose root files remain; run the organizer, review the
moves, and stage them yourself.

## Repository-specific routing

- RepoForge: names containing `sandbox`, `bwrap`, or `fortress` go to
  `playground/fortress/`. This avoids colliding with the existing
  `src/repoforge/fortress.py` module.
- ARK: names containing `safety` or `gate` go to `src/ark/safety/`.
- Names containing `example` or `demo` go to `examples/`.
- Loose `.md`, `.txt`, and `.pdf` files go to `ideas/`.
- Other loose `.py` files go to `playground/`.
- Unrecognized file types are left untouched.

The organizer is intentionally conservative. It does not reorganize existing
tracked repository content.
