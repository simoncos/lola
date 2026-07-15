"""R2 paper-grade analysis: win-based matchup structure by patch and tier.

Upgrades analysis/counter_structure.py (kill-exchange proxy) to real match
outcomes: every match yields 25 blue-vs-red champion pair observations, giving
a 128x128 "i's team beat j's team" win matrix W. Side advantage cancels
because both orientations are folded together.

For each slice (overall / per patch family / per tier bucket) we run the same
weighted HodgeRank decomposition: log-odds A_ij = log((W_ij+1)/(W_ji+1)) into
a transitive rating plus a cyclic (counter-pick) residual, with weights
N_ij = W_ij + W_ji (cf. mElo / Nash averaging, Balduzzi et al. 2018).

Input: the anonymized Parquet export (participants.parquet).

Usage:
    python analysis/matchup_structure.py --parquet <dir> [--out analysis/output]
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

MIN_PAIR_GAMES = 300  # threshold for reporting individual pairs

TIER_BUCKETS = {
    "BRONZE": "low", "SILVER": "low",
    "GOLD": "mid", "PLATINUM": "mid",
    "DIAMOND": "high", "MASTER": "high", "CHALLENGER": "high",
}


def load_pairs(parquet_dir: str) -> pd.DataFrame:
    """Return one row per (match, blue champion, red champion) pair."""
    p = pd.read_parquet(
        Path(parquet_dir) / "participants.parquet",
        columns=["match_id", "champion", "side", "participant_win",
                 "previous_season_tier", "version"],
    )

    # Majority previous-season tier per match -> tier bucket
    tier_counts = (
        p.groupby(["match_id", "previous_season_tier"]).size().reset_index(name="n")
        .sort_values("n", ascending=False)
        .drop_duplicates("match_id")
        .rename(columns={"previous_season_tier": "majority_tier"})
    )
    tier_counts["tier_bucket"] = tier_counts["majority_tier"].map(TIER_BUCKETS)

    blue = p[p["side"] == "blue"]
    red = p[p["side"] == "red"]
    pairs = blue.merge(
        red[["match_id", "champion"]].rename(columns={"champion": "red_champion"}),
        on="match_id",
    ).rename(columns={"champion": "blue_champion", "participant_win": "blue_win"})
    pairs["patch"] = pairs["version"].str.extract(r"^(\d+\.\d+)")[0]
    pairs = pairs.merge(
        tier_counts[["match_id", "tier_bucket"]], on="match_id", how="left"
    )
    return pairs[["match_id", "blue_champion", "red_champion", "blue_win",
                  "patch", "tier_bucket"]]


def win_matrix(pairs: pd.DataFrame, champions: list[str]) -> np.ndarray:
    """W[i, j] = number of times i's team beat j's team (side-agnostic)."""
    idx = {c: k for k, c in enumerate(champions)}
    n = len(champions)
    g = (
        pairs.groupby(["blue_champion", "red_champion"])["blue_win"]
        .agg(["sum", "count"])
        .reset_index()
    )
    W = np.zeros((n, n))
    bi = g["blue_champion"].map(idx).to_numpy()
    ri = g["red_champion"].map(idx).to_numpy()
    np.add.at(W, (bi, ri), g["sum"].to_numpy(float))          # blue i beat red j
    np.add.at(W, (ri, bi), (g["count"] - g["sum"]).to_numpy(float))  # red j beat blue i
    return W


def hodge(W: np.ndarray) -> dict:
    """Weighted HodgeRank decomposition of the pairwise win matrix."""
    N = W + W.T
    A = np.log(W + 1.0) - np.log(W.T + 1.0)
    D = np.diag(N.sum(axis=1))
    b = (N * A).sum(axis=1)
    r, *_ = np.linalg.lstsq(D - N, b, rcond=None)
    r -= r.mean()
    C = A - (r[:, None] - r[None, :])
    total = float((N * A**2).sum())
    cyclic = float((N * C**2).sum())
    return {
        "rating": r,
        "cyclic_residual": C,
        "weights": N,
        "transitive_share": 1 - cyclic / total,
        "cyclic_share": cyclic / total,
    }


def hodge_energies(W: np.ndarray) -> tuple[float, float]:
    """(transitive_energy, cyclic_energy) of the weighted decomposition."""
    h = hodge(W)
    N, C = h["weights"], h["cyclic_residual"]
    A = np.log(W + 1.0) - np.log(W.T + 1.0)
    total = float((N * A**2).sum())
    cyclic = float((N * C**2).sum())
    return total - cyclic, cyclic


def null_energies(pairs: pd.DataFrame, champions: list[str],
                  n_perm: int = 3, seed: int = 7) -> tuple[float, float]:
    """Mean (transitive, cyclic) energies under match-level outcome
    permutation - a pure-noise baseline with the same pairing structure,
    marginals and intra-match correlation (each match's 25 pair rows stay
    tied to a single outcome)."""
    rng = np.random.default_rng(seed)
    match_win = pairs.drop_duplicates("match_id")[["match_id", "blue_win"]]
    et, ec = [], []
    for _ in range(n_perm):
        shuffled = match_win.assign(
            blue_win=rng.permutation(match_win["blue_win"].to_numpy())
        )
        perm = pairs.drop(columns="blue_win").merge(shuffled, on="match_id")
        t, c = hodge_energies(win_matrix(perm, champions))
        et.append(t)
        ec.append(c)
    return float(np.mean(et)), float(np.mean(ec))


def summarize_slice(pairs: pd.DataFrame, champions: list[str], label: str) -> dict:
    W = win_matrix(pairs, champions)
    h = hodge(W)
    order = np.argsort(-h["rating"])

    # Noise-corrected signal decomposition. Raw cyclic share is a sample-size
    # artifact (binomial noise is almost entirely non-transitive and its
    # energy is roughly constant per pair, while signal energy grows with
    # games) - so we subtract the permutation-null energies before forming
    # the share.
    obs_t, obs_c = hodge_energies(W)
    null_t, null_c = null_energies(pairs, champions)
    sig_t = max(0.0, obs_t - null_t)
    sig_c = max(0.0, obs_c - null_c)
    corrected = sig_c / (sig_t + sig_c) if (sig_t + sig_c) > 0 else float("nan")

    return {
        "slice": label,
        "matches": int(pairs["match_id"].nunique()),
        "pair_observations": int(len(pairs)),
        "transitive_share_raw": round(h["transitive_share"], 4),
        "cyclic_share_raw": round(h["cyclic_share"], 4),
        "cyclic_share_corrected": round(corrected, 4),
        "signal_to_noise": round((sig_t + sig_c) / (null_t + null_c), 3),
        "top10": [
            {"champion": champions[i], "rating": round(float(h["rating"][i]), 4)}
            for i in order[:10]
        ],
        "bottom5": [
            {"champion": champions[i], "rating": round(float(h["rating"][i]), 4)}
            for i in order[-5:]
        ],
        "_hodge": h,
    }


def top_cyclic_pairs(h: dict, champions: list[str], k: int = 12) -> list[dict]:
    C, N = h["cyclic_residual"], h["weights"]
    out = []
    for i, j in itertools.combinations(range(len(champions)), 2):
        if N[i, j] >= MIN_PAIR_GAMES:
            out.append((abs(C[i, j]), C[i, j], i, j, int(N[i, j])))
    out.sort(reverse=True)
    return [
        {
            "pair": (f"{champions[i]} counters {champions[j]}" if c > 0
                     else f"{champions[j]} counters {champions[i]}"),
            "cyclic_logodds": round(abs(float(c)), 3),
            "games": n,
        }
        for _, c, i, j, n in out[:k]
    ]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", required=True)
    ap.add_argument("--out", default="analysis/output")
    args = ap.parse_args()

    pairs = load_pairs(args.parquet)
    champions = sorted(set(pairs["blue_champion"]) | set(pairs["red_champion"]))
    print(f"{pairs['match_id'].nunique():,} matches, "
          f"{len(pairs):,} pair observations, {len(champions)} champions")

    slices: list[dict] = [summarize_slice(pairs, champions, "overall")]
    for patch in ["5.22", "5.23", "5.24"]:  # 5.21 (8) and 6.1 (1.3k) too thin
        slices.append(
            summarize_slice(pairs[pairs["patch"] == patch], champions, f"patch {patch}")
        )
    for bucket in ["low", "mid", "high"]:
        slices.append(
            summarize_slice(pairs[pairs["tier_bucket"] == bucket], champions,
                            f"tier {bucket}")
        )

    overall = slices[0]
    cyclic_pairs = top_cyclic_pairs(overall["_hodge"], champions)

    # Rating stability across slices (Spearman vs overall)
    overall_rating = pd.Series(overall["_hodge"]["rating"], index=champions)
    stability = {}
    for s in slices[1:]:
        r = pd.Series(s["_hodge"]["rating"], index=champions)
        stability[s["slice"]] = round(float(overall_rating.corr(r, method="spearman")), 4)

    for s in slices:
        s.pop("_hodge")
    result = {
        "champions": len(champions),
        "slices": slices,
        "top_cyclic_pairs_overall": cyclic_pairs,
        "rating_spearman_vs_overall": stability,
    }

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "matchup_structure.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False)
    )

    md = [
        "# Win-Based Matchup Structure by Patch and Tier",
        "",
        "Real match outcomes (25 blue-vs-red champion pairs per match), weighted",
        "HodgeRank decomposition into transitive strength + cyclic counter residual.",
        "Side advantage cancels by folding both orientations.",
        "",
        "## Transitive vs cyclic structure by slice",
        "",
        "Raw cyclic shares are sample-size artifacts: binomial noise is almost",
        "entirely non-transitive and contributes near-constant energy per pair,",
        "while signal energy grows with the number of games (a match-level",
        "permutation null shows ~92% 'cyclic' share on pure noise). The",
        "corrected column subtracts the permutation-null energies (3 perms)",
        "from both components before forming the share.",
        "",
        "| Slice | Matches | Cyclic (raw) | **Cyclic (corrected)** | Signal/noise | Rating Spearman vs overall |",
        "|---|---|---|---|---|---|",
    ]
    for s in slices:
        md.append(
            f"| {s['slice']} | {s['matches']:,} | {s['cyclic_share_raw']:.1%} "
            f"| **{s['cyclic_share_corrected']:.1%}** "
            f"| {s['signal_to_noise']} "
            f"| {stability.get(s['slice'], '—')} |"
        )
    md += ["", "## Top 10 champions by matchup strength (overall)", "",
           "| # | Champion | Rating (log-odds) |", "|---|---|---|"]
    for k, row in enumerate(overall["top10"], 1):
        md.append(f"| {k} | {row['champion']} | {row['rating']:.4f} |")
    md += ["", "## Strongest counter relationships (cyclic residual, overall)", "",
           "| Relationship | Cyclic log-odds | Games |", "|---|---|---|"]
    for cp in cyclic_pairs:
        md.append(f"| {cp['pair']} | {cp['cyclic_logodds']} | {cp['games']:,} |")
    md += ["", "Notes: pairs reported only when the two champions met in >= "
           f"{MIN_PAIR_GAMES} games. Patches 5.21 (8 matches) and 6.1 (1,298) "
           "excluded from per-patch slices for sample size.", ""]
    (out_dir / "matchup_structure.md").write_text("\n".join(md))
    print(f"reports written to {out_dir}/matchup_structure.{{md,json}}")
    for s in slices:
        print(f"  {s['slice']}: cyclic raw {s['cyclic_share_raw']:.1%} -> "
              f"corrected {s['cyclic_share_corrected']:.1%} "
              f"(S/N {s['signal_to_noise']}) ({s['matches']:,} matches)")


if __name__ == "__main__":
    main()
