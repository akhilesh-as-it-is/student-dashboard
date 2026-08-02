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
from theme import MPL_THEME, SEABORN_STYLE


def _fig_to_base64(fig: plt.Figure, bg: str) -> str:
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight", facecolor=bg)
    buffer.seek(0)
    encoded = base64.b64encode(buffer.read()).decode()
    plt.close(fig)
    return f"data:image/png;base64,{encoded}"


def build_violin_plot(df: pd.DataFrame, theme: str = "dark") -> str:
    """Violin plot of score distributions per subject."""
    colors = MPL_THEME.get(theme, MPL_THEME["dark"])
    bg = colors["bg"]
    text = colors["text"]

    long_df = df.melt(
        id_vars=["Student"],
        value_vars=config.SUBJECT_COLS,
        var_name="Subject",
        value_name="Marks",
    )

    sns.set_theme(
        style=SEABORN_STYLE.get(theme, "darkgrid"),
        rc={"axes.facecolor": bg, "figure.facecolor": bg},
    )
    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor=bg)

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

    ax.set_title("Score Distribution by Subject (Seaborn)", color=text, fontsize=14)
    ax.set_xlabel("Subject", color=text)
    ax.set_ylabel("Marks", color=text)
    ax.tick_params(colors=text)

    fig.tight_layout()
    return _fig_to_base64(fig, bg)
