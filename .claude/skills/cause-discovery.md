---
name: cause-discovery
description: Root cause analysis and discovery — helps trace effects back to their underlying causes through structured questioning and analysis frameworks.
---

# Cause Discovery

A 4-stage pipeline for discovering and analyzing root causes from tabular data.

## Pipeline

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────┐
│ ① Understand │───▶│ ② Attribution │───▶│ ③ Interpret  │───▶│ ④ Render │
│  (LLM+脚本)  │    │   (脚本)      │    │   (LLM)      │    │  (脚本)  │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────┘
```

### Stage 1 — Understand (LLM-driven, script-assisted)
- Read data via pandas (`pd.read_*`)
- Profile: dtypes, nulls, cardinality, distributions
- LLM classifies columns as **dimensions** (can group/split) vs **measures** (can aggregate)
- LLM determines aggregation semantics: which measures are additive along which dimensions

### Stage 2 — Attribution (script)
- Decompose a target measure across dimensions
- Calculate contribution scores (absolute & percentage)
- Detect interaction effects between dimensions
- Output structured `AttributionResult`

### Stage 3 — Interpret (LLM)
- LLM reads the `AttributionResult` and writes natural-language narrative
- Identifies primary drivers, secondary effects, surprises
- Assigns confidence levels

### Stage 4 — Render (script)
- Generate self-contained HTML report
- Includes: data summary, contribution charts, narrative text
- Uses pure HTML/CSS/JS (no server needed)

## When to Use

Invoke this skill when the user wants to:
- Understand why a KPI changed (e.g., "why did revenue drop 5%?")
- Decompose a metric along multiple dimensions
- Trace a symptom back to its underlying causes from data
- Generate a causal analysis report

## Implementation

Package: `src/cause_discovery/`

| Module | Role | Driver |
|--------|------|--------|
| `pipeline.py` | Orchestrator | — |
| `understand.py` | Stage ① data reading & profiling | LLM + script |
| `attribution.py` | Stage ② contribution decomposition | script |
| `interpret.py` | Stage ③ narrative synthesis | LLM |
| `render.py` | Stage ④ HTML report generation | script |
| `models.py` | Shared dataclasses | — |
