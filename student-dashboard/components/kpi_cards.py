"""KPI card components."""

from __future__ import annotations

from dash import html
import dash_bootstrap_components as dbc


KPI_CONFIG = [
    ("total_students", "Total Students", "bi-people-fill", "primary"),
    ("avg_attendance", "Average Attendance", "bi-calendar-check", "info"),
    ("highest_avg", "Highest Average", "bi-trophy-fill", "success"),
    ("lowest_avg", "Lowest Average", "bi-arrow-down-circle", "warning"),
    ("class_average", "Class Average", "bi-graph-up", "secondary"),
    ("above_85", "Students Above 85%", "bi-star-fill", "success"),
    ("below_60", "Students Below 60%", "bi-exclamation-triangle", "danger"),
    ("at_risk", "At-Risk Students", "bi-shield-exclamation", "warning"),
]


def _format_value(key: str, kpis: dict) -> str:
    if key == "highest_avg":
        return f"{kpis['highest_avg']} ({kpis['highest_student']})"
    if key == "lowest_avg":
        return f"{kpis['lowest_avg']} ({kpis['lowest_student']})"
    if key in ("avg_attendance", "class_average"):
        return f"{kpis[key]}%"
    return str(kpis.get(key, "—"))


def build_kpi_cards(kpis: dict) -> dbc.Row:
    """Build a row of 8 KPI cards."""
    cards = []
    for key, label, icon, color in KPI_CONFIG:
        cards.append(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.Div(
                                [
                                    html.I(className=f"bi {icon} kpi-icon"),
                                    html.Div(
                                        [
                                            html.P(label, className="kpi-label mb-1"),
                                            html.H4(
                                                _format_value(key, kpis),
                                                className="kpi-value mb-0",
                                                id=f"kpi-{key}",
                                            ),
                                        ],
                                        className="kpi-text",
                                    ),
                                ],
                                className="d-flex align-items-center gap-3",
                            )
                        ]
                    ),
                    className=f"kpi-card kpi-card-{color}",
                ),
                xs=12,
                sm=6,
                lg=3,
                className="mb-3",
            )
        )
    return dbc.Row(cards, className="kpi-row")
