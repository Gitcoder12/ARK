# ARK repository organization

Keep the repository easy to navigate. The package under `src/ark/` is the
canonical home for maintained application and research code.

## Canonical layout

```text
ARK/
├── README.md
├── START_HERE.md
├── pyproject.toml
├── src/ark/       # product and research modules
├── tests/         # automated tests
├── examples/      # runnable demonstrations
├── pages/         # Streamlit pages
├── docs/          # research, design and contributor documentation
├── data/          # versioned, non-secret datasets
├── configs/       # non-secret example policies
├── scripts/       # maintained developer utilities
├── playground/    # disposable experiments
└── ideas/         # unvalidated notes
```

## Placement rules

- New importable modules belong inside the appropriate `src/ark/<area>/`
  package, with tests under `tests/`.
- Runnable examples belong in `examples/`.
- Maintained automation belongs in `scripts/`.
- Research and design notes belong in `docs/`; unvalidated scratch notes go
  in `ideas/`.
- Keep credentials, private datasets and generated artifacts out of Git.
- Do not create new root-level Python files or duplicate modules under a
  second package tree.

## Branch naming and lifecycle

Use one short-lived branch per reviewable change:

- `feat/<short-name>`
- `fix/<short-name>`
- `docs/<short-name>`

`main` remains the integration baseline. Keep branches backing open PRs.
After a merge, verify the merge commit and main CI, then delete the source
branch. Before removing an orphan branch, compare it with `main` and preserve
any unique commits or files. Never delete branches in bulk just because they
look old.

## Conservative organizer

The existing `scripts/auto_organize.py` only previews or routes eligible
untracked files directly inside the repository root. It does not reorganize
tracked content. Preview before applying:

```bash
python scripts/auto_organize.py
python scripts/auto_organize.py --apply
git status --short
```

Review every proposed move and stage only intended paths. The organizer is a
guard against loose new files, not a substitute for architecture refactoring.
