"""
charts.py
All plotting logic lives here, isolated from the GUI. Every function takes
a pandas DataFrame plus a ChartStyle and returns a matplotlib Figure, which
gui.py then embeds into the Tkinter canvas. Keeping figure construction
separate from rendering makes these functions independently testable and
reusable (e.g. for save_chart / report generation).
"""

import matplotlib
matplotlib.use("Agg")  # safe default backend; gui.py swaps in TkAgg when embedding

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns


def _apply_grid(ax, style):
    if style.grid:
        ax.grid(True, linestyle="--", alpha=0.5)
    else:
        ax.grid(False)


def line_chart(df: pd.DataFrame, x_col: str, y_col: str, style) -> plt.Figure:
    """Line chart of y_col over x_col."""
    fig, ax = plt.subplots(figsize=(6, 4.2), dpi=100)
    style_kwargs = style.as_dict()
    # Sort by x-axis column to ensure proper line ordering
    df_sorted = df.sort_values(by=x_col)
    ax.plot(
        df_sorted[x_col],
        df_sorted[y_col],
        color=style_kwargs["color"],
        marker="none",
        linestyle=style_kwargs["linestyle"],
        linewidth=2.0,
    )
    ax.set_title(f"Line Chart: {y_col} vs {x_col}")
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    _apply_grid(ax, style)
    fig.tight_layout()
    return fig


def bar_chart(df: pd.DataFrame, x_col: str, y_col: str, style) -> plt.Figure:
    """Bar chart of y_col grouped/aggregated by x_col."""
    fig, ax = plt.subplots(figsize=(6, 4.2), dpi=100)

    grouped = df.groupby(x_col)[y_col].mean().reset_index()
    # Cap the number of bars shown so wide categorical columns stay readable.
    if len(grouped) > 25:
        grouped = grouped.iloc[:25]

    ax.bar(grouped[x_col].astype(str), grouped[y_col], color=style.color)
    ax.set_title(f"Bar Chart: {y_col} by {x_col}")
    ax.set_xlabel(x_col)
    ax.set_ylabel(f"Mean {y_col}")
    ax.tick_params(axis="x", rotation=45)
    _apply_grid(ax, style)
    fig.tight_layout()
    return fig


def pie_chart(df: pd.DataFrame, category_col: str, value_col: str, style) -> plt.Figure:
    """Pie chart of value_col totals broken down by category_col."""
    fig, ax = plt.subplots(figsize=(5.5, 5.5), dpi=100)

    grouped = df.groupby(category_col)[value_col].sum()
    # Too many slices makes a pie chart unreadable; keep the top 8 and
    # roll the remainder into "Other".
    if len(grouped) > 8:
        grouped = grouped.sort_values(ascending=False)
        top = grouped.iloc[:8]
        other = grouped.iloc[8:].sum()
        top["Other"] = other
        grouped = top

    ax.pie(
        grouped.values,
        labels=[str(i) for i in grouped.index],
        autopct="%1.1f%%",
        startangle=90,
    )
    ax.set_title(f"Pie Chart: {value_col} share by {category_col}")
    ax.axis("equal")
    fig.tight_layout()
    return fig


def histogram(df: pd.DataFrame, col: str, style, bins: int = 20) -> plt.Figure:
    """Histogram showing the distribution of a numeric column."""
    fig, ax = plt.subplots(figsize=(6, 4.2), dpi=100)
    ax.hist(df[col].dropna(), bins=bins, color=style.color, edgecolor="black", alpha=0.8)
    ax.set_title(f"Histogram: {col}")
    ax.set_xlabel(col)
    ax.set_ylabel("Frequency")
    _apply_grid(ax, style)
    fig.tight_layout()
    return fig


def scatter_plot(df: pd.DataFrame, x_col: str, y_col: str, style) -> plt.Figure:
    """Scatter plot of y_col vs x_col."""
    fig, ax = plt.subplots(figsize=(6, 4.2), dpi=100)
    marker = style.as_dict()["marker"] or "o"
    ax.scatter(df[x_col], df[y_col], color=style.color, marker=marker, alpha=0.75)
    ax.set_title(f"Scatter Plot: {y_col} vs {x_col}")
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    _apply_grid(ax, style)
    fig.tight_layout()
    return fig


def box_plot(df: pd.DataFrame, col: str, style) -> plt.Figure:
    """Box plot showing distribution and outliers of a numeric column."""
    fig, ax = plt.subplots(figsize=(6, 4.2), dpi=100)
    numeric_series = pd.to_numeric(df[col], errors='coerce').dropna()
    ax.boxplot(numeric_series, patch_artist=True, 
               boxprops=dict(facecolor=style.color, alpha=0.7),
               medianprops=dict(color='white', linewidth=2))
    ax.set_title(f"Box Plot: {col}")
    ax.set_ylabel(col)
    ax.set_xticks([])
    _apply_grid(ax, style)
    fig.tight_layout()
    return fig


def correlation_heatmap(df: pd.DataFrame, style) -> plt.Figure:
    """Correlation heatmap for all numeric columns."""
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.empty or len(numeric_df.columns) < 2:
        # Return empty figure if not enough numeric columns
        fig, ax = plt.subplots(figsize=(6, 4.2), dpi=100)
        ax.text(0.5, 0.5, "Need at least 2 numeric columns", 
                ha='center', va='center', transform=ax.transAxes)
        ax.set_title("Correlation Heatmap")
        return fig
    
    fig, ax = plt.subplots(figsize=(7, 5), dpi=100)
    corr_matrix = numeric_df.corr()
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                center=0, square=True, ax=ax, cbar_kws={'shrink': 0.8})
    ax.set_title("Correlation Heatmap")
    fig.tight_layout()
    return fig


def donut_chart(df: pd.DataFrame, category_col: str, value_col: str, style) -> plt.Figure:
    """Donut chart (pie with hole) of value_col totals by category_col."""
    grouped = df.groupby(category_col)[value_col].sum()
    
    # Limit to top 8 categories
    if len(grouped) > 8:
        grouped = grouped.sort_values(ascending=False)
        top = grouped.iloc[:8]
        other = grouped.iloc[8:].sum()
        top["Other"] = other
        grouped = top
    
    fig, ax = plt.subplots(figsize=(5.5, 5.5), dpi=100)
    colors = plt.cm.Set3(range(len(grouped)))
    wedges, texts, autotexts = ax.pie(
        grouped.values,
        labels=[str(i) for i in grouped.index],
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        wedgeprops=dict(width=0.4, edgecolor='white')
    )
    ax.set_title(f"Donut Chart: {value_col} by {category_col}")
    fig.tight_layout()
    return fig
