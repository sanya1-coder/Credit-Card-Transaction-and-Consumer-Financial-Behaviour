# AI Usage Log

**Project:** P19 — Credit Card Transaction and Consumer Financial Behaviour
**Course:** ECO 6810
**Team:** Sanya Mittal, Astha Rawat, Divya Mahendru, Harsh Lathwal, Siddhanth Pandita

This log records every place AI assistance was used during the project, what it produced, and what we verified ourselves. It is written honestly — we did not use AI for everything, and wherever we did, we checked the output against the actual data and results.

---

## Summary Table

| Area | AI used? | What we verified manually |
|---|---|---|
| Research question (CUR as target) | No | Chose CUR based on FICO scoring literature; decision made before any AI interaction |
| Dataset selection and licence check | No | Evaluated dataset ourselves for field availability, licence (CC0 1.0), and size suitability |
| Data loading and merge logic | Partially | Checked merge key, output shape, CUR range |
| CUR construction formula | No | Derived from charter definition |
| Feature engineering (15 features) | Partially | Reviewed each feature for domain sense |
| Baseline (global mean) | No | Computed and checked ourselves |
| Model selection (Ridge vs. OLS) | Partially | Read scikit-learn docs, confirmed alpha choice |
| `main.py` pipeline | Yes | Ran locally, verified all output files |
| Hypothesis test code | Partially | Checked t-test direction and p-value interpretation |
| Reproducibility fix (clean-clone test) | Yes | Deleted archive/, re-ran from scratch |
| Output JSON schema | Yes | Compared against rubric in CHARTER.md |
| `report.md` | Yes | Verified every number against actual JSON outputs |
| `AI_USAGE_LOG.md` | Yes | Written and reviewed by the team |
| CHARTER.md | Partially | Edited threshold revision section ourselves |
| README.md | Partially | Reviewed and edited run instructions |

---

## Detailed Log

### 1. Research Question

**AI used:** No.

We chose credit utilisation ratio (CUR) as the target variable ourselves, based on reading about credit scoring models and the FICO score methodology. CUR is one of the five factors in FICO scoring (weighted at 30 %) and is a well-established predictor of financial stress. This decision was made before any AI interaction.

---

### 2. Dataset Selection

**AI used:** No.

We found the IBM Credit Card Transactions dataset on Kaggle independently. We evaluated it ourselves for: (a) licence compatibility (CC0 1.0 — no restrictions), (b) whether it contained the fields needed to construct CUR (`Total Debt` in users file, `Credit Limit` in cards file), and (c) whether it was large enough to be interesting but small enough to run on a laptop.

---

### 3. Data Loading and Merge

**What we asked AI:** How to merge `sd254_users.csv` and `sd254_cards.csv` on user ID and aggregate credit limits per user.

**What AI produced:** Pandas merge code using `Person` as the join key, with a `groupby` to sum credit limits per user.

**What we verified:** We inspected the raw CSV headers ourselves to confirm the join key name. We checked the merged dataframe shape (2,000 rows × expected columns) and confirmed CUR values were clipped to [0, 100]. We also verified that the training-set mean CUR (77.90 %) matched the value written to `baseline_metric.json`.

---

### 4. CUR Construction

**AI used:** No.

The formula `CUR = (Total Debt / Total Credit Limit) × 100` comes directly from the charter definition we wrote. We implemented it ourselves and verified the output distribution matched expectations (heavy concentration at 100 % due to the ceiling effect).

---

### 5. Feature Engineering

**What we asked AI:** Suggestions for features that might predict CUR from the available demographic and card fields.

**What AI produced:** A list of 15 features including derived ratios (`Debt_to_Income`, `Spend_to_Limit`, `Income_per_Card`) and transaction aggregates (`Txn_Count`, `Total_Spend`, `Mean_Txn`, `Std_Txn`, `Max_Txn`).

**What we verified:** We reviewed each feature for domain sense before including it. `Debt_to_Income` and `Income_per_Card` are standard in consumer credit literature. We removed a suggested zip-code feature because it had too many categories and no interpretable signal. We confirmed that all 15 features appear in `primary_metric.json` under the `features` key.

---

### 6. Baseline Model

