"""Legacy exploratory decomposition of the champion kill matrix.

Kill exchanges are not lane matchups or causal counter-picks. This prototype is
retained for audit history and is not an active publication result.

Runs on the in-repo derived matrix (results/kill_matrix_22k.csv), so it works
before the full lola.db is available. Method:

1. Pairwise dominance. For champions i, j let K_ij be kills of j by i. The
   kill-exchange probability p_ij = K_ij / (K_ij + K_ji) conditions on an
   interaction occurring between the pair, so co-occurrence exposure cancels
   and no pick normalization is needed (unlike the 2016 centrality analysis).

2. Log-odds matrix A_ij = log(K_ij + a) - log(K_ji + a) (Laplace a=1),
   antisymmetric by construction.

3. HodgeRank / least-squares Elo: fit ratings r minimizing
   sum_ij w_ij (A_ij - (r_i - r_j))^2 with interaction weights
   w_ij = K_ij + K_ji. The fitted part is the *transitive* component
   (cf. mElo / Nash averaging, Balduzzi et al. 2018); the residual
   C = A - grad(r) is the *cyclic* (rock-paper-scissors) component.

4. Report: transitive vs cyclic energy share, rating ranking (vs legacy
   eigenvector-centrality ranking), and the strongest cyclic triads.

Usage:
    python analysis/counter_structure.py [--kill-matrix results/kill_matrix_22k.csv]
                                         [--out analysis/output]
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

LAPLACE = 1.0
MIN_INTERACTIONS = 200  # pairs with fewer total kills are down-weighted naturally


def load_kill_matrix(path: str) -> pd.DataFrame:
    k = pd.read_csv(path, index_col=0)
    assert list(k.index) == list(k.columns), "matrix must be square and aligned"
    np.fill_diagonal(k.values, 0)  # source data has a stray diagonal entry
    return k


def decompose(k: pd.DataFrame) -> dict:
    names = list(k.index)
    K = k.values.astype(float)
    n = len(names)

    W = K + K.T                                   # interaction weights
    A = np.log(K + LAPLACE) - np.log(K.T + LAPLACE)  # antisymmetric log-odds

    # Weighted least squares for r: (D - W) r = b, b_i = sum_j w_ij A_ij.
    # Graph Laplacian system, singular (gauge freedom) -> lstsq + zero-mean.
    D = np.diag(W.sum(axis=1))
    b = (W * A).sum(axis=1)
    r, *_ = np.linalg.lstsq(D - W, b, rcond=None)
    r -= r.mean()

    G = r[:, None] - r[None, :]                   # transitive (gradient) part
    C = A - G                                     # cyclic residual

    total = float((W * A**2).sum())
    cyclic = float((W * C**2).sum())
    shares = {
        "transitive_share": round(1 - cyclic / total, 4),
        "cyclic_share": round(cyclic / total, 4),
    }

    ratings = (
        pd.DataFrame({"champion": names, "rating": r})
        .sort_values("rating", ascending=False)
        .reset_index(drop=True)
    )

    # Strongest cyclic triads: cycle strength s = A_ij + A_jk + A_ki, weighted
    # by the weakest pairwise interaction count to suppress noise triads.
    triads = []
    for i, j, l in itertools.combinations(range(n), 3):
        w_min = min(W[i, j], W[j, l], W[l, i])
        if w_min < MIN_INTERACTIONS:
            continue
        s = A[i, j] + A[j, l] + A[l, i]
        triads.append((abs(s), s, names[i], names[j], names[l], int(w_min)))
    triads.sort(reverse=True)
    top_triads = [
        {
            # reverse direction when s < 0 so the arrow always reads i beats j
            "cycle": (f"{a} > {b} > {c} > {a}" if s > 0 else f"{a} > {c} > {b} > {a}"),
            "strength_logodds": round(abs(s), 3),
            "min_pair_interactions": w,
        }
        for _, s, a, b, c, w in triads[:15]
    ]

    # Legacy comparison: eigenvector centrality of row-sum-normalized K
    # (the 2016 champion_rank.py method, row_sum_norm=True).
    Kn = K / K.sum(axis=1, keepdims=True)
    eigvals, eigvecs = np.linalg.eig(Kn)
    ev = np.abs(np.real(eigvecs[:, np.argmax(np.real(eigvals))]))
    legacy = pd.Series(ev, index=names).rank(ascending=False)
    modern = pd.Series(r, index=names).rank(ascending=False)
    spearman = float(legacy.corr(modern, method="spearman"))

    # Most counter-defining pairs: largest |C_ij| among well-observed pairs
    pairs = []
    for i, j in itertools.combinations(range(n), 2):
        if W[i, j] >= MIN_INTERACTIONS:
            pairs.append((abs(C[i, j]), C[i, j], names[i], names[j], int(W[i, j])))
    pairs.sort(reverse=True)
    top_pairs = [
        {
            "pair": f"{a} beats {b}" if c > 0 else f"{b} beats {a}",
            "cyclic_logodds": round(abs(c), 3),
            "interactions": w,
        }
        for _, c, a, b, w in pairs[:15]
    ]

    return {
        "status": "legacy_exploratory_not_citable",
        "interpretation": (
            "Kill-exchange association only; not a causal counter-pick or lane matchup."
        ),
        "champions": len(names),
        "total_kill_events": int(K.sum()),
        "energy_shares": shares,
        "spearman_vs_legacy_eigenvector": round(spearman, 4),
        "top_ratings": ratings.head(15).to_dict("records"),
        "bottom_ratings": ratings.tail(5).to_dict("records"),
        "top_cyclic_triads": top_triads,
        "top_cyclic_pairs": top_pairs,
    }


def write_report(result: dict, out_dir: Path, source: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "counter_structure_22k.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False)
    )

    md = [
        "# Legacy Kill-Exchange Decomposition (not citable)",
        "",
        "> Kill-exchange association only; not a causal counter-pick or lane matchup.",
        "",
        f"Source: `{source}` — {result['champions']} champions, "
        f"{result['total_kill_events']:,} kill events (full-crawl derived matrix).",
        "",
        "Method: pairwise kill-exchange log-odds -> weighted HodgeRank "
        "decomposition into a transitive rating (least-squares Elo, cf. "
        "mElo/Nash averaging, Balduzzi et al. 2018) plus a cyclic "
        "(rock-paper-scissors) residual.",
        "",
        "## Headline numbers",
        "",
        f"- **Transitive share of pairwise structure: "
        f"{result['energy_shares']['transitive_share']:.1%}**",
        f"- **Cyclic kill-association share: "
        f"{result['energy_shares']['cyclic_share']:.1%}**",
        f"- Spearman correlation of the modern rating vs the 2016 "
        f"eigenvector-centrality ranking: "
        f"{result['spearman_vs_legacy_eigenvector']:.3f}",
        "",
        "Interpretation: the near-zero correlation with the 2016 ranking is "
        "itself a finding - eigenvector centrality on the row-normalized kill "
        "matrix largely tracks kill *volume* (popularity x aggression), "
        "whereas the HodgeRank rating measures pairwise kill *dominance* "
        "conditioned on interactions. The two methods answer different "
        "questions; the 2016 report's 'no significant difference from average "
        "score' observation is consistent with this.",
        "",
        "## Top 15 champions by transitive kill-dominance rating",
        "",
        "| # | Champion | Rating (log-odds) |",
        "|---|---|---|",
    ]
    for idx, row in enumerate(result["top_ratings"], 1):
        md.append(f"| {idx} | {row['champion']} | {row['rating']:.3f} |")
    md += ["", "## Strongest cyclic triads (rock-paper-scissors)", ""]
    md += ["| Cycle | Strength (log-odds) | Min pair interactions |", "|---|---|---|"]
    for t in result["top_cyclic_triads"]:
        md.append(
            f"| {t['cycle']} | {t['strength_logodds']} | {t['min_pair_interactions']:,} |"
        )
    md += ["", "## Strongest pairwise counter relationships (cyclic residual)", ""]
    md += ["| Relationship | Cyclic log-odds | Interactions |", "|---|---|---|"]
    for p in result["top_cyclic_pairs"]:
        md.append(f"| {p['pair']} | {p['cyclic_logodds']} | {p['interactions']:,} |")
    md += [
        "",
        "## Caveats (prototype)",
        "",
        "- Kill exchanges are a *proxy* for matchup dominance; the paper-grade "
        "version uses per-match win/loss matchup matrices sliced by patch and "
        "tier (requires full lola.db).",
        "- Kills reflect aggression profiles (assassins kill more than tanks "
        "regardless of matchup advantage); the transitive rating is therefore "
        "a 'kill-dominance' rating, not a strength rating. The win-based "
        "matrix removes this bias.",
        "- No patch/tier slicing yet - this aggregates patches 5.21-6.1 and "
        "all tiers.",
        "",
    ]
    (out_dir / "counter_structure_22k.md").write_text("\n".join(md))
    print(f"reports written to {out_dir}/counter_structure_22k.{{md,json}}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kill-matrix", default="results/kill_matrix_22k.csv")
    ap.add_argument("--out", default="analysis/output")
    args = ap.parse_args()

    k = load_kill_matrix(args.kill_matrix)
    result = decompose(k)
    write_report(result, Path(args.out), args.kill_matrix)
    print(json.dumps(result["energy_shares"], indent=2))
    print("spearman vs legacy:", result["spearman_vs_legacy_eigenvector"])


if __name__ == "__main__":
    main()
