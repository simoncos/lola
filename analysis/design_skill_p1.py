"""Legacy cross-player general-skill transfer analysis.

P0 measured win-rate vs player TIER, which is confounded: the population
piloting a hard champion at high tier is self-selected (dedicated mains). P1
replaces the tier axis with each player's OWN demonstrated skill, measured on
the champions they are NOT currently being scored on (leave-one-out baseline).

Skill amplification of champion C = weighted slope of
    (a player's performance ON champion C)  vs
    (that player's baseline performance on all their OTHER champions).
A champion has a high transfer slope if players who are good in general (high
baseline) also overperform on C. This conditions on the actual player's
revealed skill rather than a tier bucket, but it does not measure within-player
learning or mastery.

The active mastery analysis is ``python -m analysis.mastery_learning``.

Two metrics:
  - win (participant_win, available for all rows) — matchmaking pulls this to
    ~0.5, so amplification is muted but unbiased.
  - lane_diff = mean(cs_diff + xp_diff per min) over the 0-10 & 10-20 segments
    — a lane-dominance signal far less compressed by matchmaking; the more
    design-meaningful "did this player out-execute their lane opponent" metric.

We then correlate the P1 amplification ranking with the P0 tier-slope ranking:
agreement => the P0 effect was not merely selection; divergence => selection
mattered and P1 is the trustworthy measure.

Usage:
    python analysis/design_skill_p1.py --parquet <dir> [--out analysis/output]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

MIN_PLAYER_GAMES = 15      # total games for a stable leave-one-out baseline
MIN_CELL_GAMES = 3         # games on champion C for a (player, C) cell
MIN_PLAYERS_PER_CHAMP = 80  # qualifying players for a champion to be scored
EARLY = ["zero_to_ten", "ten_to_twenty"]


def lane_diff_metric(parquet: Path) -> pd.DataFrame:
    """Per (match, summoner) early-game lane dominance = cs_diff + xp_diff /min."""
    t = pd.read_parquet(
        parquet / "participant_timelines.parquet",
        columns=["summoner_id", "match_id", "delta",
                 "cs_diff_per_min_delta", "xp_diff_per_min_delta"],
    )
    t = t[t["delta"].isin(EARLY)]
    t["lane_diff"] = t["cs_diff_per_min_delta"].fillna(0) + t["xp_diff_per_min_delta"].fillna(0)
    return (
        t.groupby(["match_id", "summoner_id"])["lane_diff"].mean().reset_index()
    )


def amplification(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    """Leave-one-out baseline + per-champion weighted slope of on-champ vs baseline."""
    # Per-player totals and per-(player,champion) cells
    ptot = df.groupby("summoner_id")[metric].agg(sum="sum", n="count")
    ptot = ptot[ptot["n"] >= MIN_PLAYER_GAMES]
    cell = (
        df[df["summoner_id"].isin(ptot.index)]
        .groupby(["summoner_id", "champion"])[metric]
        .agg(csum="sum", cn="count").reset_index()
    )
    cell = cell[cell["cn"] >= MIN_CELL_GAMES]
    cell = cell.join(ptot, on="summoner_id")
    # leave-one-out baseline: player's mean on OTHER champions
    denom = cell["n"] - cell["cn"]
    cell = cell[denom > 0]
    cell["baseline"] = (cell["sum"] - cell["csum"]) / (cell["n"] - cell["cn"])
    cell["on_champ"] = cell["csum"] / cell["cn"]

    rows = []
    gb0 = df[metric].mean()
    for champ, g in cell.groupby("champion"):
        if len(g) < MIN_PLAYERS_PER_CHAMP:
            continue
        w = g["cn"].to_numpy(float)
        x = g["baseline"].to_numpy(float)
        y = g["on_champ"].to_numpy(float)
        W = w.sum()
        xb = (w * x).sum() / W
        yb = (w * y).sum() / W
        var = (w * (x - xb) ** 2).sum()
        slope = (w * (x - xb) * (y - yb)).sum() / var if var > 0 else np.nan
        rows.append({
            "champion": champ,
            f"amp_slope_{metric}": round(float(slope), 4),
            f"n_players_{metric}": int(len(g)),
            f"mean_on_champ_{metric}": round(float(yb), 4),
        })
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", required=True)
    ap.add_argument("--out", default="analysis/output")
    args = ap.parse_args()
    d = Path(args.parquet)

    parts = pd.read_parquet(
        d / "participants.parquet",
        columns=["match_id", "summoner_id", "champion", "participant_win"],
    ).rename(columns={"participant_win": "win"})

    print("computing win amplification...")
    amp_win = amplification(parts, "win")

    print("computing lane-diff amplification...")
    lane = lane_diff_metric(d)
    parts_lane = parts.merge(lane, on=["match_id", "summoner_id"], how="inner")
    amp_lane = amplification(parts_lane, "lane_diff")

    amp = amp_win.merge(amp_lane, on="champion", how="outer")

    # Correlate with P0 tier-slope if available
    p0_path = Path(args.out) / "skill_expression.csv"
    corr = {}
    if p0_path.exists():
        p0 = pd.read_csv(p0_path)[["champion", "skill_reward_slope"]]
        m = amp.merge(p0, on="champion", how="inner")
        for col in ["amp_slope_win", "amp_slope_lane_diff"]:
            sub = m[[col, "skill_reward_slope"]].dropna()
            if len(sub) > 5:
                corr[f"{col}_vs_P0_tier_slope_spearman"] = round(
                    float(sub[col].corr(sub["skill_reward_slope"], method="spearman")), 4
                )
        corr["n_champions_compared"] = int(len(m.dropna(subset=["amp_slope_win"])))

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    amp_sorted = amp.sort_values("amp_slope_lane_diff", ascending=False)
    amp_sorted.to_csv(out_dir / "skill_amplification_p1.csv", index=False)

    top = amp.dropna(subset=["amp_slope_lane_diff"]).sort_values(
        "amp_slope_lane_diff", ascending=False)
    summary = {
        "status": "legacy_exploratory_transfer_not_mastery",
        "interpretation": "Cross-player general-skill transfer; not learning or mastery.",
        "config": {"min_player_games": MIN_PLAYER_GAMES,
                   "min_cell_games": MIN_CELL_GAMES,
                   "min_players_per_champ": MIN_PLAYERS_PER_CHAMP},
        "champions_scored": int(len(top)),
        "correlation_with_P0": corr,
        "top10_lane_diff_amplifiers": top.head(10)[
            ["champion", "amp_slope_lane_diff", "amp_slope_win", "n_players_lane_diff"]
        ].to_dict("records"),
        "bottom10_lane_diff_amplifiers": top.tail(10)[
            ["champion", "amp_slope_lane_diff", "amp_slope_win", "n_players_lane_diff"]
        ].to_dict("records"),
    }
    (out_dir / "design_p1.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))

    md = [
        "# Legacy P1: Cross-Player General-Skill Transfer (prototype)",
        "",
        "> **Not a mastery or learning estimate.** Use mastery_learning.py for the",
        "> active within-player, within-champion analysis.",
        "",
        "General-skill transfer = weighted slope of a player's on-champion performance",
        "vs their leave-one-out baseline on all other champions. Conditions on each",
        "player's revealed skill instead of tier, reducing one cross-tier selection",
        "problem while remaining a cross-sectional association.",
        "",
        f"Config: players with >= {MIN_PLAYER_GAMES} games, cells with >= "
        f"{MIN_CELL_GAMES} games, champions with >= {MIN_PLAYERS_PER_CHAMP} players. "
        f"{len(top)} champions scored.",
        "",
        "## Correlation with P0 tier-slope ranking",
        "",
    ]
    for k, v in corr.items():
        md.append(f"- {k}: {v}")
    md += ["", "## Top 10 transfer slopes (lane-dominance metric)", "",
           "| Champion | amp slope (lane) | amp slope (win) | players |",
           "|---|---|---|---|"]
    for r in summary["top10_lane_diff_amplifiers"]:
        md.append(f"| {r['champion']} | {r['amp_slope_lane_diff']:+.3f} "
                  f"| {r['amp_slope_win']:+.3f} | {r['n_players_lane_diff']} |")
    md += ["", "## Bottom 10 transfer slopes", "",
           "| Champion | amp slope (lane) | amp slope (win) | players |",
           "|---|---|---|---|"]
    for r in summary["bottom10_lane_diff_amplifiers"]:
        md.append(f"| {r['champion']} | {r['amp_slope_lane_diff']:+.3f} "
                  f"| {r['amp_slope_win']:+.3f} | {r['n_players_lane_diff']} |")
    md.append("")
    (out_dir / "design_p1.md").write_text("\n".join(md))
    print(f"reports -> {out_dir}/design_p1.{{md,json}}, skill_amplification_p1.csv")
    print("correlation with P0:", corr)
    print("top lane amplifiers:", [r["champion"] for r in summary["top10_lane_diff_amplifiers"][:5]])


if __name__ == "__main__":
    main()
