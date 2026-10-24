"""
ui_components.py
Reusable UI components for the DataVision Studio interface.
Includes summary cards, data tables, upload areas, and navigation.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Callable, Optional, Dict, Any


# Theme colors
BG_COLOR = "#1e1e2e"
PANEL_COLOR = "#2a2a3d"
ACCENT_COLOR = "#4f8ef7"
SECONDARY_ACCENT = "#a78bfa"
TEXT_COLOR = "#e8e8f0"
SUCCESS_COLOR = "#22c55e"
WARNING_COLOR = "#f59e0b"
ERROR_COLOR = "#ef4444"
FONT_HEADER = ("Segoe UI", 16, "bold")
FONT_SECTION = ("Segoe UI", 11, "bold")
FONT_NORMAL = ("Segoe UI", 10)
FONT_SMALL = ("Segoe UI", 9)


class SummaryCard(tk.Frame):
    """A card displaying a summary metric with icon and value."""
    
    def __init__(self, parent, title: str, value: str, icon: str = "", 
                 color: str = ACCENT_COLOR, **kwargs):
        super().__init__(parent, bg=PANEL_COLOR, **kwargs)
        self.title = title
        self.value = value
        self.icon = icon
        self.color = color
        self._build_ui()
    
    def _build_ui(self):
        # Icon/title row
        top_frame = tk.Frame(self, bg=PANEL_COLOR)
        top_frame.pack(fill="x", padx=12, pady=(10, 5))
        
        if self.icon:
            tk.Label(top_frame, text=self.icon, bg=PANEL_COLOR, fg=self.color,
                    font=("Segoe UI", 14)).pack(side="left")
        
        tk.Label(top_frame, text=self.title, bg=PANEL_COLOR, fg=TEXT_COLOR,
                font=FONT_SMALL).pack(side="left", padx=(8 if self.icon else 0, 0))
        
        # Value
        tk.Label(self, text=self.value, bg=PANEL_COLOR, fg=self.color,
                font=("Segoe UI", 20, "bold")).pack(anchor="w", padx=12, pady=(0, 10))
    
    def update_value(self, new_value: str):
        """Update the displayed value."""
        self.value = new_value
        for widget in self.winfo_children():
            if isinstance(widget, tk.Label) and widget.cget("font")[2] == "bold":
                widget.config(text=new_value)


class DataTable(tk.Frame):
    """A scrollable table displaying DataFrame rows."""
    
    def __init__(self, parent, df=None, max_rows: int = 100, **kwargs):
        super().__init__(parent, bg=PANEL_COLOR, **kwargs)
        self.df = df
        self.max_rows = max_rows
        self.tree = None
        self._build_ui()
        if df is not None:
            self.load_data(df)
    
    def _build_ui(self):
        # Search bar
        search_frame = tk.Frame(self, bg=PANEL_COLOR)
        search_frame.pack(fill="x", padx=8, pady=(8, 4))
        
        tk.Label(search_frame, text="Search:", bg=PANEL_COLOR, fg=TEXT_COLOR,
                font=FONT_SMALL).pack(side="left")
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, 
                               bg="#15151f", fg=TEXT_COLOR, font=FONT_NORMAL)
        search_entry.pack(side="left", padx=(8, 0), fill="x", expand=True)
        search_entry.bind("<KeyRelease>", self._on_search)
        
        # Treeview
        tree_frame = tk.Frame(self, bg=PANEL_COLOR)
        tree_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        
        self.tree = ttk.Treeview(tree_frame, show="headings", selectmode="browse")
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#15151f", foreground=TEXT_COLOR,
                       fieldbackground="#15151f", rowheight=25)
        style.configure("Treeview.Heading", background=PANEL_COLOR, 
                       foreground=ACCENT_COLOR, font=FONT_SECTION)
        style.map("Treeview", background=[("selected", ACCENT_COLOR)])
    
    def load_data(self, df):
        """Load DataFrame into the table."""
        self.df = df
        
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if df is None or df.empty:
            return
        
        # Set columns
        self.tree["columns"] = list(df.columns)
        for col in df.columns:
            self.tree.heading(col, text=str(col))
            self.tree.column(col, width=100, anchor="w")
        
        # Add rows (limited)
        display_df = df.head(self.max_rows)
        for _, row in display_df.iterrows():
            self.tree.insert("", "end", values=[str(v) for v in row])
    
    def _on_search(self, event=None):
        """Filter table based on search."""
        if self.df is None:
            return
        
        search_term = self.search_var.get().lower()
        
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filter and display
        if not search_term:
            display_df = self.df.head(self.max_rows)
        else:
            mask = self.df.astype(str).apply(lambda x: x.str.lower().str.contains(search_term, na=False)).any(axis=1)
            display_df = self.df[mask].head(self.max_rows)
        
        for _, row in display_df.iterrows():
            self.tree.insert("", "end", values=[str(v) for v in row])


class UploadArea(tk.Frame):
    """A drag-and-drop upload area for CSV files."""
    
    def __init__(self, parent, on_upload: Callable, **kwargs):
        super().__init__(parent, bg=PANEL_COLOR, **kwargs)
        self.on_upload = on_upload
        self._build_ui()
    
    def _build_ui(self):
        # Container
        container = tk.Frame(self, bg=PANEL_COLOR, bd=2, relief="solid")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Content
        tk.Label(container, text="📁", bg=PANEL_COLOR, fg=ACCENT_COLOR,
                font=("Segoe UI", 48)).pack(pady=(40, 20))
        
        tk.Label(container, text="Drag & Drop CSV File Here", bg=PANEL_COLOR,
                fg=TEXT_COLOR, font=FONT_HEADER).pack(pady=(0, 8))
        
        tk.Label(container, text="or", bg=PANEL_COLOR, fg=TEXT_COLOR,
                font=FONT_NORMAL).pack(pady=(0, 8))
        
        upload_btn = tk.Button(container, text="Browse Files", 
                              command=self._browse_file,
                              bg=ACCENT_COLOR, fg="white", font=FONT_SECTION,
                              relief="flat", padx=20, pady=8)
        upload_btn.pack(pady=(0, 40))
        
        # Info text
        info_text = "Supported formats: CSV\nMax file size: 50MB"
        tk.Label(container, text=info_text, bg=PANEL_COLOR, fg="#888899",
                font=FONT_SMALL).pack(pady=(0, 20))
    
    def _browse_file(self):
        """Open file browser."""
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if path:
            self.on_upload(path)


class NavigationSidebar(tk.Frame):
    """Sidebar with navigation buttons."""
    
    def __init__(self, parent, on_navigate: Callable, **kwargs):
        super().__init__(parent, bg=BG_COLOR, **kwargs)
        self.on_navigate = on_navigate
        self.current_page = "dashboard"
        self.buttons = {}
        self._build_ui()
    
    def _build_ui(self):
        # Logo
        tk.Label(self, text="📊", bg=BG_COLOR, fg=ACCENT_COLOR,
                font=("Segoe UI", 24)).pack(pady=(20, 10))
        
        tk.Label(self, text="DataVision", bg=BG_COLOR, fg=TEXT_COLOR,
                font=("Segoe UI", 14, "bold")).pack(pady=(0, 5))
        
        tk.Label(self, text="Studio", bg=BG_COLOR, fg=SECONDARY_ACCENT,
                font=("Segoe UI", 12)).pack(pady=(0, 30))
        
        # Navigation items
        nav_items = [
            ("dashboard", "🏠 Dashboard"),
            ("upload", "📂 Upload Dataset"),
            ("explore", "🔍 Explore Data"),
            ("visualize", "📈 Visualizations"),
            ("reports", "📄 Reports"),
        ]
        
        for page_id, label in nav_items:
            btn = tk.Button(self, text=label, 
                          command=lambda p=page_id: self._navigate(p),
                          bg=BG_COLOR, fg=TEXT_COLOR, font=FONT_NORMAL,
                          relief="flat", anchor="w", padx=20, pady=12,
                          cursor="hand2")
            btn.pack(fill="x", padx=10, pady=2)
            self.buttons[page_id] = btn
        
        self._update_active_button()
    
    def _navigate(self, page_id: str):
        """Navigate to a page."""
        self.current_page = page_id
        self._update_active_button()
        self.on_navigate(page_id)
    
    def _update_active_button(self):
        """Update button styles based on active page."""
        for page_id, btn in self.buttons.items():
            if page_id == self.current_page:
                btn.config(bg=PANEL_COLOR, fg=ACCENT_COLOR)
            else:
                btn.config(bg=BG_COLOR, fg=TEXT_COLOR)


class InsightsPanel(tk.Frame):
    """Panel displaying automatic insights."""
    
    def __init__(self, parent, insights: list = None, **kwargs):
        super().__init__(parent, bg=PANEL_COLOR, **kwargs)
        self.insights = insights or []
        self._build_ui()
    
    def _build_ui(self):
        tk.Label(self, text="💡 Automatic Insights", bg=PANEL_COLOR, fg=ACCENT_COLOR,
                font=FONT_SECTION).pack(anchor="w", padx=12, pady=(12, 8))
        
        self.text_widget = scrolledtext.ScrolledText(
            self, bg="#15151f", fg=TEXT_COLOR, font=FONT_SMALL,
            relief="flat", wrap="word", height=10
        )
        self.text_widget.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.text_widget.config(state="disabled")
        
        self.update_insights(self.insights)
    
    def update_insights(self, insights: list):
        """Update the displayed insights."""
        self.insights = insights
        self.text_widget.config(state="normal")
        self.text_widget.delete("1.0", "end")
        
        if not insights:
            self.text_widget.insert("1.0", "No insights available.")
        else:
            for insight in insights[:15]:  # Limit to 15 insights
                severity_icon = {
                    'warning': '⚠️',
                    'info': 'ℹ️',
                    'error': '❌'
                }.get(insight.get('severity', 'info'), 'ℹ️')
                
                self.text_widget.insert("end", f"{severity_icon} {insight['message']}\n\n")
        
        self.text_widget.config(state="disabled")


class ChartRecommendationPanel(tk.Frame):
    """Panel displaying recommended charts."""
    
    def __init__(self, parent, recommendations: list = None, on_select: Callable = None, **kwargs):
        super().__init__(parent, bg=PANEL_COLOR, **kwargs)
        self.recommendations = recommendations or []
        self.on_select = on_select
        self._build_ui()
    
    def _build_ui(self):
        tk.Label(self, text="📊 Recommended Charts", bg=PANEL_COLOR, fg=ACCENT_COLOR,
                font=FONT_SECTION).pack(anchor="w", padx=12, pady=(12, 8))
        
        self.scroll_frame = tk.Frame(self, bg=PANEL_COLOR)
        self.scroll_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        
        self.update_recommendations(self.recommendations)
    
    def update_recommendations(self, recommendations: list):
        """Update the displayed recommendations."""
        self.recommendations = recommendations
        
        # Clear existing
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        if not recommendations:
            tk.Label(self.scroll_frame, text="No recommendations available.",
                    bg=PANEL_COLOR, fg=TEXT_COLOR, font=FONT_SMALL).pack(pady=20)
            return
        
        for i, rec in enumerate(recommendations[:8]):  # Limit to 8 recommendations
            frame = tk.Frame(self.scroll_frame, bg="#15151f", bd=1, relief="solid")
            frame.pack(fill="x", pady=4)
            
            # Chart type icon
            icons = {
                'line': '📈',
                'bar': '📊',
                'pie': '🥧',
                'scatter': '🔵',
                'histogram': '📉',
                'box': '📦',
                'heatmap': '🔥',
                'donut': '🍩'
            }
            icon = icons.get(rec.chart_type, '📊')
            
            content = tk.Frame(frame, bg="#15151f")
            content.pack(fill="x", padx=10, pady=8)
            
            tk.Label(content, text=icon, bg="#15151f", fg=ACCENT_COLOR,
                    font=("Segoe UI", 16)).pack(side="left")
            
            text_frame = tk.Frame(content, bg="#15151f")
            text_frame.pack(side="left", padx=(10, 0), fill="x", expand=True)
            
            tk.Label(text_frame, text=rec.title, bg="#15151f", fg=TEXT_COLOR,
                    font=FONT_SECTION, anchor="w").pack(fill="x")
            
            tk.Label(text_frame, text=rec.reason, bg="#15151f", fg="#888899",
                    font=FONT_SMALL, anchor="w", wraplength=300).pack(fill="x")
            
            if self.on_select:
                btn = tk.Button(frame, text="View", 
                              command=lambda r=rec: self.on_select(r),
                              bg=ACCENT_COLOR, fg="white", font=FONT_SMALL,
                              relief="flat", padx=10, pady=4)
                btn.pack(side="right", padx=10, pady=8)
