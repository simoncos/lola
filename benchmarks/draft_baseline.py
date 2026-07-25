"""T1 benchmark: pre-match win prediction from champion picks only.

The feature contract is deliberately narrow and matches the implementation:
signed champion one-hot features (+1 blue, -1 red).  Bans, tier, patch, and
player history are reserved for enhanced baselines and are not represented by
the numbers produced here.

Run with ``python -m benchmarks.draft_baseline --parquet <dir>``.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss, roc_auc_score

from benchmarks.splits import benchmark_splits, write_split_manifest
from lola_dataset.cohort import eligible_matches, filter_to_eligible
from lola_dataset.provenance import write_run_manifest


LR_CANDIDATES = [0.1, 0.5, 1.0]
GBT_LEAF_CANDIDATES = [15, 31, 63]


def load_matches(parquet_dir: str) -> tuple[pd.DataFrame, list[str], np.ndarray]:
    root = Path(parquet_dir)
    cohort = eligible_matches(root)
    participants = pd.read_parquet(
        root / "participants.parquet",
        columns=["match_id", "champion", "side", "participant_win"],
    )
    participants = filter_to_eligible(participants, cohort)
    participants = participants.merge(
        cohort[["match_id", "version"]], on="match_id", how="inner", validate="many_to_one"
    )

    counts = participants.groupby("match_id").size()
    bad = counts[counts != 10]
    if len(bad):
        raise ValueError(f"eligible cohort has {len(bad)} matches without 10 participants")

    champions = sorted(participants["champion"].unique())
    champion_index = {champion: index for index, champion in enumerate(champions)}
    participants = participants.sort_values("match_id")
    sign = np.where(participants["side"].to_numpy() == "blue", 1.0, -1.0)
    champion_codes = participants["champion"].map(champion_index).to_numpy()
    match_codes, match_ids = pd.factorize(participants["match_id"], sort=True)

    features = np.zeros((len(match_ids), len(champions)), dtype=np.float32)
    features[match_codes, champion_codes] = sign

    blue = (
        participants[participants["side"] == "blue"]
        .drop_duplicates("match_id")
        .set_index("match_id")
    )
    frame = pd.DataFrame(
        {
            "match_id": match_ids.astype(str),
            "blue_win": blue.loc[match_ids, "participant_win"].to_numpy(),
            "version": blue.loc[match_ids, "version"].to_numpy(),
        }
    )
    return frame.assign(row=np.arange(len(frame))), champions, features


def ece(y: np.ndarray, probability: np.ndarray, bins: int = 10) -> float:
    edges = np.linspace(0, 1, bins + 1)
    total = 0.0
    for lower, upper in zip(edges[:-1], edges[1:]):
        mask = (probability >= lower) & (
            probability < upper if upper < 1 else probability <= upper
        )
        if mask.sum() == 0:
            continue
        total += mask.mean() * abs(y[mask].mean() - probability[mask].mean())
    return float(total)


def evaluate(y: np.ndarray, probability: np.ndarray) -> dict:
    prediction = (probability >= 0.5).astype(int)
    return {
        "accuracy": round(float(accuracy_score(y, prediction)), 4),
        "auc": round(float(roc_auc_score(y, probability)), 4),
        "log_loss": round(float(log_loss(y, probability, labels=[0, 1])), 4),
        "ece": round(ece(y, probability), 4),
    }


def _fit_selected_model(
    family: str,
    features: np.ndarray,
    labels: np.ndarray,
    train: np.ndarray,
    val: np.ndarray,
    test: np.ndarray,
) -> dict:
    if family == "logistic_regression":
        candidates = [
            (f"C={value}", LogisticRegression(C=value, max_iter=2000, solver="lbfgs"))
            for value in LR_CANDIDATES
        ]
    elif family == "gradient_boosting":
        candidates = [
            (
                f"max_leaf_nodes={value}",
                HistGradientBoostingClassifier(
                    max_iter=300,
                    learning_rate=0.08,
                    max_leaf_nodes=value,
                    early_stopping=False,
                    random_state=0,
                ),
            )
            for value in GBT_LEAF_CANDIDATES
        ]
    else:  # pragma: no cover - protected by callers
        raise ValueError(f"unknown model family: {family}")

    scored = []
    for description, model in candidates:
        model.fit(features[train], labels[train])
        probability = model.predict_proba(features[val])[:, 1]
        scored.append((log_loss(labels[val], probability, labels=[0, 1]), description, model))
    validation_loss, description, selected = min(scored, key=lambda item: item[0])
    combined = np.concatenate([train, val])
    selected.fit(features[combined], labels[combined])
    result = evaluate(labels[test], selected.predict_proba(features[test])[:, 1])
    result["selected"] = description
    result["validation_log_loss"] = round(float(validation_loss), 4)
    return result


def run_setting(
    name: str,
    features: np.ndarray,
    labels: np.ndarray,
    split: dict[str, np.ndarray],
) -> dict:
    train, val, test = split["train"], split["val"], split["test"]
    train_prevalence = float(labels[train].mean())
    majority_probability = np.full(len(test), train_prevalence)
    out = {
        "setting": name,
        "sizes": {key: int(len(value)) for key, value in split.items()},
        "majority": evaluate(labels[test], majority_probability),
        "logistic_regression": _fit_selected_model(
            "logistic_regression", features, labels, train, val, test
        ),
        "gradient_boosting": _fit_selected_model(
            "gradient_boosting", features, labels, train, val, test
        ),
    }
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parquet", required=True)
    parser.add_argument("--out", default="benchmarks/output")
    args = parser.parse_args()

    frame, champions, features = load_matches(args.parquet)
    labels = frame["blue_win"].to_numpy().astype(int)
    settings = benchmark_splits(frame)
    results = [
        run_setting(name, features, labels, split) for name, split in settings.items()
    ]

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "draft_baseline.json"
    md_path = out_dir / "draft_baseline.md"
    split_path = write_split_manifest(frame, settings, out_dir / "draft_split_manifest.csv")
    payload = {
        "protocol_version": 2,
        "feature_contract": "signed champion picks only",
        "champions": champions,
        "results": results,
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    markdown = [
        "# T1 Draft Win-Prediction Baselines",
        "",
        f"Signed champion one-hot features ({len(champions)} dimensions); canonical cohort.",
        "Validation data selects hyperparameters and is merged into the final training fit.",
        "",
    ]
    for result in results:
        sizes = result["sizes"]
        markdown += [
            f"## {result['setting']} (train {sizes['train']:,} / val {sizes['val']:,} / test {sizes['test']:,})",
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
        "The IID mixed-patch and same-build settings are controls, not causal estimates",
        "of patch drift. Compare settings descriptively and report uncertainty.",
        "",
    ]
    md_path.write_text("\n".join(markdown))
    write_run_manifest(
        out_dir,
        "draft_baseline",
        parameters={
            "protocol_version": 2,
            "feature_contract": payload["feature_contract"],
            "lr_candidates": LR_CANDIDATES,
            "gbt_leaf_candidates": GBT_LEAF_CANDIDATES,
        },
        inputs=[
            Path(args.parquet) / "matches.parquet",
            Path(args.parquet) / "participants.parquet",
        ],
        outputs=[json_path, md_path, split_path],
    )
    print(f"reports written to {out_dir}")


if __name__ == "__main__":
    main()
