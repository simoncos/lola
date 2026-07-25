"""Within-player, within-champion learning-curve analysis.

The estimand is the change in early lane performance as the same player gains
observed games on the same champion. It is not inferred from cross-player
differences in general skill. Match IDs and build order are only a temporal
proxy because the source schema has no timestamp; estimates remain descriptive
and may be affected by survivorship and unobserved play outside this archive.

Run with ``python -m analysis.mastery_learning --parquet <dir>``.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from lola_dataset.cohort import eligible_matches, filter_to_eligible
from lola_dataset.provenance import write_run_manifest


POSITION = {
    ("JUNGLE", "NONE"): "jungle",
    ("TOP", "SOLO"): "top",
    ("MIDDLE", "SOLO"): "mid",
    ("BOTTOM", "DUO_CARRY"): "adc",
    ("BOTTOM", "DUO_SUPPORT"): "support",
}
EARLY_SEGMENTS = ["zero_to_ten", "ten_to_twenty"]
MIN_CELL_GAMES = 5
MIN_PLAYER_CHAMPION_CELLS = 40


def build_learning_frame(parquet_dir: Path) -> pd.DataFrame:
    cohort = eligible_matches(parquet_dir, min_duration=20)
    participants = pd.read_parquet(
        parquet_dir / "participants.parquet",
        columns=["match_id", "summoner_id", "champion"],
    )
    participants = filter_to_eligible(participants, cohort)
    timelines = pd.read_parquet(
        parquet_dir / "participant_timelines.parquet",
        columns=[
            "match_id",
            "summoner_id",
            "delta",
            "lane",
            "role",
            "cs_diff_per_min_delta",
            "xp_diff_per_min_delta",
        ],
    )
    timelines = filter_to_eligible(timelines, cohort)

    position = timelines[timelines["delta"] == "zero_to_ten"].copy()
    position["position"] = [
        POSITION.get((lane, role))
        for lane, role in zip(position["lane"], position["role"])
    ]
    position = position[["match_id", "summoner_id", "position"]].dropna()
    if position.duplicated(["match_id", "summoner_id"]).any():
        raise ValueError("timeline has duplicate zero_to_ten player rows")

    early = timelines[timelines["delta"].isin(EARLY_SEGMENTS)].copy()
    early["lane_diff"] = early[
        ["cs_diff_per_min_delta", "xp_diff_per_min_delta"]
    ].sum(axis=1, min_count=2)
    lane = early.groupby(["match_id", "summoner_id"], as_index=False).agg(
        lane_diff=("lane_diff", "mean"),
        observed_early_segments=("lane_diff", "count"),
    )
    lane = lane[lane["observed_early_segments"] == len(EARLY_SEGMENTS)]
    frame = (
        participants.merge(lane, on=["match_id", "summoner_id"], how="inner")
        .merge(position, on=["match_id", "summoner_id"], how="inner")
        .merge(cohort[["match_id", "version"]], on="match_id", validate="many_to_one")
    )
    group = frame.groupby(["version", "position"])["lane_diff"]
    scale = group.transform("std")
    frame["lane_z"] = (frame["lane_diff"] - group.transform("mean")) / scale
    frame = frame.replace([np.inf, -np.inf], np.nan).dropna(subset=["lane_z"])

    def build_key(value: str) -> tuple[int, ...]:
        return tuple(int(part) for part in str(value).split("."))

    builds = sorted(frame["version"].unique(), key=build_key)
    build_order = {build: rank for rank, build in enumerate(builds)}
    frame["build_order"] = frame["version"].map(build_order)
    frame["match_order"] = pd.to_numeric(frame["match_id"], errors="raise")
    keys = ["summoner_id", "champion"]
    frame = frame.sort_values(keys + ["build_order", "match_order"])
    frame["cell_games"] = frame.groupby(keys)["match_id"].transform("size")
    frame = frame[frame["cell_games"] >= MIN_CELL_GAMES].copy()
    frame["observed_game_number"] = frame.groupby(keys).cumcount() + 1
    frame["log_experience"] = np.log1p(frame["observed_game_number"] - 1)
    return frame.reset_index(drop=True)


def cell_sufficient_statistics(frame: pd.DataFrame) -> pd.DataFrame:
    """Return centered within-cell OLS sufficient statistics."""
    keys = ["summoner_id", "champion"]
    centered_x = frame["log_experience"] - frame.groupby(keys)[
        "log_experience"
    ].transform("mean")
    centered_y = frame["lane_z"] - frame.groupby(keys)["lane_z"].transform("mean")
    working = frame[keys].copy()
    working["sxx"] = centered_x**2
    working["sxy"] = centered_x * centered_y
    working["games"] = 1
    return working.groupby(keys, as_index=False).agg(
        sxx=("sxx", "sum"), sxy=("sxy", "sum"), games=("games", "sum")
    )


def estimate_champion_learning(
    cells: pd.DataFrame,
    bootstrap_reps: int = 1000,
    seed: int = 17,
) -> pd.DataFrame:
    """Pool within-cell slopes and bootstrap player-champion cells."""
    rng = np.random.default_rng(seed)
    rows = []
    for champion, group in cells.groupby("champion"):
        if len(group) < MIN_PLAYER_CHAMPION_CELLS:
            continue
        sxx = group["sxx"].to_numpy(float)
        sxy = group["sxy"].to_numpy(float)
        denominator = sxx.sum()
        if denominator <= 0:
            continue
        slope = sxy.sum() / denominator
        draws = []
        for _ in range(bootstrap_reps):
            index = rng.integers(0, len(group), len(group))
            draw_denominator = sxx[index].sum()
            if draw_denominator > 0:
                draws.append(sxy[index].sum() / draw_denominator)
        low, high = np.percentile(draws, [2.5, 97.5])
        rows.append(
            {
                "champion": champion,
                "learning_slope": float(slope),
                "ci95_low": float(low),
                "ci95_high": float(high),
                "player_champion_cells": int(len(group)),
                "games": int(group["games"].sum()),
            }
        )
    if not rows:
        return pd.DataFrame(
            columns=[
                "champion",
                "learning_slope",
                "ci95_low",
                "ci95_high",
                "player_champion_cells",
                "games",
            ]
        )
    return pd.DataFrame(rows).sort_values("learning_slope", ascending=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parquet", required=True)
    parser.add_argument("--out", default="analysis/output")
    parser.add_argument("--bootstrap-reps", type=int, default=1000)
    args = parser.parse_args()
    if args.bootstrap_reps < 200:
        raise SystemExit("--bootstrap-reps must be at least 200")

    parquet_dir = Path(args.parquet)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    frame = build_learning_frame(parquet_dir)
    cells = cell_sufficient_statistics(frame)
    estimates = estimate_champion_learning(cells, args.bootstrap_reps)
    if estimates.empty:
        raise RuntimeError("no champions met the learning-curve support thresholds")

    csv_path = out_dir / "mastery_learning.csv"
    json_path = out_dir / "mastery_learning.json"
    md_path = out_dir / "mastery_learning.md"
    estimates.to_csv(csv_path, index=False)
    payload = {
        "protocol_version": 1,
        "estimand": (
            "Within-player, within-champion change in position/build-standardized "
            "early lane performance per log observed game."
        ),
        "limitations": [
            "Match ID and build provide a temporal proxy; the source has no timestamp.",
                "Observed games may omit play outside this archive.",
            "Both 0-10 and 10-20 lane-difference segments must be observed.",
            "Survivorship can correlate continued champion use with performance.",
            "The estimates are descriptive, not causal learning effects.",
        ],
        "minimum_cell_games": MIN_CELL_GAMES,
        "minimum_player_champion_cells": MIN_PLAYER_CHAMPION_CELLS,
        "bootstrap_reps": args.bootstrap_reps,
        "eligible_games_used": int(len(frame)),
        "champions_scored": int(len(estimates)),
        "results": estimates.to_dict("records"),
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    markdown = [
        "# Within-Player Champion Learning Curves",
        "",
        "This analysis estimates changes in early lane performance as the same player",
        "accumulates observed games on the same champion. It does not call a",
        "cross-player transfer slope mastery.",
        "",
        "> Descriptive only: match order is a proxy, external games are unobserved,",
        "> and continued champion use may be selective.",
        "",
        "| Champion | Learning slope | 95% cell-bootstrap interval | Cells | Games |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in estimates.itertuples():
        markdown.append(
            f"| {row.champion} | {row.learning_slope:+.4f} | "
            f"[{row.ci95_low:+.4f}, {row.ci95_high:+.4f}] | "
            f"{row.player_champion_cells:,} | {row.games:,} |"
        )
    markdown.append("")
    md_path.write_text("\n".join(markdown))
    write_run_manifest(
        out_dir,
        "mastery_learning",
        parameters={
            "protocol_version": 1,
            "minimum_cell_games": MIN_CELL_GAMES,
            "minimum_player_champion_cells": MIN_PLAYER_CHAMPION_CELLS,
            "bootstrap_reps": args.bootstrap_reps,
        },
        inputs=[
            parquet_dir / "matches.parquet",
            parquet_dir / "participants.parquet",
            parquet_dir / "participant_timelines.parquet",
        ],
        outputs=[csv_path, json_path, md_path],
    )


if __name__ == "__main__":
    main()
