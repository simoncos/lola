# LoLA Research Review and TODOs

Last reviewed: 2026-07-25 (HKT)

This document is the compact handoff for the 2026-07 MoA review, protocol
remediation, and real-data rerun. For the full evidence ledger, see
[`REMEDIATION_STATUS.md`](REMEDIATION_STATUS.md). Pre-remediation numbers in
`HANDOFF.md` and legacy output files remain historical and must not be cited.

## Review outcome

### What is now supported

- The `dataset-v0` release asset was verified against its published SHA-256,
  and the extracted SQLite database passed `PRAGMA quick_check`.
- Strict validation passed on 222,652 matches, 2,226,520 participants,
  8,906,080 participant-timeline rows, 13,127,488 normalized kill events, and
  18,923,977 distinct assist links.
- The HMAC-pseudonymized Parquet v2 bundle contains eight tables. Every
  Parquet row count and SHA-256 matches its manifest.
- T1, T2, and T3 use explicit train/validation/test contracts. Their split
  manifests contain no match crossing partitions.
- T1 shows modest draft-composition signal: temporal-holdout logistic
  regression AUC is 0.5715.
- T2 shows strong descriptive prediction from observed game state:
  temporal-holdout logistic-regression AUC is 0.7820 at 10 minutes and 0.8899
  at 20 minutes.
- Current reports, figures, and their upstream inputs are connected by run
  manifests. Because the rerun preceded the final commit, the manifests record
  `git_dirty: true` plus the exact executable source-tree fingerprint.

### What the rerun does not support

- T3 does not show incremental predictive value from the tested 8,128
  cross-team champion-pair interactions. Test log loss worsens in all three
  evaluation settings. This is a predictive negative result, not evidence
  that causal counters do not exist.
- The within-player, within-champion learning analysis does not support the
  old positive mastery narrative. Across 123 champions, no 95% bootstrap
  interval is strictly positive; 92 are strictly negative and 31 cross zero.
- The negative learning slopes must not be interpreted as players causally
  becoming worse. Match ID is only a time proxy, play outside the archive is
  unobserved, continued champion use is selective, and the performance
  construct may itself drift across builds or positions.
- High-tier ban-win salience versus learning slope is weak and uncertain:
  Spearman 0.1448, 95% bootstrap interval [-0.0281, 0.3152].
- A ban-win salience residual is not a direct measure of anti-fun, unfairness,
  perceived power, or player motivation.

## Publication decision

The code and current result artifacts are ready for version control. The two
paper drafts are **not** publication-ready and remain withdrawn pending the
work below. Raw dataset republication remains a separate compliance decision
and was intentionally not performed in this remediation.

## TODOs

### P0 — resolve before rewriting claims

1. Diagnose the globally negative learning-slope pattern:
   - test alternative ordering proxies and build-local orderings;
   - measure attrition, survivorship, and player-champion selection;
   - run negative controls and alternative early-performance definitions;
   - report sensitivity to minimum cell size and position inclusion.
2. Add uncertainty and stability checks for T1/T2/T3:
   - repeated IID seeds where applicable;
   - cluster-aware or bootstrap uncertainty at the match/build level;
   - convergence and calibration review;
   - multiplicity control for champion-level comparisons.
3. Ask an independent reviewer to audit the new learning design and the
   interpretation of the T3 negative result before either enters a paper.

### P1 — rewrite and publication preparation

4. Rewrite both paper drafts from the v2 outputs:
   - replace abstract, results, discussion, limitations, and figure callouts;
   - retain the T3 and learning results even when they weaken the original
     narrative;
   - remove all legacy mastery, counter-cycle, anti-fun, and unfairness claims.
5. Verify every cited paper against its full text and rebuild the novelty
   comparison without relying on search snippets.
6. Select venue/template only after the revised contribution is stable; do
   not claim publication readiness from passing tests alone.

### P2 — separate release track

7. Keep the current GitHub Raw Release unchanged until the Riot
   permission/compliance decision is explicit.
8. If redistribution is approved, create a fresh release from a clean commit,
   regenerate manifests so `git_dirty` is false, verify hashes again, and
   publish only the pseudonymized bundle. Never publish `lola.db` or the HMAC
   key.

## Current evidence map

- Review ledger: [`REMEDIATION_STATUS.md`](REMEDIATION_STATUS.md)
- Benchmark protocol: [`r1-dataset-paper/BENCHMARKS.md`](r1-dataset-paper/BENCHMARKS.md)
- T1: `benchmarks/output/draft_baseline.{json,md,run.json}`
- T2: `benchmarks/output/early_game_baseline.{json,md,run.json}`
- T3: `benchmarks/output/matchup_interaction_baseline.{json,md,run.json}`
- Learning: `analysis/output/mastery_learning.{csv,json,md,run.json}`
- Ban salience: `analysis/output/design_ban_salience.{json,md,run.json}`
- Figures: `analysis/output/figures/` and `figures.run.json`

## Acceptance checklist

- [x] Release asset digest verified
- [x] SQLite quick check and strict validation passed
- [x] Parquet v2 row counts, hashes, HMAC format, and quality report verified
- [x] T1/T2/T3 rerun with audited split and run manifests
- [x] Learning, ban salience, and figures rerun
- [x] Figure dimensions, labels, clipping, and overlap reviewed
- [x] Full test suite passed (`18 passed`)
- [x] Provenance records dirty state and exact source-tree identity
- [ ] Learning-construct sensitivity analysis completed
- [ ] Model uncertainty/stability package completed
- [ ] Independent methodological rereview completed
- [ ] Both papers rewritten from v2 outputs
- [ ] Full-text citation audit completed
- [ ] Raw redistribution permission decided
