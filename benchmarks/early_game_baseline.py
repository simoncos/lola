"""T2 benchmark: early-game win prediction from observed game state.

Features are team-differential timeline telemetry, kill difference, and first
blood within the horizon.  Champion composition is not part of this baseline.

Run with ``python -m benchmarks.early_game_baseline --parquet <dir>``.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from benchmarks.draft_baseline import run_setting
from benchmarks.splits import benchmark_splits, write_split_manifest
from lola_dataset.cohort import eligible_matches, filter_to_eligible
from lola_dataset.provenance import write_run_manifest


SEGMENTS = {10: ["zero_to_ten"], 20: ["zero_to_ten", "ten_to_twenty"]}
DELTA_COLS = [
    "creeps_per_min_delta",
    "gold_per_min_delta",
    "xp_per_min_delta",
    "damage_taken_per_min_delta",
    "cs_diff_per_min_delta",
    "xp_diff_per_min_delta",
]


def team_timeline_features(
    parquet_dir: Path, horizon: int, cohort: pd.DataFrame
) -> pd.DataFrame:
    timeline = pd.read_parquet(
        parquet_dir / "participant_timelines.parquet",
        columns=["match_id", "summoner_id", "delta", "side"] + DELTA_COLS,
    )
    timeline = filter_to_eligible(timeline, cohort)
    timeline = timeline[timeline["delta"].isin(SEGMENTS[horizon])]
    team = timeline.groupby(["match_id", "side"])[DELTA_COLS].mean().reset_index()
    blue = team[team["side"] == "blue"].set_index("match_id")[DELTA_COLS]
    red = team[team["side"] == "red"].set_index("match_id")[DELTA_COLS]
    return (blue - red).add_prefix("d_").reset_index()


def kill_features(
    parquet_dir: Path,
    sides: pd.DataFrame,
    horizon: int,
    cohort: pd.DataFrame,
) -> pd.DataFrame:
    kills = pd.read_parquet(
        parquet_dir / "kill_events.parquet",
        columns=["match_id", "happen", "killer", "minute"],
    )
    kills = filter_to_eligible(kills, cohort)
    kills = kills[kills["minute"] < horizon]
    kills = kills.merge(
        sides,
        left_on=["match_id", "killer"],
        right_on=["match_id", "champion"],
        how="inner",
        validate="many_to_one",
    )
    kill_diff = (
        kills.assign(value=np.where(kills["side"] == "blue", 1, -1))
        .groupby("match_id")["value"]
        .sum()
        .rename("kill_diff")
    )
    first_blood = (
        kills.sort_values(["match_id", "minute", "happen"])
        .drop_duplicates("match_id")
        .assign(first_blood_blue=lambda frame: (frame["side"] == "blue").astype(int))
        .set_index("match_id")["first_blood_blue"]
    )
    return pd.concat([kill_diff, first_blood], axis=1).reset_index()


def build_frame(parquet_dir: Path, horizon: int) -> tuple[pd.DataFrame, list[str]]:
    cohort = eligible_matches(parquet_dir, min_duration=horizon)
    participants = pd.read_parquet(
        parquet_dir / "participants.parquet",
        columns=["match_id", "champion", "side", "participant_win"],
    )
    participants = filter_to_eligible(participants, cohort)
    blue = participants[participants["side"] == "blue"].drop_duplicates("match_id")
    frame = cohort.merge(
        blue[["match_id", "participant_win"]].rename(
            columns={"participant_win": "blue_win"}
        ),
        on="match_id",
        validate="one_to_one",
    )

    sides = participants[["match_id", "champion", "side"]].drop_duplicates()
    timeline = team_timeline_features(parquet_dir, horizon, cohort)
    kills = kill_features(parquet_dir, sides, horizon, cohort)
    frame = frame.merge(timeline, on="match_id", how="left", validate="one_to_one")
    frame = frame.merge(kills, on="match_id", how="left", validate="one_to_one")
    feature_columns = [column for column in frame.columns if column.startswith("d_")] + [
        "kill_diff",
        "first_blood_blue",
    ]
    frame[feature_columns] = frame[feature_columns].fillna(0)
    return frame.assign(row=np.arange(len(frame))), feature_columns


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parquet", required=True)
    parser.add_argument("--out", default="benchmarks/output")
    args = parser.parse_args()
    parquet_dir = Path(args.parquet)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    split_paths = []
    for horizon in (10, 20):
        frame, feature_columns = build_frame(parquet_dir, horizon)
        features = frame[feature_columns].to_numpy(np.float32)
        labels = frame["blue_win"].to_numpy(int)
        settings = benchmark_splits(frame)
        split_paths.append(
            write_split_manifest(
                frame, settings, out_dir / f"early_game_split_{horizon}min.csv"
            )
        )
        for name, split in settings.items():
            result = run_setting(name, features, labels, split)
            result["horizon_min"] = horizon
            result["feature_columns"] = feature_columns
            results.append(result)

    json_path = out_dir / "early_game_baseline.json"
    md_path = out_dir / "early_game_baseline.md"
    payload = {
        "protocol_version": 2,
        "feature_contract": "team-differential state plus kill difference and first blood",
        "results": results,
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    markdown = [
        "# T2 Early-Game Win-Prediction Baselines",
        "",
        "Canonical cohort; no champion-composition features. Validation data selects",
        "hyperparameters and is merged into the final training fit.",
        "",
    ]
    for result in results:
        sizes = result["sizes"]
        markdown += [
            f"## {result['horizon_min']} min — {result['setting']} "
            f"(train {sizes['train']:,} / val {sizes['val']:,} / test {sizes['test']:,})",
            "",
            "| Model | Accuracy | AUC | Log-loss | ECE | Selected |",
            "|---|---:|---:|---:|---:|---|",
        ]
        for model_name in ["majority", "logistic_regression", "gradient_boosting"]:
            metric = result[model_name]
            markdown.append(
                f"| {model_name} | {metric['accuracy']:.4f} | {metric['auc']:.4f} "
                f"| {metric['log_loss']:.4f} | {metric['ece']:.4f} "
                f"| {metric.get('selected', 'training prevalence')} |"
            )
        markdown.append("")
    markdown += [
        "Do not attribute differences between settings to patch drift without a",
        "matched target cohort, uncertainty intervals, and an explicit hypothesis test.",
        "",
    ]
    md_path.write_text("\n".join(markdown))
    write_run_manifest(
        out_dir,
        "early_game_baseline",
        parameters={"protocol_version": 2, "horizons": [10, 20]},
        inputs=[
            parquet_dir / "matches.parquet",
            parquet_dir / "participants.parquet",
            parquet_dir / "participant_timelines.parquet",
            parquet_dir / "kill_events.parquet",
        ],
        outputs=[json_path, md_path, *split_paths],
    )
    print(f"reports written to {out_dir}")


if __name__ == "__main__":
    main()