**AI used:** No.

The global-mean baseline (predict `mean(CUR_train)` for every test observation) was our own design, specified in the charter before any coding. We computed it ourselves and verified the output: baseline MAE = 30.41 pp, written to `outputs/baseline_metric.json`.

---

### 7. Model Selection

**What we asked AI:** Which regression model to use for a continuous target with correlated features, given interpretability requirements.

**What AI produced:** Recommendation for Ridge regression with explanation of why it handles multicollinearity better than OLS through L2 regularisation.

**What we verified:** We read the scikit-learn Ridge documentation ourselves and confirmed `alpha = 1.0` is a reasonable default for this scale. We also considered Random Forest but chose Ridge because the charter requires interpretable coefficients for the feature importance discussion. The final decision was ours.

---

### 8. `main.py` Pipeline

**What we asked AI:** Help writing the end-to-end pipeline: load data → engineer features → train/test split → fit Ridge → write output JSONs → save figures.

**What AI produced:** A complete `main.py` with all pipeline steps, JSON writing logic, and figure generation.

**What we verified:** We ran `uv run main.py` locally and confirmed:
- All five output JSON files were written with correct schemas
- `primary_metric.json` showed `"passed": true` (MAE 12.79 < threshold 15.0)
- `baseline_metric.json` showed `"passed": false` (MAE 30.41 > threshold 15.0)
- All figures were saved to `outputs/figures/`
- The pipeline completed in under 2 minutes

---

### 9. Hypothesis Tests

**What we asked AI:** How to run a two-sample t-test in Python and interpret the result for H₁ and H₂.

**What AI produced:** `scipy.stats.ttest_ind` code for both hypotheses, with results written to `outputs/hypothesis_tests.json`.

**What we verified:** We checked the t-test direction ourselves. For H₁, we confirmed the bottom quintile mean (94.70 %) was indeed higher than the top quintile mean (53.98 %), giving a gap of 40.72 pp — well above the 20 pp threshold. For H₂, we noticed the direction was reversed (transactors had *higher* CUR than revolvers) and investigated why: the ceiling effect means even low-spending users have high debt from before the transaction period. We wrote the H₂ interpretation in the report ourselves.

---

### 10. Reproducibility Fix

**What we asked AI:** The pipeline failed on a clean clone because `archive/` files were not committed. How do we fix this?

**What AI produced:** Guidance to ensure all required CSV files were committed under `archive/` and that `main.py` used relative paths.

**What we verified:** We deleted the local `archive/` folder, cloned the repo fresh, and ran `uv run main.py` again. It completed without errors and wrote all required output files. We also confirmed the `milestone_manifest.json` listed all artefacts with correct checksums.

---

### 11. `report.md`

**What we asked AI:** Help drafting the report structure and filling in sections based on our actual results.

**What AI produced:** A full draft of `report.md`.

**What we verified:** We checked every number in the report against the actual JSON outputs:
- Baseline MAE: 30.41 pp ✓ (from `baseline_metric.json`)
- Ridge MAE: 12.79 pp ✓ (from `primary_metric.json`)
- Training mean CUR: 77.90 % ✓ (from `baseline_metric.json`)
- Top-5 coefficients and signs ✓ (from `model_coefficients.json`)
- H₁ gap: 40.72 pp ✓ (from `hypothesis_tests.json`)
- H₂ result: not supported ✓ (from `hypothesis_tests.json`)

We edited the limitations section and the H₂ interpretation ourselves.

---

### 12. What We Did Not Use AI For

- Choosing CUR as the research target
- Selecting and evaluating the Kaggle dataset
- Writing the charter (v1 and the threshold revision in v2)
- Deciding to use Ridge over Random Forest (interpretability requirement)
- Interpreting whether coefficient signs made economic sense
- The H₂ failure analysis (we diagnosed the ceiling effect ourselves)
- Role assignments and project management

---

## Tools Used

| Tool | Purpose |
|---|---|
| Kiro (AI coding assistant) | Code generation, debugging, report drafting |
| GitHub Copilot | Not used |
| ChatGPT | Not used |

---

*This log was written honestly. AI helped us move faster on implementation, but every output was verified against the actual data and results before submission.*
