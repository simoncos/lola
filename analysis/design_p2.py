"""P2 for the design paper: tier-resolved perceived imbalance + RQ3 interaction.

Builds on P1 (skill amplification). Two parts, both bootstrapped:

RQ2b - Perceived vs actual power BY TIER BUCKET. Ban rate and win rate per
       champion computed within low / mid / high tier populations; the
       standardized gap (ban_z - win_z) is the perceived-imbalance signal.
       We test whether the anti-fun signal sharpens or softens with skill
       (high-tier players have better information about true power).

RQ3  - Interaction: do champions that reward mastery (high P1 lane-amplification)
       get banned as if unfair, especially in high tier? Correlate P1
       amplification with the high-tier perceived-minus-actual gap, with a
       champion-bootstrap CI.

Bans in this era are team-global (not role-slotted), so raw ban rate per match
is an unbiased perceived-threat measure; no positional choice model needed for
the ban side (unlike picks). Win rate is the actual-power proxy (matchmaking
compresses it toward 0.5, which is conservative for the gap).

Usage:
    python analysis/design_p2.py --parquet <dir> [--out analysis/output]
                                 [--difficulty <csv>]  # optional Riot labels
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

TIER_BUCKET = {
    "BRONZE": "low", "SILVER": "low",
    "GOLD": "mid", "PLATINUM": "mid",
    "DIAMOND": "high", "MASTER": "high", "CHALLENGER": "high",
}
MIN_PICKS = 200  # per champion-bucket to be scored


def match_tier_bucket(parts: pd.DataFrame) -> pd.DataFrame:
    """Majority previous-season tier bucket per match."""
    b = parts.copy()
    b["bucket"] = b["previous_season_tier"].map(TIER_BUCKET)
    b = b.dropna(subset=["bucket"])
    maj = (
        b.groupby(["match_id", "bucket"]).size().reset_index(name="n")
        .sort_values("n", ascending=False).drop_duplicates("match_id")
    )
    return maj[["match_id", "bucket"]].rename(columns={"bucket": "match_bucket"})


def gaps_by_bucket(parts: pd.DataFrame, bans: pd.DataFrame,
                   mtb: pd.DataFrame) -> pd.DataFrame:
    parts = parts.merge(mtb, on="match_id", how="inner")
    bans = bans.merge(mtb, on="match_id", how="inner")
    n_by_bucket = mtb["match_bucket"].value_counts().to_dict()

    rows = []
    for bucket in ["low", "mid", "high"]:
        p = parts[parts["match_bucket"] == bucket]
        bn = bans[bans["match_bucket"] == bucket]
        n_matches = n_by_bucket.get(bucket, 0)
        picks = p.groupby("champion").agg(
            picks=("participant_win", "count"), wins=("participant_win", "sum"))
        picks["win_rate"] = picks["wins"] / picks["picks"]
        ban_ct = bn.groupby("ban").size().rename("bans")
        df = picks.join(ban_ct).fillna({"bans": 0})
        df = df[df["picks"] >= MIN_PICKS]
        df["ban_rate"] = df["bans"] / n_matches
        for c in ["ban_rate", "win_rate"]:
            df[c + "_z"] = (df[c] - df[c].mean()) / df[c].std()
        df["perceived_minus_actual"] = df["ban_rate_z"] - df["win_rate_z"]
        df["bucket"] = bucket
        rows.append(df.reset_index()[
            ["champion", "bucket", "picks", "win_rate", "ban_rate",
             "perceived_minus_actual"]])
    return pd.concat(rows, ignore_index=True)


def boot_corr(x: np.ndarray, y: np.ndarray, reps: int = 2000,
              seed: int = 3) -> dict:
    rng = np.random.default_rng(seed)
    n = len(x)
    point = float(pd.Series(x).corr(pd.Series(y), method="spearman"))
    est = []
    for _ in range(reps):
        idx = rng.integers(0, n, n)
        est.append(pd.Series(x[idx]).corr(pd.Series(y[idx]), method="spearman"))
    lo, hi = np.nanpercentile(est, [2.5, 97.5])
    return {"spearman": round(point, 4),
            "ci95": [round(float(lo), 4), round(float(hi), 4)],
            "n": int(n)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", required=True)
    ap.add_argument("--out", default="analysis/output")
    ap.add_argument("--difficulty", help="optional CSV: champion,difficulty")
    args = ap.parse_args()
    d = Path(args.parquet)

    parts = pd.read_parquet(
        d / "participants.parquet",
        columns=["match_id", "champion", "previous_season_tier", "participant_win"])
    bans = pd.read_parquet(d / "team_bans.parquet", columns=["match_id", "ban"])

    mtb = match_tier_bucket(parts)
    gaps = gaps_by_bucket(parts, bans, mtb)
    gaps.to_csv(Path(args.out) / "perceived_gap_by_tier.csv", index=False)

    wide = gaps.pivot(index="champion", columns="bucket",
                      values="perceived_minus_actual")

    # RQ3: P1 amplification vs high-tier perceived-imbalance
    rq3 = {}
    p1_path = Path(args.out) / "skill_amplification_p1.csv"
    if p1_path.exists() and "high" in wide.columns:
        p1 = pd.read_csv(p1_path)[["champion", "amp_slope_lane_diff"]]
        m = wide.reset_index().merge(p1, on="champion").dropna(
            subset=["high", "amp_slope_lane_diff"])
        if len(m) > 10:
            rq3["amp_vs_high_tier_perceived_gap"] = boot_corr(
                m["amp_slope_lane_diff"].to_numpy(), m["high"].to_numpy())

    # Optional external validation vs Riot difficulty
    ext = {}
    if args.difficulty and Path(args.difficulty).exists():
        diff = pd.read_csv(args.difficulty)
        diff.columns = ["champion", "difficulty"]
        if p1_path.exists():
            p1 = pd.read_csv(p1_path)[["champion", "amp_slope_lane_diff"]]
            m = p1.merge(diff, on="champion").dropna()
            if len(m) > 10:
                ext["p1_amp_vs_riot_difficulty"] = boot_corr(
                    m["amp_slope_lane_diff"].to_numpy(),
                    m["difficulty"].to_numpy().astype(float))

    # tier-shift of the anti-fun signal: correlation of gap across buckets
    shift = {}
    for a, b in [("low", "mid"), ("mid", "high"), ("low", "high")]:
        if a in wide.columns and b in wide.columns:
            s = wide[[a, b]].dropna()
            shift[f"{a}_vs_{b}"] = round(
                float(s[a].corr(s[b], method="spearman")), 4)

    def top(bucket, k=8, worst=True):
        if bucket not in wide.columns:
            return []
        s = wide[bucket].dropna().sort_values(ascending=not worst)
        return [{"champion": c, "gap": round(float(v), 3)} for c, v in s.head(k).items()]

    summary = {
        "min_picks_per_cell": MIN_PICKS,
        "perceived_gap_tier_shift_spearman": shift,
        "most_anti_fun_by_tier": {b: top(b, worst=True) for b in ["low", "mid", "high"]},
        "biggest_sleepers_by_tier": {b: top(b, worst=False) for b in ["low", "mid", "high"]},
        "RQ3_amplification_vs_high_tier_anti_fun": rq3,
        "external_validation": ext,
    }
    (Path(args.out) / "design_p2.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False))

    md = ["# P2: Tier-Resolved Perceived Imbalance & RQ3 Interaction", "",
          f"Per-tier-bucket ban-vs-win gaps (>= {MIN_PICKS} picks/cell), "
          "champion-bootstrapped.", "",
          "## Perceived-imbalance signal stability across tiers (Spearman)", ""]
    for k, v in shift.items():
        md.append(f"- {k}: {v}")
    md += ["", "## Most 'anti-fun' by tier (banned relative to actual win rate)", ""]
    for b in ["low", "mid", "high"]:
        names = ", ".join(f"{r['champion']} ({r['gap']:+.2f})"
                          for r in summary["most_anti_fun_by_tier"][b])
        md.append(f"- **{b}**: {names}")
    md += ["", "## RQ3 — does rewarding mastery read as unfair in high tier?", ""]
    if rq3:
        r = rq3["amp_vs_high_tier_perceived_gap"]
        md.append(f"- P1 lane-amplification vs high-tier perceived gap: "
                  f"Spearman **{r['spearman']}** (95% CI {r['ci95']}, n={r['n']})")
        md.append("- Positive => champions that reward mastery are banned as if "
                  "unfair by high-tier players.")
    if ext:
        r = ext["p1_amp_vs_riot_difficulty"]
        md += ["", "## External validation vs Riot difficulty", "",
               f"- P1 amplification vs Riot difficulty: Spearman **{r['spearman']}** "
               f"(95% CI {r['ci95']}, n={r['n']})"]
    md.append("")
    (Path(args.out) / "design_p2.md").write_text("\n".join(md))
    print("reports -> design_p2.{md,json}, perceived_gap_by_tier.csv")
    print("tier-shift:", shift)
    print("RQ3:", rq3)
    if ext:
        print("external:", ext)


if __name__ == "__main__":
    main()
