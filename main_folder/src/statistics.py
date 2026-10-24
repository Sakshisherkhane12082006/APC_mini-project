"""
statistics.py
Computes descriptive statistics for a loaded dataset: mean, median, mode,
min, max, standard deviation, quartiles, variance, skewness, and kurtosis,
for every numeric column, plus a helper to render everything as a formatted
summary string for the GUI / reports.
"""

import pandas as pd
import numpy as np
from scipy import stats


def compute_summary(df: pd.DataFrame) -> dict:
    """
    Compute descriptive statistics for every numeric column in df.

    Returns
    -------
    dict
        {column_name: {"mean": ..., "median": ..., "mode": ...,
                        "min": ..., "max": ..., "std": ..., "q1": ..., "q3": ...,
                        "variance": ..., "skewness": ..., "kurtosis": ...}}
    """
    if df is None or df.empty:
        return {}

    numeric_df = df.select_dtypes(include=[np.number])
    summary = {}

    for col in numeric_df.columns:
        series = numeric_df[col].dropna()
        if series.empty:
            continue

        mode_series = series.mode()
        mode_val = mode_series.iloc[0] if not mode_series.empty else float("nan")

        # Calculate quartiles
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        
        # Calculate additional statistics
        variance = series.var(ddof=1) if len(series) > 1 else 0.0
        skewness_val = stats.skew(series) if len(series) > 2 else 0.0
        kurtosis_val = stats.kurtosis(series) if len(series) > 3 else 0.0

        summary[col] = {
            "mean": round(float(series.mean()), 3),
            "median": round(float(series.median()), 3),
            "mode": round(float(mode_val), 3),
            "min": round(float(series.min()), 3),
            "max": round(float(series.max()), 3),
            "std": round(float(series.std(ddof=1)) if len(series) > 1 else 0.0, 3),
            "q1": round(float(q1), 3),
            "q3": round(float(q3), 3),
            "variance": round(float(variance), 3),
            "skewness": round(float(skewness_val), 3),
            "kurtosis": round(float(kurtosis_val), 3),
        }

    return summary


def compute_column_summary(df: pd.DataFrame, column: str) -> dict:
    """Compute stats for a single numeric column. Returns {} if invalid."""
    if df is None or column not in df.columns:
        return {}

    series = pd.to_numeric(df[column], errors="coerce").dropna()
    if series.empty:
        return {}

    mode_series = series.mode()
    mode_val = mode_series.iloc[0] if not mode_series.empty else float("nan")

    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    variance = series.var(ddof=1) if len(series) > 1 else 0.0
    skewness_val = stats.skew(series) if len(series) > 2 else 0.0
    kurtosis_val = stats.kurtosis(series) if len(series) > 3 else 0.0

    return {
        "mean": round(float(series.mean()), 3),
        "median": round(float(series.median()), 3),
        "mode": round(float(mode_val), 3),
        "min": round(float(series.min()), 3),
        "max": round(float(series.max()), 3),
        "std": round(float(series.std(ddof=1)) if len(series) > 1 else 0.0, 3),
        "q1": round(float(q1), 3),
        "q3": round(float(q3), 3),
        "variance": round(float(variance), 3),
        "skewness": round(float(skewness_val), 3),
        "kurtosis": round(float(kurtosis_val), 3),
    }


def format_summary_text(df: pd.DataFrame) -> str:
    """Render the full dataset summary as a human-readable string."""
    summary = compute_summary(df)
    if not summary:
        return "No numeric columns available to summarize."

    lines = []
    for col, stats in summary.items():
        lines.append(f"Column: {col}")
        lines.append(f"  Mean     : {stats['mean']}")
        lines.append(f"  Median   : {stats['median']}")
        lines.append(f"  Mode     : {stats['mode']}")
        lines.append(f"  Min      : {stats['min']}")
        lines.append(f"  Max      : {stats['max']}")
        lines.append(f"  Std      : {stats['std']}")
        lines.append(f"  Q1 (25%) : {stats['q1']}")
        lines.append(f"  Q3 (75%) : {stats['q3']}")
        lines.append(f"  Variance : {stats['variance']}")
        lines.append(f"  Skewness : {stats['skewness']}")
        lines.append(f"  Kurtosis : {stats['kurtosis']}")
        lines.append("")

    return "\n".join(lines)
