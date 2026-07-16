"""T2 benchmark baselines: early-game win prediction from timeline telemetry.

Predicts the winner from the state of the game at 10 minutes (and 20 minutes),
using team-differential features derived from timeline deltas and kill events:

- per-team sums (blue minus red) of creeps/gold/xp/damage-taken per-min deltas
  for the 0-10 segment (plus 10-20 for the 20-minute variant)
- lane-differential sums (cs_diff, xp_diff per min)
- kill difference and first blood within the horizon (from kill events)

Splits, models and metrics mirror T1 (benchmarks/draft_baseline.py): cross-patch
chronological split + same-patch random control; majority / logistic regression
/ gradient boosting; accuracy, AUC, log-loss, ECE. The 20-minute variant is
restricted to matches lasting >= 20 minutes (standard practice: prediction at
time t conditions on the game reaching t).

Usage:
    python benchmarks/early_game_baseline.py --parquet <dir> [--out benchmarks/output]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

from draft_baseline import (MIN_DURATION_MIN, evaluate, split_cross_patch,
                            split_same_patch)

SEGMENTS = {10: ["zero_to_ten"], 20: ["zero_to_ten", "ten_to_twenty"]}
DELTA_COLS = ["creeps_per_min_delta", "gold_per_min_delta", "xp_per_min_delta",
              "damage_taken_per_min_delta", "cs_diff_per_min_delta",
              "xp_diff_per_min_delta"]


def team_timeline_features(d: Path, horizon: int) -> pd.DataFrame:
    t = pd.read_parquet(
        d / "participant_timelines.parquet",
        columns=["match_id", "summoner_id", "delta", "side"] + DELTA_COLS)
    t = t[t["delta"].isin(SEGMENTS[horizon])]
    team = (t.groupby(["match_id", "side"])[DELTA_COLS].mean().reset_index())
    blue = team[team["side"] == "blue"].set_index("match_id")[DELTA_COLS]
    red = team[team["side"] == "red"].set_index("match_id")[DELTA_COLS]
    feats = (blue - red).add_prefix("d_")
    return feats.reset_index()


def kill_features(d: Path, sides: pd.DataFrame, horizon: int) -> pd.DataFrame:
    k = pd.read_parquet(d / "kill_events.parquet",
                        columns=["match_id", "happen", "killer", "minute"])
    k = k[k["minute"] < horizon]
    k = k.merge(sides, left_on=["match_id", "killer"],
                right_on=["match_id", "champion"], how="inner")
    kill_diff = (
        k.assign(v=np.where(k["side"] == "blue", 1, -1))
        .groupby("match_id")["v"].sum().rename("kill_diff"))
    fb = (k.sort_values("happen").drop_duplicates("match_id")
          .assign(first_blood_blue=lambda x: (x["side"] == "blue").astype(int))
          .set_index("match_id")["first_blood_blue"])
    return pd.concat([kill_diff, fb], axis=1).reset_index()


def build_frame(d: Path, horizon: int) -> tuple[pd.DataFrame, list[str]]:
    parts = pd.read_parquet(
        d / "participants.parquet",
        columns=["match_id", "champion", "side", "participant_win", "version"])
    m = pd.read_parquet(d / "matches.parquet")
    m["match_id"] = m["match_id"].astype(str)
    min_dur = max(MIN_DURATION_MIN, horizon)
    ok = m[m["duration"] >= min_dur][["match_id"]]

    blue = parts[parts["side"] == "blue"].drop_duplicates("match_id")
    frame = ok.merge(
        blue[["match_id", "participant_win", "version"]].rename(
            columns={"participant_win": "blue_win"}),
        on="match_id")

    tl = team_timeline_features(d, horizon)
    kf = kill_features(d, parts[["match_id", "champion", "side"]], horizon)
    frame = frame.merge(tl, on="match_id", how="left").merge(
        kf, on="match_id", how="left")
    feat_cols = [c for c in frame.columns if c.startswith("d_")] + \
        ["kill_diff", "first_blood_blue"]
    frame[feat_cols] = frame[feat_cols].fillna(0)
    return frame.assign(row=np.arange(len(frame))), feat_cols


def run_setting(name: str, X: np.ndarray, y: np.ndarray, splits: dict) -> dict:
    tr, te = splits["train"], splits["test"]
    out = {"setting": name, "sizes": {k: int(len(v)) for k, v in splits.items()}}
    maj = max(y[tr].mean(), 1 - y[tr].mean())
    out["majority"] = {"accuracy": round(float(max(y[te].mean(), 1 - y[te].mean())), 4),
                       "auc": 0.5, "log_loss": None, "ece": None}
    lr = LogisticRegression(C=1.0, max_iter=2000)
    lr.fit(X[tr], y[tr])
    out["logistic_regression"] = evaluate(y[te], lr.predict_proba(X[te])[:, 1])
    gbt = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.08,
                                         early_stopping=True, random_state=0)
    gbt.fit(X[tr], y[tr])
    out["gradient_boosting"] = evaluate(y[te], gbt.predict_proba(X[te])[:, 1])
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", required=True)
    ap.add_argument("--out", default="benchmarks/output")
    args = ap.parse_args()
    d = Path(args.parquet)

    results = []
    for horizon in (10, 20):
        frame, feat_cols = build_frame(d, horizon)
        X = frame[feat_cols].to_numpy(np.float32)
        y = frame["blue_win"].to_numpy(int)
        print(f"horizon {horizon} min: {len(frame):,} matches, "
              f"{len(feat_cols)} features")
        for name, split in [("cross-patch", split_cross_patch(frame)),
                            ("same-patch", split_same_patch(frame))]:
            r = run_setting(name, X, y, split)
            r["horizon_min"] = horizon
            results.append(r)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "early_game_baseline.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False))

    md = ["# T2 Early-Game Win-Prediction Baselines", "",
          "Team-differential timeline features (blue minus red) + kill diff and",
          "first blood within the horizon. 20-min variant restricted to matches",
          "lasting >= 20 minutes.", ""]
    for r in results:
        md += [f"## {r['horizon_min']} min — {r['setting']} split "
               f"(train {r['sizes']['train']:,} / test {r['sizes']['test']:,})", "",
               "| Model | Accuracy | AUC | Log-loss | ECE |", "|---|---|---|---|---|"]
        for model in ["majority", "logistic_regression", "gradient_boosting"]:
            v = r[model]
            ll = "—" if v["log_loss"] is None else f"{v['log_loss']:.4f}"
            e = "—" if v["ece"] is None else f"{v['ece']:.4f}"
            md.append(f"| {model} | {v['accuracy']:.4f} | {v['auc']:.4f} | {ll} | {e} |")
        md.append("")
    md += ["Reference: literature places 10-minute prediction at ~70-75% "
           "(Silva 2018: 63.9% at 5 min; Hodge 2021: 85% pro).", ""]
    (out_dir / "early_game_baseline.md").write_text("\n".join(md))
    print(f"reports -> {out_dir}/early_game_baseline.{{md,json}}")
    for r in results:
        print(f"  {r['horizon_min']}min {r['setting']}: "
              f"LR {r['logistic_regression']['accuracy']}, "
              f"GBT {r['gradient_boosting']['accuracy']}")


if __name__ == "__main__":
    main()
