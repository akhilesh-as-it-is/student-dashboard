"""Theme constants and helpers for dark/light mode."""

from __future__ import annotations

PLOTLY_TEMPLATES = {
    "dark": "plotly_dark",
    "light": "plotly_white",
}

PLOTLY_FONT_COLORS = {
    "dark": "#adb5bd",
    "light": "#495057",
}

PLOTLY_TITLE_COLORS = {
    "dark": "#ffffff",
    "light": "#212529",
}

TABLE_STYLES = {
    "dark": {
        "header": {
            "backgroundColor": "#1e2226",
            "color": "#adb5bd",
            "fontWeight": "bold",
            "border": "1px solid #2b3035",
        },
        "cell": {
            "backgroundColor": "#15181b",
            "color": "#f8f9fa",
            "border": "1px solid #2b3035",
            "textAlign": "center",
            "padding": "8px",
        },
    },
    "light": {
        "header": {
            "backgroundColor": "#e9ecef",
            "color": "#212529",
            "fontWeight": "bold",
            "border": "1px solid #dee2e6",
        },
        "cell": {
            "backgroundColor": "#ffffff",
            "color": "#212529",
            "border": "1px solid #dee2e6",
            "textAlign": "center",
            "padding": "8px",
        },
    },
}

MPL_THEME = {
    "dark": {"bg": "#1a1d20", "text": "#adb5bd", "grid": "#2b3035"},
    "light": {"bg": "#ffffff", "text": "#212529", "grid": "#dee2e6"},
}

SEABORN_STYLE = {
    "dark": "darkgrid",
    "light": "whitegrid",
}


def resolve_theme(is_light: bool | None) -> str:
    """Convert switch value to theme name."""
    return "light" if is_light else "dark"
