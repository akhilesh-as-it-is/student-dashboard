"""Dash callback registration for all dashboard interactivity."""

from __future__ import annotations

import pandas as pd
from dash import Input, Output, State, callback_context, dash_table, html, no_update
import dash_bootstrap_components as dbc

import config
from analysis.metrics import compute_kpis, filter_dataframe, get_insights, get_student_profile
from charts import mpl_charts, plotly_charts, seaborn_charts
from components.kpi_cards import build_kpi_cards
from components.layout import (
    PAGE_SUBTITLES,
    PAGE_TITLES,
    analytics_page_layout,
    data_page_layout,
    insights_page_layout,
    overview_page_layout,
    student_page_layout,
)
from theme import TABLE_STYLES, resolve_theme


def _dataframe_table(
    df: pd.DataFrame, table_id: str = "table", theme: str = "dark"
) -> dash_table.DataTable:
    display_cols = [
        "Rank", "Student", "Python", "SQL", "Power BI", "AI",
        "Attendance", "Total", "Average", "Grade",
    ]
    display_cols = [c for c in display_cols if c in df.columns]
    styles = TABLE_STYLES.get(theme, TABLE_STYLES["dark"])

    style_cond = [
        {
            "if": {
                "filter_query": f"{{Average}} < {config.KPI_LOW_THRESHOLD}",
            },
            "backgroundColor": "rgba(231, 76, 60, 0.15)",
        },
        {
            "if": {"filter_query": "{Rank} = 1"},
            "backgroundColor": "rgba(243, 156, 18, 0.15)",
        },
    ]

    return dash_table.DataTable(
        id=table_id,
        columns=[{"name": c, "id": c} for c in display_cols],
        data=df[display_cols].to_dict("records"),
        sort_action="native",
        filter_action="native",
        page_size=10,
        style_table={"overflowX": "auto"},
        style_header=styles["header"],
        style_cell=styles["cell"],
        style_data_conditional=style_cond,
    )


def _raw_data_table(raw_df: pd.DataFrame, theme: str = "dark") -> dash_table.DataTable:
    styles = TABLE_STYLES.get(theme, TABLE_STYLES["dark"])
    return dash_table.DataTable(
        columns=[{"name": c, "id": c} for c in raw_df.columns],
        data=raw_df.fillna("Null").to_dict("records"),
        page_size=10,
        style_table={"overflowX": "auto"},
        style_header=styles["header"],
        style_cell=styles["cell"],
    )


def _simple_table(records: list[dict], columns: list[str]) -> dbc.Table:
    if not records:
        return html.P("No data available.", className="text-muted")
    header = html.Thead(html.Tr([html.Th(c) for c in columns]))
    rows = []
    for rec in records:
        rows.append(html.Tr([html.Td(rec.get(c, "")) for c in columns]))
    return dbc.Table(
        [header, html.Tbody(rows)],
        striped=True,
        bordered=True,
        hover=True,
        size="sm",
        className="text-light",
    )


