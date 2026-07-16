"""P2.5: role-stratified skill amplification (removes the position confound).

P2 external validation found the lane-diff amplification is role-sensitive:
junglers score high because cs/xp-diff means something different for them, and
supports are unscorable on farm. Fix: standardize the lane-dominance metric
WITHIN position (z-score per position) before measuring amplification, so each
champion's players are compared to same-position peers. Then validate against
Riot difficulty per position and with position controlled.

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
MIN_PLAYERS_PER_CHAMP = 60
REWORKED = {"Aatrox", "Akali", "Dr. Mundo", "Evelynn", "Fiddlesticks", "Galio",
            "Irelia", "Kayle", "Mordekaiser", "Morgana", "Nunu", "Pantheon",
            "Ryze", "Skarner", "Swain", "Taric", "Udyr", "Urgot", "Volibear",
            "Warwick", "Yorick"}


def build_metric(parquet: Path) -> pd.DataFrame:
    """(match, summoner) -> position + position-normalized lane dominance."""
    t = pd.read_parquet(
        parquet / "participant_timelines.parquet",
        columns=["summoner_id", "match_id", "delta", "role", "lane",
                 "cs_diff_per_min_delta", "xp_diff_per_min_delta"])
    pos = t[t["delta"] == "zero_to_ten"].copy()
    pos["position"] = [POSITION.get((l, r)) for l, r in zip(pos["lane"], pos["role"])]
    pos = pos[["match_id", "summoner_id", "position"]].dropna()

    early = t[t["delta"].isin(EARLY)].copy()
    early["lane_diff"] = (early["cs_diff_per_min_delta"].fillna(0)
                          + early["xp_diff_per_min_delta"].fillna(0))
    lane = early.groupby(["match_id", "summoner_id"])["lane_diff"].mean().reset_index()

    df = lane.merge(pos, on=["match_id", "summoner_id"], how="inner")
    # standardize lane dominance WITHIN position -> removes level shift
    g = df.groupby("position")["lane_diff"]
    df["lane_z"] = (df["lane_diff"] - g.transform("mean")) / g.transform("std")
    return df


def amplification(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    ptot = df.groupby("summoner_id")[metric].agg(sum="sum", n="count")
    ptot = ptot[ptot["n"] >= MIN_PLAYER_GAMES]
    cell = (df[df["summoner_id"].isin(ptot.index)]
            .groupby(["summoner_id", "champion"])[metric]
            .agg(csum="sum", cn="count").reset_index())
    cell = cell[cell["cn"] >= MIN_CELL_GAMES].join(ptot, on="summoner_id")
    cell = cell[(cell["n"] - cell["cn"]) > 0]
    cell["baseline"] = (cell["sum"] - cell["csum"]) / (cell["n"] - cell["cn"])
    cell["on_champ"] = cell["csum"] / cell["cn"]
    rows = []
    for champ, gg in cell.groupby("champion"):
        if len(gg) < MIN_PLAYERS_PER_CHAMP:
            continue
        w = gg["cn"].to_numpy(float); x = gg["baseline"].to_numpy(float)
        y = gg["on_champ"].to_numpy(float); W = w.sum()
        xb = (w * x).sum() / W; yb = (w * y).sum() / W
        var = (w * (x - xb) ** 2).sum()
        slope = (w * (x - xb) * (y - yb)).sum() / var if var > 0 else np.nan
        rows.append({"champion": champ, "amp_z": round(float(slope), 4),
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

    parts = pd.read_parquet(d / "participants.parquet",
                            columns=["match_id", "summoner_id", "champion"])
    metric = build_metric(d)
    df = parts.merge(metric, on=["match_id", "summoner_id"], how="inner")

    amp = amplification(df, "lane_z")
    # champion primary position (mode)
    prim = (df.groupby(["champion", "position"]).size().reset_index(name="n")
            .sort_values("n", ascending=False).drop_duplicates("champion"))
    amp = amp.merge(prim[["champion", "position"]], on="champion", how="left")

    diff = pd.read_csv(args.difficulty)
    diff.columns = ["champion", "difficulty"]
    amp = amp.merge(diff, on="champion", how="left")
    amp = amp.sort_values("amp_z", ascending=False)
    amp.to_csv(Path(args.out) / "skill_amplification_p2_5.csv", index=False)

    # validation vs difficulty: overall, per position, position-residualized
    overall = sp(amp["amp_z"], amp["difficulty"])
    no_rework = amp[~amp["champion"].isin(REWORKED)]
    overall_nr = sp(no_rework["amp_z"], no_rework["difficulty"])
    per_pos = {}
    for pos in ["top", "mid", "adc", "jungle", "support"]:
        sub = amp[amp["position"] == pos]
        per_pos[pos] = {"spearman": sp(sub["amp_z"], sub["difficulty"])[0],
                        "n": int(sub["amp_z"].notna().sum())}
    # position-controlled: residualize both on position means, correlate residuals
    a2 = amp.dropna(subset=["amp_z", "difficulty", "position"]).copy()
    a2["amp_res"] = a2["amp_z"] - a2.groupby("position")["amp_z"].transform("mean")
    a2["dif_res"] = a2["difficulty"] - a2.groupby("position")["difficulty"].transform("mean")
    partial = sp(a2["amp_res"], a2["dif_res"])

    def top_by_pos(pos, k=6):
        s = amp[amp["position"] == pos].sort_values("amp_z", ascending=False)
        return [{"champion": r.champion, "amp_z": r.amp_z,
                 "difficulty": (None if pd.isna(r.difficulty) else int(r.difficulty))}
                for r in s.head(k).itertuples()]

    summary = {
        "champions_scored": int(len(amp)),
        "validation_vs_riot_difficulty": {
            "overall": {"spearman": overall[0], "n": overall[1]},
            "overall_excl_reworked": {"spearman": overall_nr[0], "n": overall_nr[1]},
            "per_position": per_pos,
            "position_controlled_partial": {"spearman": partial[0], "n": partial[1]},
        },
        "top_amplifiers_by_position": {p: top_by_pos(p)
                                       for p in ["top", "mid", "adc", "jungle", "support"]},
    }
    (Path(args.out) / "design_p2_5.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False))

    md = ["# P2.5: Role-Stratified Skill Amplification", "",
          "Lane dominance is z-scored WITHIN position before measuring skill",
          "amplification, so champions are compared to same-position peers.", "",
          "## Validation vs Riot difficulty (was 0.09, role-confounded, in P2)", "",
          f"- Overall: Spearman {overall[0]} (n={overall[1]})",
          f"- Excl. 21 reworked: {overall_nr[0]} (n={overall_nr[1]})",
          f"- **Position-controlled partial: {partial[0]} (n={partial[1]})**", "",
          "Per-position Spearman(amp, difficulty):"]
    for p, v in per_pos.items():
        md.append(f"- {p}: {v['spearman']} (n={v['n']})")
    md += ["", "## Top skill amplifiers by position (role-fair)", ""]
    for p in ["top", "mid", "adc", "jungle", "support"]:
        names = ", ".join(f"{r['champion']} (amp {r['amp_z']:+.2f}, diff "
                          f"{r['difficulty']})" for r in summary["top_amplifiers_by_position"][p])
        md.append(f"- **{p}**: {names}")
    md.append("")
    (Path(args.out) / "design_p2_5.md").write_text("\n".join(md))
    print("reports -> design_p2_5.{md,json}, skill_amplification_p2_5.csv")
    print("overall vs difficulty:", overall, "| position-controlled partial:", partial)
    print("per-position:", {p: v["spearman"] for p, v in per_pos.items()})


if __name__ == "__main__":
    main()
