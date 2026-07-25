"""Legacy position-specific general-skill transfer analysis.

P2 external validation found the lane-diff amplification is role-sensitive:
junglers score high because cs/xp-diff means something different for them, and
supports are unscorable on farm. This version both standardizes within
``(build, position)`` and computes each player's leave-one-champion-out baseline
within the same position. Earlier output only did the first step and was not
truly role-stratified.

This remains a cross-player transfer analysis, not a mastery/learning estimate.
Use ``analysis.mastery_learning`` for the active mastery construct.

Position is assigned from the (lane, role) timeline fields, which map cleanly to
the 5 canonical positions for ~96% of participants:
    JUNGLE/NONE->jungle, TOP/SOLO->top, MIDDLE/SOLO->mid,
    BOTTOM/DUO_CARRY->adc, BOTTOM/DUO_SUPPORT->support.

Usage:
    python analysis/design_p2_5.py --parquet <dir> [--out analysis/output]
                                   --difficulty analysis/riot_difficulty_ddragon.csv
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from lola_dataset.cohort import eligible_matches, filter_to_eligible

POSITION = {
    ("JUNGLE", "NONE"): "jungle",
    ("TOP", "SOLO"): "top",
    ("MIDDLE", "SOLO"): "mid",
    ("BOTTOM", "DUO_CARRY"): "adc",
    ("BOTTOM", "DUO_SUPPORT"): "support",
}
EARLY = ["zero_to_ten", "ten_to_twenty"]
MIN_PLAYER_GAMES = 15
MIN_CELL_GAMES = 3
MIN_PLAYERS_PER_CHAMP_POSITION = 30
REWORKED = {"Aatrox", "Akali", "Dr. Mundo", "Evelynn", "Fiddlesticks", "Galio",
            "Irelia", "Kayle", "Mordekaiser", "Morgana", "Nunu", "Pantheon",
            "Ryze", "Skarner", "Swain", "Taric", "Udyr", "Urgot", "Volibear",
            "Warwick", "Yorick"}


def build_metric(parquet: Path) -> pd.DataFrame:
    """(match, summoner) -> position + position-normalized lane dominance."""
    cohort = eligible_matches(parquet, min_duration=20)
    t = pd.read_parquet(
        parquet / "participant_timelines.parquet",
        columns=["summoner_id", "match_id", "delta", "role", "lane",
                 "cs_diff_per_min_delta", "xp_diff_per_min_delta"])
    t = filter_to_eligible(t, cohort)
    pos = t[t["delta"] == "zero_to_ten"].copy()
    pos["position"] = [POSITION.get((l, r)) for l, r in zip(pos["lane"], pos["role"])]
    pos = pos[["match_id", "summoner_id", "position"]].dropna()

    early = t[t["delta"].isin(EARLY)].copy()
    early["lane_diff"] = early[
        ["cs_diff_per_min_delta", "xp_diff_per_min_delta"]
    ].sum(axis=1, min_count=2)
    lane = early.groupby(["match_id", "summoner_id"], as_index=False).agg(
        lane_diff=("lane_diff", "mean"),
        observed_early_segments=("lane_diff", "count"),
    )
    lane = lane[lane["observed_early_segments"] == len(EARLY)]

    df = (
        lane.merge(pos, on=["match_id", "summoner_id"], how="inner")
        .merge(cohort[["match_id", "version"]], on="match_id", validate="many_to_one")
    )
    # Standardize within build and position to avoid patch and role level shifts.
    g = df.groupby(["version", "position"])["lane_diff"]
    df["lane_z"] = (df["lane_diff"] - g.transform("mean")) / g.transform("std")
    return df


def amplification(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    player_position = ["summoner_id", "position"]
    ptot = df.groupby(player_position)[metric].agg(sum="sum", n="count")
    ptot = ptot[ptot["n"] >= MIN_PLAYER_GAMES].reset_index()
    eligible_keys = ptot[player_position]
    eligible = df.merge(eligible_keys, on=player_position, how="inner")
    cell = (eligible
            .groupby(["summoner_id", "position", "champion"])[metric]
            .agg(csum="sum", cn="count").reset_index())
    cell = cell[cell["cn"] >= MIN_CELL_GAMES].merge(
        ptot, on=player_position, validate="many_to_one"
    )
    cell = cell[(cell["n"] - cell["cn"]) > 0]
    cell["baseline"] = (cell["sum"] - cell["csum"]) / (cell["n"] - cell["cn"])
    cell["on_champ"] = cell["csum"] / cell["cn"]
    rows = []
    for (champ, position), gg in cell.groupby(["champion", "position"]):
        if len(gg) < MIN_PLAYERS_PER_CHAMP_POSITION:
            continue
        w = gg["cn"].to_numpy(float); x = gg["baseline"].to_numpy(float)
        y = gg["on_champ"].to_numpy(float); W = w.sum()
        xb = (w * x).sum() / W; yb = (w * y).sum() / W
        var = (w * (x - xb) ** 2).sum()
        slope = (w * (x - xb) * (y - yb)).sum() / var if var > 0 else np.nan
        rows.append({"champion": champ, "position": position,
                     "transfer_slope_z": round(float(slope), 4),
                     "n_players": int(len(gg))})
    return pd.DataFrame(rows)


def sp(a, b):
    s = pd.DataFrame({"a": a, "b": b}).dropna()
    return (round(float(s["a"].corr(s["b"], method="spearman")), 3), len(s)) if len(s) > 5 else (None, len(s))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", required=True)
    ap.add_argument("--out", default="analysis/output")
    ap.add_argument("--difficulty", default="analysis/riot_difficulty_ddragon.csv")
    args = ap.parse_args()
    d = Path(args.parquet)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    cohort = eligible_matches(d, min_duration=20)

    parts = pd.read_parquet(d / "participants.parquet",
                            columns=["match_id", "summoner_id", "champion"])
    parts = filter_to_eligible(parts, cohort)
    metric = build_metric(d)
    df = parts.merge(metric, on=["match_id", "summoner_id"], how="inner")

    amp = amplification(df, "lane_z")

    diff = pd.read_csv(args.difficulty)
    diff.columns = ["champion", "difficulty"]
    amp = amp.merge(diff, on="champion", how="left")
    amp = amp.sort_values(["position", "transfer_slope_z"], ascending=[True, False])
    amp.to_csv(out_dir / "skill_amplification_p2_5.csv", index=False)

    # validation vs difficulty: overall, per position, position-residualized
    overall = sp(amp["transfer_slope_z"], amp["difficulty"])
    no_rework = amp[~amp["champion"].isin(REWORKED)]
    overall_nr = sp(no_rework["transfer_slope_z"], no_rework["difficulty"])
    per_pos = {}
    for pos in ["top", "mid", "adc", "jungle", "support"]:
        sub = amp[amp["position"] == pos]
        per_pos[pos] = {
            "spearman": sp(sub["transfer_slope_z"], sub["difficulty"])[0],
            "n": int(sub["transfer_slope_z"].notna().sum()),
        }

    def top_by_pos(pos, k=6):
        s = amp[amp["position"] == pos].sort_values(
            "transfer_slope_z", ascending=False
        )
        return [{"champion": r.champion, "transfer_slope_z": r.transfer_slope_z,
                 "difficulty": (None if pd.isna(r.difficulty) else int(r.difficulty))}
                for r in s.head(k).itertuples()]

    summary = {
        "status": "legacy_exploratory_transfer_not_mastery",
        "interpretation": "Position-specific cross-player transfer; not learning or mastery.",
        "champion_position_cells_scored": int(len(amp)),
        "validation_vs_riot_difficulty": {
            "overall": {"spearman": overall[0], "n": overall[1]},
            "overall_excl_reworked": {"spearman": overall_nr[0], "n": overall_nr[1]},
            "per_position": per_pos,
        },
        "top_transfer_slopes_by_position": {p: top_by_pos(p)
                                       for p in ["top", "mid", "adc", "jungle", "support"]},
    }
    (out_dir / "design_p2_5.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False))

    md = ["# Legacy P2.5: Position-Specific General-Skill Transfer", "",
          "> This is not a mastery or learning estimate.", "",
          "Lane dominance is z-scored within build and position. Each player's",
          "leave-one-champion-out baseline is also computed within position.", "",
          "## Validation vs Riot difficulty (was 0.09, role-confounded, in P2)", "",
          f"- Overall: Spearman {overall[0]} (n={overall[1]})",
          f"- Excl. 21 reworked: {overall_nr[0]} (n={overall_nr[1]})",
          "Per-position Spearman(amp, difficulty):"]
    for p, v in per_pos.items():
        md.append(f"- {p}: {v['spearman']} (n={v['n']})")
    md += ["", "## Top transfer slopes by position", ""]
    for p in ["top", "mid", "adc", "jungle", "support"]:
        names = ", ".join(
            f"{r['champion']} (slope {r['transfer_slope_z']:+.2f}, diff "
            f"{r['difficulty']})"
            for r in summary["top_transfer_slopes_by_position"][p]
        )
        md.append(f"- **{p}**: {names}")
    md.append("")
    (out_dir / "design_p2_5.md").write_text("\n".join(md))
    print("reports -> design_p2_5.{md,json}, skill_amplification_p2_5.csv")
    print("overall vs difficulty:", overall)
    print("per-position:", {p: v["spearman"] for p, v in per_pos.items()})


if __name__ == "__main__":
    main()
