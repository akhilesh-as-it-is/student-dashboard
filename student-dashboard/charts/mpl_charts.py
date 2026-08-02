"""Matplotlib chart builders embedded as base64 images."""

from __future__ import annotations

import base64
import io

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import config

DARK_BG = "#1a1d20"
TEXT_COLOR = "#adb5bd"


def _fig_to_base64(fig: plt.Figure) -> str:
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight", facecolor=DARK_BG)
    buffer.seek(0)
    encoded = base64.b64encode(buffer.read()).decode()
    plt.close(fig)
    return f"data:image/png;base64,{encoded}"


def build_grouped_bar_with_error(df: pd.DataFrame) -> str:
    """Grouped bar chart with std error bars per subject."""
    means = df[config.SUBJECT_COLS].mean()
    stds = df[config.SUBJECT_COLS].std()

    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor=DARK_BG)
    ax.set_facecolor(DARK_BG)

    x = np.arange(len(config.SUBJECT_COLS))
    bars = ax.bar(
        x,
        means,
        yerr=stds,
        capsize=6,
        color=config.COLOR_SEQUENCE[: len(config.SUBJECT_COLS)],
        edgecolor="white",
        linewidth=0.5,
        alpha=0.9,
    )

    ax.set_xticks(x)
    ax.set_xticklabels(config.SUBJECT_COLS, color=TEXT_COLOR)
    ax.set_ylabel("Average Marks", color=TEXT_COLOR)
    ax.set_title("Subject Averages with Std Dev (Matplotlib)", color="white", fontsize=14)
    ax.tick_params(colors=TEXT_COLOR)
    ax.spines["bottom"].set_color(TEXT_COLOR)
    ax.spines["left"].set_color(TEXT_COLOR)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    for bar, mean_val in zip(bars, means):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            f"{mean_val:.1f}",
            ha="center",
            va="bottom",
            color=TEXT_COLOR,
            fontsize=9,
        )

    fig.tight_layout()
    return _fig_to_base64(fig)
