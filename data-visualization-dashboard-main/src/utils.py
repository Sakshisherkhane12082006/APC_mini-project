"""
utils.py
Common helper functions shared across the application:
- show_message(): unified popup messaging (info / warning / error)
- clear_frame(): remove all child widgets from a Tkinter frame
- validate_dataset(): sanity-check a loaded DataFrame before plotting
- get_numeric_columns(): convenience helper for chart dropdowns
"""

from tkinter import messagebox


def show_message(kind: str, title: str, message: str) -> None:
    """
    Show a Tkinter message box.

    Parameters
    ----------
    kind : str
        One of "info", "warning", "error".
    title : str
        Dialog title.
    message : str
        Dialog body text.
    """
    kind = kind.lower().strip()
    if kind == "info":
        messagebox.showinfo(title, message)
    elif kind == "warning":
        messagebox.showwarning(title, message)
    elif kind == "error":
        messagebox.showerror(title, message)
    else:
        # Fall back to info if an unknown kind is passed rather than
        # silently swallowing the message.
        messagebox.showinfo(title, message)


def clear_frame(frame) -> None:
    """Destroy every child widget inside the given frame."""
    for widget in frame.winfo_children():
        widget.destroy()


def validate_dataset(df) -> tuple[bool, str]:
    """
    Run basic sanity checks on a loaded DataFrame.

    Returns
    -------
    (is_valid, message) : tuple[bool, str]
        is_valid is False if the dataset can't reasonably be visualized.
    """
    if df is None:
        return False, "No dataset is currently loaded."

    if df.empty:
        return False, "The loaded dataset is empty."

    if len(df.columns) < 1:
        return False, "The dataset has no columns."

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if len(numeric_cols) == 0:
        return False, "The dataset has no numeric columns to plot."

    return True, "Dataset looks valid."


def get_numeric_columns(df) -> list:
    """Return a list of numeric column names, empty list if df is None."""
    if df is None:
        return []
    return df.select_dtypes(include="number").columns.tolist()


def get_all_columns(df) -> list:
    """Return a list of all column names, empty list if df is None."""
    if df is None:
        return []
    return df.columns.tolist()
