"""Central configuration for the Student Performance Dashboard."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "student_data.csv"
PROCESSED_DATA_PATH = BASE_DIR / "processed_student_data.csv"
EXPORTS_DIR = BASE_DIR / "exports"

SUBJECT_COLS = ["Python", "SQL", "Power BI", "AI"]
NUMERIC_COLS = SUBJECT_COLS + ["Attendance"]
ALL_COLS = ["Student"] + NUMERIC_COLS

GRADE_BANDS = [
    ("A", 90),
    ("B", 80),
    ("C", 70),
    ("D", 60),
    ("F", 0),
]

KPI_HIGH_THRESHOLD = 85
KPI_LOW_THRESHOLD = 60
AT_RISK_AVG_THRESHOLD = 70
AT_RISK_ATT_THRESHOLD = 85
PERFECT_ATTENDANCE = 100

COLOR_SEQUENCE = [
    "#00bc8c",
    "#3498db",
    "#e74c3c",
    "#f39c12",
    "#9b59b6",
    "#1abc9c",
]

PLOTLY_TEMPLATE = "plotly_dark"
CHART_HEIGHT = 380

APP_TITLE = "Student Performance Dashboard"
APP_HOST = "127.0.0.1"
APP_PORT = 8050

PAGES = [
    {"id": "overview", "label": "Overview", "icon": "bi-speedometer2"},
    {"id": "student", "label": "Student Explorer", "icon": "bi-person-lines-fill"},
    {"id": "analytics", "label": "Analytics", "icon": "bi-bar-chart-line"},
    {"id": "insights", "label": "Insights", "icon": "bi-lightbulb"},
    {"id": "data", "label": "Data & Quality", "icon": "bi-database"},
]
