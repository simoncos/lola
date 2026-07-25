"""T3 benchmark: incremental value of cross-team champion interactions.

This benchmark avoids interpreting 25 Cartesian champion pairs from one match
as 25 independent head-to-head contests.  It compares a regularized logistic
model with champion main effects against the same model plus anti-symmetric
cross-team pair interactions, using the same match-level splits as T1/T2.

The result is predictive evidence about lineup interactions.  Individual
coefficients are associations conditional on this model, not causal counters or
lane-matchup effects.

Run with ``python -m benchmarks.matchup_interaction_baseline --parquet <dir>``.
"""

from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss

from benchmarks.draft_baseline import evaluate, load_matches
from benchmarks.splits import benchmark_splits, write_split_manifest
from lola_dataset.cohort import eligible_matches, filter_to_eligible
from lola_dataset.provenance import write_run_manifest


C_CANDIDATES = [0.01, 0.1, 1.0]


def _pair_index(champion_count: int) -> tuple[dict[tuple[int, int], int], list[tuple[int, int]]]:
    pairs = list(combinations(range(champion_count), 2))
    return {pair: index for index, pair in enumerate(pairs)}, pairs


def build_interaction_features(
    parquet_dir: Path,
    frame: pd.DataFrame,
    champions: list[str],
) -> tuple[sparse.csr_matrix, list[tuple[int, int]]]:
    cohort = eligible_matches(parquet_dir)
    participants = pd.read_parquet(
        parquet_dir / "participants.parquet", columns=["match_id", "champion", "side"]
    )
    participants = filter_to_eligible(participants, cohort)
    champion_index = {champion: index for index, champion in enumerate(champions)}
    participants["champion_index"] = participants["champion"].map(champion_index)
    if participants["champion_index"].isna().any():
        raise ValueError("participant champion missing from T1 champion vocabulary")

    ordered_ids = frame.sort_values("row")["match_id"].astype(str).tolist()
    sides = {}
    for side in ["blue", "red"]:
        subset = participants[participants["side"] == side].copy()
        subset["slot"] = subset.groupby("match_id").cumcount()
        wide = subset.pivot(index="match_id", columns="slot", values="champion_index")
        wide = wide.reindex(ordered_ids)
        if wide.shape[1] != 5 or wide.isna().any().any():
            raise ValueError(f"cannot build five-{side}-champion interaction matrix")
        sides[side] = wide.to_numpy(dtype=np.int32)

    pair_to_column, pairs = _pair_index(len(champions))
    observations = len(frame) * 25
    columns = np.empty(observations, dtype=np.int32)
    values = np.empty(observations, dtype=np.int8)
    offset = 0
    for blue_slot in range(5):
        for red_slot in range(5):
            blue = sides["blue"][:, blue_slot]
            red = sides["red"][:, red_slot]
            lower = np.minimum(blue, red)
            upper = np.maximum(blue, red)
            columns[offset : offset + len(frame)] = [
                pair_to_column[(int(a), int(b))] for a, b in zip(lower, upper)
            ]
            values[offset : offset + len(frame)] = np.where(blue < red, 1, -1)
            offset += len(frame)

    # The slot loop writes match-sized blocks, whereas ``rows`` above is
    # match-major. Rebuild matching row IDs for the block-major arrays.
    rows = np.tile(np.arange(len(frame), dtype=np.int32), 25)
    matrix = sparse.coo_matrix(
        (values, (rows, columns)), shape=(len(frame), len(pairs)), dtype=np.float32
    ).tocsr()
    return matrix, pairs


def _fit_logistic(
    features: sparse.spmatrix,
    labels: np.ndarray,
    split: dict[str, np.ndarray],
) -> dict:
    train, val, test = split["train"], split["val"], split["test"]
    candidates = []
    for c_value in C_CANDIDATES:
        model = LogisticRegression(
            C=c_value,
            max_iter=1000,
            solver="saga",
            random_state=0,
        )
        model.fit(features[train], labels[train])
        probability = model.predict_proba(features[val])[:, 1]
        candidates.append(
            (log_loss(labels[val], probability, labels=[0, 1]), c_value, model)
        )
    validation_loss, selected_c, selected = min(candidates, key=lambda item: item[0])
    combined = np.concatenate([train, val])
    selected.fit(features[combined], labels[combined])
    result = evaluate(labels[test], selected.predict_proba(features[test])[:, 1])
    result["selected_C"] = selected_c
    result["validation_log_loss"] = round(float(validation_loss), 4)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parquet", required=True)
    parser.add_argument("--out", default="benchmarks/output")
    args = parser.parse_args()
    parquet_dir = Path(args.parquet)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    frame, champions, main_dense = load_matches(str(parquet_dir))
    labels = frame["blue_win"].to_numpy(int)
    main = sparse.csr_matrix(main_dense)
    interactions, pair_vocabulary = build_interaction_features(
        parquet_dir, frame, champions
    )
    combined = sparse.hstack([main, interactions], format="csr")
    settings = benchmark_splits(frame)

    results = []
    for setting, split in settings.items():
        main_result = _fit_logistic(main, labels, split)
        interaction_result = _fit_logistic(combined, labels, split)
        results.append(
            {
                "setting": setting,
                "sizes": {key: int(len(value)) for key, value in split.items()},
                "main_effects": main_result,
                "main_plus_pair_interactions": interaction_result,
                "test_log_loss_delta": round(
                    interaction_result["log_loss"] - main_result["log_loss"], 4
                ),
            }
        )

    json_path = out_dir / "matchup_interaction_baseline.json"
    md_path = out_dir / "matchup_interaction_baseline.md"
    split_path = write_split_manifest(
        frame, settings, out_dir / "matchup_interaction_split_manifest.csv"
    )
    payload = {
        "protocol_version": 1,
        "interpretation": (
            "Predictive incremental value of regularized cross-team pair interactions; "
            "not causal counter effects."
        ),
        "champion_main_effects": len(champions),
        "pair_interactions": len(pair_vocabulary),
        "results": results,
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    markdown = [
        "# T3 Lineup-Interaction Prediction Benchmark",
        "",
        "This benchmark tests whether regularized cross-team pair interactions improve",
        "held-out prediction after champion main effects. It does not identify causal",
        "counter-picks or lane matchups.",
        "",
        "| Setting | Main log-loss | Main+pair log-loss | Delta | Main AUC | Main+pair AUC |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for result in results:
        main_result = result["main_effects"]
        pair_result = result["main_plus_pair_interactions"]
        markdown.append(
            f"| {result['setting']} | {main_result['log_loss']:.4f} "
            f"| {pair_result['log_loss']:.4f} | {result['test_log_loss_delta']:+.4f} "
            f"| {main_result['auc']:.4f} | {pair_result['auc']:.4f} |"
        )
    markdown += [
        "",
        "A negative delta means the interaction model improved test log-loss. Report",
        "uncertainty before making a substantive claim.",
        "",
    ]
    md_path.write_text("\n".join(markdown))
    write_run_manifest(
        out_dir,
        "matchup_interaction_baseline",
        parameters={"protocol_version": 1, "C_candidates": C_CANDIDATES},
        inputs=[parquet_dir / "matches.parquet", parquet_dir / "participants.parquet"],
        outputs=[json_path, md_path, split_path],
    )
    print(f"reports written to {out_dir}")


if __name__ == "__main__":
    main()
