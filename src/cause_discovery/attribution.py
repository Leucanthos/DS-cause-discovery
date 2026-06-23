"""Stage 2 — Attribution Analysis (script).

Decomposes a target measure across dimensions and calculates contribution scores.
"""

from .models import AttributionResult, Contribution, DataProfile

import pandas as pd
import numpy as np


def decompose(
    profile: DataProfile,
    target_measure: str,
    base_period_filter: pd.Series | None = None,
    current_period_filter: pd.Series | None = None,
) -> AttributionResult:
    """Decompose change in target_measure across all dimensions.

    Args:
        profile: DataProfile from Stage 1 with loaded df
        target_measure: Name of the measure column to analyze
        base_period_filter: Boolean mask for base period rows
        current_period_filter: Boolean mask for current period rows

    Returns:
        AttributionResult with contribution breakdown.
    """
    df = profile.df
    dimensions = profile.dimensions or _guess_dimensions(profile)

    if base_period_filter is None or current_period_filter is None:
        raise ValueError("base_period_filter and current_period_filter are required")

    base = df[base_period_filter][target_measure].sum()
    current = df[current_period_filter][target_measure].sum()
    total_change = current - base

    contributions: list[Contribution] = []

    for dim in dimensions:
        base_by_dim = (
            df[base_period_filter].groupby(dim)[target_measure].sum().reset_index()
        )
        current_by_dim = (
            df[current_period_filter].groupby(dim)[target_measure].sum().reset_index()
        )

        merged = base_by_dim.merge(
            current_by_dim, on=dim, how="outer", suffixes=("_base", "_current")
        ).fillna(0)

        for _, row in merged.iterrows():
            dim_value = str(row[dim])
            base_val = float(row[f"{target_measure}_base"])
            current_val = float(row[f"{target_measure}_current"])
            abs_contrib = current_val - base_val
            pct_contrib = (abs_contrib / total_change * 100) if total_change != 0 else 0.0

            contributions.append(
                Contribution(
                    dimension=dim,
                    dimension_value=dim_value,
                    absolute_contribution=abs_contrib,
                    percentage_contribution=pct_contrib,
                )
            )

    return AttributionResult(
        target_measure=target_measure,
        base_value=base,
        current_value=current,
        total_change=total_change,
        contributions=contributions,
        method="period-over-period decomposition",
    )


def _guess_dimensions(profile: DataProfile) -> list[str]:
    """Fallback: treat low-cardinality non-numeric columns as dimensions."""
    candidates = []
    for c in profile.columns:
        if c.role == "dimension":
            candidates.append(c.name)
        elif c.role == "" and c.dtype in ("object", "string", "category", "bool"):
            if c.unique_count <= 50:
                candidates.append(c.name)
    return candidates


def top_contributors(result: AttributionResult, n: int = 10) -> list[Contribution]:
    """Return top N contributors by absolute contribution magnitude."""
    sorted_contribs = sorted(
        result.contributions,
        key=lambda c: abs(c.absolute_contribution),
        reverse=True,
    )
    return sorted_contribs[:n]
