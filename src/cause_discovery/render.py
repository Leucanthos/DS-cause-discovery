"""Stage 4 — HTML Report Generation (script).

Generates a self-contained HTML report with:
- Data summary table
- Contribution bar chart (Plotly or Vega-Lite via CDN)
- Narrative text from the LLM interpretation
"""

from __future__ import annotations

from .models import AttributionResult, DataProfile, Interpretation

import json
import webbrowser
from pathlib import Path


_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cause Discovery Report</title>
<script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
<style>
  :root {{
    --bg: #fafbfc;
    --card-bg: #fff;
    --text: #1a1a2e;
    --muted: #6b7280;
    --border: #e5e7eb;
    --accent: #2563eb;
    --positive: #059669;
    --negative: #dc2626;
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    padding: 2rem;
  }}
  .container {{ max-width: 960px; margin: 0 auto; }}
  h1 {{ font-size: 1.75rem; margin-bottom: .25rem; }}
  h2 {{ font-size: 1.25rem; margin: 1.5rem 0 .5rem; border-bottom: 1px solid var(--border); padding-bottom: .25rem; }}
  .meta {{ color: var(--muted); font-size: .875rem; margin-bottom: 1.5rem; }}
  .card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 2px rgba(0,0,0,.04);
  }}
  .kpi-row {{ display:flex; gap: 1rem; flex-wrap:wrap; }}
  .kpi {{
    flex: 1; min-width: 140px;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
  }}
  .kpi-label {{ font-size: .75rem; color: var(--muted); text-transform: uppercase; }}
  .kpi-value {{ font-size: 1.5rem; font-weight: 700; }}
  .kpi-value.pos {{ color: var(--positive); }}
  .kpi-value.neg {{ color: var(--negative); }}
  .contributors {{ width:100%; border-collapse:collapse; font-size:.875rem; }}
  .contributors th, .contributors td {{ padding: .5rem .75rem; text-align:left; border-bottom: 1px solid var(--border); }}
  .contributors th {{ color: var(--muted); font-weight:600; }}
  .contributors .pos {{ color: var(--positive); font-weight:600; }}
  .contributors .neg {{ color: var(--negative); font-weight:600; }}
  #chart {{ width: 100%; height: 400px; }}
  .narrative {{ white-space: pre-wrap; }}
  .section-label {{ font-weight:600; margin-top:.75rem; }}
</style>
</head>
<body>
<div class="container">
  <h1>Cause Discovery Report</h1>
  <p class="meta">Generated: {generated_at} &middot; Method: {method}</p>

  <h2>Overview</h2>
  <div class="kpi-row">
    {kpi_cards}
  </div>

  <h2>Top Contributors</h2>
  <div class="card">
    <table class="contributors">
      <thead><tr><th>Dimension</th><th>Value</th><th>Change</th><th>%</th></tr></thead>
      <tbody>{contributor_rows}</tbody>
    </table>
  </div>

  <h2>Contribution Chart</h2>
  <div class="card"><div id="chart"></div></div>

  <h2>Narrative</h2>
  <div class="card narrative">{narrative_html}</div>
</div>
<script>
  const spec = {vega_spec};
  vegaEmbed('#chart', spec, {{actions:false}}).catch(console.error);
</script>
</body>
</html>"""


def render(
    profile: DataProfile,
    attribution: AttributionResult,
    interpretation: Interpretation,
    output_path: str = "report.html",
) -> str:
    """Generate a self-contained HTML report.

    Args:
        profile: DataProfile from Stage 1
        attribution: AttributionResult from Stage 2
        interpretation: Interpretation from Stage 3
        output_path: File path for the output HTML

    Returns:
        Absolute path to the generated HTML file.
    """
    top_n = sorted(
        attribution.contributions,
        key=lambda c: abs(c.percentage_contribution),
        reverse=True,
    )[:15]

    # KPI cards
    change_class = "pos" if attribution.total_change >= 0 else "neg"
    change_sign = "+" if attribution.total_change >= 0 else ""
    kpi_cards = f"""
    <div class="kpi"><div class="kpi-label">Base</div><div class="kpi-value">{attribution.base_value:,.2f}</div></div>
    <div class="kpi"><div class="kpi-label">Current</div><div class="kpi-value">{attribution.current_value:,.2f}</div></div>
    <div class="kpi"><div class="kpi-label">Change</div><div class="kpi-value {change_class}">{change_sign}{attribution.total_change:,.2f}</div></div>
    """  # noqa: E501

    # Contributor table rows
    rows = ""
    for c in top_n:
        cls = "pos" if c.absolute_contribution >= 0 else "neg"
        sign = "+" if c.absolute_contribution >= 0 else ""
        rows += (
            f'<tr><td>{c.dimension}</td><td>{c.dimension_value}</td>'
            f'<td class="{cls}">{sign}{c.absolute_contribution:,.2f}</td>'
            f'<td class="{cls}">{sign}{c.percentage_contribution:.1f}%</td></tr>\n'
        )

    # Vega-Lite bar chart spec
    chart_data = [
        {
            "dim_val": f"{c.dimension}={c.dimension_value}",
            "contribution": c.absolute_contribution,
            "pct": c.percentage_contribution,
        }
        for c in top_n
    ]
    vega_spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "data": {"values": chart_data},
        "mark": "bar",
        "encoding": {
            "x": {"field": "contribution", "type": "quantitative", "title": "Contribution"},
            "y": {
                "field": "dim_val",
                "type": "nominal",
                "title": "",
                "sort": "-x",
            },
            "color": {
                "field": "contribution",
                "type": "quantitative",
                "scale": {"scheme": "redblue", "domainMid": 0},
                "legend": None,
            },
            "tooltip": [
                {"field": "dim_val", "title": "Dimension=Value"},
                {"field": "contribution", "title": "Change", "format": ",.2f"},
                {"field": "pct", "title": "%", "format": ".1f"},
            ],
        },
    }

    # Narrative
    narrative_parts = []
    if interpretation.summary:
        narrative_parts.append(f"<p><strong>Summary:</strong> {interpretation.summary}</p>")
    if interpretation.primary_drivers:
        drivers = "".join(f"<li>{d}</li>" for d in interpretation.primary_drivers)
        narrative_parts.append(
            f'<p class="section-label">Primary Drivers</p><ul>{drivers}</ul>'
        )
    if interpretation.secondary_effects:
        effects = "".join(f"<li>{e}</li>" for e in interpretation.secondary_effects)
        narrative_parts.append(
            f'<p class="section-label">Secondary Effects</p><ul>{effects}</ul>'
        )
    if interpretation.surprises:
        surprises = "".join(f"<li>{s}</li>" for s in interpretation.surprises)
        narrative_parts.append(
            f'<p class="section-label">Surprises</p><ul>{surprises}</ul>'
        )
    if interpretation.confidence:
        narrative_parts.append(
            f'<p><strong>Confidence:</strong> {interpretation.confidence}</p>'
        )
    narrative_html = "\n".join(narrative_parts)

    from datetime import datetime

    html = _HTML_TEMPLATE.format(
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        method=attribution.method,
        kpi_cards=kpi_cards,
        contributor_rows=rows,
        vega_spec=json.dumps(vega_spec, ensure_ascii=False),
        narrative_html=narrative_html,
    )

    out_path = Path(output_path).resolve()
    out_path.write_text(html, encoding="utf-8")
    return str(out_path)


def open_report(path: str) -> None:
    """Open the HTML report in the default browser."""
    webbrowser.open(f"file://{path}")
