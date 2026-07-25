"""Legacy P0 prototype retained for audit history.

The tier slope is not mastery, and ban-minus-win is not evidence of anti-fun,
fairness, perceived power, or player motives. Active analyses are
``analysis.mastery_learning`` and ``analysis.design_p2``.

Two design-facing measurements on real data, both riding the per-player tier label:

RQ1 - Skill expression: for each champion, how does win rate rise with the
      operator's previous-season tier? The slope of win-rate vs ordinal tier is
      a "mastery reward" index. Also reports low-tier vs high-tier win-rate gap.

RQ2 - Bans as perceived power: ban rate per champion vs actual win rate. The
      standardized gap (ban_z - win_z) separates 'anti-fun' (banned but not
      strong) from 'sleeper' (strong but rarely banned).

Prototype caveats (see PROPOSAL): no selection-confound correction yet (players
who pick a champion differ by tier), no positional model for bans, single
performance metric (win). Paper-grade version adds mixed-effects + same-player
cross-tier controls + conditional-logit ban model.

Usage:
    python analysis/design_skill_and_bans.py --parquet <dir> [--out analysis/output]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

# Ordinal tier scale (Unranked excluded from the slope; reported separately).
TIER_ORDINAL = {
    "BRONZE": 0, "SILVER": 1, "GOLD": 2, "PLATINUM": 3,
    "DIAMOND": 4, "MASTER": 5, "CHALLENGER": 6,
}
TIER_BUCKET = {
    "BRONZE": "low", "SILVER": "low",
    "GOLD": "mid", "PLATINUM": "mid",
    "DIAMOND": "high", "MASTER": "high", "CHALLENGER": "high",
}
MIN_PICKS_PER_TIER = 50   # per champion-tier cell to enter the slope fit
MIN_TOTAL_PICKS = 2000


def skill_expression(parts: pd.DataFrame) -> pd.DataFrame:
    """Per-champion weighted least-squares slope of win rate vs ordinal tier."""
    parts = parts[parts["previous_season_tier"].isin(TIER_ORDINAL)].copy()
    parts["t"] = parts["previous_season_tier"].map(TIER_ORDINAL)

    cell = (
        parts.groupby(["champion", "t"])["participant_win"]
        .agg(wins="sum", n="count").reset_index()
    )
    cell = cell[cell["n"] >= MIN_PICKS_PER_TIER]
    cell["wr"] = cell["wins"] / cell["n"]

    rows = []
    for champ, g in cell.groupby("champion"):
        if g["t"].nunique() < 4 or g["n"].sum() < MIN_TOTAL_PICKS:
            continue
        # weighted linear fit wr ~ t, weights = cell size
        w = g["n"].to_numpy(float)
        t = g["t"].to_numpy(float)
        y = g["wr"].to_numpy(float)
        W = w.sum()
        tbar = (w * t).sum() / W
        ybar = (w * y).sum() / W
        cov = (w * (t - tbar) * (y - ybar)).sum()
        var = (w * (t - tbar) ** 2).sum()
        slope = cov / var if var > 0 else np.nan
        # low vs high bucket win rates
        gb = g.assign(bucket=g["t"].map(lambda x: "low" if x <= 1 else
                                        ("mid" if x <= 3 else "high")))
        bw = gb.groupby("bucket").apply(
            lambda d: d["wins"].sum() / d["n"].sum(), include_groups=False
        )
        rows.append({
            "champion": champ,
            "skill_reward_slope": round(float(slope), 5),
            "wr_low": round(float(bw.get("low", np.nan)), 4),
            "wr_high": round(float(bw.get("high", np.nan)), 4),
            "high_minus_low": round(float(bw.get("high", np.nan) - bw.get("low", np.nan)), 4),
            "total_picks": int(g["n"].sum()),
        })
    return pd.DataFrame(rows).sort_values("skill_reward_slope", ascending=False)


def ban_vs_power(parts: pd.DataFrame, bans: pd.DataFrame, n_matches: int) -> pd.DataFrame:
    picks = parts.groupby("champion").agg(
        picks=("participant_win", "count"),
        wins=("participant_win", "sum"),
    )
    picks["win_rate"] = picks["wins"] / picks["picks"]
    ban_counts = bans.groupby("ban").size().rename("bans")
    df = picks.join(ban_counts).fillna({"bans": 0})
    df["ban_rate"] = df["bans"] / n_matches          # per match (10 ban slots)
    df["pick_rate"] = df["picks"] / (n_matches * 10)

    for col in ["ban_rate", "win_rate"]:
        df[col + "_z"] = (df[col] - df[col].mean()) / df[col].std()
    df["perceived_minus_actual"] = df["ban_rate_z"] - df["win_rate_z"]

    def quad(r):
        strong = r["win_rate_z"] > 0
        banned = r["ban_rate_z"] > 0
        return {(True, True): "overpowered", (False, True): "anti-fun",
                (True, False): "sleeper", (False, False): "fair"}[(strong, banned)]
    df["quadrant"] = df.apply(quad, axis=1)
    return df.reset_index().sort_values("perceived_minus_actual", ascending=False)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", required=True)
    ap.add_argument("--out", default="analysis/output")
    args = ap.parse_args()

    d = Path(args.parquet)
    parts = pd.read_parquet(
        d / "participants.parquet",
        columns=["match_id", "champion", "previous_season_tier", "participant_win"],
    )
    bans = pd.read_parquet(d / "team_bans.parquet", columns=["match_id", "ban"])
    n_matches = pd.read_parquet(d / "matches.parquet", columns=["match_id"]).shape[0]

    skill = skill_expression(parts)
    bp = ban_vs_power(parts, bans, n_matches)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    skill.to_csv(out_dir / "skill_expression.csv", index=False)
    bp.to_csv(out_dir / "ban_vs_power.csv", index=False)

    quad_counts = bp["quadrant"].value_counts().to_dict()
    summary = {
        "status": "legacy_exploratory_not_citable",
        "interpretation": (
            "Tier slope is not mastery; ban-minus-win does not identify anti-fun, "
            "fairness, perception, or motive."
        ),
        "champions_scored_skill": int(len(skill)),
        "skill_reward_top10": skill.head(10)[
            ["champion", "skill_reward_slope", "wr_low", "wr_high"]
        ].to_dict("records"),
        "skill_reward_bottom10": skill.tail(10)[
            ["champion", "skill_reward_slope", "wr_low", "wr_high"]
        ].to_dict("records"),
        "quadrant_counts": quad_counts,
        "most_anti_fun": bp[bp["quadrant"] == "anti-fun"].head(10)[
            ["champion", "ban_rate", "win_rate", "perceived_minus_actual"]
        ].round(4).to_dict("records"),
        "biggest_sleepers": bp[bp["quadrant"] == "sleeper"].tail(10)[
            ["champion", "ban_rate", "win_rate", "perceived_minus_actual"]
        ].round(4).to_dict("records"),
    }
    (out_dir / "design_p0.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))

    md = [
        "# Legacy P0 Prototype (not citable)",
        "",
        "> Tier slope is not mastery; ban-minus-win is descriptive salience only.",
        "",
        f"Real data, {n_matches:,} matches. Win-based single metric; no confound "
        "correction yet (see PROPOSAL caveats).",
        "",
        "## RQ1 — Champions that most reward mastery (win-rate slope vs tier)",
        "",
        "| Champion | slope (WR per tier step) | WR low (Bronze/Silver) | WR high (Diamond+) |",
        "|---|---|---|---|",
    ]
    for r in summary["skill_reward_top10"]:
        md.append(f"| {r['champion']} | {r['skill_reward_slope']:+.4f} "
                  f"| {r['wr_low']:.3f} | {r['wr_high']:.3f} |")
    md += ["", "### Champions that punish (or don't reward) skill — bottom 10", "",
           "| Champion | slope | WR low | WR high |", "|---|---|---|---|"]
    for r in summary["skill_reward_bottom10"]:
        md.append(f"| {r['champion']} | {r['skill_reward_slope']:+.4f} "
                  f"| {r['wr_low']:.3f} | {r['wr_high']:.3f} |")
    md += ["", "## RQ2 — Ban vs actual power quadrants", "",
           f"Counts: {quad_counts}", "",
           "### Most 'anti-fun' (banned hard, not actually strong)", "",
           "| Champion | ban rate | win rate | perceived−actual |", "|---|---|---|---|"]
    for r in summary["most_anti_fun"]:
        md.append(f"| {r['champion']} | {r['ban_rate']:.3f} | {r['win_rate']:.3f} "
                  f"| {r['perceived_minus_actual']:+.3f} |")
    md += ["", "### Biggest 'sleepers' (strong, rarely banned)", "",
           "| Champion | ban rate | win rate | perceived−actual |", "|---|---|---|---|"]
    for r in summary["biggest_sleepers"]:
        md.append(f"| {r['champion']} | {r['ban_rate']:.3f} | {r['win_rate']:.3f} "
                  f"| {r['perceived_minus_actual']:+.3f} |")
    md.append("")
    (out_dir / "design_p0.md").write_text("\n".join(md))
    print(f"reports -> {out_dir}/design_p0.{{md,json}}, skill_expression.csv, ban_vs_power.csv")
    print("skill top3:", [r["champion"] for r in summary["skill_reward_top10"][:3]])
    print("anti-fun top3:", [r["champion"] for r in summary["most_anti_fun"][:3]])
    print("quadrants:", quad_counts)


if __name__ == "__main__":
    main()
