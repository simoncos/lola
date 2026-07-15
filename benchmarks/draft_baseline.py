"""T1 benchmark baselines: pre-match win prediction from draft composition.

Implements the split defined in docs/r1-dataset-paper/BENCHMARKS.md:

- cross-patch (primary): train = builds up to 5.24.0.254, val = first 20% of
  5.24.0.256 by match_id, test = rest of 5.24.0.256 + 5.24.0.259 + 6.1.0.484
- same-patch (control): random 80/10/10 by match_id hash

Features: signed champion one-hot (+1 blue pick, -1 red pick; 128 dims).
Models: majority class, logistic regression, gradient-boosted trees.
Metrics: accuracy, AUC, log-loss, ECE (10 equal-width bins) - calibration is
a first-class metric here (rarely reported in the MOBA literature).

Matches shorter than 10 minutes are excluded (early surrenders).

Usage:
    python benchmarks/draft_baseline.py --parquet <dir> [--out benchmarks/output]
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss, roc_auc_score

TRAIN_BUILDS = {"5.21.0.297", "5.22.0.289", "5.22.0.297", "5.22.0.301",
                "5.23.0.239", "5.23.0.250", "5.24.0.251", "5.24.0.254"}
VAL_TEST_PIVOT_BUILD = "5.24.0.256"
LATE_BUILDS = {"5.24.0.259", "6.1.0.484"}
MIN_DURATION_MIN = 10


def load_matches(parquet_dir: str) -> tuple[pd.DataFrame, list[str]]:
    d = Path(parquet_dir)
    p = pd.read_parquet(d / "participants.parquet",
                        columns=["match_id", "champion", "side",
                                 "participant_win", "version"])
    m = pd.read_parquet(d / "matches.parquet")
    ok = set(m.loc[m["duration"] >= MIN_DURATION_MIN, "match_id"].astype(str))
    p = p[p["match_id"].astype(str).isin(ok)]

    champions = sorted(p["champion"].unique())
    idx = {c: k for k, c in enumerate(champions)}

    p = p.sort_values("match_id")
    sign = np.where(p["side"].to_numpy() == "blue", 1.0, -1.0)
    ci = p["champion"].map(idx).to_numpy()
    codes, uniques = pd.factorize(p["match_id"], sort=True)

    X = np.zeros((len(uniques), len(champions)), dtype=np.float32)
    X[codes, ci] = sign  # each champion appears once per match

    blue = p[p["side"] == "blue"].drop_duplicates("match_id").set_index("match_id")
    frame = pd.DataFrame({
        "match_id": uniques,
        "blue_win": blue.loc[uniques, "participant_win"].to_numpy(),
        "version": blue.loc[uniques, "version"].to_numpy(),
    })
    return frame.assign(row=np.arange(len(frame))), champions, X


def split_cross_patch(frame: pd.DataFrame) -> dict[str, np.ndarray]:
    train = frame["version"].isin(TRAIN_BUILDS)
    pivot = frame[frame["version"] == VAL_TEST_PIVOT_BUILD].sort_values(
        "match_id", key=lambda s: s.astype(np.int64)
    )
    n_val = int(len(pivot) * 0.2)
    val_ids = set(pivot["match_id"].iloc[:n_val])
    val = frame["match_id"].isin(val_ids)
    test = (~train) & (~val)
    return {"train": frame.loc[train, "row"].to_numpy(),
            "val": frame.loc[val, "row"].to_numpy(),
            "test": frame.loc[test, "row"].to_numpy()}


def split_same_patch(frame: pd.DataFrame) -> dict[str, np.ndarray]:
    h = frame["match_id"].astype(str).map(
        lambda s: int(hashlib.sha256(s.encode()).hexdigest()[:8], 16) % 100
    )
    return {"train": frame.loc[h < 80, "row"].to_numpy(),
            "val": frame.loc[(h >= 80) & (h < 90), "row"].to_numpy(),
            "test": frame.loc[h >= 90, "row"].to_numpy()}


def ece(y: np.ndarray, prob: np.ndarray, bins: int = 10) -> float:
    edges = np.linspace(0, 1, bins + 1)
    total = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        mask = (prob >= lo) & (prob < hi if hi < 1 else prob <= hi)
        if mask.sum() == 0:
            continue
        total += mask.mean() * abs(y[mask].mean() - prob[mask].mean())
    return float(total)


def evaluate(y: np.ndarray, prob: np.ndarray) -> dict:
    pred = (prob >= 0.5).astype(int)
    return {
        "accuracy": round(float(accuracy_score(y, pred)), 4),
        "auc": round(float(roc_auc_score(y, prob)), 4),
        "log_loss": round(float(log_loss(y, prob)), 4),
        "ece": round(ece(y, prob), 4),
    }


def run_setting(name: str, X: np.ndarray, y: np.ndarray,
                splits: dict[str, np.ndarray]) -> dict:
    tr, te = splits["train"], splits["test"]
    out = {"setting": name,
           "sizes": {k: int(len(v)) for k, v in splits.items()}}

    p_major = np.full(len(te), max(y[tr].mean(), 1 - y[tr].mean()))
    y_major = y[te] if y[tr].mean() >= 0.5 else 1 - y[te]
    out["majority"] = {
        "accuracy": round(float((y_major == 1).mean()), 4),
        "auc": 0.5,
        "log_loss": round(float(log_loss(y_major, p_major, labels=[0, 1])), 4),
        "ece": None,
    }

    lr = LogisticRegression(C=0.5, max_iter=2000, solver="lbfgs")
    lr.fit(X[tr], y[tr])
    out["logistic_regression"] = evaluate(y[te], lr.predict_proba(X[te])[:, 1])

    gbt = HistGradientBoostingClassifier(
        max_iter=300, learning_rate=0.08, max_depth=None,
        early_stopping=True, validation_fraction=0.1, random_state=0,
    )
    gbt.fit(X[tr], y[tr])
    out["gradient_boosting"] = evaluate(y[te], gbt.predict_proba(X[te])[:, 1])
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", required=True)
    ap.add_argument("--out", default="benchmarks/output")
    args = ap.parse_args()

    frame, champions, X = load_matches(args.parquet)
    y = frame["blue_win"].to_numpy().astype(int)
    print(f"{len(frame):,} matches after filtering, {len(champions)} champions")

    results = [
        run_setting("cross-patch", X, y, split_cross_patch(frame)),
        run_setting("same-patch", X, y, split_same_patch(frame)),
    ]

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "draft_baseline.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False)
    )

    md = [
        "# T1 Draft Win-Prediction Baselines",
        "",
        f"Signed champion one-hot features ({len(champions)} dims); matches "
        f"< {MIN_DURATION_MIN} min excluded.",
        "",
    ]
    for r in results:
        md += [f"## {r['setting']} split "
               f"(train {r['sizes']['train']:,} / val {r['sizes']['val']:,} "
               f"/ test {r['sizes']['test']:,})", "",
               "| Model | Accuracy | AUC | Log-loss | ECE |", "|---|---|---|---|---|"]
        for model in ["majority", "logistic_regression", "gradient_boosting"]:
            v = r[model]
            e = "—" if v["ece"] is None else f"{v['ece']:.4f}"
            md.append(f"| {model} | {v['accuracy']:.4f} | {v['auc']:.4f} "
                      f"| {v['log_loss']:.4f} | {e} |")
        md.append("")
    md += ["Interpretation targets: literature consensus puts draft-only",
           "accuracy at ~52-58% on balanced data (DraftRec: ~55% with a",
           "transformer + player histories). The cross-patch vs same-patch",
           "gap quantifies patch drift.", ""]
    (out_dir / "draft_baseline.md").write_text("\n".join(md))
    print(f"reports written to {out_dir}/draft_baseline.{{md,json}}")
    for r in results:
        print(f"  {r['setting']}: LR acc {r['logistic_regression']['accuracy']}, "
              f"GBT acc {r['gradient_boosting']['accuracy']}")


if __name__ == "__main__":
    main()
