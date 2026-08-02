"""KPI computation, filtering, and insight helpers."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

import config


def filter_dataframe(
    df: pd.DataFrame,
    search: str | None = None,
    min_avg: float = 0,
    min_attendance: float = 0,
    grades: list[str] | None = None,
    subject: str | None = None,
) -> pd.DataFrame:
    """Apply common dashboard filters to the DataFrame."""
    filtered = df.copy()

    if search:
        filtered = filtered[
            filtered["Student"].str.contains(search, case=False, na=False)
        ]

    filtered = filtered[filtered["Average"] >= min_avg]
    filtered = filtered[filtered["Attendance"] >= min_attendance]

    if grades:
        filtered = filtered[filtered["Grade"].isin(grades)]

    if subject and subject != "All" and subject in config.SUBJECT_COLS:
        filtered = filtered[filtered[subject] >= min_avg]

    return filtered.sort_values("Rank")


def compute_kpis(df: pd.DataFrame) -> dict[str, Any]:
    """Compute all overview KPI values."""
    if df.empty:
        return {
            "total_students": 0,
            "avg_attendance": 0,
            "highest_avg": 0,
            "highest_student": "N/A",
            "lowest_avg": 0,
            "lowest_student": "N/A",
            "class_average": 0,
            "above_85": 0,
            "below_60": 0,
            "at_risk": 0,
        }

    top_row = df.loc[df["Average"].idxmax()]
    bottom_row = df.loc[df["Average"].idxmin()]

    at_risk = df[
        (df["Average"] < config.AT_RISK_AVG_THRESHOLD)
        | (df["Attendance"] < config.AT_RISK_ATT_THRESHOLD)
    ]

    return {
        "total_students": len(df),
        "avg_attendance": round(float(df["Attendance"].mean()), 2),
        "highest_avg": round(float(top_row["Average"]), 2),
        "highest_student": str(top_row["Student"]),
        "lowest_avg": round(float(bottom_row["Average"]), 2),
        "lowest_student": str(bottom_row["Student"]),
        "class_average": round(float(df["Average"].mean()), 2),
        "above_85": int((df["Average"] > config.KPI_HIGH_THRESHOLD).sum()),
        "below_60": int((df["Average"] < config.KPI_LOW_THRESHOLD).sum()),
        "at_risk": len(at_risk),
    }


def get_subject_averages(df: pd.DataFrame) -> pd.Series:
    """Return mean score per subject."""
    return df[config.SUBJECT_COLS].mean().round(2).sort_values(ascending=False)


def get_correlation(df: pd.DataFrame) -> float:
    """Pearson correlation between Attendance and Average."""
    if len(df) < 2:
        return 0.0
    return round(float(np.corrcoef(df["Attendance"], df["Average"])[0, 1]), 3)


def get_insights(df: pd.DataFrame) -> dict[str, Any]:
    """Build insight payloads for the Insights page."""
    subject_avg = get_subject_averages(df)
    perfect_att = df[df["Attendance"] == config.PERFECT_ATTENDANCE]["Student"].tolist()
    needs_improvement = df[df["Average"] < config.KPI_LOW_THRESHOLD][
        ["Student", "Average", "Grade", "Attendance"]
    ].to_dict("records")

    top5 = df.nsmallest(5, "Rank")[
        ["Rank", "Student", "Average", "Grade", "Attendance"]
    ].to_dict("records")
    bottom5 = df.nlargest(5, "Rank")[
        ["Rank", "Student", "Average", "Grade", "Attendance"]
    ].to_dict("records")

    topper = df.loc[df["Rank"] == 1, "Student"].iloc[0] if not df.empty else "N/A"
    lowest = df.loc[df["Rank"] == df["Rank"].max(), "Student"].iloc[0] if not df.empty else "N/A"

    return {
        "top5": top5,
        "bottom5": bottom5,
        "highest_subject": subject_avg.idxmax(),
        "highest_subject_score": round(subject_avg.max(), 2),
        "lowest_subject": subject_avg.idxmin(),
        "lowest_subject_score": round(subject_avg.min(), 2),
        "subject_averages": subject_avg.to_dict(),
        "correlation": get_correlation(df),
        "perfect_attendance": perfect_att,
        "needs_improvement": needs_improvement,
        "topper": topper,
        "lowest_performer": lowest,
        "class_std": round(float(df["Average"].std()), 2) if len(df) > 1 else 0,
    }


def get_student_profile(df: pd.DataFrame, student: str) -> dict[str, Any] | None:
    """Return a single student's profile dict."""
    rows = df[df["Student"] == student]
    if rows.empty:
        return None
    row = rows.iloc[0]
    percentile = round(
        float(np.sum(df["Average"] <= row["Average"]) / len(df) * 100), 1
    )
    return {
        "student": row["Student"],
        "average": row["Average"],
        "total": row["Total"],
        "grade": row["Grade"],
        "rank": int(row["Rank"]),
        "attendance": row["Attendance"],
        "strongest": row["StrongestSubject"],
        "weakest": row["WeakestSubject"],
        "is_topper": int(row["Rank"]) == 1,
        "percentile": percentile,
        "marks": {s: row[s] for s in config.SUBJECT_COLS},
    }


def compare_students(df: pd.DataFrame, student_a: str, student_b: str) -> pd.DataFrame:
    """Return side-by-side marks for two students."""
    rows = df[df["Student"].isin([student_a, student_b])]
    return rows[["Student"] + config.SUBJECT_COLS + ["Average", "Attendance", "Grade", "Rank"]]
