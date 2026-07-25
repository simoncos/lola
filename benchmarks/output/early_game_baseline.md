# T2 Early-Game Win-Prediction Baselines

Canonical cohort; no champion-composition features. Validation data selects
hyperparameters and is merged into the final training fit.

## 10 min — temporal-holdout (train 112,921 / val 16,235 / test 93,460)

| Model | Accuracy | AUC | Log-loss | ECE | Selected |
|---|---:|---:|---:|---:|---|
| majority | 0.5064 | 0.5000 | 0.6931 | 0.0016 | training prevalence |
| logistic_regression | 0.7085 | 0.7820 | 0.5598 | 0.0032 | C=1.0 |
| gradient_boosting | 0.7075 | 0.7810 | 0.5614 | 0.0042 | max_leaf_nodes=15 |

## 10 min — iid-mixed-patch (train 177,751 / val 22,556 / test 22,309)

| Model | Accuracy | AUC | Log-loss | ECE | Selected |
|---|---:|---:|---:|---:|---|
| majority | 0.5036 | 0.5000 | 0.6931 | 0.0028 | training prevalence |
| logistic_regression | 0.7134 | 0.7836 | 0.5587 | 0.0069 | C=0.1 |
| gradient_boosting | 0.7119 | 0.7830 | 0.5599 | 0.0075 | max_leaf_nodes=15 |

## 10 min — same-build-5.24.0.256 (train 64,825 / val 8,241 / test 8,112)

| Model | Accuracy | AUC | Log-loss | ECE | Selected |
|---|---:|---:|---:|---:|---|
| majority | 0.5025 | 0.5000 | 0.6932 | 0.0062 | training prevalence |
| logistic_regression | 0.7198 | 0.7903 | 0.5522 | 0.0144 | C=1.0 |
| gradient_boosting | 0.7155 | 0.7870 | 0.5564 | 0.0145 | max_leaf_nodes=15 |

## 20 min — temporal-holdout (train 110,600 / val 15,947 / test 91,854)

| Model | Accuracy | AUC | Log-loss | ECE | Selected |
|---|---:|---:|---:|---:|---|
| majority | 0.5055 | 0.5000 | 0.6931 | 0.0013 | training prevalence |
| logistic_regression | 0.8029 | 0.8899 | 0.4150 | 0.0062 | C=1.0 |
| gradient_boosting | 0.8024 | 0.8895 | 0.4151 | 0.0031 | max_leaf_nodes=15 |

## 20 min — iid-mixed-patch (train 174,368 / val 22,160 / test 21,873)

| Model | Accuracy | AUC | Log-loss | ECE | Selected |
|---|---:|---:|---:|---:|---|
| majority | 0.5028 | 0.5000 | 0.6932 | 0.0031 | training prevalence |
| logistic_regression | 0.8027 | 0.8901 | 0.4146 | 0.0087 | C=0.5 |
| gradient_boosting | 0.8019 | 0.8903 | 0.4139 | 0.0061 | max_leaf_nodes=15 |

## 20 min — same-build-5.24.0.256 (train 63,665 / val 8,111 / test 7,961)

| Model | Accuracy | AUC | Log-loss | ECE | Selected |
|---|---:|---:|---:|---:|---|
| majority | 0.5022 | 0.5000 | 0.6932 | 0.0057 | training prevalence |
| logistic_regression | 0.8053 | 0.8919 | 0.4117 | 0.0120 | C=1.0 |
| gradient_boosting | 0.8042 | 0.8916 | 0.4119 | 0.0095 | max_leaf_nodes=15 |

Do not attribute differences between settings to patch drift without a
matched target cohort, uncertainty intervals, and an explicit hypothesis test.
