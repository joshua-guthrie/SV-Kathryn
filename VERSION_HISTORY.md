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
duplicate downloaded archive containers are ignored. The original reference
files remain local; no remote is configured.

Commits are authored as `Codex <codex@local.invalid>` because this environment
has no configured Git user identity. This identity is scoped to this repository.

SOMA's automatic Git timeline expects standard `.git` metadata and may not show
this alternate local history. When that mount is writable in a future session,
the metadata can be moved into `.git` and normal `git` commands will work.
