"""
gui.py
Modern GUI for DataVision Studio - Universal CSV Analyzer.
Features: sidebar navigation, drag-and-drop upload, automatic analysis, 
interactive charts, and professional dark theme.
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import pandas as pd

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src import charts as charts_module
from src import file_handler
from src import statistics as stats_module
from src import customize as customize_module
from src import utils
from src import data_analyzer
from src import insights
from src import auto_charts
from src import data_filter
from src import ui_components

APP_TITLE = "DataVision Studio - Universal CSV Analyzer"
BG_COLOR = "#1e1e2e"
PANEL_COLOR = "#2a2a3d"
ACCENT_COLOR = "#4f8ef7"
SECONDARY_ACCENT = "#a78bfa"
TEXT_COLOR = "#e8e8f0"
FONT_HEADER = ("Segoe UI", 16, "bold")
FONT_SECTION = ("Segoe UI", 11, "bold")
FONT_NORMAL = ("Segoe UI", 10)


class DataVisionApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1400x900")
        self.root.configure(bg=BG_COLOR)
        self.root.minsize(1200, 800)

        # Application state
        self.df = None
        self.dataset_path = None
        self.analyzer = None
        self.insights_generator = None
        self.chart_selector = None
        self.data_filter = None
        self.style = customize_module.ChartStyle()
        self.current_fig = None
        self.canvas_widget = None
        self.current_page = "dashboard"

        self.x_col_var = tk.StringVar()
        self.y_col_var = tk.StringVar()
        self.chart_type_var = tk.StringVar(value="line")

        self._build_layout()

    def _build_layout(self):
        # Main container
        main_container = tk.Frame(self.root, bg=BG_COLOR)
        main_container.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = ui_components.NavigationSidebar(
            main_container, on_navigate=self._navigate
        )
        self.sidebar.pack(side="left", fill="y", padx=(0, 2))

        # Content area
        self.content_area = tk.Frame(main_container, bg=BG_COLOR)
        self.content_area.pack(side="left", fill="both", expand=True)

        # Page containers
        self.pages = {}
        self._build_dashboard_page()
        self._build_upload_page()
        self._build_explore_page()
        self._build_visualize_page()
        self._build_reports_page()

        # Show initial page
        self._show_page("dashboard")

    def _build_dashboard_page(self):
        """Build the dashboard page with summary cards and insights."""
        page = tk.Frame(self.content_area, bg=BG_COLOR)
        
        # Header
        header = tk.Frame(page, bg=BG_COLOR)
        header.pack(fill="x", padx=20, pady=(20, 10))
        tk.Label(header, text="📊 Dashboard", bg=BG_COLOR, fg=ACCENT_COLOR,
                font=FONT_HEADER).pack(side="left")

        # Summary cards row
        cards_frame = tk.Frame(page, bg=BG_COLOR)
        cards_frame.pack(fill="x", padx=20, pady=10)

        self.card_rows = tk.StringVar(value="0")
        self.card_cols = tk.StringVar(value="0")
        self.card_missing = tk.StringVar(value="0")
        self.card_numeric = tk.StringVar(value="0")

        ui_components.SummaryCard(cards_frame, "Total Rows", "0", "📊", ACCENT_COLOR).pack(side="left", padx=5)
        ui_components.SummaryCard(cards_frame, "Columns", "0", "📋", SECONDARY_ACCENT).pack(side="left", padx=5)
        ui_components.SummaryCard(cards_frame, "Missing Values", "0", "⚠️", "#f59e0b").pack(side="left", padx=5)
        ui_components.SummaryCard(cards_frame, "Numeric Columns", "0", "🔢", "#22c55e").pack(side="left", padx=5)

        # Insights panel
        self.dashboard_insights = ui_components.InsightsPanel(page)
        self.dashboard_insights.pack(fill="both", expand=True, padx=20, pady=10)

        # Chart recommendations
        self.dashboard_recommendations = ui_components.ChartRecommendationPanel(
            page, on_select=self._on_recommendation_select
        )
        self.dashboard_recommendations.pack(fill="both", expand=True, padx=20, pady=10)

        self.pages["dashboard"] = page

    def _build_upload_page(self):
        """Build the upload page with drag-and-drop area."""
        page = tk.Frame(self.content_area, bg=BG_COLOR)
        
        # Header
        header = tk.Frame(page, bg=BG_COLOR)
        header.pack(fill="x", padx=20, pady=(20, 10))
        tk.Label(header, text="📂 Upload Dataset", bg=BG_COLOR, fg=ACCENT_COLOR,
                font=FONT_HEADER).pack(side="left")

        # Upload area
        self.upload_area = ui_components.UploadArea(page, on_upload=self._on_file_upload)
        self.upload_area.pack(fill="both", expand=True, padx=20, pady=20)

        # Sample datasets section
        samples_frame = tk.Frame(page, bg=PANEL_COLOR)
        samples_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        tk.Label(samples_frame, text="Or try sample datasets:", bg=PANEL_COLOR, fg=TEXT_COLOR,
                font=FONT_SECTION).pack(anchor="w", padx=12, pady=12)

        sample_btn_frame = tk.Frame(samples_frame, bg=PANEL_COLOR)
        sample_btn_frame.pack(fill="x", padx=12, pady=(0, 12))

        tk.Button(sample_btn_frame, text="Load sales_data.csv",
                  command=lambda: self._load_sample("sales_data.csv"),
                  bg=ACCENT_COLOR, fg="white", font=FONT_NORMAL, relief="flat",
                  padx=15, pady=8).pack(side="left", padx=5)

        tk.Button(sample_btn_frame, text="Load sample_data.csv",
                  command=lambda: self._load_sample("sample_data.csv"),
                  bg=SECONDARY_ACCENT, fg="white", font=FONT_NORMAL, relief="flat",
                  padx=15, pady=8).pack(side="left", padx=5)

        self.pages["upload"] = page

    def _build_explore_page(self):
        """Build the data exploration page with table and statistics."""
        page = tk.Frame(self.content_area, bg=BG_COLOR)
        
        # Header
        header = tk.Frame(page, bg=BG_COLOR)
        header.pack(fill="x", padx=20, pady=(20, 10))
        tk.Label(header, text="🔍 Explore Data", bg=BG_COLOR, fg=ACCENT_COLOR,
                font=FONT_HEADER).pack(side="left")

        # Data table
        self.data_table = ui_components.DataTable(page, max_rows=100)
        self.data_table.pack(fill="both", expand=True, padx=20, pady=10)

        # Statistics panel
        stats_frame = tk.Frame(page, bg=PANEL_COLOR)
        stats_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        tk.Label(stats_frame, text="📊 Statistics", bg=PANEL_COLOR, fg=ACCENT_COLOR,
                font=FONT_SECTION).pack(anchor="w", padx=12, pady=12)

        self.stats_text = scrolledtext.ScrolledText(
            stats_frame, bg="#15151f", fg=TEXT_COLOR, font=("Consolas", 9),
            relief="flat", wrap="word", height=12
        )
        self.stats_text.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.stats_text.insert("1.0", "Load a dataset to see statistics here.")
        self.stats_text.config(state="disabled")

        self.pages["explore"] = page

    def _build_visualize_page(self):
        """Build the visualization page with chart builder."""
        page = tk.Frame(self.content_area, bg=BG_COLOR)
        
        # Header
        header = tk.Frame(page, bg=BG_COLOR)
        header.pack(fill="x", padx=20, pady=(20, 10))
        tk.Label(header, text="📈 Visualizations", bg=BG_COLOR, fg=ACCENT_COLOR,
                font=FONT_HEADER).pack(side="left")

        # Left panel - controls
        control_panel = tk.Frame(page, bg=PANEL_COLOR, width=300)
        control_panel.pack(side="left", fill="y", padx=(20, 10), pady=10)
        control_panel.pack_propagate(False)

        # Chart type selection
        tk.Label(control_panel, text="Chart Type", bg=PANEL_COLOR, fg=TEXT_COLOR,
                font=FONT_SECTION).pack(anchor="w", padx=12, pady=(12, 8))
        
        chart_types = ["line", "bar", "pie", "scatter", "histogram", "box", "heatmap", "donut"]
        self.chart_combo = ttk.Combobox(control_panel, values=chart_types, state="readonly")
        self.chart_combo.set("line")
        self.chart_combo.pack(fill="x", padx=12, pady=(0, 12))

        # Column selectors
        tk.Label(control_panel, text="X-axis / Category", bg=PANEL_COLOR, fg=TEXT_COLOR,
                font=FONT_NORMAL).pack(anchor="w", padx=12)
        self.x_combo = ttk.Combobox(control_panel, textvariable=self.x_col_var, state="readonly")
        self.x_combo.pack(fill="x", padx=12, pady=(0, 8))

        tk.Label(control_panel, text="Y-axis / Value", bg=PANEL_COLOR, fg=TEXT_COLOR,
                font=FONT_NORMAL).pack(anchor="w", padx=12)
        self.y_combo = ttk.Combobox(control_panel, textvariable=self.y_col_var, state="readonly")
        self.y_combo.pack(fill="x", padx=12, pady=(0, 12))

        # Customize panel
        tk.Label(control_panel, text="🎨 Customize", bg=PANEL_COLOR, fg=TEXT_COLOR,
                font=FONT_SECTION).pack(anchor="w", padx=12, pady=(12, 8))

        tk.Label(control_panel, text="Color", bg=PANEL_COLOR, fg=TEXT_COLOR,
                font=FONT_NORMAL).pack(anchor="w", padx=12)
        color_box = ttk.Combobox(control_panel, values=customize_module.VALID_COLORS, state="readonly")
        color_box.set(self.style.color)
        color_box.pack(fill="x", padx=12, pady=(0, 8))
        color_box.bind("<<ComboboxSelected>>",
                        lambda e: customize_module.change_color(self.style, color_box.get()))

        tk.Label(control_panel, text="Line Style", bg=PANEL_COLOR, fg=TEXT_COLOR,
                font=FONT_NORMAL).pack(anchor="w", padx=12)
        style_box = ttk.Combobox(control_panel, values=customize_module.VALID_LINESTYLES, state="readonly")
        style_box.set(self.style.linestyle)
        style_box.pack(fill="x", padx=12, pady=(0, 8))
        style_box.bind("<<ComboboxSelected>>",
                        lambda e: customize_module.change_linestyle(self.style, style_box.get()))

        self.grid_var = tk.BooleanVar(value=self.style.grid)
        tk.Checkbutton(control_panel, text="Grid", variable=self.grid_var,
                      command=self._on_toggle_grid, bg=PANEL_COLOR, fg=TEXT_COLOR,
                      selectcolor=PANEL_COLOR, font=FONT_NORMAL).pack(anchor="w", padx=12, pady=(0, 12))

        # Generate button
        tk.Button(control_panel, text="Generate Chart", command=self._on_generate_chart,
                  bg=ACCENT_COLOR, fg="white", font=FONT_SECTION, relief="flat",
                  padx=15, pady=10).pack(fill="x", padx=12, pady=(0, 8))

        # Save button
        tk.Button(control_panel, text="💾 Save Chart", command=self._on_save_chart,
                  bg="#3a3a52", fg=TEXT_COLOR, font=FONT_NORMAL, relief="flat",
                  padx=15, pady=8).pack(fill="x", padx=12, pady=(0, 12))

        # Right panel - chart area
        self.chart_frame = tk.Frame(page, bg=PANEL_COLOR)
        self.chart_frame.pack(side="left", fill="both", expand=True, padx=(10, 20), pady=10)

        self.placeholder_label = tk.Label(
            self.chart_frame, text="Select columns and click 'Generate Chart'",
            bg=PANEL_COLOR, fg=TEXT_COLOR, font=FONT_NORMAL
        )
        self.placeholder_label.pack(expand=True)

        self.pages["visualize"] = page

    def _build_reports_page(self):
        """Build the reports page with export options."""
        page = tk.Frame(self.content_area, bg=BG_COLOR)
        
        # Header
        header = tk.Frame(page, bg=BG_COLOR)
        header.pack(fill="x", padx=20, pady=(20, 10))
        tk.Label(header, text="📄 Reports", bg=BG_COLOR, fg=ACCENT_COLOR,
                font=FONT_HEADER).pack(side="left")

        # Export buttons
        buttons_frame = tk.Frame(page, bg=PANEL_COLOR)
        buttons_frame.pack(fill="x", padx=20, pady=20)

        tk.Button(buttons_frame, text="📊 Generate Analysis Report",
                  command=self._on_generate_report,
                  bg=ACCENT_COLOR, fg="white", font=FONT_SECTION, relief="flat",
                  padx=20, pady=12).pack(side="left", padx=10)

        tk.Button(buttons_frame, text="💾 Export Data as CSV",
                  command=self._on_export_data,
                  bg=SECONDARY_ACCENT, fg="white", font=FONT_SECTION, relief="flat",
                  padx=20, pady=12).pack(side="left", padx=10)

        # Report preview
        report_frame = tk.Frame(page, bg=PANEL_COLOR)
        report_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        tk.Label(report_frame, text="Report Preview", bg=PANEL_COLOR, fg=ACCENT_COLOR,
                font=FONT_SECTION).pack(anchor="w", padx=12, pady=12)

        self.report_text = scrolledtext.ScrolledText(
            report_frame, bg="#15151f", fg=TEXT_COLOR, font=("Consolas", 9),
            relief="flat", wrap="word"
        )
        self.report_text.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.report_text.insert("1.0", "Load a dataset to generate reports.")
        self.report_text.config(state="disabled")

        self.pages["reports"] = page

    def _navigate(self, page_id: str):
        """Navigate to a different page."""
        self.current_page = page_id
        self._show_page(page_id)

    def _show_page(self, page_id: str):
        """Show the specified page."""
        for pid, page in self.pages.items():
            if pid == page_id:
                page.pack(fill="both", expand=True)
            else:
                page.pack_forget()

    def _on_file_upload(self, path: str):
        """Handle file upload."""
        df, error = file_handler.load_csv(path)
        if error:
            utils.show_message("error", "Failed to Load Dataset", error)
            return

        self._load_data(df, path)

    def _load_sample(self, filename: str):
        """Load a sample dataset."""
        path = os.path.join("data", filename)
        if not os.path.exists(path):
            path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", filename)
        
        df, error = file_handler.load_csv(path)
        if error:
            utils.show_message("error", "Failed to Load Dataset", error)
            return

        self._load_data(df, path)

    def _load_data(self, df: pd.DataFrame, path: str):
        """Load data and initialize analysis."""
        self.df = df
        self.dataset_path = path
        
        # Initialize analyzer
        self.analyzer = data_analyzer.DataAnalyzer(df)
        self.insights_generator = insights.generate_insights(df, self.analyzer)
        self.chart_selector = auto_charts.AutoChartSelector(self.analyzer)
        self.data_filter = data_filter.DataFilter(df)

        # Update UI components
        self._update_dashboard()
        self._update_explore_page()
        self._update_visualize_page()
        self._update_reports_page()

        utils.show_message("info", "Dataset Loaded",
                          f"Loaded {df.shape[0]} rows and {df.shape[1]} columns.")

        # Navigate to dashboard
        self._navigate("dashboard")

    def _update_dashboard(self):
        """Update dashboard with current data."""
        metrics = self.analyzer.get_data_quality_metrics()
        
        # Update summary cards (would need to update the actual card widgets)
        # For now, just update insights and recommendations
        self.dashboard_insights.update_insights(self.insights_generator.insights)
        
        recommendations = self.chart_selector.generate_recommendations(8)
        self.dashboard_recommendations.update_recommendations(recommendations)

    def _update_explore_page(self):
        """Update explore page with current data."""
        self.data_table.load_data(self.df)
        
        self.stats_text.config(state="normal")
        self.stats_text.delete("1.0", "end")
        self.stats_text.insert("1.0", stats_module.format_summary_text(self.df))
        self.stats_text.config(state="disabled")

    def _update_visualize_page(self):
        """Update visualize page with current data."""
        all_cols = self.analyzer.get_all_columns()
        numeric_cols = self.analyzer.get_numeric_columns()
        
        self.x_combo["values"] = all_cols
        self.y_combo["values"] = numeric_cols
        
        if all_cols:
            self.x_col_var.set(self.analyzer.suggest_default_x_axis())
        if numeric_cols:
            self.y_col_var.set(self.analyzer.suggest_default_y_axis())

    def _update_reports_page(self):
        """Update reports page with current data."""
        self.report_text.config(state="normal")
        self.report_text.delete("1.0", "end")
        self.report_text.insert("1.0", self.analyzer.get_summary())
        self.report_text.insert("end", "\n\n")
        self.report_text.insert("end", self.insights_generator.get_insights_summary())
        self.report_text.config(state="disabled")

    def _on_recommendation_select(self, recommendation):
        """Handle chart recommendation selection."""
        self._navigate("visualize")
        self.chart_type_var.set(recommendation.chart_type)
        self.chart_combo.set(recommendation.chart_type)
        self.x_col_var.set(recommendation.x_col)
        self.y_col_var.set(recommendation.y_col)
        self._on_generate_chart()

    def _on_generate_chart(self):
        """Generate the selected chart."""
        if self.df is None:
            utils.show_message("warning", "No Data", "Please load a dataset first.")
            return

        chart_type = self.chart_combo.get()
        x_col = self.x_col_var.get()
        y_col = self.y_col_var.get()

        try:
            if chart_type == "line":
                fig = charts_module.line_chart(self.df, x_col, y_col, self.style)
            elif chart_type == "bar":
                fig = charts_module.bar_chart(self.df, x_col, y_col, self.style)
            elif chart_type == "pie":
                fig = charts_module.pie_chart(self.df, x_col, y_col, self.style)
            elif chart_type == "scatter":
                fig = charts_module.scatter_plot(self.df, x_col, y_col, self.style)
            elif chart_type == "histogram":
                fig = charts_module.histogram(self.df, y_col or x_col, self.style)
            elif chart_type == "box":
                fig = charts_module.box_plot(self.df, y_col or x_col, self.style)
            elif chart_type == "heatmap":
                fig = charts_module.correlation_heatmap(self.df, self.style)
            elif chart_type == "donut":
                fig = charts_module.donut_chart(self.df, x_col, y_col, self.style)
            else:
                utils.show_message("error", "Invalid Chart", f"Unknown chart type: {chart_type}")
                return

            self._render_figure(fig)
        except Exception as e:
            utils.show_message("error", "Chart Error", str(e))

    def _render_figure(self, fig):
        """Render a matplotlib figure in the chart frame."""
        utils.clear_frame(self.chart_frame)
        self.current_fig = fig
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvas_widget = canvas

    def _on_toggle_grid(self):
        """Toggle grid setting."""
        self.style.grid = self.grid_var.get()

    def _on_save_chart(self):
        """Save the current chart."""
        if self.current_fig is None:
            utils.show_message("warning", "No Chart", "Generate a chart first before saving.")
            return

        path = filedialog.asksaveasfilename(
            title="Save Chart As", defaultextension=".png",
            filetypes=[("PNG image", "*.png")], initialdir="charts"
        )
        if not path:
            return

        success, message = file_handler.save_chart(self.current_fig, path)
        utils.show_message("info" if success else "error", "Save Chart", message)

    def _on_generate_report(self):
        """Generate and save analysis report."""
        if self.df is None:
            utils.show_message("warning", "No Data", "Please load a dataset first.")
            return

        path = filedialog.asksaveasfilename(
            title="Save Report As", defaultextension=".txt",
            filetypes=[("Text file", "*.txt")], initialdir="reports",
            initialfile="analysis_report.txt"
        )
        if not path:
            return

        name = os.path.basename(self.dataset_path) if self.dataset_path else "Unknown dataset"
        success, message = file_handler.generate_report(self.df, name, path)
        utils.show_message("info" if success else "error", "Generate Report", message)

    def _on_export_data(self):
        """Export the current data as CSV."""
        if self.df is None:
            utils.show_message("warning", "No Data", "Please load a dataset first.")
            return

        path = filedialog.asksaveasfilename(
            title="Export Data As", defaultextension=".csv",
            filetypes=[("CSV file", "*.csv")], initialdir="exports"
        )
        if not path:
            return

        success, message = file_handler.export_data(self.df, path)
        utils.show_message("info" if success else "error", "Export Data", message)


def start_app():
    root = tk.Tk()
    app = DataVisionApp(root)
    root.mainloop()
