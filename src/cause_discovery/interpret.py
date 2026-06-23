"""Stage 3 — LLM Interpretation.

Takes the AttributionResult and produces a natural-language narrative.
The LLM reads the numbers and writes the story.
"""

from .models import AttributionResult, Interpretation


def build_prompt(result: AttributionResult) -> str:
    """Build the LLM prompt from attribution results.

    Placeholder — the LLM fills in the narrative at runtime.
    """
    top_contrib = sorted(
        result.contributions,
        key=lambda c: abs(c.percentage_contribution),
        reverse=True,
    )[:15]

    lines = [
        f"Measure: {result.target_measure}",
        f"Base: {result.base_value:,.2f}  →  Current: {result.current_value:,.2f}",
        f"Total change: {result.total_change:+,.2f}",
        f"Method: {result.method}",
        "",
        "Top contributors:",
    ]

    for c in top_contrib:
        lines.append(
            f"  {c.dimension}={c.dimension_value}: "
            f"{c.absolute_contribution:+,.2f} ({c.percentage_contribution:+.1f}%)"
        )

    prompt = (
        "You are a data analyst. Given the following attribution results, write a "
        "clear narrative interpretation.\n\n"
        + "\n".join(lines)
        + "\n\n"
        "Structure your response as:\n"
        "1. SUMMARY: One-paragraph overview\n"
        "2. PRIMARY DRIVERS: Bullet list of top drivers\n"
        "3. SECONDARY EFFECTS: Noteworthy smaller effects\n"
        "4. SURPRISES: Anything counterintuitive or unexpected\n"
        "5. CONFIDENCE: high / medium / low with rationale\n"
    )
    return prompt


def run(result: AttributionResult, llm_response: str) -> Interpretation:
    """Parse the LLM response into an Interpretation.

    Args:
        result: Attribution result from Stage 2
        llm_response: Raw LLM text response

    Returns:
        Structured Interpretation
    """
    interpretation = Interpretation()

    # Simple section parser — extracts content between headers.
    sections = _parse_sections(llm_response)

    interpretation.summary = sections.get("summary", "")
    interpretation.primary_drivers = _bullet_items(sections.get("primary_drivers", ""))
    interpretation.secondary_effects = _bullet_items(
        sections.get("secondary_effects", "")
    )
    interpretation.surprises = _bullet_items(sections.get("surprises", ""))
    interpretation.confidence = sections.get("confidence", "medium").strip().lower()
    interpretation.narrative = llm_response

    return interpretation


def _parse_sections(text: str) -> dict[str, str]:
    """Parse numbered/header sections from LLM output into a dict."""
    import re

    sections = {}
    current_key = None
    current_lines: list[str] = []

    section_pattern = re.compile(
        r"^\d+\.\s*(SUMMARY|PRIMARY DRIVERS|SECONDARY EFFECTS|SURPRISES|CONFIDENCE)",
        re.IGNORECASE,
    )

    for line in text.split("\n"):
        m = section_pattern.match(line.strip())
        if m:
            if current_key:
                sections[current_key] = "\n".join(current_lines).strip()
            current_key = m.group(1).lower().replace(" ", "_")
            current_lines = [line[m.end() :].strip()] if line[m.end() :].strip() else []
        elif current_key is not None:
            current_lines.append(line)

    if current_key and current_lines:
        sections[current_key] = "\n".join(current_lines).strip()

    return sections


def _bullet_items(text: str) -> list[str]:
    """Extract bullet-point items from text."""
    items = []
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith(("-", "*", "•")):
            items.append(stripped.lstrip("-*• ").strip())
        elif stripped and items:
            items[-1] += " " + stripped
    return items if items else [text.strip()] if text.strip() else []