def register_callbacks(app, raw_df: pd.DataFrame, df: pd.DataFrame, audit: dict) -> None:
    """Register all dashboard callbacks."""
    student_list = df["Student"].tolist()
    topper = df.loc[df["Rank"] == 1, "Student"].iloc[0]

    # --- Theme switcher (clientside: body class + label + store) ---
    app.clientside_callback(
        """
        function(is_light) {
            document.body.classList.toggle('light-mode', is_light);
            document.body.classList.toggle('dark-mode', !is_light);
            return [is_light ? 'Dark Mode' : 'Light Mode', is_light ? 'light' : 'dark'];
        }
        """,
        [Output("theme-switch", "label"), Output("theme-store", "data")],
        Input("theme-switch", "value"),
    )

    # --- Page navigation ---
    @app.callback(
        Output("active-page", "data"),
        Output("nav-overview", "active"),
        Output("nav-student", "active"),
        Output("nav-analytics", "active"),
        Output("nav-insights", "active"),
        Output("nav-data", "active"),
        Output("page-title", "children"),
        Output("page-subtitle", "children"),
        Output("page-content", "children"),
        Input("nav-overview", "n_clicks"),
        Input("nav-student", "n_clicks"),
        Input("nav-analytics", "n_clicks"),
        Input("nav-insights", "n_clicks"),
        Input("nav-data", "n_clicks"),
        State("active-page", "data"),
        prevent_initial_call=False,
    )
    def navigate_pages(n1, n2, n3, n4, n5, current_page):
        ctx = callback_context
        page_map = {
            "nav-overview": "overview",
            "nav-student": "student",
            "nav-analytics": "analytics",
            "nav-insights": "insights",
            "nav-data": "data",
        }

        page = current_page or "overview"
        if ctx.triggered and ctx.triggered[0]["prop_id"] != "active-page.data":
            trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
            page = page_map.get(trigger_id, page)

        active_flags = {p["id"]: p["id"] == page for p in config.PAGES}

        layouts = {
            "overview": overview_page_layout(),
            "student": student_page_layout(student_list),
            "analytics": analytics_page_layout(),
            "insights": insights_page_layout(),
            "data": data_page_layout(),
        }

        return (
            page,
            active_flags["overview"],
            active_flags["student"],
            active_flags["analytics"],
            active_flags["insights"],
            active_flags["data"],
            PAGE_TITLES[page],
            PAGE_SUBTITLES[page],
            layouts[page],
        )

    # --- Overview page ---
    @app.callback(
        Output("overview-kpis", "children"),
        Output("chart-grade-pie", "figure"),
        Output("chart-subject-bar", "figure"),
        Output("chart-avg-hist", "figure"),
        Output("chart-subject-line", "figure"),
        Input("active-page", "data"),
        Input("theme-switch", "value"),
    )
    def update_overview(page, is_light):
        if page != "overview":
            return no_update, no_update, no_update, no_update, no_update

        theme = resolve_theme(is_light)
        kpis = compute_kpis(df)
        return (
            build_kpi_cards(kpis),
            plotly_charts.build_grade_pie(df, theme),
            plotly_charts.build_subject_bar(df, theme),
            plotly_charts.build_average_histogram(df, theme),
            plotly_charts.build_subject_line(df, theme),
        )

    # --- Student explorer ---
    @app.callback(
        Output("student-profile", "children"),
        Output("chart-student-bar", "figure"),
        Output("chart-radar", "figure"),
        Output("chart-attendance-scatter", "figure"),
        Output("chart-compare-bar", "figure"),
        Output("compare-table", "children"),
        Input("student-dropdown-visible", "value"),
        Input("compare-dropdown-visible", "value"),
        Input("subject-dropdown-visible", "value"),
        Input("active-page", "data"),
        Input("theme-switch", "value"),
    )
    def update_student_page(student, compare_student, subject, page, is_light):
        if page != "student":
            return no_update, no_update, no_update, no_update, no_update, no_update

        theme = resolve_theme(is_light)
        student = student or student_list[0]
        compare_student = compare_student or (student_list[1] if len(student_list) > 1 else student)

        profile_data = get_student_profile(df, student)
        if profile_data is None:
            return html.P("Student not found."), *([no_update] * 5)

        topper_badge = (
            html.Div(
                [html.I(className="bi bi-trophy-fill me-1"), "Class Topper!"],
                className="topper-badge",
            )
            if profile_data["is_topper"]
            else None
        )

        profile = dbc.Card(
            dbc.CardBody(
                [
                    html.H4(profile_data["student"], className="text-light"),
                    html.P(f"Average: {profile_data['average']}%", className="mb-1"),
                    html.P(f"Total Marks: {profile_data['total']}", className="mb-1"),
                    html.P(f"Grade: {profile_data['grade']}", className="mb-1"),
                    html.P(f"Rank: #{profile_data['rank']}", className="mb-1"),
                    html.P(f"Attendance: {profile_data['attendance']}%", className="mb-1"),
                    html.P(
                        f"Strongest: {profile_data['strongest']} | Weakest: {profile_data['weakest']}",
                        className="mb-1 text-muted",
                    ),
                    html.P(
                        f"Percentile: {profile_data['percentile']}%",
                        className="mb-1 text-muted",
                    ),
                    topper_badge,
                ]
            ),
            className="profile-card",
        )

        filtered_df = df

        return (
            profile,
            plotly_charts.build_student_bar(filtered_df, student, theme),
            plotly_charts.build_radar_chart(filtered_df, student, theme),
            plotly_charts.build_attendance_scatter(
                filtered_df, highlight_student=student, topper=topper, theme=theme
            ),
            plotly_charts.build_compare_bar(filtered_df, student, compare_student, theme),
            _simple_table(
                df[df["Student"].isin([student, compare_student])][
                    ["Student", "Average", "Attendance", "Grade", "Rank"]
                ].to_dict("records"),
                ["Student", "Average", "Attendance", "Grade", "Rank"],
            ),
        )

    # --- Analytics page ---
    @app.callback(
        Output("chart-heatmap", "figure"),
        Output("chart-box", "figure"),
        Output("chart-bubble", "figure"),
        Output("chart-area", "figure"),
        Output("chart-mpl", "src"),
        Output("chart-seaborn", "src"),
        Input("active-page", "data"),
        Input("theme-switch", "value"),
    )
    def update_analytics(page, is_light):
        if page != "analytics":
            return no_update, no_update, no_update, no_update, no_update, no_update

        theme = resolve_theme(is_light)
        return (
            plotly_charts.build_correlation_heatmap(df, theme),
            plotly_charts.build_box_plot(df, theme),
            plotly_charts.build_bubble_chart(df, theme),
            plotly_charts.build_area_chart(df, theme),
            mpl_charts.build_grouped_bar_with_error(df, theme),
            seaborn_charts.build_violin_plot(df, theme),
        )

    # --- Insights page ---
    @app.callback(
        Output("insight-alerts", "children"),
        Output("top5-table", "children"),
        Output("bottom5-table", "children"),
        Output("chart-insight-bar", "figure"),
        Output("insight-side-panel", "children"),
        Input("active-page", "data"),
        Input("theme-switch", "value"),
    )
    def update_insights(page, is_light):
        if page != "insights":
            return no_update, no_update, no_update, no_update, no_update

        theme = resolve_theme(is_light)
        insights = get_insights(df)

        alerts = dbc.Row(
            [
                dbc.Col(
                    dbc.Alert(
                        f"Highest scoring subject: {insights['highest_subject']} "
                        f"({insights['highest_subject_score']})",
                        color="success",
                        className="insight-alert",
                    ),
                    lg=6,
                ),
                dbc.Col(
                    dbc.Alert(
                        f"Lowest scoring subject: {insights['lowest_subject']} "
                        f"({insights['lowest_subject_score']})",
                        color="warning",
                        className="insight-alert",
                    ),
                    lg=6,
                ),
                dbc.Col(
                    dbc.Alert(
                        f"Attendance–Marks correlation: {insights['correlation']} | "
                        f"Class topper: {insights['topper']} | "
                        f"Lowest performer: {insights['lowest_performer']}",
                        color="info",
                        className="insight-alert",
                    ),
                    lg=12,
                    className="mt-2",
                ),
            ]
        )

        side_panel = html.Div(
            [
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H6("Perfect Attendance (100%)", className="text-light"),
                            html.Ul(
                                [html.Li(name) for name in insights["perfect_attendance"]]
                                or [html.Li("None")]
                            ),
                            html.Hr(),
                            html.H6("Students Needing Improvement (< 60%)", className="text-light"),
                            html.Ul(
                                [
                                    html.Li(f"{s['Student']} ({s['Average']}%)")
                                    for s in insights["needs_improvement"]
                                ]
                                or [html.Li("None")]
                            ),
                            html.Hr(),
                            html.P(
                                f"Class Std Dev: {insights['class_std']}",
                                className="text-muted mb-0",
                            ),
                        ]
                    ),
                    className="chart-card",
                )
            ]
        )

        return (
            alerts,
            _simple_table(insights["top5"], ["Rank", "Student", "Average", "Grade", "Attendance"]),
            _simple_table(insights["bottom5"], ["Rank", "Student", "Average", "Grade", "Attendance"]),
            plotly_charts.build_subject_insight_bar(insights["subject_averages"], theme),
            side_panel,
        )

    # --- Data & Quality page ---
    @app.callback(
        Output("audit-panel", "children"),
        Output("info-panel", "children"),
        Output("describe-panel", "children"),
        Output("data-table", "children"),
        Output("raw-table", "children"),
        Input("active-page", "data"),
        Input("search-input-visible", "value"),
        Input("avg-slider-visible", "value"),
        Input("att-slider-visible", "value"),
        Input("grade-filter-visible", "value"),
        Input("theme-switch", "value"),
    )
    def update_data_page(page, search, min_avg, min_att, grades, is_light):
        if page != "data":
            return no_update, no_update, no_update, no_update, no_update

        theme = resolve_theme(is_light)
        filtered = filter_dataframe(
            df,
            search=search or "",
            min_avg=min_avg or 0,
            min_attendance=min_att or 0,
            grades=grades,
        )

        validation = audit.get("validation", {})
        validation_items = [
            html.Li(
                f"{k.replace('_', ' ').title()}: {'Passed' if v else 'Failed'}",
                style={"color": "#00bc8c" if v else "#e74c3c"},
            )
            for k, v in validation.items()
        ]

        audit_panel = html.Div(
            [
                html.H6("Missing Values (Before Cleaning)", className="text-light"),
                html.Pre(str(audit.get("nulls_before", {})), className="info-pre"),
                html.H6("Zero Values Detected", className="text-light mt-3"),
                html.Pre(str(audit.get("zeros_before", {})), className="info-pre"),
                html.H6("Duplicates Found", className="text-light mt-3"),
                html.P(f"{audit.get('duplicates_found', 0)} duplicate row(s)"),
                html.H6("Outliers (IQR on Average)", className="text-light mt-3"),
                html.Pre(str(audit.get("outliers", [])), className="info-pre"),
                html.H6("Imputation Strategy", className="text-light mt-3"),
                html.P(audit.get("imputation_strategy", ""), className="text-muted"),
                html.H6("Validation Checks", className="text-light mt-3"),
                html.Ul(validation_items),
            ]
        )

        describe_df = filtered[config.NUMERIC_COLS + ["Average"]].describe().round(2)
        describe_table = dbc.Table.from_dataframe(
            describe_df.reset_index(),
            striped=True,
            bordered=True,
            hover=True,
            size="sm",
            className="text-light",
        )

        return (
            audit_panel,
            audit.get("raw_inspection", {}).get("info", "No info available."),
            describe_table,
            _dataframe_table(filtered, "processed-table", theme),
            _raw_data_table(raw_df, theme),
        )

    # --- CSV export ---
    @app.callback(
        Output("download-csv", "data"),
        Input("btn-export-csv", "n_clicks"),
        State("search-input-visible", "value"),
        State("avg-slider-visible", "value"),
        State("att-slider-visible", "value"),
        State("grade-filter-visible", "value"),
        prevent_initial_call=True,
    )
    def export_csv(n_clicks, search, min_avg, min_att, grades):
        filtered = filter_dataframe(
            df,
            search=search or "",
            min_avg=min_avg or 0,
            min_attendance=min_att or 0,
            grades=grades,
        )
        return dict(content=filtered.to_csv(index=False), filename="student_performance_export.csv")

    # --- HTML export ---
    @app.callback(
        Output("download-html", "data"),
        Input("btn-export-html", "n_clicks"),
        State("theme-store", "data"),
        prevent_initial_call=True,
    )
    def export_html(n_clicks, theme):
        html_content = plotly_charts.build_html_report(df, theme or "dark")
        return dict(content=html_content, filename="student_dashboard_report.html")
