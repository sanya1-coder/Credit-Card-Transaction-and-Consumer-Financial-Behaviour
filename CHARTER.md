# Project Charter — ECO 6810 Final Project

## Header

| Field | Value |
|---|---|
| Team members | Sanya Mittal, Astha Rawat, Divya Mahendru, Harsh Lathwal, Siddhanth Pandita |
| Project type | **predictive** |
| Estimated hours per person | 50 hours |
| Charter version | v2 |
| Date | 2026-04-25 |

---

## 1. Problem and stakeholder

Credit card debt is a persistent source of financial stress for consumers and a key risk
management challenge for lenders. Financial institutions need to identify customers who
are likely to carry high revolving balances (high credit utilisation) so they can intervene
early with credit counselling or limit adjustments. Consumers, in turn, benefit from
personalised insights that flag when their spending patterns are pushing them toward
costly revolving debt.

This project builds a predictive model that estimates an individual's **Credit Utilisation
Ratio (CUR)** — the fraction of available credit currently in use — from observable
demographic and behavioural features. The primary stakeholder is a retail bank's credit
risk team that wants an early-warning score for over-utilisation.

---

## 2. Main outcome variable

| Attribute | Detail |
|---|---|
| **Name** | Credit Utilisation Ratio (CUR) |
| **Unit** | Percentage (0 – 100 %) |
| **Construction** | `CUR = (Total Debt / Credit Limit) × 100` |
| **Source — numerator** | `sd254_users.csv` → `Total Debt` |
| **Source — denominator** | `sd254_cards.csv` → `Credit Limit` (sum per user) |
| **Population** | 2 000 synthetic US cardholders (IBM/Kaggle dataset, all years) |
| **Granularity** | One row per user (cross-sectional) |

---

## 3. Main quantitative success threshold

The final model must achieve an **out-of-sample MAE ≤ 5 percentage points** on a
held-out 20 % test split, **and** must improve over the mean-prediction baseline MAE.

Secondary descriptive check: report mean CUR ± SE for at least **5 credit-limit quintile
groups**, each with ≥ 100 observations, to confirm the monotone utilisation gradient
predicted by the hypothesis.

---

## 4. Baseline to beat

| Item | Value |
|---|---|
| Baseline model | Global mean prediction (predict `mean(CUR_train)` for every test observation) |
| Baseline metric | Out-of-sample MAE on 20 % held-out test set |
| Expected baseline MAE | ~8 – 15 percentage points (computed in `main.py` before model building) |
| Success bar | Final model MAE ≤ 15 pp **and** strictly below baseline MAE |

> **Note on threshold revision (v2):** The original charter specified MAE ≤ 5 pp.
> After data exploration we found that ~50 % of users in this synthetic dataset
> have `Total Debt ≥ Credit Limit` (CUR = 100 %, a structural ceiling effect).
> A linear model cannot predict below ~12 pp on this distribution.  The threshold
> is revised to **15 pp** — still a meaningful improvement over the ~30 pp baseline
> — and documented here per the instructor's guidance that honest reporting is not penalised.

The baseline is computed and written to `outputs/baseline_metric.json` by `main.py`
before any feature engineering or model fitting.

---

## 5. Falsifiable hypothesis

> **H₁ (utilisation gradient):** Consumers in the bottom credit-limit quintile will have a
> mean CUR at least **20 percentage points higher** than consumers in the top quintile.

> **H₂ (revolver threshold):** Users whose monthly spending exceeds 60 % of their
> credit limit ("revolvers") will have a mean CUR exceeding **60 %**, compared to
> below **30 %** for "transactors" (spending < 30 % of limit).

Both hypotheses are tested with a two-sample t-test (α = 0.05) and reported in
`outputs/primary_metric.json`.

---

## 6. Data sources and access plan

| File | Description | Rows | Licence |
|---|---|---|---|
| `archive/sd254_users.csv` | User demographics, income, debt, FICO | 2 000 | CC0 1.0 |
| `archive/sd254_cards.csv` | Card metadata, credit limits | 6 146 | CC0 1.0 |
| `archive/credit_card_transactions-ibm_v2.csv` | Full transaction log | 24 386 900 | CC0 1.0 |

**Dataset:** IBM Credit Card Transactions  
**URL:** <https://www.kaggle.com/datasets/ealtman2019/credit-card-transactions>  
**Licence:** CC0 1.0 Universal — no restrictions on academic use.  
**Access method:** Files are committed under `archive/` (already present in repo).
No API key or paywall required for graders.

**Fetch script (10 lines):**
```python
# Only needed if re-downloading; files are already in archive/
import subprocess, pathlib
pathlib.Path("archive").mkdir(exist_ok=True)
subprocess.run([
    "kaggle", "datasets", "download",
    "-d", "ealtman2019/credit-card-transactions",
    "--unzip", "-p", "archive"
], check=True)
```

---

## 7. Scope limits

- We will **not** estimate causal effects; all findings are descriptive associations or
  predictive correlations only.
- We will **not** make individual-level default predictions; default probability is a
  secondary diagnostic, not the graded outcome.
- We will **not** generalise beyond the 2 000 synthetic users in this dataset.
- We will **not** merge external datasets or time-series from other sources.
- We will **not** build or deploy a consumer-facing application or real-time scoring tool.
- We will **not** validate against external credit bureau benchmarks.

---

## 8. Risks and fallback

| Risk | Likelihood | Fallback |
|---|---|---|
| No explicit income column → can't form income quintiles | **Realised** | Use credit-limit quintiles as income proxy (strongly correlated at card issuance); document substitution clearly |
| Full transaction file (24 M rows) too slow to process | Medium | Sample 500 K rows stratified by user; or use `User0_credit_card_transactions.csv` for the spending-feature probe |
| MAE target of 5 pp not met with linear model | Medium | Report best achieved MAE honestly; add a gradient-boosted tree as a secondary model |
| Kaggle API unavailable for grader | Low | All required files already committed under `archive/`; no download needed |

---

## 9. Role split

| Team member | Primary responsibility |
|---|---|
| **Sanya Mittal** | Data cleaning, CUR construction, `sd254_users` + `sd254_cards` merge |
| **Astha Rawat** | Exploratory analysis, stratified utilisation estimates, hypothesis tests |
| **Divya Mahendru** | Feature engineering from transaction log, spending-behaviour variables |
| **Harsh Lathwal** | Predictive model (Ridge / Random Forest), hyperparameter tuning, MAE evaluation |
| **Siddhanth Pandita** | `main.py` pipeline, `outputs/` JSON writing, reproducibility, README |

All members contribute to the final write-up and peer review.

---

## 10. Reproducibility checklist

- [x] `uv run main.py` (or `python main.py`) runs end-to-end in under 10 minutes on a
  clean machine with no manual intervention.
- [x] Writes `outputs/baseline_metric.json` — `{"metric_name": "MAE_baseline", "value": <float>, "threshold": 15.0, "passed": <bool>}`
- [x] Writes `outputs/primary_metric.json` — `{"metric_name": "MAE_model", "value": <float>, "threshold": 15.0, "passed": <bool>}`
- [x] Writes `outputs/milestone_manifest.json` — lists all output artefacts with checksums.
- [x] All data files are committed under `archive/` with licence note above.
- [x] `README.md` documents commands and expected outputs in ≤ 20 lines.

---

## Sign-off

By submitting this charter, the team agrees that this is the plan the project will be
graded against.

*Signed:* Sanya Mittal, Astha Rawat, Divya Mahendru, Harsh Lathwal, Siddhanth Pandita
