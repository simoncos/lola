# T2 Early-Game Win-Prediction Baselines

Team-differential timeline features (blue minus red) + kill diff and
first blood within the horizon. 20-min variant restricted to matches
lasting >= 20 minutes.

## 10 min — cross-patch split (train 112,921 / test 93,460)

| Model | Accuracy | AUC | Log-loss | ECE |
|---|---|---|---|---|
| majority | 0.5064 | 0.5000 | — | — |
| logistic_regression | 0.7088 | 0.7820 | 0.5597 | 0.0034 |
| gradient_boosting | 0.7071 | 0.7811 | 0.5608 | 0.0044 |

## 10 min — same-patch split (train 177,751 / test 22,309)

| Model | Accuracy | AUC | Log-loss | ECE |
|---|---|---|---|---|
| majority | 0.5036 | 0.5000 | — | — |
| logistic_regression | 0.7133 | 0.7836 | 0.5587 | 0.0067 |
| gradient_boosting | 0.7123 | 0.7832 | 0.5596 | 0.0089 |

## 20 min — cross-patch split (train 110,600 / test 91,854)

| Model | Accuracy | AUC | Log-loss | ECE |
|---|---|---|---|---|
| majority | 0.5055 | 0.5000 | — | — |
| logistic_regression | 0.8029 | 0.8899 | 0.4150 | 0.0062 |
| gradient_boosting | 0.8023 | 0.8898 | 0.4148 | 0.0041 |

## 20 min — same-patch split (train 174,368 / test 21,873)

| Model | Accuracy | AUC | Log-loss | ECE |
|---|---|---|---|---|
| majority | 0.5028 | 0.5000 | — | — |
| logistic_regression | 0.8028 | 0.8901 | 0.4146 | 0.0089 |
| gradient_boosting | 0.8026 | 0.8903 | 0.4138 | 0.0074 |

Reference: literature places 10-minute prediction at ~70-75% (Silva 2018: 63.9% at 5 min; Hodge 2021: 85% pro).
