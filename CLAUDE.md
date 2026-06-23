# DS Cause Discovery

A Claude Code skill project for cause discovery and analysis.

## Project Overview

This project provides custom Claude Code skills for discovering, analyzing, and
understanding root causes across various domains.

## Directory Structure

```
.claude/
  skills/       # Skill definition files (.md)
  settings.json # Project-specific Claude Code settings
```

## Skills

- `cause-discovery` — Root cause analysis and discovery

## Development

- Skills are authored as Markdown files with YAML frontmatter in `.claude/skills/`
- Each skill defines its own instructions, tools, and behaviors
- Run `claude` in this directory to use the skills

## Git Workflow

This project enforces a disciplined Git workflow:

### Rule 1: Every change must be committed locally

- After **each** modification (file creation, edit, deletion, rename), immediately
  stage and commit.
- Commit messages use [Conventional Commits](https://www.conventionalcommits.org/)
  format: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`.
- Commit message body must end with `Co-Authored-By: Claude <noreply@anthropic.com>`.
- Never leave uncommitted changes in the working tree.

### Rule 2: Push after every commit

- After **each** local commit, immediately push to `origin`.
- This ensures the remote is always in sync with local — no batch accumulation.
- Since you push after every commit, there is never more than 1 ahead-of-remote
  commit at push time.

### Rule 3: Squash before push (safety net)

- If multiple local commits happen to accumulate ahead of `<remote>/<branch>`
  (e.g., due to network issues), squash them into a **single** commit before pushing.
- Use `git reset --soft <remote>/<branch>` then `git commit` a consolidated message.
- If the remote branch does not yet exist, squash from root before `git push -u`.

## Conventions

- Follow Anthropic skill format: YAML frontmatter + Markdown body
- Keep skills focused and composable
- Use memory files for persistent context (`~/.claude/projects/`)

## Data Stack

- **pandas** is the primary data manipulation API. All tabular data operations
  (loading, filtering, grouping, joining, transforming, aggregation) must use
  pandas DataFrames and Series — do not use plain Python lists, dicts, or
  manual loops where a pandas vectorized operation applies.
- Preferred imports pattern:
  ```python
  import pandas as pd
  import numpy as np
  ```
- CSV/Excel/Parquet/JSON tabular data is read via `pd.read_*` and written via
  `DataFrame.to_*`.
