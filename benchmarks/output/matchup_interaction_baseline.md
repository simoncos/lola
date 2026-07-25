# T3 Lineup-Interaction Prediction Benchmark

This benchmark tests whether regularized cross-team pair interactions improve
held-out prediction after champion main effects. It does not identify causal
counter-picks or lane matchups.

| Setting | Main log-loss | Main+pair log-loss | Delta | Main AUC | Main+pair AUC |
|---|---:|---:|---:|---:|---:|
| temporal-holdout | 0.6854 | 0.6891 | +0.0037 | 0.5717 | 0.5660 |
| iid-mixed-patch | 0.6835 | 0.6865 | +0.0030 | 0.5784 | 0.5719 |
| same-build-5.24.0.256 | 0.6834 | 0.6854 | +0.0020 | 0.5782 | 0.5775 |

A negative delta means the interaction model improved test log-loss. Report
uncertainty before making a substantive claim.
