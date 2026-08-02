# Student Performance Dashboard

A modern, interactive **Plotly Dash** dashboard for analyzing student performance data. Built as the Python deliverable for the Mini Project specification (`Mini_Project.ipynb`).

## Features

- **5-page sidebar navigation**: Overview, Student Explorer, Analytics, Insights, Data & Quality
- **8 KPI cards**: Total students, average attendance, highest/lowest averages, class average, above 85%, below 60%, at-risk count
- **Multi-library visualizations**: Plotly (interactive), Matplotlib, Seaborn
- **Interactive filters**: Student/subject dropdowns, search, sliders, grade multi-select, sortable tables
- **Student comparison**: Side-by-side subject comparison for two students
- **Data cleaning audit**: Missing values, zeros, duplicates, outliers, validation checks
- **Export**: Processed CSV download + standalone HTML report

## Dataset

| File | Description |
|------|-------------|
| `student_data.csv` | Original dataset (notebook references `student_performance.csv` — same data) |
| `processed_student_data.csv` | Auto-generated on startup after cleaning and enrichment |

### Data Cleaning Assumptions

- **Missing values (NaN)** are imputed with the column mean
- **Zero values** in subject/attendance columns are treated as missing entries and replaced with the non-zero column mean (documented assumption for this dataset)
- **Duplicates** are detected and removed
- **Outliers** flagged via IQR method on `Average`

### Calculated Columns

- `Total` — sum of subject marks
- `Average` — mean of subject marks
- `Grade` — A (≥90), B (≥80), C (≥70), D (≥60), F (<60)
- `Rank` — class rank by average (1 = topper)
- `StrongestSubject` / `WeakestSubject`
- `IsOutlier` — IQR-based flag

## Project Structure

```
student-dashboard/
├── app.py                  # Entry point
├── config.py               # Constants and paths
├── data/loader.py            # Load, clean, enrich pipeline
├── analysis/metrics.py       # KPIs, filters, insights
├── charts/                   # Plotly, Matplotlib, Seaborn builders
├── components/               # Layout and KPI cards
├── callbacks/callbacks.py    # Dash interactivity
├── assets/custom.css         # Theme styling
└── exports/                  # Runtime exports (gitignored)
```

## Setup & Run

```bash
cd student-dashboard
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:8050** in your browser.

## Dependencies

- dash, dash-bootstrap-components
- pandas, numpy
- plotly, matplotlib, seaborn
- kaleido (optional, for PNG export)

## Deliverables Checklist

| Deliverable | Status |
|-------------|--------|
| Python source code | `app.py` + modular packages |
| Dataset | `student_data.csv` |
| Processed dataset | `processed_student_data.csv` (auto-generated) |
| Dashboard application | Run via `python app.py` |
| README | This file |
| Screenshots | Capture after running the app |

## Screenshots

_Add screenshots of each dashboard page here after running the application._

## Requirements Mapping (Mini_Project.ipynb)

| Section | Implementation |
|---------|----------------|
| §1 Data Import | `data/loader.py` + Data & Quality page |
| §2 Overview KPIs | 8 KPI cards on Overview page |
| §3 Student Analysis | Student Explorer + Insights pages |
| §4 Visualizations | Bar, line, pie, scatter, bubble, histogram, box, heatmap, area, radar |
| §5 Interactive | Dropdowns, filters, search, sort, dynamic updates |
| §6 Insights | Top/bottom 5, correlation, perfect attendance, improvement list |
| §7 Data Cleaning | Audit panel with full cleaning report |
| §8 Export | CSV + HTML download buttons |
| §9 UI | Cyborg dark theme, responsive layout, labelled charts |
