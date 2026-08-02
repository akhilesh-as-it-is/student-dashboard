"""Seaborn chart builders embedded as base64 images."""

from __future__ import annotations

import base64
import io

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import config

DARK_BG = "#1a1d20"


def _fig_to_base64(fig: plt.Figure) -> str:
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight", facecolor=DARK_BG)
    buffer.seek(0)
    encoded = base64.b64encode(buffer.read()).decode()
    plt.close(fig)
    return f"data:image/png;base64,{encoded}"


def build_violin_plot(df: pd.DataFrame) -> str:
    """Violin plot of score distributions per subject."""
    long_df = df.melt(
        id_vars=["Student"],
        value_vars=config.SUBJECT_COLS,
        var_name="Subject",
        value_name="Marks",
    )

    sns.set_theme(style="darkgrid", rc={"axes.facecolor": DARK_BG, "figure.facecolor": DARK_BG})
    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor=DARK_BG)

    sns.violinplot(
        data=long_df,
        x="Subject",
        y="Marks",
        hue="Subject",
        palette=config.COLOR_SEQUENCE[: len(config.SUBJECT_COLS)],
        ax=ax,
        inner="quartile",
        legend=False,
    )

    ax.set_title("Score Distribution by Subject (Seaborn)", color="white", fontsize=14)
    ax.set_xlabel("Subject", color="#adb5bd")
    ax.set_ylabel("Marks", color="#adb5bd")
    ax.tick_params(colors="#adb5bd")

    fig.tight_layout()
    return _fig_to_base64(fig)
