"""Generate publication figures for the design paper (PAPER_DRAFT.md).

Print-appropriate matplotlib: colorblind-safe Okabe-Ito palette for positions,
single axis per panel, direct labels for annotated champions, recessive grid.
Outputs 300-dpi PNGs to analysis/output/figures/.

Usage: python analysis/make_figures.py [--out analysis/output]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Okabe-Ito colorblind-safe palette (fixed order by position)
POS_COLOR = {
    "top": "#E69F00", "jungle": "#009E73", "mid": "#0072B2",
    "adc": "#D55E00", "support": "#CC79A7",
}
INK = "#222222"; MUTED = "#888888"; GRID = "#DDDDDD"

plt.rcParams.update({
    "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 300, "savefig.dpi": 300, "savefig.bbox": "tight",
})


def _panel_scatter(ax, x, y, xl, yl, rho):
    ax.scatter(x, y, s=14, c="#0072B2", alpha=0.6, edgecolor="none")
    ax.set_xlabel(xl); ax.set_ylabel(yl)
    ax.grid(True, color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    ax.set_title(f"Spearman = {rho:+.2f}", fontsize=9, color=MUTED)


def fig1(out: Path, data: Path):
    """Three operationalizations of skill expression are mutually uncorrelated."""
    se = pd.read_csv(data / "skill_expression.csv")[["champion", "skill_reward_slope"]]
    p1 = pd.read_csv(data / "skill_amplification_p1.csv")[["champion", "amp_slope_lane_diff"]]
    df = pd.read_csv(data / "riot_difficulty_ddragon.csv") if (data / "riot_difficulty_ddragon.csv").exists() \
        else pd.read_csv("analysis/riot_difficulty_ddragon.csv")
    df.columns = ["champion", "difficulty"]
    m = se.merge(p1, on="champion").merge(df, on="champion").dropna()

    def rho(a, b): return float(pd.Series(a).corr(pd.Series(b), method="spearman"))
    fig, axs = plt.subplots(1, 3, figsize=(9, 3))
    _panel_scatter(axs[0], m["skill_reward_slope"], m["amp_slope_lane_diff"],
                   "win-rate slope vs tier", "lane amplification",
                   rho(m["skill_reward_slope"], m["amp_slope_lane_diff"]))
    _panel_scatter(axs[1], m["amp_slope_lane_diff"], m["difficulty"],
                   "lane amplification", "Riot difficulty",
                   rho(m["amp_slope_lane_diff"], m["difficulty"]))
    _panel_scatter(axs[2], m["skill_reward_slope"], m["difficulty"],
                   "win-rate slope vs tier", "Riot difficulty",
                   rho(m["skill_reward_slope"], m["difficulty"]))
    fig.suptitle("Three measures of 'skill expression' are mutually uncorrelated",
                 fontsize=10, y=1.02)
    fig.tight_layout()
    fig.savefig(out / "fig1_three_measures.png")
    plt.close(fig)


def fig2(out: Path, data: Path):
    """Skill reward (role-stratified) vs mechanical difficulty — dissociation."""
    m = pd.read_csv(data / "skill_amplification_p2_5.csv").dropna(subset=["amp_z", "difficulty", "position"])
    fig, ax = plt.subplots(figsize=(5.2, 4))
    for pos, c in POS_COLOR.items():
        s = m[m["position"] == pos]
        jitter = (np.arange(len(s)) % 5 - 2) * 0.04
        ax.scatter(s["difficulty"] + jitter, s["amp_z"], s=22, c=c, alpha=0.8,
                   edgecolor="white", linewidth=0.4, label=pos)
    # annotate a few illustrative champions
    for name in ["Azir", "LeBlanc", "Jax", "Cho'Gath", "Dr. Mundo", "Bard",
                 "Fiddlesticks", "Rek'Sai", "Nidalee"]:
        r = m[m["champion"] == name]
        if len(r):
            ax.annotate(name, (r["difficulty"].iloc[0], r["amp_z"].iloc[0]),
                        fontsize=7, color=INK, xytext=(3, 3),
                        textcoords="offset points")
    ax.set_xlabel("Riot mechanical difficulty (1–10)")
    ax.set_ylabel("skill amplification (role-stratified)")
    ax.set_title("Skill reward is not mechanical difficulty\n(partial Spearman −0.03)",
                 fontsize=10)
    ax.grid(True, color=GRID, lw=0.5); ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=8, loc="lower left", ncol=1)
    fig.savefig(out / "fig2_reward_vs_difficulty.png")
    plt.close(fig)


def fig3(out: Path, data: Path):
    """Ban vs actual power quadrants."""
    m = pd.read_csv(data / "ban_vs_power.csv")
    fig, ax = plt.subplots(figsize=(5.6, 5))
    colors = {"overpowered": "#D55E00", "anti-fun": "#CC79A7",
              "sleeper": "#009E73", "fair": "#BBBBBB"}
    for q, c in colors.items():
        s = m[m["quadrant"] == q]
        ax.scatter(s["win_rate_z"], s["ban_rate_z"], s=20, c=c, alpha=0.8,
                   edgecolor="white", linewidth=0.4, label=q)
    ax.axhline(0, color=MUTED, lw=0.8); ax.axvline(0, color=MUTED, lw=0.8)
    for name in ["Yasuo", "Illaoi", "Tahm Kench", "Darius", "Janna", "Amumu",
                 "Malzahar", "Sona"]:
        r = m[m["champion"] == name]
        if len(r):
            ax.annotate(name, (r["win_rate_z"].iloc[0], r["ban_rate_z"].iloc[0]),
                        fontsize=7, color=INK, xytext=(3, 3), textcoords="offset points")
    ax.set_xlabel("actual power  (win rate, z)")
    ax.set_ylabel("perceived threat  (ban rate, z)")
    ax.set_title("Bans separate perceived from actual power\nanti-fun ≠ overpowered",
                 fontsize=10)
    ax.grid(True, color=GRID, lw=0.5); ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.savefig(out / "fig3_ban_quadrants.png")
    plt.close(fig)


def fig4(out: Path, data: Path):
    """RQ3: mastery reward vs high-tier perceived-imbalance gap."""
    gap = pd.read_csv(data / "perceived_gap_by_tier.csv")
    gap = gap[gap["bucket"] == "high"][["champion", "perceived_minus_actual"]]
    p1 = pd.read_csv(data / "skill_amplification_p1.csv")[["champion", "amp_slope_lane_diff"]]
    m = gap.merge(p1, on="champion").dropna()
    x, y = m["amp_slope_lane_diff"].to_numpy(), m["perceived_minus_actual"].to_numpy()
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.scatter(x, y, s=18, c="#0072B2", alpha=0.6, edgecolor="none")
    b, a = np.polyfit(x, y, 1)
    xs = np.linspace(x.min(), x.max(), 50)
    ax.plot(xs, a + b * xs, color="#D55E00", lw=2)
    rho = float(pd.Series(x).corr(pd.Series(y), method="spearman"))
    ax.set_xlabel("skill amplification (P1, lane)")
    ax.set_ylabel("high-tier perceived − actual gap")
    ax.set_title(f"Mastery-rewarding champions skew anti-fun at high tier\n"
                 f"Spearman {rho:+.2f} (95% CI [0.00, 0.34])", fontsize=10)
    ax.grid(True, color=GRID, lw=0.5); ax.set_axisbelow(True)
    fig.savefig(out / "fig4_rq3_interaction.png")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="analysis/output")
    args = ap.parse_args()
    data = Path(args.out)
    figdir = data / "figures"; figdir.mkdir(parents=True, exist_ok=True)
    fig1(figdir, data); fig2(figdir, data); fig3(figdir, data); fig4(figdir, data)
    print(f"figures -> {figdir}/fig[1-4]_*.png")


if __name__ == "__main__":
    main()
