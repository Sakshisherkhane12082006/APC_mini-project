"""
data_analyzer.py
Automatic data type detection and quality analysis for universal CSV handling.
Detects numeric, categorical, date/time, and text columns, and provides data quality metrics.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Any


class ColumnType:
    """Enum-like class for column types."""
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    DATETIME = "datetime"
    TEXT = "text"


class DataAnalyzer:
    """Analyzes DataFrame structure and provides column type detection and quality metrics."""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.column_types = {}
        self._detect_column_types()
    
    def _detect_column_types(self):
        """Detect the type of each column in the DataFrame."""
        for col in self.df.columns:
            self.column_types[col] = self._detect_single_column_type(col)
    
    def _detect_single_column_type(self, col: str) -> str:
        """Detect the type of a single column."""
        series = self.df[col].dropna()
        
        if len(series) == 0:
            return ColumnType.TEXT
        
        # Try numeric first
        try:
            numeric_series = pd.to_numeric(series, errors='coerce')
            if numeric_series.notna().sum() / len(series) > 0.8:
                return ColumnType.NUMERIC
        except Exception:
            pass
        
        # Try datetime
        try:
            datetime_series = pd.to_datetime(series, errors='coerce', infer_datetime_format=True)
            if datetime_series.notna().sum() / len(series) > 0.8:
                return ColumnType.DATETIME
        except Exception:
            pass
        
        # Check if categorical (low cardinality)
        unique_ratio = series.nunique() / len(series)
        if unique_ratio < 0.5 or series.nunique() < 20:
            return ColumnType.CATEGORICAL
        
        return ColumnType.TEXT
    
    def get_columns_by_type(self, col_type: str) -> List[str]:
        """Get all columns of a specific type."""
        return [col for col, dtype in self.column_types.items() if dtype == col_type]
    
    def get_numeric_columns(self) -> List[str]:
        """Get all numeric columns."""
        return self.get_columns_by_type(ColumnType.NUMERIC)
    
    def get_categorical_columns(self) -> List[str]:
        """Get all categorical columns."""
        return self.get_columns_by_type(ColumnType.CATEGORICAL)
    
    def get_datetime_columns(self) -> List[str]:
        """Get all datetime columns."""
        return self.get_columns_by_type(ColumnType.DATETIME)
    
    def get_text_columns(self) -> List[str]:
        """Get all text columns."""
        return self.get_columns_by_type(ColumnType.TEXT)
    
    def get_all_columns(self) -> List[str]:
        """Get all column names."""
        return self.df.columns.tolist()
    
    def get_data_quality_metrics(self) -> Dict[str, Any]:
        """Calculate data quality metrics for the entire dataset."""
        metrics = {
            'total_rows': len(self.df),
            'total_columns': len(self.df.columns),
            'missing_values': self.df.isnull().sum().sum(),
            'missing_percentage': (self.df.isnull().sum().sum() / (len(self.df) * len(self.df.columns))) * 100,
            'duplicate_rows': self.df.duplicated().sum(),
            'duplicate_percentage': (self.df.duplicated().sum() / len(self.df)) * 100 if len(self.df) > 0 else 0,
            'numeric_columns': len(self.get_numeric_columns()),
            'categorical_columns': len(self.get_categorical_columns()),
            'datetime_columns': len(self.get_datetime_columns()),
            'text_columns': len(self.get_text_columns()),
        }
        
        # Column-specific missing values
        metrics['column_missing'] = {}
        for col in self.df.columns:
            missing_count = self.df[col].isnull().sum()
            metrics['column_missing'][col] = {
                'count': int(missing_count),
                'percentage': float((missing_count / len(self.df)) * 100) if len(self.df) > 0 else 0
            }
        
        return metrics
    
    def get_column_info(self, col: str) -> Dict[str, Any]:
        """Get detailed information about a specific column."""
        if col not in self.df.columns:
            return {}
        
        series = self.df[col]
        info = {
            'name': col,
            'type': self.column_types.get(col, 'unknown'),
            'missing_count': int(series.isnull().sum()),
            'missing_percentage': float((series.isnull().sum() / len(self.df)) * 100) if len(self.df) > 0 else 0,
            'unique_count': int(series.nunique()),
            'unique_percentage': float((series.nunique() / len(self.df)) * 100) if len(self.df) > 0 else 0,
        }
        
        # Type-specific information
        if info['type'] == ColumnType.NUMERIC:
            numeric_series = pd.to_numeric(series, errors='coerce').dropna()
            if len(numeric_series) > 0:
                info.update({
                    'min': float(numeric_series.min()),
                    'max': float(numeric_series.max()),
                    'mean': float(numeric_series.mean()),
                    'median': float(numeric_series.median()),
                    'std': float(numeric_series.std()) if len(numeric_series) > 1 else 0.0,
                })
        
        elif info['type'] == ColumnType.CATEGORICAL:
            value_counts = series.value_counts()
            if len(value_counts) > 0:
                info.update({
                    'most_common': str(value_counts.index[0]),
                    'most_common_count': int(value_counts.iloc[0]),
                    'categories': int(series.nunique()),
                })
        
        elif info['type'] == ColumnType.DATETIME:
            datetime_series = pd.to_datetime(series, errors='coerce').dropna()
            if len(datetime_series) > 0:
                info.update({
                    'min_date': str(datetime_series.min()),
                    'max_date': str(datetime_series.max()),
                    'date_range_days': int((datetime_series.max() - datetime_series.min()).days),
                })
        
        return info
    
    def get_all_columns_info(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed information for all columns."""
        return {col: self.get_column_info(col) for col in self.df.columns}
    
    def suggest_default_x_axis(self) -> str:
        """Suggest a default X-axis column based on data types."""
        # Prefer datetime columns
        datetime_cols = self.get_datetime_columns()
        if datetime_cols:
            return datetime_cols[0]
        
        # Then categorical columns
        categorical_cols = self.get_categorical_columns()
        if categorical_cols:
            return categorical_cols[0]
        
        # Fall back to first column
        if self.df.columns.size > 0:
            return self.df.columns[0]
        
        return None
    
    def suggest_default_y_axis(self) -> str:
        """Suggest a default Y-axis column based on data types."""
        numeric_cols = self.get_numeric_columns()
        if numeric_cols:
            return numeric_cols[0]
        
        return None
    
    def get_summary(self) -> str:
        """Get a human-readable summary of the dataset."""
        metrics = self.get_data_quality_metrics()
        
        lines = [
            f"Dataset Overview",
            f"-" * 40,
            f"Total Rows: {metrics['total_rows']:,}",
            f"Total Columns: {metrics['total_columns']}",
            f"Missing Values: {metrics['missing_values']:,} ({metrics['missing_percentage']:.1f}%)",
            f"Duplicate Rows: {metrics['duplicate_rows']:,} ({metrics['duplicate_percentage']:.1f}%)",
            f"",
            f"Column Types:",
            f"  Numeric: {metrics['numeric_columns']}",
            f"  Categorical: {metrics['categorical_columns']}",
            f"  DateTime: {metrics['datetime_columns']}",
            f"  Text: {metrics['text_columns']}",
        ]
        
        return "\n".join(lines)


def analyze_dataframe(df: pd.DataFrame) -> DataAnalyzer:
    """Convenience function to create a DataAnalyzer instance."""
    return DataAnalyzer(df)
