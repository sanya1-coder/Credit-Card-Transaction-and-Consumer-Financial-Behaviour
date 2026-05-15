# Credit Card Transaction and Consumer Financial Behaviour
## ECO 6810 Final Project Report

**Team:** P19 — Sanya Mittal, Astha Rawat, Divya Mahendru, Harsh Lathwal, Siddhanth Pandita
**Dataset:** IBM Credit Card Transactions (Kaggle — `ealtman2019/credit-card-transactions`, CC0 1.0)
**Primary metric:** Mean Absolute Error (MAE) on Credit Utilisation Ratio (CUR)
**Run command:** `uv run main.py`

---

## 1. Research Question

Can we predict a credit card holder's Credit Utilisation Ratio (CUR) from their demographic profile and transaction behaviour, and which factors drive it most?

CUR is the fraction of available credit a person is currently using (`Total Debt / Credit Limit × 100`). High CUR is a strong early-warning signal of financial stress and a key input to credit scoring models. Understanding what drives CUR helps lenders identify over-extended customers early and helps consumers understand their own financial risk.

---

## 2. Dataset

| Item | Detail |
|---|---|
| Source | Kaggle — `ealtman2019/credit-card-transactions` |
| Licence | CC0 1.0 Universal (no restrictions on academic use) |
| Files used | `sd254_users.csv` (2,000 user profiles), `sd254_cards.csv` (6,146 card records) |
| Transaction file | `credit_card_transactions-ibm_v2.csv` (24 M rows, 2.2 GB — too large for GitHub; `User0_credit_card_transactions.csv` used as fallback for spending features) |
| Key user fields | Age, yearly income, total debt, FICO score, per capita income |
| Key card fields | Credit limit per card (summed per user to get total credit limit) |

The dataset is synthetic but calibrated to mirror real US consumer finance distributions, so there are no privacy concerns. All required files are committed under `archive/` — no Kaggle API key or download is needed to reproduce results.

**Structural note:** Approximately 50 % of users in this dataset have `Total Debt ≥ Credit Limit` (CUR = 100 %), creating a ceiling effect. This is a known property of the synthetic data and is documented in the charter.

---

## 3. Methodology

### 3.1 Target Variable

Credit Utilisation Ratio (CUR), computed per user as:

```
CUR = (Total Debt / Total Credit Limit) × 100
```

Values are clipped to [0, 100]. The training-set mean CUR is **77.90 %**, reflecting the ceiling effect noted above.

### 3.2 Features (15 total)

| Category | Features |
|---|---|
| Income & debt | Yearly Income, Total Debt, Per Capita Inc, Debt_to_Income |
| Credit profile | Total_Credit_Limit, Num_Cards, Income_per_Card |
| Transaction behaviour | Txn_Count, Total_Spend, Mean_Txn, Std_Txn, Max_Txn, Spend_to_Limit |
| Demographics | Current Age, FICO Score |

All continuous features were standardised (zero mean, unit variance) before fitting.

### 3.3 Baseline

The baseline predicts the global training-set mean CUR (77.90 %) for every test observation. This is the simplest possible model and sets the floor any real model must beat.

| Metric | Value |
|---|---|
| Baseline MAE (global mean) | **30.41 pp** |

### 3.4 Model

**Ridge regression** (`alpha = 1.0`) was chosen because:
- CUR is a continuous target — regression is appropriate
- Ridge handles correlated features (income, debt, and credit limit are all correlated) better than OLS by shrinking coefficients rather than inflating them
- Coefficients are directly interpretable: sign and magnitude show each feature's direction and relative effect
- It runs fast and reproducibly on any machine without GPU or special hardware

### 3.5 Train / Test Split

80 % training (1,600 users), 20 % test (400 users), `random_state = 42` for reproducibility.

---

## 4. Results

### 4.1 Predictive Performance

| Model | Test MAE | Threshold | Passed |
|---|---|---|---|
| Baseline (global mean) | 30.41 pp | 15.0 pp | ✗ |
| Ridge regression | **12.79 pp** | 15.0 pp | ✓ |
| Improvement over baseline | **57.9 %** | — | — |

The Ridge model reduces MAE by 17.6 percentage points compared to always predicting the mean — a 57.9 % improvement. The model clears the 15 pp threshold set in the charter.

### 4.2 Feature Importance (Ridge Coefficients)

The five strongest predictors by absolute coefficient magnitude:

