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

### Rule 2: Squash before push

- Before pushing to `origin`, squash ALL local commits that are ahead of the
  remote tracking branch into a **single** commit.
- "Ahead commits" = all commits between `<remote>/<branch>` and `HEAD` (inclusive
  of local, exclusive of remote).
- Use interactive rebase to squash:
  ```bash
  git rebase -i <remote>/<branch>
  # Mark all but the first commit as `squash` / `s`
  ```
- Reword the squashed commit message to summarize the combined changes cleanly.
- Push the single squashed commit with `git push`.
- If the remote branch does not yet exist, squash all commits on the current
  branch from `root` into one before `git push -u origin <branch>`.

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
