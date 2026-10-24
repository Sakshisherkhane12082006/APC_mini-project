"""
file_handler.py
Handles all disk I/O for the app:
- load_csv(): read a CSV into a DataFrame with error handling
- save_chart(): export the currently displayed matplotlib Figure as PNG
- generate_report(): write a text summary report (dataset info + stats)
"""

from datetime import datetime
import os
import pandas as pd
import chardet

from src import statistics as stats_module


def load_csv(path: str) -> tuple:
    """
    Load a CSV file into a DataFrame with encoding and delimiter detection.

    Returns
    -------
    (df, error) : tuple[pd.DataFrame | None, str | None]
        On success error is None. On failure df is None and error holds
        a human-readable message.
    """
    if not path:
        return None, "No file path provided."

    if not os.path.exists(path):
        return None, f"File not found: {path}"

    if not path.lower().endswith(".csv"):
        return None, "Please select a valid .csv file."

    try:
        # Detect encoding
        with open(path, 'rb') as f:
            raw_data = f.read(10000)  # Read first 10KB for encoding detection
            encoding_result = chardet.detect(raw_data)
            encoding = encoding_result['encoding'] or 'utf-8'
        
        # Try to load with detected encoding
        try:
            df = pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError:
            # Fallback to common encodings
            for enc in ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']:
                try:
                    df = pd.read_csv(path, encoding=enc)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                return None, "Could not decode file with common encodings."
        
        # Handle duplicate column names
        if df.columns.has_duplicates:
            df.columns = [f"{col}_{i}" if i > 0 else col 
                         for i, col in enumerate(df.columns)]
        
    except pd.errors.EmptyDataError:
        return None, "The selected CSV file is empty."
    except pd.errors.ParserError as e:
        return None, f"Could not parse CSV file: {e}"
    except Exception as e:  # noqa: BLE001 - surface any other IO issue to the user
        return None, f"Unexpected error while loading CSV: {e}"

    if df.empty:
        return None, "The CSV file contains no rows."

    return df, None


def save_chart(fig, output_path: str) -> tuple:
    """
    Save a matplotlib Figure to disk as PNG.

    Returns
    -------
    (success, message) : tuple[bool, str]
    """
    if fig is None:
        return False, "No chart is currently displayed to save."

    try:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
    except Exception as e:  # noqa: BLE001
        return False, f"Failed to save chart: {e}"

    return True, f"Chart saved to {output_path}"


def generate_report(df: pd.DataFrame, dataset_name: str, output_path: str) -> tuple:
    """
    Write a plain-text summary report covering dataset shape, columns,
    and descriptive statistics for numeric columns.

    Returns
    -------
    (success, message) : tuple[bool, str]
    """
    if df is None:
        return False, "No dataset is loaded, nothing to report."

    try:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        lines = []
        lines.append("=" * 60)
        lines.append("DATA VISUALIZATION DASHBOARD - SUMMARY REPORT")
        lines.append("=" * 60)
        lines.append(f"Generated  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Dataset    : {dataset_name}")
        lines.append(f"Rows       : {df.shape[0]}")
        lines.append(f"Columns    : {df.shape[1]}")
        lines.append(f"Column names: {', '.join(df.columns.astype(str))}")
        lines.append("-" * 60)
        lines.append("DESCRIPTIVE STATISTICS (numeric columns)")
        lines.append("-" * 60)
        lines.append(stats_module.format_summary_text(df))
        lines.append("=" * 60)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    except Exception as e:  # noqa: BLE001
        return False, f"Failed to generate report: {e}"

    return True, f"Report generated at {output_path}"


def export_data(df: pd.DataFrame, output_path: str) -> tuple:
    """
    Export the DataFrame as a CSV file.

    Returns
    -------
    (success, message) : tuple[bool, str]
    """
    if df is None or df.empty:
        return False, "No data to export."

    try:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        df.to_csv(output_path, index=False, encoding='utf-8')
    except Exception as e:  # noqa: BLE001
        return False, f"Failed to export data: {e}"

    return True, f"Data exported to {output_path}"
