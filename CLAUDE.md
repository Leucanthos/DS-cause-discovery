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

## Conventions

- Follow Anthropic skill format: YAML frontmatter + Markdown body
- Keep skills focused and composable
- Use memory files for persistent context (`~/.claude/projects/`)
