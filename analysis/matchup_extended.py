"""R2 extended analysis: build-level meta evolution + bootstrap CIs.

Builds on matchup_structure.py (imported). Three additions:

1. Build-level rating evolution: HodgeRank ratings per game build (>= 10k
   matches), Spearman stability between consecutive builds, and the biggest
   rating movers across each build boundary (meta-shift detection).
2. Bootstrap confidence intervals for the noise-corrected cyclic share
   (match-level resampling; one permutation null per replicate).
3. Consecutive-build counter-relationship stability: correlation of the
   cyclic residual matrices between builds.

Usage:
    python analysis/matchup_extended.py --parquet <dir> [--out analysis/output]
                                        [--boot-reps 12]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from matchup_structure import hodge, hodge_energies, load_pairs, null_energies, win_matrix

MIN_BUILD_MATCHES = 10_000


def build_evolution(pairs: pd.DataFrame, champions: list[str]) -> dict:
    """Per-build ratings, consecutive stability, and top movers."""
    pairs = pairs.copy()
    pairs["build"] = pairs["version"]
    counts = pairs.groupby("build")["match_id"].nunique().sort_index()
    builds = [b for b, c in counts.items() if c >= MIN_BUILD_MATCHES]

    ratings: dict[str, pd.Series] = {}
    residuals: dict[str, np.ndarray] = {}
    for b in builds:
        h = hodge(win_matrix(pairs[pairs["build"] == b], champions))
        ratings[b] = pd.Series(h["rating"], index=champions)
        residuals[b] = h["cyclic_residual"]

    stability, movers, residual_corr = [], [], []
    for prev, cur in zip(builds, builds[1:]):
        rho = float(ratings[prev].corr(ratings[cur], method="spearman"))
        stability.append({"from": prev, "to": cur, "rating_spearman": round(rho, 4)})

        diff = (ratings[cur] - ratings[prev]).sort_values()
        movers.append({
            "boundary": f"{prev} -> {cur}",
            "biggest_gainers": [
                {"champion": c, "delta": round(float(d), 4)}
                for c, d in diff.tail(5).iloc[::-1].items()
            ],
            "biggest_losers": [
                {"champion": c, "delta": round(float(d), 4)}
                for c, d in diff.head(5).items()
            ],
        })

        iu = np.triu_indices(len(champions), k=1)
        r = float(np.corrcoef(residuals[prev][iu], residuals[cur][iu])[0, 1])
        residual_corr.append({"from": prev, "to": cur,
                              "cyclic_residual_pearson": round(r, 4)})

    return {
        "builds": [{"build": b, "matches": int(counts[b])} for b in builds],
        "rating_stability": stability,
        "top_movers": movers,
        "counter_stability": residual_corr,
    }


def corrected_cyclic_share(pairs: pd.DataFrame, champions: list[str],
                           n_perm: int = 1, seed: int = 0) -> float:
    obs_t, obs_c = hodge_energies(win_matrix(pairs, champions))
    null_t, null_c = null_energies(pairs, champions, n_perm=n_perm, seed=seed)
    sig_t = max(0.0, obs_t - null_t)
    sig_c = max(0.0, obs_c - null_c)
    return sig_c / (sig_t + sig_c) if (sig_t + sig_c) > 0 else float("nan")


def bootstrap_ci(pairs: pd.DataFrame, champions: list[str], reps: int,
                 seed: int = 11) -> dict:
    """Match-level bootstrap of the corrected cyclic share."""
    rng = np.random.default_rng(seed)
    match_ids = pairs["match_id"].unique()
    point = corrected_cyclic_share(pairs, champions, n_perm=3, seed=seed)

    estimates = []
    for rep in range(reps):
        sampled = rng.choice(match_ids, size=len(match_ids), replace=True)
        mult = pd.Series(sampled).value_counts().rename_axis("match_id").reset_index(name="w")
        boot = pairs.merge(mult, on="match_id")
        boot = boot.loc[boot.index.repeat(boot["w"])].drop(columns="w")
        estimates.append(
            corrected_cyclic_share(boot, champions, n_perm=1, seed=seed + rep + 1)
        )
    lo, hi = np.percentile(estimates, [2.5, 97.5])
    return {
        "point_estimate": round(point, 4),
        "bootstrap_reps": reps,
        "ci95": [round(float(lo), 4), round(float(hi), 4)],
        "replicates": [round(float(e), 4) for e in estimates],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", required=True)
    ap.add_argument("--out", default="analysis/output")
    ap.add_argument("--boot-reps", type=int, default=12)
    args = ap.parse_args()

    pairs = load_pairs(args.parquet)
    champions = sorted(set(pairs["blue_champion"]) | set(pairs["red_champion"]))

    print("build-level evolution...")
    evo = build_evolution(pairs, champions)
    print("bootstrap CI (overall)...")
    ci = bootstrap_ci(pairs, champions, reps=args.boot_reps)

    result = {"build_evolution": evo, "corrected_cyclic_share_overall_ci": ci}
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "matchup_extended.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False)
    )

    md = [
        "# Meta Evolution Across Builds and Uncertainty of the Cyclic Share",
        "",
        f"Builds with >= {MIN_BUILD_MATCHES:,} matches, Pre-Season 2016.",
        "",
        "## Corrected cyclic share, overall (bootstrap over matches)",
        "",
        f"- Point estimate: **{ci['point_estimate']:.1%}**",
        f"- 95% CI ({ci['bootstrap_reps']} replicates): "
        f"[{ci['ci95'][0]:.1%}, {ci['ci95'][1]:.1%}]",
        "",
        "## Rating stability between consecutive builds",
        "",
        "| From | To | Rating Spearman | Cyclic-residual Pearson |",
        "|---|---|---|---|",
    ]
    cs = {(c["from"], c["to"]): c["cyclic_residual_pearson"]
          for c in evo["counter_stability"]}
    for s in evo["rating_stability"]:
        md.append(f"| {s['from']} | {s['to']} | {s['rating_spearman']} "
                  f"| {cs[(s['from'], s['to'])]} |")
    md += ["", "## Biggest rating movers per build boundary", ""]
    for m in evo["top_movers"]:
        md.append(f"### {m['boundary']}")
        md.append("")
        gain = ", ".join(f"{g['champion']} (+{g['delta']})" for g in m["biggest_gainers"])
        lose = ", ".join(f"{g['champion']} ({g['delta']})" for g in m["biggest_losers"])
        md.append(f"- Gainers: {gain}")
        md.append(f"- Losers: {lose}")
        md.append("")
    (out_dir / "matchup_extended.md").write_text("\n".join(md))
    print(f"reports written to {out_dir}/matchup_extended.{{md,json}}")


if __name__ == "__main__":
    main()
