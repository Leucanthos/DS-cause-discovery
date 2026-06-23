"""Shared data models for the cause-discovery pipeline."""

from dataclasses import dataclass, field
from typing import Optional

import pandas as pd


@dataclass
class ColumnProfile:
    """A single column's metadata."""

    name: str
    dtype: str
    null_count: int
    null_pct: float
    unique_count: int
    role: str = ""  # "dimension" | "measure" | "ignore"
    additive: bool = True  # for measures: safe to sum along any dimension?
    sample_values: list = field(default_factory=list)


@dataclass
class DataProfile:
    """Stage 1 output — full understanding of the loaded data."""

    df: pd.DataFrame
    columns: list[ColumnProfile] = field(default_factory=list)
    row_count: int = 0
    dimensions: list[str] = field(default_factory=list)
    measures: list[str] = field(default_factory=list)
    llm_notes: str = ""


@dataclass
class Contribution:
    """A single contribution entry."""

    dimension: str
    dimension_value: str
    absolute_contribution: float
    percentage_contribution: float
    interaction_with: str = ""


@dataclass
class AttributionResult:
    """Stage 2 output — decomposed contributions."""

    target_measure: str
    base_value: float
    current_value: float
    total_change: float
    contributions: list[Contribution] = field(default_factory=list)
    method: str = ""


@dataclass
class Interpretation:
    """Stage 3 output — LLM-generated narrative."""

    summary: str = ""
    primary_drivers: list[str] = field(default_factory=list)
    secondary_effects: list[str] = field(default_factory=list)
    surprises: list[str] = field(default_factory=list)
    confidence: str = ""  # "high" | "medium" | "low"
    narrative: str = ""


@dataclass
class PipelineResult:
    """Full pipeline output."""

    data_profile: DataProfile
    attribution: AttributionResult
    interpretation: Interpretation
    html_path: str = ""
