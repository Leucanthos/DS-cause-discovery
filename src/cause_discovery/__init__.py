"""Cause Discovery — 4-stage root cause analysis pipeline.

Stages:
    1. Understand — read & profile data (LLM + script)
    2. Attribution — decompose & calculate contributions (script)
    3. Interpret  — LLM narrative synthesis
    4. Render     — self-contained HTML report (script)
"""

from .pipeline import Pipeline

__all__ = ["Pipeline"]
