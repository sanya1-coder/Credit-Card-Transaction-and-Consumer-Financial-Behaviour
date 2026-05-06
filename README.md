# Project Charter — ECO 6810 Final Project

> Need the big picture first? Read the [Final Project brief](./FINAL_PROJECT.md) before you fill this out.
>
> **What this is.** Your short approved project plan. It tells me what you are trying to do, what data you will use, what your main metric is, and what a good result would look like.
>
> **What this is not.** A brainstorm or a long proposal. Keep it short, specific, and concrete.
>
> **Why we use it.** It keeps the project focused. Once this is approved, the milestone and the final submission are judged against this plan, not against shifting expectations later.
>
> **How to fill it.** Copy this file. Answer every field. Keep it under two pages. If a field asks for a number, give a real number with a unit.
>
> **Where this lives.** Fill this out inside your team GitHub repo. That repo is where we will review and approve the charter.
>
> **How approval works.** Revise `CHARTER.md` in the repo until it is approved. Do not treat the charter as a separate detached file living somewhere else.
>
> **Simplest editing path.** Open `CHARTER.md` on GitHub, click the pencil icon, edit the file, and commit the change.
>
> **After approval.** One teammate can freeze the approved version as a PDF with:
> `pandoc CHARTER.md -o charter_approved.pdf`
> Then commit that PDF to the repo as the locked approved copy.

---

## Header

| Field | Value |
|---|---|
| Team members | Sanya Mittal, Astha Rawat, Divya Mahendru, Harsh Lathwal, Siddhanth Pandita |
| Project type | descriptive  |
| Estimated hours per person | 50 hours|
| Charter version | v1 |
| Date | 2026-04-25 |

---

## 1. Problem and stakeholder

Despite the convenience of credit cards, they often lead to impulsive buying and high-
interest debt accumulation. Financial institutions face the constant challenge of predicting
credit defaults and managing risk, while consumers often lack personalized insights into
their spending habits. There is a critical need to analyze transaction data to accurately
segment customers, predict default probabilities, and understand the behavioral drivers
behind credit reliance (e.g., &quot;revolvers&quot; who carry debt versus &quot;transactors&quot; who pay in
full).


---

## 2. Main outcome variable

The single number your project centres on. State:

- **Name** Credit Utilization Ratio
- **Unit** Percentage (%)
- **Source table/column/field**credit_used (total outstanding balance)
credit_limit (maximum available credit)

Constructed variable:
credit_used (total outstanding balance)
credit_limit (maximum available credit)


- **Population / panel** (which rows: which years, which geographies, which people)
- Individuals holding credit cards
Observations at the monthly level
Time period: (e.g., 2020–2024 — update based in our dataset)
Geography: (e.g., India / global dataset)




---

## 3. Main quantitative success threshold

Main quantitative success threshold (Descriptive):
Produce stratified estimates of Credit Utilization Ratio across at least 5 consumer groups (e.g., income quintiles or spending categories), each with sample size ≥ 100 observations, and report mean and standard errors for each group.

## 4. Baseline to beat

Baseline model:
Mean-prediction baseline.

Before building any advanced model, the project will first compute a simple baseline where every individual’s predicted Credit Utilization Ratio is equal to the average Credit Utilization Ratio in the training data.

Baseline metric:
The baseline will produce an out-of-sample Mean Absolute Error (MAE) on the held-out 20% test set.

Success requirement:
The final model must achieve MAE ≤ 5 percentage points, and it must improve over the baseline MAE.

Expected baseline:
The baseline MAE will be computed before model building. If the baseline MAE is around 8 percentage points or higher, the final model must reduce prediction error meaningfully below that level.

---

## 5. Falsifiable hypothesis
Consumers in the bottom income quintile will have a mean Credit Utilization Ratio at least 20 percentage points higher than consumers in the top income quintile, and revolvers (those who carry month-end balances) will exhibit a mean Credit Utilization Ratio exceeding 60%, compared to below 30% for transactors (those who pay in full monthly.

---

## 6. Data sources and access plan
- **Credit Card Transactions Dataset:**
   -Name and URL: Credit Card Transactions Dataset — https://www.kaggle.com/datasets/ealtman2019/credit-card-transactions

   - Licence or permission to use: CC0 1.0 Universal (Public Domain Dedication) — no restrictions on use, modification, or redistribution. Free for academic use without attribution requirement.

   - Access method: Direct download via Kaggle web interface (manual) or via the Kaggle API (kaggle datasets download). Requires a free Kaggle account and an API token (kaggle.json). No paywall or institutional login beyond account registration.

10-line fetch script: import pandas as pd





---

## 7. Scope limits
- We will not estimate a structural causal effect of income or spending behaviour on credit utilization; all findings are descriptive associations only.

- We will not make individual-level default predictions; default probability is a secondary diagnostic, not the graded outcome.

- We will not generalise findings beyond the population represented in the dataset; no claims are made about national or cross-country credit behaviour.

- We will not harmonise across multiple datasets or time periods; analysis is confined to the single dataset committed under data/.

- We will not build or deploy a consumer-facing application, dashboard, or real-time scoring tool.

- We will not validate results against external credit bureau benchmarks or proprietary bank data.



---

## 8. Risks and fallback
Risk: The dataset does not contain an explicit income variable, making it impossible to construct income quintiles as specified in the success threshold. Fallback: We will proxy income groups using credit limit deciles (since credit limits are strongly correlated with assessed income at card issuance), segment the population into five decile-based groups, and report mean Credit Utilization Ratio with standard errors for each group. The substitution will be clearly documented in the README and results section.


---

## 9. Reproducibility checklist

Your final repo must satisfy all of these:

- [ ] `uv run main.py` runs end-to-end in under 10 minutes on a clean machine with no manual intervention.
- [ ] It writes `outputs/primary_metric.json` containing a single JSON object with at least `{"metric_name": "...", "value": <number>, "threshold": <number>, "passed": <bool>}`.
- [ ] It writes `outputs/baseline_metric.json` in the same shape.
- [ ] A `README.md` documents the commands and expected outputs in ≤ 20 lines.
- [ ] All data sources are either fetched in-script or committed under `data/` with a licence note.

If you cannot commit to this, your project is probably still too broad. Talk to the instructor before proceeding.

---

## Sign-off

By submitting this charter, the team agrees that this is the plan the project will be graded against. The instructor will not penalize you just because the topic turns out to be difficult, as long as the project stays honest and within the approved scope.

*Signed:* _(team member names)_
