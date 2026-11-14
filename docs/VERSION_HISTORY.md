# Local version history

The user authorized frequent local commits on 2026-11-11. Save each coherent,
buildable modeling increment with a detailed commit message explaining the
problem, the change, source evidence or assumptions, validation and remaining
work. Do not publish or add a remote unless asked.

This session exposes `.git/` as an empty, read-only mount. Normal `git init`
therefore fails. The repository metadata lives in `.local-git/`; use the helper:

```sh
./project-git status
./project-git log --oneline
./project-git show
```

Source code, checks, measured drawing data, reports and original reference files
are versioned. SOMA state, generated STEP exports, renders, Python caches and
duplicate downloaded archive containers are ignored.

## Remote

`origin` is https://github.com/joshua-guthrie/SV-Kathryn.git, branch `main`.
The user requested the first push on 2026-11-14. The remote's initial commit
(a README stub and GPL-3.0 LICENSE) had no common ancestor, so it was merged
with `--allow-unrelated-histories`; the project README replaced the stub and
the LICENSE is kept. Push only when the user asks. The pushed tree contains the
source, checks, docs and references; `.local-git/`, `.soma/`, `output/`,
`renders/` and `exports/` remain local. The README links to `SV-Kathryn.stl` and
`SV-Kathryn.soma`, which are not in the repository yet.

Commits are authored as `Codex <codex@local.invalid>` because this environment
has no configured Git user identity. This identity is scoped to this repository.

SOMA's automatic Git timeline expects standard `.git` metadata and may not show
this alternate local history. When that mount is writable in a future session,
the metadata can be moved into `.git` and normal `git` commands will work.

## Post-commit build verification

The interrupted src/ cleanup showed that a clean working tree is not enough:
the committed tree must build on its own. After every commit that touches
model geometry, `src/`, checks, build inputs or reference data, run

```sh
./project-git status --short          # must print nothing
python src/checks/check_committed_build.py
```

The check exports the commit with `project-git archive` into a temporary
directory (no `.soma`, `output/`, renders or caches), runs a full
`python -m soma build` there, and requires status `ok`, no warnings, the
expected part count (874) and a STEP export. It then runs
`check_model_scale.py` and `check_registered_deck.py` in the clean tree.
Use `--ref <commit>` to verify an older checkpoint and `--keep` to inspect the
temporary tree. A failed check keeps the tree and prints its path.

Do not accept a model increment until this check passes for its commit. When
the part count legitimately changes, update `EXPECTED_PARTS` in the check and
the count in the commit message together.
