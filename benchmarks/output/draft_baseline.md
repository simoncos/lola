# T1 Draft Win-Prediction Baselines

Signed champion one-hot features (128 dimensions); canonical cohort.
Validation data selects hyperparameters and is merged into the final training fit.

## temporal-holdout (train 112,921 / val 16,235 / test 93,460)

| Model | Accuracy | AUC | Log-loss | ECE | Selected |
|---|---:|---:|---:|---:|---|
| majority | 0.5064 | 0.5000 | 0.6931 | 0.0016 | training prevalence |
| logistic_regression | 0.5504 | 0.5715 | 0.6856 | 0.0126 | C=0.1 |
| gradient_boosting | 0.5474 | 0.5643 | 0.6868 | 0.0030 | max_leaf_nodes=15 |

## iid-mixed-patch (train 177,751 / val 22,556 / test 22,309)

| Model | Accuracy | AUC | Log-loss | ECE | Selected |
|---|---:|---:|---:|---:|---|
| majority | 0.5036 | 0.5000 | 0.6931 | 0.0028 | training prevalence |
| logistic_regression | 0.5562 | 0.5785 | 0.6834 | 0.0047 | C=0.1 |
| gradient_boosting | 0.5496 | 0.5717 | 0.6849 | 0.0051 | max_leaf_nodes=15 |

## same-build-5.24.0.256 (train 64,825 / val 8,241 / test 8,112)

| Model | Accuracy | AUC | Log-loss | ECE | Selected |
|---|---:|---:|---:|---:|---|
| majority | 0.5025 | 0.5000 | 0.6932 | 0.0062 | training prevalence |
| logistic_regression | 0.5496 | 0.5783 | 0.6834 | 0.0141 | C=0.1 |
| gradient_boosting | 0.5454 | 0.5650 | 0.6869 | 0.0075 | max_leaf_nodes=15 |

The IID mixed-patch and same-build settings are controls, not causal estimates
of patch drift. Compare settings descriptively and report uncertainty.
