"""Pipeline orchestrator — wires Stage 1→2→3→4 together."""

from __future__ import annotations

import pandas as pd

from .models import AttributionResult, DataProfile, Interpretation, PipelineResult
from .understand import run as stage1_run
from .attribution import decompose
from .interpret import build_prompt, run as stage3_run
from .render import render, open_report


class Pipeline:
    """Cause Discovery pipeline.

    Usage:
        pipeline = Pipeline()
        result = pipeline.run(
            data_path="data.csv",
            target_measure="revenue",
            base_mask=df["month"] == "2024-01",
            current_mask=df["month"] == "2024-02",
            # llm_classify=<callable>,   # Stage 1 LLM
            # llm_interpret=<callable>,  # Stage 3 LLM
        )
        pipeline.open_report()
    """

    def __init__(self):
        self._result: PipelineResult | None = None

    def run(
        self,
        data_path: str,
        target_measure: str,
        base_mask: pd.Series,
        current_mask: pd.Series,
        llm_classify: callable | None = None,
        llm_interpret: callable | None = None,
        output_html: str = "report.html",
    ) -> PipelineResult:
        """Execute the full 4-stage pipeline.

        Args:
            data_path: Path to data file.
            target_measure: Name of the measure column to analyze.
            base_mask: Boolean mask selecting base-period rows.
            current_mask: Boolean mask selecting current-period rows.
            llm_classify: Callable(prompt: str) -> str for Stage 1 column classification.
            llm_interpret: Callable(prompt: str) -> str for Stage 3 interpretation.
            output_html: Path for the generated HTML report.

        Returns:
            PipelineResult with all stage outputs.
        """
        # Stage 1: Understand
        profile = stage1_run(data_path)
        if llm_classify:
            prompt = _build_classify_prompt(profile)
            response = llm_classify(prompt)
            profile.llm_notes = response
            # TODO: parse structured classification from LLM response
        self._classify_heuristic(profile)

        # Stage 2: Attribution
        attribution = decompose(
            profile, target_measure, base_mask, current_mask
        )

        # Stage 3: Interpret
        interpretation = Interpretation()
        if llm_interpret:
            prompt = build_prompt(attribution)
            llm_response = llm_interpret(prompt)
            interpretation = stage3_run(attribution, llm_response)

        # Stage 4: Render
        html_path = render(profile, attribution, interpretation, output_html)

        self._result = PipelineResult(
            data_profile=profile,
            attribution=attribution,
            interpretation=interpretation,
            html_path=html_path,
        )
        return self._result

    @property
    def result(self) -> PipelineResult | None:
        return self._result

    def open_report(self) -> None:
        """Open the generated HTML report in browser."""
        if self._result and self._result.html_path:
            open_report(self._result.html_path)

    @staticmethod
    def _classify_heuristic(profile: DataProfile) -> None:
        """Heuristic column classification (fallback when no LLM)."""
        for c in profile.columns:
            if c.role:
                continue
            if c.dtype in ("object", "string", "category", "bool"):
                if c.unique_count <= 50:
                    c.role = "dimension"
                    profile.dimensions.append(c.name)
                else:
                    c.role = "ignore"
            elif "int" in c.dtype or "float" in c.dtype:
                c.role = "measure"
                c.additive = True
                profile.measures.append(c.name)
            else:
                c.role = "ignore"


def _build_classify_prompt(profile: DataProfile) -> str:
    """Build prompt for Stage 1 LLM column classification."""
    from .understand import llm_classify_columns

    return llm_classify_columns(profile)
