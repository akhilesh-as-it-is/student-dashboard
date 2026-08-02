"""Student Performance Dashboard — entry point."""

from dash import Dash
import dash_bootstrap_components as dbc

import config
from callbacks.callbacks import register_callbacks
from components.layout import create_layout
from data.loader import load_and_process


def create_app() -> Dash:
    """Initialize and configure the Dash application."""
    raw_df, processed_df, audit = load_and_process()
    student_list = processed_df["Student"].tolist()

    app = Dash(
        __name__,
        external_stylesheets=[
            dbc.themes.CYBORG,
            dbc.icons.BOOTSTRAP,
        ],
        suppress_callback_exceptions=True,
        title=config.APP_TITLE,
    )

    app.layout = create_layout(student_list)
    register_callbacks(app, raw_df, processed_df, audit)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host=config.APP_HOST, port=config.APP_PORT)
