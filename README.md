<div align="center">

# 📊 DataVision Studio — Universal CSV Analyzer

A professional desktop GUI application for automatic CSV data analysis and visualization.
Upload any CSV file and get instant insights, automatic chart recommendations, and interactive visualizations.

**Python · Tkinter · Matplotlib · Seaborn · Pandas · NumPy · SciPy**

[![Python](https://img.shields.io/badge/Python-3.9%2B-4f8ef7?logo=python&logoColor=white)](https://www.python.org/)
[![Tkinter](https://img.shields.io/badge/GUI-Tkinter-4fd1c5)](https://docs.python.org/3/library/tkinter.html)
[![Matplotlib](https://img.shields.io/badge/Charts-Matplotlib-f7b84f)](https://matplotlib.org/)

</div>

---

## 📌 Project Overview

DataVision Studio is a universal CSV analyzer that automatically detects data types, generates insights, and recommends appropriate visualizations. Unlike basic charting tools, it intelligently analyzes your data structure and suggests the best ways to explore it.

**Key Capabilities:**
- **Universal CSV Support** - Works with any CSV file, no hardcoded column names
- **Automatic Type Detection** - Identifies numeric, categorical, datetime, and text columns
- **Smart Insights** - Detects outliers, correlations, distributions, and data quality issues
- **Automatic Chart Recommendations** - Suggests appropriate visualizations based on data types
- **8 Chart Types** - Line, Bar, Pie, Scatter, Histogram, Box Plot, Heatmap, Donut
- **Professional UI** - Modern dark theme with sidebar navigation and 5 dedicated pages

---

## ✨ Features

| Category | What it does |
|---|---|
| ✅ **Universal CSV Upload** | Load any CSV with automatic encoding detection and error handling |
| ✅ **Automatic Analysis** | Detects column types, missing values, duplicates, and data quality metrics |
| ✅ **Smart Insights** | Identifies outliers, correlations, skewness, and key statistics |
| ✅ **Chart Recommendations** | Automatically suggests appropriate visualizations |
| ✅ **8 Chart Types** | Line, Bar, Pie, Scatter, Histogram, Box Plot, Heatmap, Donut |
| ✅ **Interactive Builder** | Select columns, customize styles, and generate charts |
| ✅ **Data Exploration** | Searchable data table with first 100 rows |
| ✅ **Enhanced Statistics** | Mean, median, mode, quartiles, variance, skewness, kurtosis |
| ✅ **Export Options** | Save charts as PNG, export data as CSV, generate analysis reports |
| ✅ **Professional UI** | Dark theme, sidebar navigation, responsive layout |

---

## 🛠 Installation

```bash
# 1. Navigate to project directory
cd data-visualization-dashboard-main

# 2. (Recommended) create a virtual environment
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python main.py
```

**Requirements:** Python 3.9+ with Tkinter available (Tkinter ships with most standard Python installers; on Linux you may need `sudo apt install python3-tk`).

---

## 🚀 Quick Start

1. **Launch the application** - Run `python main.py`
2. **Upload a CSV** - Go to "📂 Upload Dataset" and either:
   - Click "Browse Files" to select a CSV from your computer
   - Click "Load sales_data.csv" or "Load sample_data.csv" to try sample datasets
3. **View Dashboard** - Automatic insights and chart recommendations appear instantly
4. **Explore Data** - Go to "🔍 Explore Data" to view the data table and statistics
5. **Create Visualizations** - Go to "📈 Visualizations" to:
   - Select chart type from dropdown
   - Choose X and Y axis columns
   - Customize colors and styles
   - Generate and save charts
6. **Export** - Go to "📄 Reports" to generate analysis reports or export data

---

## 📂 Folder Structure

```
data-visualization-dashboard-main/
│
├── main.py                  # Entry point — run this
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/                    # Sample datasets
│   ├── sales_data.csv       # Sales data with dates, categories, numeric values
│   ├── sample_data.csv      # Numeric and categorical sample
│   ├── test_numeric_only.csv    # Test: only numeric columns
│   ├── test_categorical_only.csv # Test: only categorical columns
│   ├── test_date_numeric.csv    # Test: dates + numeric values
│   ├── test_missing_values.csv  # Test: data with missing values
│   └── test_empty.csv          # Test: empty file handling
│
└── src/                      # Application source
    ├── gui.py               # Modern GUI with sidebar navigation
    ├── charts.py            # 8 chart types (line, bar, pie, scatter, histogram, box, heatmap, donut)
    ├── file_handler.py      # CSV loading with encoding detection, export functions
    ├── statistics.py        # Enhanced statistics (quartiles, variance, skewness, kurtosis)
    ├── customize.py         # Chart styling state
    ├── utils.py             # Helper functions
    ├── data_analyzer.py     # Automatic column type detection and data quality analysis
    ├── insights.py          # Automatic insights generation (outliers, correlations)
    ├── auto_charts.py       # Automatic chart selection based on data types
    ├── data_filter.py       # Interactive data filtering
    └── ui_components.py     # Reusable UI components (cards, tables, upload area)
```

---

## 📊 Supported Charts

| Chart | Best for |
|---|---|
| 📈 **Line Chart** | Trends over time (datetime + numeric columns) |
| 📊 **Bar Chart** | Comparing numeric values across categories |
| 🥧 **Pie Chart** | Proportional share across categories (≤8 categories) |
| 🍩 **Donut Chart** | Modern alternative to pie chart |
| 📉 **Histogram** | Distribution of a single numeric column |
| 📦 **Box Plot** | Distribution with outliers visualization |
| 🔵 **Scatter Plot** | Relationship between two numeric columns |
| 🔥 **Heatmap** | Correlation matrix for multiple numeric columns |

---

## 📚 Concepts Used

- **Python** — Core language with modular architecture
- **Pandas** — CSV loading, data manipulation, type inference
- **NumPy** — Numeric computations and statistical calculations
- **SciPy** — Advanced statistics (skewness, kurtosis)
- **Matplotlib** — Chart rendering and embedding
- **Seaborn** — Statistical visualizations (box plots, heatmaps)
- **Tkinter** — Desktop GUI framework
- **Chardet** — Automatic encoding detection
- **Automatic Type Detection** — Smart column classification
- **Exception Handling** — Graceful error handling for all edge cases

---

## 🧪 Testing

The application has been tested with:

✅ **sales_data.csv** - Mixed data (dates, categories, numeric)  
✅ **sample_data.csv** - Numeric and categorical data  
✅ **test_numeric_only.csv** - Only numeric columns  
✅ **test_categorical_only.csv** - Only categorical columns  
✅ **test_date_numeric.csv** - Date + numeric columns  
✅ **test_missing_values.csv** - Data with missing values  
✅ **test_empty.csv** - Empty file handling  

---

## 🔧 Technical Details

### Automatic Column Type Detection
- **Numeric** - Columns with >80% numeric values
- **Datetime** - Columns with >80% parseable dates
- **Categorical** - Low cardinality (<20 unique values or <50% unique ratio)
- **Text** - High cardinality text columns

### Automatic Insights
- Outlier detection using IQR method
- Correlation analysis for numeric columns
- Distribution skewness analysis
- Missing value warnings
- Duplicate row detection warnings

### Chart Selection Logic
- Time series → Line charts (datetime + numeric)
- Categorical breakdown → Bar/Pie charts (categorical + numeric)
- Distributions → Histograms/Box plots (single numeric)
- Relationships → Scatter plots (numeric + numeric)
- Multiple numeric → Correlation heatmaps

---

## 🚀 Limitations

- Drag-and-drop UI is visual only (requires additional libraries for full DnD)
- Light/dark theme toggle not implemented (dark theme only)
- Interactive filtering UI not exposed (backend logic exists)
- Plotly installed but not actively used (Matplotlib/Seaborn for all charts)
- Very large datasets (>100K rows) may have performance issues
- Date detection works for common formats but may fail on unusual formats

---

## 👩‍💻 Author

Built as a professional-grade data analysis tool demonstrating modern GUI development, automatic data analysis, and intelligent visualization recommendations in Python.

---

<div align="center">
<sub>Licensed under the <a href="LICENSE">MIT License</a>.</sub>
</div>



<!-- 
cd "C:\Users\Sakshi\Documents\APC_mini-project"
py -m pip install -r requirements.txt
py main.py -->