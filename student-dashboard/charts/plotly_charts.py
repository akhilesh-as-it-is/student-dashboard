"""Plotly chart builders for the dashboard."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import config


def _base_layout(fig: go.Figure, title: str) -> go.Figure:
    fig.update_layout(
        title=title,
        template=config.PLOTLY_TEMPLATE,
        height=config.CHART_HEIGHT,
        margin=dict(l=40, r=40, t=60, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#adb5bd"),
        title_font=dict(color="#ffffff", size=16),
    )
    return fig


def build_grade_pie(df: pd.DataFrame) -> go.Figure:
    grade_counts = df["Grade"].value_counts().sort_index().reset_index()
    grade_counts.columns = ["Grade", "Count"]
    fig = px.pie(
        grade_counts,
        names="Grade",
        values="Count",
        color_discrete_sequence=config.COLOR_SEQUENCE,
    )
    return _base_layout(fig, "Grade Distribution")


def build_subject_bar(df: pd.DataFrame) -> go.Figure:
    subject_avg = df[config.SUBJECT_COLS].mean().round(2).reset_index()
    subject_avg.columns = ["Subject", "Average"]
    fig = px.bar(
        subject_avg,
        x="Subject",
        y="Average",
        color="Subject",
        text="Average",
        color_discrete_sequence=config.COLOR_SEQUENCE,
    )
    fig.update_traces(textposition="outside")
    return _base_layout(fig, "Subject-Wise Average Marks")


def build_average_histogram(df: pd.DataFrame) -> go.Figure:
    fig = px.histogram(
        df,
        x="Average",
        nbins=10,
        color_discrete_sequence=[config.COLOR_SEQUENCE[1]],
    )
    fig.update_layout(xaxis_title="Average Marks", yaxis_title="Number of Students")
    return _base_layout(fig, "Distribution of Class Averages")


def build_subject_line(df: pd.DataFrame) -> go.Figure:
    subject_avg = df[config.SUBJECT_COLS].mean().round(2)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=list(subject_avg.index),
            y=list(subject_avg.values),
            mode="lines+markers",
            line=dict(color=config.COLOR_SEQUENCE[0], width=3),
            marker=dict(size=10),
            name="Average",
        )
    )
    fig.update_layout(xaxis_title="Subject", yaxis_title="Average Marks")
    return _base_layout(fig, "Subject Performance Trend")


def build_correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    cols = config.SUBJECT_COLS + ["Attendance", "Average"]
    corr = df[cols].corr()
    fig = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        aspect="auto",
    )
    fig.update_layout(xaxis_title="", yaxis_title="")
    return _base_layout(fig, "Correlation Heatmap")


def build_box_plot(df: pd.DataFrame) -> go.Figure:
    long_df = df.melt(
        id_vars=["Student"],
        value_vars=config.SUBJECT_COLS,
        var_name="Subject",
        value_name="Marks",
    )
    fig = px.box(
        long_df,
        x="Subject",
        y="Marks",
        color="Subject",
        color_discrete_sequence=config.COLOR_SEQUENCE,
    )
    return _base_layout(fig, "Marks Spread by Subject")


def build_bubble_chart(df: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        df,
        x="Attendance",
        y="Average",
        size="Total",
        color="Grade",
        hover_name="Student",
        size_max=40,
        color_discrete_sequence=config.COLOR_SEQUENCE,
    )
    fig.update_layout(
        xaxis_title="Attendance (%)",
        yaxis_title="Average Marks",
    )
    return _base_layout(fig, "Attendance vs Performance (Bubble Chart)")


def build_area_chart(df: pd.DataFrame) -> go.Figure:
    subject_totals = df[config.SUBJECT_COLS].sum()
    cumulative = subject_totals.cumsum()
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=list(cumulative.index),
            y=list(cumulative.values),
            fill="tozeroy",
            mode="lines",
            line=dict(color=config.COLOR_SEQUENCE[2]),
            name="Cumulative Marks",
        )
    )
    fig.update_layout(xaxis_title="Subject", yaxis_title="Cumulative Total Marks")
    return _base_layout(fig, "Cumulative Subject Scores (Area Chart)")


def build_attendance_scatter(
    df: pd.DataFrame,
    highlight_student: str | None = None,
    topper: str | None = None,
) -> go.Figure:
    fig = px.scatter(
        df,
        x="Attendance",
        y="Average",
        color="Grade",
        hover_name="Student",
        size="Total",
        size_max=25,
        color_discrete_sequence=config.COLOR_SEQUENCE,
    )

    if topper:
        top_row = df[df["Student"] == topper]
        if not top_row.empty:
            fig.add_trace(
                go.Scatter(
                    x=top_row["Attendance"],
                    y=top_row["Average"],
                    mode="markers+text",
                    marker=dict(size=18, color="gold", symbol="star"),
                    text=["Topper"],
                    textposition="top center",
                    name="Class Topper",
                    showlegend=True,
                )
            )

    if highlight_student and highlight_student != topper:
        row = df[df["Student"] == highlight_student]
        if not row.empty:
            fig.add_trace(
                go.Scatter(
                    x=row["Attendance"],
                    y=row["Average"],
                    mode="markers",
                    marker=dict(size=16, color="#e74c3c", symbol="diamond"),
                    name=highlight_student,
                )
            )

    fig.update_layout(
        xaxis_title="Attendance (%)",
        yaxis_title="Average Marks",
    )
    return _base_layout(fig, "Attendance vs Average Marks")


def build_student_bar(df: pd.DataFrame, student: str) -> go.Figure:
    row = df[df["Student"] == student].iloc[0]
    marks = pd.DataFrame(
        {"Subject": config.SUBJECT_COLS, "Marks": [row[s] for s in config.SUBJECT_COLS]}
    )
    fig = px.bar(
        marks,
        x="Subject",
        y="Marks",
        color="Subject",
        text="Marks",
        color_discrete_sequence=config.COLOR_SEQUENCE,
    )
    fig.update_traces(textposition="outside")
    return _base_layout(fig, f"{student}'s Marks by Subject")


def build_radar_chart(df: pd.DataFrame, student: str) -> go.Figure:
    row = df[df["Student"] == student].iloc[0]
    values = [row[s] for s in config.SUBJECT_COLS]
    values_closed = values + [values[0]]
    categories = config.SUBJECT_COLS + [config.SUBJECT_COLS[0]]

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values_closed,
            theta=categories,
            fill="toself",
            name=student,
            line_color=config.COLOR_SEQUENCE[0],
        )
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
    )
    return _base_layout(fig, f"{student}'s Subject Profile (Radar)")


def build_compare_bar(df: pd.DataFrame, student_a: str, student_b: str) -> go.Figure:
    rows = df[df["Student"].isin([student_a, student_b])]
    long_df = rows.melt(
        id_vars=["Student"],
        value_vars=config.SUBJECT_COLS,
        var_name="Subject",
        value_name="Marks",
    )
    fig = px.bar(
        long_df,
        x="Subject",
        y="Marks",
        color="Student",
        barmode="group",
        text="Marks",
        color_discrete_sequence=config.COLOR_SEQUENCE[:2],
    )
    fig.update_traces(textposition="outside")
    return _base_layout(fig, f"Compare: {student_a} vs {student_b}")


def build_subject_insight_bar(subject_averages: dict[str, float]) -> go.Figure:
    data = pd.DataFrame(
        {"Subject": list(subject_averages.keys()), "Average": list(subject_averages.values())}
    )
    fig = px.bar(
        data,
        x="Subject",
        y="Average",
        color="Subject",
        text="Average",
        color_discrete_sequence=config.COLOR_SEQUENCE,
    )
    fig.update_traces(textposition="outside")
    return _base_layout(fig, "Subject-Wise Performance")


def build_html_report(df: pd.DataFrame) -> str:
    """Build a standalone HTML report with key charts."""
    figures = [
        build_grade_pie(df),
        build_subject_bar(df),
        build_average_histogram(df),
        build_correlation_heatmap(df),
        build_bubble_chart(df),
        build_attendance_scatter(df, topper=df.loc[df["Rank"] == 1, "Student"].iloc[0]),
    ]
    html_parts = [
        "<html><head><title>Student Performance Report</title></head><body>",
        "<h1>Student Performance Dashboard Report</h1>",
    ]
    for fig in figures:
        html_parts.append(fig.to_html(full_html=False, include_plotlyjs="cdn"))
    html_parts.append("</body></html>")
    return "\n".join(html_parts)
