"""Tier-resolved champion ban salience relative to observed win rate.

The standardized residual ``ban_rate_z - win_rate_z`` is a descriptive salience
measure. It does not identify anti-fun, fairness, perceived power, or player
motives. Optional correlations with within-player learning slopes are likewise
descriptive champion-level associations.

Run with ``python -m analysis.design_p2 --parquet <dir>``.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from lola_dataset.cohort import eligible_matches, filter_to_eligible
from lola_dataset.provenance import file_identity, write_run_manifest


TIER_BUCKET = {
    "BRONZE": "low",
    "SILVER": "low",
    "GOLD": "mid",
    "PLATINUM": "mid",
    "DIAMOND": "high",
    "MASTER": "high",
    "CHALLENGER": "high",
}
MIN_PICKS = 200


def verify_learning_artifact(learning_path: Path, parquet_dir: Path) -> Path:
    """Reject a stale learning CSV from another data bundle or run."""
    manifest_path = learning_path.with_name("mastery_learning.run.json")
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"{learning_path} exists without its required provenance manifest"
        )
    manifest = json.loads(manifest_path.read_text())
    recorded_inputs = {item["file"]: item["sha256"] for item in manifest["inputs"]}
    recorded_outputs = {item["file"]: item["sha256"] for item in manifest["outputs"]}
    for path in [
        parquet_dir / "matches.parquet",
        parquet_dir / "participants.parquet",
        parquet_dir / "participant_timelines.parquet",
    ]:
        identity = file_identity(path)
        if recorded_inputs.get(identity["file"]) != identity["sha256"]:
            raise ValueError(f"learning artifact input mismatch: {identity['file']}")
    learning_identity = file_identity(learning_path)
    if recorded_outputs.get(learning_identity["file"]) != learning_identity["sha256"]:
        raise ValueError("mastery_learning.csv does not match its run manifest")
    return manifest_path


def match_tier_bucket(parts: pd.DataFrame) -> pd.DataFrame:
    """Assign a bucket only for a sufficiently ranked, unique plurality."""
    ranked = parts.assign(bucket=parts["previous_season_tier"].map(TIER_BUCKET))
    counts = (
        ranked.dropna(subset=["bucket"])
        .groupby(["match_id", "bucket"])
        .size()
        .unstack(fill_value=0)
    )
    for bucket in ["low", "mid", "high"]:
        if bucket not in counts:
            counts[bucket] = 0
    counts = counts[["low", "mid", "high"]]
    total_ranked = counts.sum(axis=1)
    largest = counts.max(axis=1)
    unique_plurality = counts.eq(largest, axis=0).sum(axis=1).eq(1)
    counts["match_bucket"] = counts.idxmax(axis=1).where(
        (total_ranked >= 6) & unique_plurality
    )
    return counts[["match_bucket"]].dropna().reset_index()


def salience_by_bucket(
    parts: pd.DataFrame,
    bans: pd.DataFrame,
    buckets: pd.DataFrame,
) -> pd.DataFrame:
    parts = parts.merge(buckets, on="match_id", how="inner")
    bans = bans.merge(buckets, on="match_id", how="inner")
    bans = bans[
        bans["ban"].notna()
        & ~bans["ban"].astype(str).str.upper().isin({"", "-1", "NONE"})
    ].drop_duplicates(["match_id", "ban"])
    match_counts = buckets["match_bucket"].value_counts().to_dict()

    rows = []
    for bucket in ["low", "mid", "high"]:
        participants = parts[parts["match_bucket"] == bucket]
        bucket_bans = bans[bans["match_bucket"] == bucket]
        n_matches = int(match_counts.get(bucket, 0))
        if n_matches == 0:
            continue
        picks = participants.groupby("champion").agg(
            picks=("participant_win", "count"),
            wins=("participant_win", "sum"),
        )
        picks["win_rate"] = picks["wins"] / picks["picks"]
        ban_count = bucket_bans.groupby("ban").size().rename("bans")
        frame = picks.join(ban_count).fillna({"bans": 0})
        frame = frame[frame["picks"] >= MIN_PICKS].copy()
        frame["ban_rate"] = frame["bans"] / n_matches
        for column in ["ban_rate", "win_rate"]:
            standard_deviation = frame[column].std()
            if not np.isfinite(standard_deviation) or standard_deviation == 0:
                raise ValueError(f"cannot standardize {column} for {bucket}")
            frame[f"{column}_z"] = (
                frame[column] - frame[column].mean()
            ) / standard_deviation
        frame["ban_win_salience_residual"] = (
            frame["ban_rate_z"] - frame["win_rate_z"]
        )
        frame["bucket"] = bucket
        rows.append(
            frame.reset_index()[
                [
                    "champion",
                    "bucket",
                    "picks",
                    "win_rate",
                    "ban_rate",
                    "ban_win_salience_residual",
                ]
            ]
        )
    if not rows:
        raise RuntimeError("no tier buckets met the salience-analysis requirements")
    return pd.concat(rows, ignore_index=True)


def bootstrap_spearman(
    x: np.ndarray,
    y: np.ndarray,
    reps: int = 2000,
    seed: int = 3,
) -> dict:
    rng = np.random.default_rng(seed)
    n = len(x)
    point = float(pd.Series(x).corr(pd.Series(y), method="spearman"))
    estimates = []
    for _ in range(reps):
        index = rng.integers(0, n, n)
        estimates.append(
            pd.Series(x[index]).corr(pd.Series(y[index]), method="spearman")
        )
    low, high = np.nanpercentile(estimates, [2.5, 97.5])
    return {
        "spearman": round(point, 4),
        "ci95": [round(float(low), 4), round(float(high), 4)],
        "champions": int(n),
        "bootstrap_reps": reps,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parquet", required=True)
    parser.add_argument("--out", default="analysis/output")
    parser.add_argument("--bootstrap-reps", type=int, default=2000)
    args = parser.parse_args()
    if args.bootstrap_reps < 200:
        raise SystemExit("--bootstrap-reps must be at least 200")

    parquet_dir = Path(args.parquet)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    cohort = eligible_matches(parquet_dir)
    parts = pd.read_parquet(
        parquet_dir / "participants.parquet",
        columns=[
            "match_id",
            "champion",
            "previous_season_tier",
            "participant_win",
        ],
    )
    bans = pd.read_parquet(
        parquet_dir / "team_bans.parquet", columns=["match_id", "ban"]
    )
    parts = filter_to_eligible(parts, cohort)
    bans = filter_to_eligible(bans, cohort)
    buckets = match_tier_bucket(parts)
    salience = salience_by_bucket(parts, bans, buckets)
    wide = salience.pivot(
        index="champion", columns="bucket", values="ban_win_salience_residual"
    )

    stability = {}
    for first, second in [("low", "mid"), ("mid", "high"), ("low", "high")]:
        if first in wide.columns and second in wide.columns:
            pair = wide[[first, second]].dropna()
            stability[f"{first}_vs_{second}"] = round(
                float(pair[first].corr(pair[second], method="spearman")), 4
            )

    learning_association = {}
    learning_path = out_dir / "mastery_learning.csv"
    learning_manifest_path = None
    if learning_path.exists() and "high" in wide.columns:
        learning_manifest_path = verify_learning_artifact(learning_path, parquet_dir)
        learning = pd.read_csv(learning_path)[["champion", "learning_slope"]]
        comparison = (
            wide.reset_index()
            .merge(learning, on="champion", how="inner")
            .dropna(subset=["high", "learning_slope"])
        )
        if len(comparison) > 10:
            learning_association = bootstrap_spearman(
                comparison["learning_slope"].to_numpy(),
                comparison["high"].to_numpy(),
                reps=args.bootstrap_reps,
            )

    def extremes(bucket: str, ascending: bool, count: int = 8) -> list[dict]:
        if bucket not in wide.columns:
            return []
        series = wide[bucket].dropna().sort_values(ascending=ascending)
        return [
            {"champion": champion, "residual": round(float(value), 3)}
            for champion, value in series.head(count).items()
        ]

    csv_path = out_dir / "ban_salience_by_tier.csv"
    json_path = out_dir / "design_ban_salience.json"
    md_path = out_dir / "design_ban_salience.md"
    salience.to_csv(csv_path, index=False)
    payload = {
        "protocol_version": 1,
        "interpretation": (
            "Standardized ban-rate minus win-rate residual; descriptive salience, "
            "not anti-fun, unfairness, perceived power, or a causal effect."
        ),
        "minimum_picks_per_bucket": MIN_PICKS,
        "bucketed_matches": int(buckets["match_id"].nunique()),
        "salience_stability_spearman": stability,
        "highest_residual_by_tier": {
            bucket: extremes(bucket, ascending=False)
            for bucket in ["low", "mid", "high"]
        },
        "lowest_residual_by_tier": {
            bucket: extremes(bucket, ascending=True)
            for bucket in ["low", "mid", "high"]
        },
        "learning_slope_vs_high_tier_salience": learning_association,
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    markdown = [
        "# Tier-Resolved Ban Salience Relative to Win Rate",
        "",
        "The reported value is standardized ban rate minus standardized observed win",
        "rate. It is a descriptive residual, not evidence of anti-fun, unfairness,",
        "player perception, or motivation.",
        "",
        "## Rank stability across tier buckets (Spearman)",
        "",
    ]
    for label, value in stability.items():
        markdown.append(f"- {label}: {value}")
    markdown += ["", "## Highest salience residuals", ""]
    for bucket in ["low", "mid", "high"]:
        names = ", ".join(
            f"{row['champion']} ({row['residual']:+.2f})"
            for row in payload["highest_residual_by_tier"][bucket]
        )
        markdown.append(f"- **{bucket}**: {names}")
    markdown += ["", "## Learning-slope association", ""]
    if learning_association:
        markdown.append(
            f"- High-tier salience vs learning slope: Spearman "
            f"{learning_association['spearman']} (95% bootstrap interval "
            f"{learning_association['ci95']}, n={learning_association['champions']})."
        )
        markdown.append("- This champion-level association has no causal interpretation.")
    else:
        markdown.append("- Pending a current mastery_learning.csv rerun.")
    markdown.append("")
    md_path.write_text("\n".join(markdown))
    inputs = [
        parquet_dir / "matches.parquet",
        parquet_dir / "participants.parquet",
        parquet_dir / "team_bans.parquet",
    ]
    if learning_manifest_path is not None:
        inputs.append(learning_path)
        inputs.append(learning_manifest_path)
    write_run_manifest(
        out_dir,
        "design_ban_salience",
        parameters={
            "protocol_version": 1,
            "minimum_picks": MIN_PICKS,
            "bootstrap_reps": args.bootstrap_reps,
        },
        inputs=inputs,
        outputs=[csv_path, json_path, md_path],
    )


if __name__ == "__main__":
    main()
