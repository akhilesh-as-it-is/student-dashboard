"""Main Dash application layout."""

from __future__ import annotations

from dash import dcc, html
import dash_bootstrap_components as dbc

import config


def _sidebar_link(page: dict) -> dbc.NavLink:
    return dbc.NavLink(
        [html.I(className=f"bi {page['icon']} me-2"), page["label"]],
        id=f"nav-{page['id']}",
        href="#",
        active=False,
        className="sidebar-link",
    )


def create_layout(student_list: list[str]) -> dbc.Container:
    """Build the full application layout shell."""
    return dbc.Container(
        [
            dcc.Store(id="active-page", data="overview"),
            dcc.Store(id="filter-store", data={}),
            dcc.Store(id="theme-store", data="dark"),
            dcc.Download(id="download-csv"),
            dcc.Download(id="download-html"),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.I(className="bi bi-mortarboard-fill brand-icon"),
                                        html.Div(
                                            [
                                                html.H5(config.APP_TITLE, className="brand-title mb-0"),
                                                html.Small("Analytics Portal", className="brand-subtitle"),
                                            ]
                                        ),
                                    ],
                                    className="brand-block mb-4",
                                ),
                                dbc.Nav(
                                    [_sidebar_link(p) for p in config.PAGES],
                                    vertical=True,
                                    pills=True,
                                    className="sidebar-nav",
                                ),
                            ],
                            className="sidebar-panel",
                        ),
                        width=12,
                        lg=2,
                        className="sidebar-col",
                    ),
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H2(
                                                id="page-title",
                                                children="Overview",
                                                className="page-title mb-1",
                                            ),
                                            html.P(
                                                id="page-subtitle",
                                                children="Class performance summary and key metrics",
                                                className="page-subtitle mb-0",
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        dbc.Switch(
                                            id="theme-switch",
                                            label="Light Mode",
                                            value=False,
                                            className="theme-switch",
                                        ),
                                        className="header-actions",
                                    ),
                                ],
                                className="page-header d-flex justify-content-between align-items-start",
                            ),
                            html.Div(id="page-content", className="page-content mt-4"),
                        ],
                        width=12,
                        lg=10,
                        className="main-col",
                    ),
                ],
                className="g-0 app-shell",
            ),
        ],
        fluid=True,
        className="dashboard-container px-0",
    )


def overview_page_layout() -> html.Div:
    return html.Div(
        [
            html.Div(id="overview-kpis"),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="chart-grade-pie"), lg=6, className="mb-3"),
                    dbc.Col(dcc.Graph(id="chart-subject-bar"), lg=6, className="mb-3"),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="chart-avg-hist"), lg=6, className="mb-3"),
                    dbc.Col(dcc.Graph(id="chart-subject-line"), lg=6, className="mb-3"),
                ]
            ),
        ]
    )


def student_page_layout(student_list: list[str]) -> html.Div:
    options = [{"label": s, "value": s} for s in student_list]
    subject_options = [{"label": "All Subjects", "value": "All"}] + [
        {"label": s, "value": s} for s in config.SUBJECT_COLS
    ]
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Select Student", className="filter-label"),
                            dcc.Dropdown(
                                id="student-dropdown-visible",
                                options=options,
                                value=student_list[0] if student_list else None,
                                clearable=False,
                                className="dash-dropdown",
                            ),
                        ],
                        lg=4,
                    ),
                    dbc.Col(
                        [
                            html.Label("Compare With", className="filter-label"),
                            dcc.Dropdown(
                                id="compare-dropdown-visible",
                                options=options,
                                value=student_list[1] if len(student_list) > 1 else None,
                                clearable=False,
                                className="dash-dropdown",
                            ),
                        ],
                        lg=4,
                    ),
                    dbc.Col(
                        [
                            html.Label("Subject Filter", className="filter-label"),
                            dcc.Dropdown(
                                id="subject-dropdown-visible",
                                options=subject_options,
                                value="All",
                                clearable=False,
                                className="dash-dropdown",
                            ),
                        ],
                        lg=4,
                    ),
                ],
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(html.Div(id="student-profile"), lg=4, className="mb-3"),
                    dbc.Col(dcc.Graph(id="chart-student-bar"), lg=8, className="mb-3"),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="chart-radar"), lg=6, className="mb-3"),
                    dbc.Col(dcc.Graph(id="chart-attendance-scatter"), lg=6, className="mb-3"),
                ]
            ),
            dbc.Row([dbc.Col(dcc.Graph(id="chart-compare-bar"), lg=12, className="mb-3")]),
            html.Div(id="compare-table"),
        ]
    )


