"""
auto_charts.py
Automatic chart selection and recommendation based on data types and characteristics.
Suggests appropriate visualizations for different column combinations.
"""

import pandas as pd
from typing import List, Dict, Any, Tuple
from src.data_analyzer import DataAnalyzer, ColumnType


class ChartRecommendation:
    """Represents a recommended chart configuration."""
    
    def __init__(self, chart_type: str, x_col: str, y_col: str = None, 
                 group_col: str = None, title: str = "", reason: str = ""):
        self.chart_type = chart_type
        self.x_col = x_col
        self.y_col = y_col
        self.group_col = group_col
        self.title = title
        self.reason = reason
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for easy serialization."""
        return {
            'chart_type': self.chart_type,
            'x_col': self.x_col,
            'y_col': self.y_col,
            'group_col': self.group_col,
            'title': self.title,
            'reason': self.reason
        }


class AutoChartSelector:
    """Automatically selects appropriate charts based on data types."""
    
    def __init__(self, analyzer: DataAnalyzer):
        self.analyzer = analyzer
        self.recommendations = []
    
    def generate_recommendations(self, max_recommendations: int = 10) -> List[ChartRecommendation]:
        """Generate chart recommendations based on data characteristics."""
        self.recommendations = []
        
        numeric_cols = self.analyzer.get_numeric_columns()
        categorical_cols = self.analyzer.get_categorical_columns()
        datetime_cols = self.analyzer.get_datetime_columns()
        
        # Strategy 1: Time series (datetime + numeric)
        if datetime_cols and numeric_cols:
            self._recommend_time_series(datetime_cols, numeric_cols)
        
        # Strategy 2: Distribution (single numeric)
        if numeric_cols:
            self._recommend_distributions(numeric_cols)
        
        # Strategy 3: Categorical breakdown (categorical + numeric)
        if categorical_cols and numeric_cols:
            self._recommend_categorical_breakdown(categorical_cols, numeric_cols)
        
        # Strategy 4: Correlation (numeric + numeric)
        if len(numeric_cols) >= 2:
            self._recommend_correlations(numeric_cols)
        
        # Strategy 5: Categorical frequency (single categorical)
        if categorical_cols:
            self._recommend_categorical_frequency(categorical_cols)
        
        # Strategy 6: Correlation heatmap (multiple numeric)
        if len(numeric_cols) >= 3:
            self._recommend_correlation_heatmap(numeric_cols)
        
        return self.recommendations[:max_recommendations]
    
    def _recommend_time_series(self, datetime_cols: List[str], numeric_cols: List[str]):
        """Recommend line charts for time series data."""
        for dt_col in datetime_cols[:2]:  # Limit to 2 datetime columns
            for num_col in numeric_cols[:3]:  # Limit to 3 numeric columns
                self.recommendations.append(ChartRecommendation(
                    chart_type='line',
                    x_col=dt_col,
                    y_col=num_col,
                    title=f"{num_col} over Time",
                    reason=f"Line chart shows {num_col} trends over {dt_col}"
                ))
    
    def _recommend_distributions(self, numeric_cols: List[str]):
        """Recommend histograms and box plots for numeric distributions."""
        for col in numeric_cols[:5]:  # Limit to 5 numeric columns
            # Histogram
            self.recommendations.append(ChartRecommendation(
                chart_type='histogram',
                x_col=col,
                title=f"Distribution of {col}",
                reason=f"Histogram shows the distribution of {col}"
            ))
            
            # Box plot
            self.recommendations.append(ChartRecommendation(
                chart_type='box',
                x_col=col,
                title=f"Box Plot of {col}",
                reason=f"Box plot shows spread and outliers in {col}"
            ))
    
    def _recommend_categorical_breakdown(self, categorical_cols: List[str], 
                                        numeric_cols: List[str]):
        """Recommend bar charts for categorical vs numeric data."""
        for cat_col in categorical_cols[:3]:  # Limit to 3 categorical columns
            for num_col in numeric_cols[:3]:  # Limit to 3 numeric columns
                # Check cardinality
                col_info = self.analyzer.get_column_info(cat_col)
                if col_info['unique_count'] <= 15:
                    # Bar chart
                    self.recommendations.append(ChartRecommendation(
                        chart_type='bar',
                        x_col=cat_col,
                        y_col=num_col,
                        title=f"{num_col} by {cat_col}",
                        reason=f"Bar chart compares {num_col} across {cat_col}"
                    ))
                    
                    # Pie/donut chart (only for low cardinality)
                    if col_info['unique_count'] <= 8:
                        self.recommendations.append(ChartRecommendation(
                            chart_type='pie',
                            x_col=cat_col,
                            y_col=num_col,
                            title=f"{num_col} Share by {cat_col}",
                            reason=f"Pie chart shows {num_col} distribution by {cat_col}"
                        ))
    
    def _recommend_correlations(self, numeric_cols: List[str]):
        """Recommend scatter plots for numeric correlations."""
        for i, col1 in enumerate(numeric_cols[:4]):  # Limit to 4 numeric columns
            for col2 in numeric_cols[i+1:i+4]:  # Avoid duplicates
                self.recommendations.append(ChartRecommendation(
                    chart_type='scatter',
                    x_col=col1,
                    y_col=col2,
                    title=f"{col2} vs {col1}",
                    reason=f"Scatter plot shows relationship between {col1} and {col2}"
                ))
    
    def _recommend_categorical_frequency(self, categorical_cols: List[str]):
        """Recommend bar/pie charts for categorical frequency."""
        for col in categorical_cols[:3]:  # Limit to 3 categorical columns
            col_info = self.analyzer.get_column_info(col)
            
            if col_info['unique_count'] <= 15:
                self.recommendations.append(ChartRecommendation(
                    chart_type='bar',
                    x_col=col,
                    title=f"Frequency of {col}",
                    reason=f"Bar chart shows frequency of categories in {col}"
                ))
                
                if col_info['unique_count'] <= 8:
                    self.recommendations.append(ChartRecommendation(
                        chart_type='pie',
                        x_col=col,
                        title=f"{col} Distribution",
                        reason=f"Pie chart shows distribution of {col}"
                    ))
    
    def _recommend_correlation_heatmap(self, numeric_cols: List[str]):
        """Recommend correlation heatmap for multiple numeric columns."""
        self.recommendations.append(ChartRecommendation(
            chart_type='heatmap',
            x_col=', '.join(numeric_cols),
            title="Correlation Heatmap",
            reason="Heatmap shows correlations between all numeric columns"
        ))
    
    def get_best_recommendation(self) -> ChartRecommendation:
        """Get the single best chart recommendation."""
        if not self.recommendations:
            self.generate_recommendations()
        
        if not self.recommendations:
            return None
        
        # Prioritize: time series > correlation > distribution > categorical
        priority_order = ['line', 'scatter', 'histogram', 'bar', 'pie', 'box', 'heatmap']
        
        for chart_type in priority_order:
            for rec in self.recommendations:
                if rec.chart_type == chart_type:
                    return rec
        
        return self.recommendations[0]
    
    def get_recommendations_summary(self) -> str:
        """Get a human-readable summary of recommendations."""
        if not self.recommendations:
            self.generate_recommendations()
        
        if not self.recommendations:
            return "No chart recommendations available."
        
        lines = ["Recommended Charts", "=" * 40]
        
        for i, rec in enumerate(self.recommendations[:8], 1):
            lines.append(f"{i}. {rec.chart_type.upper()}: {rec.title}")
            lines.append(f"   {rec.reason}")
        
        if len(self.recommendations) > 8:
            lines.append(f"\n... and {len(self.recommendations) - 8} more recommendations")
        
        return "\n".join(lines)


def get_chart_recommendations(analyzer: DataAnalyzer, max_recommendations: int = 10) -> List[ChartRecommendation]:
    """Convenience function to get chart recommendations."""
    selector = AutoChartSelector(analyzer)
    return selector.generate_recommendations(max_recommendations)
