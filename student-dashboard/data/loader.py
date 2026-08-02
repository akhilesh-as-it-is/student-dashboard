"""Data loading, cleaning, validation, and enrichment pipeline."""

from __future__ import annotations

import io
from typing import Any

import numpy as np
import pandas as pd

import config


def load_data(filepath: str | None = None) -> pd.DataFrame:
    """Read the student CSV into a DataFrame."""
    path = filepath or str(config.DATA_PATH)
    return pd.read_csv(path)


def inspect_data(df: pd.DataFrame) -> dict[str, Any]:
    """Return inspection summary for UI display."""
    buffer = io.StringIO()
    df.info(buf=buffer)

    null_counts = df.isnull().sum().to_dict()
    zero_counts = {
        col: int((df[col] == 0).sum())
        for col in config.NUMERIC_COLS
        if col in df.columns
    }

    return {
        "head": df.head().to_dict("records"),
        "head_columns": list(df.columns),
        "info": buffer.getvalue(),
        "describe": df.describe().round(2).to_dict(),
        "describe_index": list(df.describe().index),
        "null_counts": null_counts,
        "zero_counts": zero_counts,
        "shape": df.shape,
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
    }


def clean_data(df: pd.DataFrame, audit: dict[str, Any] | None = None) -> pd.DataFrame:
    """
    Handle missing values and zero entries.

    Zeros in subject/attendance columns are treated as missing entries and
    imputed with the non-zero column mean.
    """
    df = df.copy()
    audit = audit if audit is not None else {}

    audit["nulls_before"] = df.isnull().sum().to_dict()
    audit["zeros_before"] = {
        col: int((df[col] == 0).sum()) for col in config.NUMERIC_COLS
    }

    for col in config.SUBJECT_COLS:
        col_mean = df[col].mean()
        df[col] = df[col].fillna(round(col_mean, 2))

    df["Attendance"] = df["Attendance"].fillna(round(df["Attendance"].mean(), 2))

    for col in config.SUBJECT_COLS:
        nonzero_mean = df.loc[df[col] != 0, col].mean()
        df[col] = df[col].replace(0, round(nonzero_mean, 2))

    att_nonzero_mean = df.loc[df["Attendance"] != 0, "Attendance"].mean()
    df["Attendance"] = df["Attendance"].replace(0, round(att_nonzero_mean, 2))

    duplicates_found = int(df.duplicated().sum())
    audit["duplicates_found"] = duplicates_found
    df = df.drop_duplicates()

    audit["nulls_after"] = df.isnull().sum().to_dict()
    audit["imputation_strategy"] = "Column mean for NaN; non-zero column mean for zeros"
    audit["rows_after_cleaning"] = len(df)

    return df


def validate_data(df: pd.DataFrame) -> dict[str, bool]:
    """Run data validation checks."""
    checks = {
        "required_columns": all(col in df.columns for col in config.ALL_COLS),
        "no_nulls": df.isnull().sum().sum() == 0,
        "no_duplicate_students": df["Student"].duplicated().sum() == 0,
        "score_range_valid": all(
            df[col].between(0, 100).all() for col in config.NUMERIC_COLS
        ),
    }
    return checks


def _get_grade(avg: float) -> str:
    for grade, threshold in config.GRADE_BANDS:
        if avg >= threshold:
            return grade
    return "F"


def add_calculated_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add Total, Average, Grade, Rank, and subject strength columns."""
    df = df.copy()

    df["Total"] = df[config.SUBJECT_COLS].sum(axis=1)
    df["Average"] = df[config.SUBJECT_COLS].mean(axis=1).round(2)
    df["Grade"] = df["Average"].apply(_get_grade)
    df["Rank"] = df["Average"].rank(ascending=False, method="min").astype(int)

    df["StrongestSubject"] = df[config.SUBJECT_COLS].idxmax(axis=1)
    df["WeakestSubject"] = df[config.SUBJECT_COLS].idxmin(axis=1)

    return df.sort_values("Rank").reset_index(drop=True)


def detect_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """Flag outliers on Average using the IQR method."""
    df = df.copy()
    q1 = df["Average"].quantile(0.25)
    q3 = df["Average"].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    df["IsOutlier"] = (df["Average"] < lower) | (df["Average"] > upper)
    return df


def save_processed_data(df: pd.DataFrame, filepath: str | None = None) -> None:
    """Write the processed dataset to CSV."""
    path = filepath or str(config.PROCESSED_DATA_PATH)
    df.to_csv(path, index=False)


def load_and_process() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """
    Full pipeline: load raw data, clean, enrich, validate, and export.

    Returns (raw_df, processed_df, audit_report).
    """
    audit: dict[str, Any] = {}

    raw_df = load_data()
    audit["raw_inspection"] = inspect_data(raw_df)

    cleaned = clean_data(raw_df, audit=audit)
    enriched = add_calculated_columns(cleaned)
    processed_df = detect_outliers(enriched)

    audit["validation"] = validate_data(processed_df)
    audit["outliers"] = processed_df.loc[
        processed_df["IsOutlier"], ["Student", "Average"]
    ].to_dict("records")
    audit["outlier_count"] = int(processed_df["IsOutlier"].sum())

    config.EXPORTS_DIR.mkdir(exist_ok=True)
    save_processed_data(processed_df)

    return raw_df, processed_df, audit