def analytics_page_layout() -> html.Div:
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="chart-heatmap"), lg=6, className="mb-3"),
                    dbc.Col(dcc.Graph(id="chart-box"), lg=6, className="mb-3"),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="chart-bubble"), lg=6, className="mb-3"),
                    dbc.Col(dcc.Graph(id="chart-area"), lg=6, className="mb-3"),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Matplotlib — Subject Averages with Std Dev"),
                                dbc.CardBody(html.Img(id="chart-mpl", className="static-chart-img")),
                            ],
                            className="chart-card mb-3",
                        ),
                        lg=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Seaborn — Score Distribution Violin Plot"),
                                dbc.CardBody(html.Img(id="chart-seaborn", className="static-chart-img")),
                            ],
                            className="chart-card mb-3",
                        ),
                        lg=6,
                    ),
                ]
            ),
        ]
    )


def insights_page_layout() -> html.Div:
    return html.Div(
        [
            dbc.Row(id="insight-alerts", className="mb-3"),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Top 5 Performers"),
                                dbc.CardBody(html.Div(id="top5-table")),
                            ],
                            className="chart-card",
                        ),
                        lg=6,
                        className="mb-3",
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Bottom 5 Performers"),
                                dbc.CardBody(html.Div(id="bottom5-table")),
                            ],
                            className="chart-card",
                        ),
                        lg=6,
                        className="mb-3",
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="chart-insight-bar"), lg=8, className="mb-3"),
                    dbc.Col(html.Div(id="insight-side-panel"), lg=4, className="mb-3"),
                ]
            ),
        ]
    )


def data_page_layout() -> html.Div:
    grade_options = [{"label": g, "value": g} for g in ["A", "B", "C", "D", "F"]]
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Search Student", className="filter-label"),
                            dcc.Input(
                                id="search-input-visible",
                                type="text",
                                placeholder="Type a name...",
                                debounce=True,
                                className="form-control search-input",
                            ),
                        ],
                        lg=3,
                    ),
                    dbc.Col(
                        [
                            html.Label("Min Average", className="filter-label"),
                            dcc.Slider(
                                id="avg-slider-visible",
                                min=0,
                                max=100,
                                step=5,
                                value=0,
                                marks={i: str(i) for i in range(0, 101, 20)},
                            ),
                        ],
                        lg=3,
                    ),
                    dbc.Col(
                        [
                            html.Label("Min Attendance", className="filter-label"),
                            dcc.Slider(
                                id="att-slider-visible",
                                min=0,
                                max=100,
                                step=5,
                                value=0,
                                marks={i: str(i) for i in range(0, 101, 20)},
                            ),
                        ],
                        lg=3,
                    ),
                    dbc.Col(
                        [
                            html.Label("Grade Filter", className="filter-label"),
                            dcc.Dropdown(
                                id="grade-filter-visible",
                                options=grade_options,
                                multi=True,
                                placeholder="All grades",
                                className="dash-dropdown",
                            ),
                        ],
                        lg=3,
                    ),
                ],
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            [html.I(className="bi bi-download me-2"), "Export CSV"],
                            id="btn-export-csv",
                            color="success",
                            className="me-2",
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        dbc.Button(
                            [html.I(className="bi bi-file-earmark-code me-2"), "Export HTML Report"],
                            id="btn-export-html",
                            color="info",
                        ),
                        width="auto",
                    ),
                ],
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [dbc.CardHeader("Data Cleaning Audit"), dbc.CardBody(html.Div(id="audit-panel"))],
                            className="chart-card mb-3",
                        ),
                        lg=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [dbc.CardHeader("Dataset Info"), dbc.CardBody(html.Pre(id="info-panel", className="info-pre"))],
                            className="chart-card mb-3",
                        ),
                        lg=6,
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Descriptive Statistics"),
                                dbc.CardBody(html.Div(id="describe-panel")),
                            ],
                            className="chart-card mb-3",
                        ),
                        lg=12,
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Processed Student Data"),
                                dbc.CardBody(html.Div(id="data-table")),
                            ],
                            className="chart-card mb-3",
                        ),
                        lg=12,
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Raw Dataset (Before Cleaning)"),
                                dbc.CardBody(html.Div(id="raw-table")),
                            ],
                            className="chart-card mb-3",
                        ),
                        lg=12,
                    ),
                ]
            ),
        ]
    )


PAGE_SUBTITLES = {
    "overview": "Class performance summary and key metrics",
    "student": "Individual student profiles, comparisons, and attendance analysis",
    "analytics": "Advanced charts across Plotly, Matplotlib, and Seaborn",
    "insights": "Top performers, improvement areas, and correlation insights",
    "data": "Data quality audit, filters, and export options",
}

PAGE_TITLES = {
    "overview": "Overview",
    "student": "Student Explorer",
    "analytics": "Analytics",
    "insights": "Insights",
    "data": "Data & Quality",
}
