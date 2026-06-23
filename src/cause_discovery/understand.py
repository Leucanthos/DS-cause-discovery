"""Stage 1 — Read & Understand Data (LLM-driven, script-assisted).

Reads tabular data via pandas, profiles it, then uses LLM reasoning to
classify columns and determine aggregation semantics.
"""

from .models import ColumnProfile, DataProfile

import pandas as pd


def read_data(path: str, **kwargs) -> pd.DataFrame:
    """Read tabular data from path. Infers format from extension.

    Supports: .csv, .xlsx, .parquet, .json
    """
    if path.endswith(".csv"):
        return pd.read_csv(path, **kwargs)
    elif path.endswith((".xlsx", ".xls")):
        return pd.read_excel(path, **kwargs)
    elif path.endswith(".parquet"):
        return pd.read_parquet(path, **kwargs)
    elif path.endswith(".json"):
        return pd.read_json(path, **kwargs)
    else:
        raise ValueError(f"Unsupported file format: {path}")


def profile_dataframe(df: pd.DataFrame) -> DataProfile:
    """Generate column-level profiles for a DataFrame."""
    columns = []
    for col_name in df.columns:
        series = df[col_name]
        null_count = int(series.isna().sum())
        cp = ColumnProfile(
            name=str(col_name),
            dtype=str(series.dtype),
            null_count=null_count,
            null_pct=round(null_count / len(series) * 100, 2) if len(series) > 0 else 0,
            unique_count=int(series.nunique()),
            sample_values=series.dropna().head(5).tolist(),
        )
        columns.append(cp)

    return DataProfile(
        df=df,
        columns=columns,
        row_count=len(df),
    )


def llm_classify_columns(profile: DataProfile) -> str:
    """Generate a prompt for LLM to classify columns.

    Returns the prompt text; the LLM response sets profile.dimensions,
    profile.measures, and per-column .role / .additive.

    Placeholder — to be filled by LLM at runtime.
    """
    col_summary = []
    for c in profile.columns:
        col_summary.append(
            f"  - {c.name}: dtype={c.dtype}, unique={c.unique_count}, "
            f"null%={c.null_pct}, samples={c.sample_values}"
        )

    prompt = f"""Given this DataFrame profile ({profile.row_count} rows):

Columns:
{chr(10).join(col_summary)}

Classify each column as:
- "dimension": categorical / grouping column (e.g., region, product, date)
- "measure": numeric column that can be aggregated (e.g., revenue, count)
- "ignore": metadata, IDs, or unusable columns

For each measure, determine if it's additive (safe to sum along any dimension split).

Return your classification as a structured response.
"""
    return prompt


def run(path: str) -> DataProfile:
    """Run Stage 1 — read, profile, and prepare for classification.

    Args:
        path: Path to data file (.csv, .xlsx, .parquet, .json)

    Returns:
        DataProfile with loaded DataFrame and column profiles.
    """
    df = read_data(path)
    profile = profile_dataframe(df)
    return profile
