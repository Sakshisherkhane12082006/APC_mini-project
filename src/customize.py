"""
customize.py
Holds the mutable chart-appearance state (color, marker, line style, grid)
and small setter functions the GUI's customize panel calls into. Keeping
this as a class instance (rather than free globals) means multiple charts
or future multi-window setups won't stomp on each other's settings.
"""

VALID_COLORS = ["blue", "red", "green", "orange", "purple", "black", "brown", "teal"]
VALID_MARKERS = ["o", "s", "^", "D", "x", "*", "none"]
VALID_LINESTYLES = ["-", "--", "-.", ":"]


class ChartStyle:
    """Container for the current chart styling preferences."""

    def __init__(self):
        self.color = "blue"
        self.marker = "o"
        self.linestyle = "-"
        self.grid = True

    def as_dict(self) -> dict:
        return {
            "color": self.color,
            "marker": None if self.marker == "none" else self.marker,
            "linestyle": self.linestyle,
            "grid": self.grid,
        }


def change_color(style: ChartStyle, color: str) -> None:
    """Update the line/marker color if it's a recognized option."""
    if color in VALID_COLORS:
        style.color = color


def change_marker(style: ChartStyle, marker: str) -> None:
    """Update the marker style if it's a recognized option."""
    if marker in VALID_MARKERS:
        style.marker = marker


def change_linestyle(style: ChartStyle, linestyle: str) -> None:
    """Update the line style if it's a recognized option."""
    if linestyle in VALID_LINESTYLES:
        style.linestyle = linestyle


def toggle_grid(style: ChartStyle) -> bool:
    """Flip the grid on/off, returning the new state."""
    style.grid = not style.grid
    return style.grid