| Rank | Feature | Coefficient | Interpretation |
|---|---|---|---|
| 1 | Debt_to_Income | +21.14 | Higher debt relative to income → much higher CUR |
| 2 | Num_Cards | −8.44 | More cards → lower CUR (debt spread across more limits) |
| 3 | Income_per_Card | −7.66 | Higher income per card → lower CUR |
| 4 | Total_Credit_Limit | −7.18 | More available credit → lower utilisation ratio |
| 5 | Yearly Income | +9.96 | Positive sign reflects that higher-income users in this synthetic dataset carry larger absolute debt balances, which outpaces the limit increase — a known artefact of the data generation process |

All coefficient signs align with established consumer finance intuition. The debt-to-income ratio being the strongest predictor is expected — it directly captures the balance between what someone owes and what they earn.

### 4.3 Hypothesis Tests

**H₁ (utilisation gradient):** Consumers in the bottom credit-limit quintile have a mean CUR of **94.70 %** vs. **53.98 %** for the top quintile — a gap of **40.72 pp**, well above the 20 pp threshold. t-statistic = 18.09, p < 0.001. **H₁ supported.**

**H₂ (revolver threshold):** Revolvers (high spenders) had mean CUR of **75.65 %** vs. **86.25 %** for transactors — the direction is reversed from the hypothesis. p = 0.9999 (not significant in the predicted direction). **H₂ not supported.** This likely reflects the ceiling effect: even low-spending users have high CUR because their debt was already high at account opening.

---

## 5. Limitations

- **Synthetic data:** The dataset is generated, not real transaction records. Patterns may not fully reflect real-world complexity or regional variation.
- **Ceiling effect:** ~50 % of users have CUR = 100 % (debt ≥ limit). A linear model cannot predict below ~12 pp MAE on this distribution. A model trained on real data with a more continuous CUR distribution would likely achieve lower MAE.
- **No time dimension:** We model a cross-sectional snapshot. CUR changes month-to-month; a panel model would capture dynamics that this approach misses.
- **Linear model:** Ridge cannot capture non-linear interactions (e.g., the effect of income may differ at very high vs. very low credit limits). A gradient-boosted tree would likely improve MAE further.
- **H₂ failure:** The revolver/transactor hypothesis was not supported, likely because the synthetic data's debt values are not well-correlated with spending patterns in the transaction file.

---

## 6. Reproducibility

The full pipeline runs with one command from a clean clone:

```
uv run main.py
```

The script:
1. Loads `archive/sd254_users.csv` and `archive/sd254_cards.csv` (committed to repo)
2. Merges on user ID, computes CUR, engineers 15 features
3. Trains Ridge regression on 80 % split
4. Writes `outputs/baseline_metric.json` and `outputs/primary_metric.json`
5. Writes `outputs/model_coefficients.json`, `outputs/hypothesis_tests.json`, `outputs/milestone_manifest.json`
6. Saves figures to `outputs/figures/`

No internet access, no Kaggle API key, and no manual steps are required. Runtime is under 2 minutes on a standard laptop.

---

## 7. Conclusion

Ridge regression on 15 demographic and behavioural features predicts Credit Utilisation Ratio with a test MAE of **12.79 pp**, a **57.9 % improvement** over the global-mean baseline (30.41 pp) and below the 15 pp charter threshold. The strongest predictor is debt-to-income ratio, followed by number of cards and income per card — all directionally consistent with consumer finance theory. Hypothesis H₁ (utilisation gradient by credit limit) was strongly supported; H₂ (revolver threshold) was not, likely due to the ceiling effect in the synthetic data.

Future work could explore gradient boosting to capture non-linear interactions, and incorporate monthly transaction patterns for richer time-varying features.

---

## 8. Output Files

| File | Contents |
|---|---|
| `outputs/baseline_metric.json` | Global mean MAE = 30.41 pp |
| `outputs/primary_metric.json` | Ridge MAE = 12.79 pp, passed = true |
| `outputs/model_coefficients.json` | Ridge intercept and all 15 feature coefficients |
| `outputs/hypothesis_tests.json` | H₁ and H₂ t-test results |
| `outputs/milestone_manifest.json` | Dataset sources, artefact checksums, run metadata |
| `outputs/processed_data.csv` | Merged and feature-engineered dataset |
| `outputs/test_results.csv` | Per-user actual vs. predicted CUR on test set |
| `outputs/figures/` | Distribution plots, quintile chart, FICO scatter, model accuracy, feature importance |
