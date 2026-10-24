"""
insights.py
Automatic insights generation from data analysis.
Identifies patterns, outliers, correlations, and key statistics.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from scipy import stats


class InsightsGenerator:
    """Generates explainable insights from a DataFrame."""
    
    def __init__(self, df: pd.DataFrame, analyzer):
        self.df = df
        self.analyzer = analyzer
        self.insights = []
    
    def generate_all_insights(self) -> List[Dict[str, Any]]:
        """Generate all possible insights from the dataset."""
        self.insights = []
        
        self._numeric_insights()
        self._categorical_insights()
        self._correlation_insights()
        self._outlier_insights()
        self._datetime_insights()
        self._data_quality_insights()
        
        return self.insights
    
    def _numeric_insights(self):
        """Generate insights for numeric columns."""
        numeric_cols = self.analyzer.get_numeric_columns()
        
        for col in numeric_cols:
            series = pd.to_numeric(self.df[col], errors='coerce').dropna()
            if len(series) == 0:
                continue
            
            col_info = self.analyzer.get_column_info(col)
            
            # Highest and lowest values
            self.insights.append({
                'type': 'numeric_extremes',
                'column': col,
                'message': f"Column '{col}' ranges from {col_info['min']:.2f} to {col_info['max']:.2f}",
                'severity': 'info'
            })
            
            # Distribution insight
            skewness = stats.skew(series) if len(series) > 2 else 0
            if abs(skewness) > 1:
                direction = "right-skewed" if skewness > 0 else "left-skewed"
                self.insights.append({
                    'type': 'distribution',
                    'column': col,
                    'message': f"Column '{col}' is {direction} (skewness: {skewness:.2f})",
                    'severity': 'info'
                })
    
    def _categorical_insights(self):
        """Generate insights for categorical columns."""
        categorical_cols = self.analyzer.get_categorical_columns()
        
        for col in categorical_cols:
            series = self.df[col].dropna()
            if len(series) == 0:
                continue
            
            col_info = self.analyzer.get_column_info(col)
            
            # Most frequent category
            self.insights.append({
                'type': 'categorical_mode',
                'column': col,
                'message': f"Most common value in '{col}': '{col_info['most_common']}' ({col_info['most_common_count']} occurrences)",
                'severity': 'info'
            })
            
            # High cardinality warning
            if col_info['unique_percentage'] > 50:
                self.insights.append({
                    'type': 'high_cardinality',
                    'column': col,
                    'message': f"Column '{col}' has high cardinality ({col_info['categories']} unique values)",
                    'severity': 'warning'
                })
    
    def _correlation_insights(self):
        """Generate insights about correlations between numeric columns."""
        numeric_cols = self.analyzer.get_numeric_columns()
        
        if len(numeric_cols) < 2:
            return
        
        # Calculate correlation matrix
        numeric_df = self.df[numeric_cols].apply(pd.to_numeric, errors='coerce')
        corr_matrix = numeric_df.corr()
        
        # Find strong correlations
        strong_correlations = []
        for i, col1 in enumerate(numeric_cols):
            for j, col2 in enumerate(numeric_cols):
                if i < j:  # Avoid duplicates and self-correlation
                    corr_value = corr_matrix.loc[col1, col2]
                    if not pd.isna(corr_value) and abs(corr_value) > 0.7:
                        strong_correlations.append((col1, col2, corr_value))
        
        for col1, col2, corr_value in strong_correlations:
            direction = "positive" if corr_value > 0 else "negative"
            self.insights.append({
                'type': 'correlation',
                'columns': [col1, col2],
                'message': f"Strong {direction} correlation ({corr_value:.2f}) between '{col1}' and '{col2}'",
                'severity': 'info',
                'correlation_value': corr_value
            })
    
    def _outlier_insights(self):
        """Identify potential outliers in numeric columns."""
        numeric_cols = self.analyzer.get_numeric_columns()
        
        for col in numeric_cols:
            series = pd.to_numeric(self.df[col], errors='coerce').dropna()
            if len(series) < 4:
                continue
            
            # Use IQR method for outlier detection
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = series[(series < lower_bound) | (series > upper_bound)]
            outlier_count = len(outliers)
            outlier_percentage = (outlier_count / len(series)) * 100
            
            if outlier_count > 0:
                self.insights.append({
                    'type': 'outliers',
                    'column': col,
                    'message': f"Column '{col}' has {outlier_count} potential outliers ({outlier_percentage:.1f}%)",
                    'severity': 'warning' if outlier_percentage > 5 else 'info'
                })
    
    def _datetime_insights(self):
        """Generate insights for datetime columns."""
        datetime_cols = self.analyzer.get_datetime_columns()
        
        for col in datetime_cols:
            col_info = self.analyzer.get_column_info(col)
            
            if 'date_range_days' in col_info:
                self.insights.append({
                    'type': 'date_range',
                    'column': col,
                    'message': f"Column '{col}' spans {col_info['date_range_days']} days",
                    'severity': 'info'
                })
    
    def _data_quality_insights(self):
        """Generate insights about data quality."""
        metrics = self.analyzer.get_data_quality_metrics()
        
        # Missing values warning
        if metrics['missing_percentage'] > 10:
            self.insights.append({
                'type': 'missing_values',
                'message': f"Dataset has {metrics['missing_percentage']:.1f}% missing values",
                'severity': 'warning'
            })
        
        # Duplicate rows warning
        if metrics['duplicate_percentage'] > 5:
            self.insights.append({
                'type': 'duplicate_rows',
                'message': f"Dataset has {metrics['duplicate_percentage']:.1f}% duplicate rows",
                'severity': 'warning'
            })
        
        # Column-specific missing value warnings
        for col, missing_info in metrics['column_missing'].items():
            if missing_info['percentage'] > 20:
                self.insights.append({
                    'type': 'column_missing',
                    'column': col,
                    'message': f"Column '{col}' has {missing_info['percentage']:.1f}% missing values",
                    'severity': 'warning'
                })
    
    def get_insights_summary(self) -> str:
        """Get a human-readable summary of insights."""
        if not self.insights:
            return "No insights generated."
        
        lines = ["Key Insights", "=" * 40]
        
        # Group by severity
        warnings = [i for i in self.insights if i['severity'] == 'warning']
        info = [i for i in self.insights if i['severity'] == 'info']
        
        if warnings:
            lines.append("\nWarnings:")
            for insight in warnings[:5]:  # Limit to 5 warnings
                lines.append(f"  • {insight['message']}")
        
        if info:
            lines.append("\nFindings:")
            for insight in info[:10]:  # Limit to 10 info items
                lines.append(f"  • {insight['message']}")
        
        if len(self.insights) > 15:
            lines.append(f"\n... and {len(self.insights) - 15} more insights")
        
        return "\n".join(lines)


def generate_insights(df: pd.DataFrame, analyzer) -> InsightsGenerator:
    """Convenience function to create an InsightsGenerator instance."""
    generator = InsightsGenerator(df, analyzer)
    generator.generate_all_insights()
    return generator
