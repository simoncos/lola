# T1 Draft Win-Prediction Baselines

Signed champion one-hot features (128 dims); matches < 10 min excluded.

## cross-patch split (train 112,921 / val 16,235 / test 93,460)

| Model | Accuracy | AUC | Log-loss | ECE |
|---|---|---|---|---|
| majority | 0.5064 | 0.5000 | 0.6931 | — |
| logistic_regression | 0.5474 | 0.5683 | 0.6867 | 0.0171 |
| gradient_boosting | 0.5430 | 0.5604 | 0.6876 | 0.0044 |

## same-patch split (train 177,751 / val 22,556 / test 22,309)

| Model | Accuracy | AUC | Log-loss | ECE |
|---|---|---|---|---|
| majority | 0.5036 | 0.5000 | 0.6931 | — |
| logistic_regression | 0.5552 | 0.5787 | 0.6834 | 0.0061 |
| gradient_boosting | 0.5485 | 0.5684 | 0.6857 | 0.0060 |

Interpretation targets: literature consensus puts draft-only
accuracy at ~52-58% on balanced data (DraftRec: ~55% with a
transformer + player histories). The cross-patch vs same-patch
gap quantifies patch drift.
