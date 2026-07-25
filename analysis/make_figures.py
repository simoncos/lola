"""Generate figures from current, provenance-backed design-analysis outputs.

The script deliberately refuses to fall back to the pre-audit P0/P1/P2 files.
Run ``analysis.mastery_learning`` and ``analysis.design_p2`` first.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from lola_dataset.provenance import write_run_manifest


INK = "#222222"
MUTED = "#777777"
GRID = "#DDDDDD"
BLUE = "#0072B2"
ORANGE = "#D55E00"

plt.rcParams.update(
    {
        "font.size": 9,
        "axes.edgecolor": MUTED,
        "axes.labelcolor": INK,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "text.color": INK,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
    }
)


def _require(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(
            f"missing current analysis artifact: {path}; rerun the active pipeline"
        )
    return path


def learning_forest(output: Path, learning: pd.DataFrame) -> None:
    selected = pd.concat([learning.head(8), learning.tail(8)]).drop_duplicates(
        "champion"
    )
    selected = selected.sort_values("learning_slope")
    figure, axis = plt.subplots(figsize=(6.2, 5.2))
    y = np.arange(len(selected))
    errors = np.vstack(
        [
            selected["learning_slope"] - selected["ci95_low"],
            selected["ci95_high"] - selected["learning_slope"],
        ]
    )
    axis.errorbar(
        selected["learning_slope"],
        y,
        xerr=errors,
        fmt="o",
        color=BLUE,
        ecolor=MUTED,
        capsize=2,
    )
    axis.axvline(0, color=INK, linewidth=0.8)
    axis.set_yticks(y, selected["champion"])
    axis.set_xlabel("within-player learning slope per log observed game")
    axis.set_title("Champion learning-curve estimates")
    axis.grid(axis="x", color=GRID, linewidth=0.5)
    figure.tight_layout()
    figure.savefig(output / "fig1_learning_curves.png")
    plt.close(figure)


def learning_vs_difficulty(output: Path, learning: pd.DataFrame, difficulty: pd.DataFrame) -> None:
    frame = learning.merge(difficulty, on="champion", how="inner").dropna()
    figure, axis = plt.subplots(figsize=(5.2, 4.1))
    axis.scatter(frame["difficulty"], frame["learning_slope"], color=BLUE, alpha=0.7)
    rho = frame["difficulty"].corr(frame["learning_slope"], method="spearman")
    axis.axhline(0, color=MUTED, linewidth=0.8)
    axis.set_xlabel("Riot mechanical difficulty (1-10)")
    axis.set_ylabel("within-player learning slope")
    axis.set_title(f"Learning slope vs mechanical difficulty (Spearman {rho:+.2f})")
    axis.grid(color=GRID, linewidth=0.5)
    figure.tight_layout()
    figure.savefig(output / "fig2_learning_vs_difficulty.png")
    plt.close(figure)


def salience_stability(output: Path, salience: pd.DataFrame) -> None:
    wide = salience.pivot(
        index="champion", columns="bucket", values="ban_win_salience_residual"
    ).dropna(subset=["low", "high"])
    figure, axis = plt.subplots(figsize=(5.2, 4.2))
    axis.scatter(wide["low"], wide["high"], color=ORANGE, alpha=0.7)
    rho = wide["low"].corr(wide["high"], method="spearman")
    axis.axhline(0, color=MUTED, linewidth=0.8)
    axis.axvline(0, color=MUTED, linewidth=0.8)
    axis.set_xlabel("low-tier ban-win salience residual")
    axis.set_ylabel("high-tier ban-win salience residual")
    axis.set_title(f"Ban-salience rank stability (Spearman {rho:+.2f})")
    axis.grid(color=GRID, linewidth=0.5)
    figure.tight_layout()
    figure.savefig(output / "fig3_salience_stability.png")
    plt.close(figure)


def learning_vs_salience(
    output: Path, learning: pd.DataFrame, salience: pd.DataFrame
) -> None:
    high = salience[salience["bucket"] == "high"]
    frame = learning.merge(high, on="champion", how="inner").dropna(
        subset=["learning_slope", "ban_win_salience_residual"]
    )
    figure, axis = plt.subplots(figsize=(5.2, 4.2))
    axis.scatter(
        frame["learning_slope"],
        frame["ban_win_salience_residual"],
        color=BLUE,
        alpha=0.7,
    )
    rho = frame["learning_slope"].corr(
        frame["ban_win_salience_residual"], method="spearman"
    )
    axis.axhline(0, color=MUTED, linewidth=0.8)
    axis.axvline(0, color=MUTED, linewidth=0.8)
    axis.set_xlabel("within-player learning slope")
    axis.set_ylabel("high-tier ban-win salience residual")
    axis.set_title(f"Descriptive association (Spearman {rho:+.2f})")
    axis.grid(color=GRID, linewidth=0.5)
    figure.tight_layout()
    figure.savefig(output / "fig4_learning_vs_salience.png")
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="analysis/output")
    args = parser.parse_args()
    data_dir = Path(args.out)
    figure_dir = data_dir / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)

    learning_path = _require(data_dir / "mastery_learning.csv")
    learning_manifest = _require(data_dir / "mastery_learning.run.json")
    salience_path = _require(data_dir / "ban_salience_by_tier.csv")
    salience_manifest = _require(data_dir / "design_ban_salience.run.json")
    difficulty_path = _require(Path("analysis/riot_difficulty_ddragon.csv"))
    learning = pd.read_csv(learning_path)
    salience = pd.read_csv(salience_path)
    difficulty = pd.read_csv(difficulty_path)
    difficulty.columns = ["champion", "difficulty"]
    learning_forest(figure_dir, learning)
    learning_vs_difficulty(figure_dir, learning, difficulty)
    salience_stability(figure_dir, salience)
    learning_vs_salience(figure_dir, learning, salience)
    outputs = [
        figure_dir / "fig1_learning_curves.png",
        figure_dir / "fig2_learning_vs_difficulty.png",
        figure_dir / "fig3_salience_stability.png",
        figure_dir / "fig4_learning_vs_salience.png",
    ]
    write_run_manifest(
        figure_dir,
        "figures",
        parameters={"protocol_version": 1, "figure_count": len(outputs)},
        inputs=[
            learning_path,
            learning_manifest,
            salience_path,
            salience_manifest,
            difficulty_path,
        ],
        outputs=outputs,
    )
    print(f"current figures written to {figure_dir}")


if __name__ == "__main__":
    main()
