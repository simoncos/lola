# Output status

The benchmark result files committed before the 2026-07-20 protocol-v2
remediation are **stale and not citable**. They use earlier feature/split
contracts and have no current run or split manifest.

The corrected real-data rerun completed on 2026-07-21. The current citable
benchmark set is:

- `draft_baseline.*` plus `draft_baseline.run.json` and
  `draft_split_manifest.csv`;
- `early_game_baseline.*` plus `early_game_baseline.run.json` and the 10/20
  minute split manifests;
- `matchup_interaction_baseline.*` plus its run and split manifests.

All output hashes match their run manifests and the split manifests contain no
match crossing partitions. See `docs/REMEDIATION_STATUS.md` and
`docs/r1-dataset-paper/BENCHMARKS.md` for interpretation limits.
