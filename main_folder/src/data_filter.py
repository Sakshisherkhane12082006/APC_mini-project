"""
data_filter.py
Interactive data filtering functionality.
Allows users to filter data by column values, ranges, and conditions.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class DataFilter:
    """Manages filtering operations on a DataFrame."""
    
    def __init__(self, df: pd.DataFrame):
        self.original_df = df.copy()
        self.filtered_df = df.copy()
        self.active_filters = []
    
    def reset_filters(self):
        """Reset all filters and restore original data."""
        self.filtered_df = self.original_df.copy()
        self.active_filters = []
    
    def apply_filter(self, column: str, operation: str, value: Any) -> bool:
        """Apply a single filter to the data.
        
        Parameters
        ----------
        column : str
            Column name to filter on
        operation : str
            Filter operation: 'equals', 'not_equals', 'greater_than', 'less_than',
            'contains', 'starts_with', 'ends_with', 'is_null', 'is_not_null'
        value : Any
            Value to compare against
        
        Returns
        -------
        bool
            True if filter was applied successfully
        """
        if column not in self.filtered_df.columns:
            return False
        
        try:
            if operation == 'equals':
                mask = self.filtered_df[column] == value
            elif operation == 'not_equals':
                mask = self.filtered_df[column] != value
            elif operation == 'greater_than':
                mask = pd.to_numeric(self.filtered_df[column], errors='coerce') > value
            elif operation == 'less_than':
                mask = pd.to_numeric(self.filtered_df[column], errors='coerce') < value
            elif operation == 'contains':
                mask = self.filtered_df[column].astype(str).str.contains(str(value), case=False, na=False)
            elif operation == 'starts_with':
                mask = self.filtered_df[column].astype(str).str.startswith(str(value), na=False)
            elif operation == 'ends_with':
                mask = self.filtered_df[column].astype(str).str.endswith(str(value), na=False)
            elif operation == 'is_null':
                mask = self.filtered_df[column].isnull()
            elif operation == 'is_not_null':
                mask = self.filtered_df[column].notnull()
            else:
                return False
            
            self.filtered_df = self.filtered_df[mask]
            self.active_filters.append({
                'column': column,
                'operation': operation,
                'value': value
            })
            return True
            
        except Exception:
            return False
    
    def apply_range_filter(self, column: str, min_value: Any, max_value: Any) -> bool:
        """Apply a range filter to a numeric column."""
        if column not in self.filtered_df.columns:
            return False
        
        try:
            numeric_series = pd.to_numeric(self.filtered_df[column], errors='coerce')
            mask = (numeric_series >= min_value) & (numeric_series <= max_value)
            self.filtered_df = self.filtered_df[mask]
            self.active_filters.append({
                'column': column,
                'operation': 'range',
                'value': f"{min_value} - {max_value}"
            })
            return True
        except Exception:
            return False
    
    def apply_date_range_filter(self, column: str, start_date: str, end_date: str) -> bool:
        """Apply a date range filter to a datetime column."""
        if column not in self.filtered_df.columns:
            return False
        
        try:
            datetime_series = pd.to_datetime(self.filtered_df[column], errors='coerce')
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            mask = (datetime_series >= start_dt) & (datetime_series <= end_dt)
            self.filtered_df = self.filtered_df[mask]
            self.active_filters.append({
                'column': column,
                'operation': 'date_range',
                'value': f"{start_date} - {end_date}"
            })
            return True
        except Exception:
            return False
    
    def apply_categorical_filter(self, column: str, selected_values: List[Any]) -> bool:
        """Filter a categorical column to only include selected values."""
        if column not in self.filtered_df.columns:
            return False
        
        try:
            mask = self.filtered_df[column].isin(selected_values)
            self.filtered_df = self.filtered_df[mask]
            self.active_filters.append({
                'column': column,
                'operation': 'in_list',
                'value': f"{len(selected_values)} values"
            })
            return True
        except Exception:
            return False
    
    def get_filtered_data(self) -> pd.DataFrame:
        """Get the currently filtered DataFrame."""
        return self.filtered_df
    
    def get_original_data(self) -> pd.DataFrame:
        """Get the original unfiltered DataFrame."""
        return self.original_df
    
    def get_filter_summary(self) -> str:
        """Get a summary of active filters."""
        if not self.active_filters:
            return "No filters applied"
        
        lines = ["Active Filters:"]
        for i, f in enumerate(self.active_filters, 1):
            lines.append(f"{i}. {f['column']} {f['operation']} {f['value']}")
        
        lines.append(f"\nRows: {len(self.original_df)} → {len(self.filtered_df)}")
        return "\n".join(lines)
    
    def get_filter_count(self) -> int:
        """Get the number of active filters."""
        return len(self.active_filters)
    
    def has_filters(self) -> bool:
        """Check if any filters are active."""
        return len(self.active_filters) > 0


def create_filter(df: pd.DataFrame) -> DataFilter:
    """Convenience function to create a DataFilter instance."""
    return DataFilter(df)
