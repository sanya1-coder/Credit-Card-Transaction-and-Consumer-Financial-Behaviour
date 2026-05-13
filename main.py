"""
main.py — ECO 6810 Final Project Pipeline
==========================================
Team: Sanya Mittal, Astha Rawat, Divya Mahendru, Harsh Lathwal, Siddhanth Pandita

What this script does (in order):
  1. Load users + cards, construct Credit Utilisation Ratio (CUR).
  2. Sample the transaction log (500 K rows) to build spending-behaviour features.
  3. Merge everything into one modelling frame.
  4. Compute and save the mean-prediction BASELINE metric.
  5. Train a Ridge regression model; compute and save the PRIMARY metric.
  6. Run the two falsifiable hypothesis tests.
  7. Write outputs/milestone_manifest.json listing all artefacts.

Run:
    python main.py          # standard Python
    uv run main.py          # via uv

Outputs (all in outputs/):
    baseline_metric.json    MAE of the mean-prediction baseline
    primary_metric.json     MAE of the Ridge model
    stratified_cur.csv      Mean CUR ± SE by credit-limit quintile
    hypothesis_tests.json   t-test results for H1 and H2
    milestone_manifest.json Artefact list with sizes and checksums
"""

import hashlib
import json
import pathlib
import time
import warnings

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from scipy import stats

warnings.filterwarnings("ignore")

# ── paths ──────────────────────────────────────────────────────────────────────
ARCHIVE = pathlib.Path("archive")
OUTPUTS = pathlib.Path("outputs")
OUTPUTS.mkdir(exist_ok=True)

USERS_CSV  = ARCHIVE / "sd254_users.csv"
CARDS_CSV  = ARCHIVE / "sd254_cards.csv"
TXNS_CSV_FULL   = ARCHIVE / "credit_card_transactions-ibm_v2.csv"
TXNS_CSV_SMALL  = ARCHIVE / "User0_credit_card_transactions.csv"
# Use the full file if available, otherwise fall back to the committed sample
TXNS_CSV = TXNS_CSV_FULL if TXNS_CSV_FULL.exists() else TXNS_CSV_SMALL

SAMPLE_ROWS = 500_000   # rows sampled per chunk pass from the 24 M transaction file
RANDOM_SEED = 42
TEST_SIZE   = 0.20
MAE_THRESHOLD = 15.0    # percentage points — realistic bar given ~50 % of users at 100 % CUR ceiling


# ── helpers ────────────────────────────────────────────────────────────────────

def clean_dollar(series: pd.Series) -> pd.Series:
    """Strip '$' and ',' then cast to float."""
    return series.astype(str).str.replace(r"[\$,]", "", regex=True).astype(float)


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: pathlib.Path, obj: dict) -> None:
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)
    print(f"  [DONE] wrote {path}")


# ── step 1 · load users & cards, construct CUR ────────────────────────────────

def load_users_cards() -> pd.DataFrame:
    print("\n[1/7] Loading users and cards …")

    users = pd.read_csv(USERS_CSV)
    users.columns = users.columns.str.strip()
    users["Yearly Income"]  = clean_dollar(users["Yearly Income - Person"])
    users["Total Debt"]     = clean_dollar(users["Total Debt"])
    users["Per Capita Inc"] = clean_dollar(users["Per Capita Income - Zipcode"])

    cards = pd.read_csv(CARDS_CSV)
    cards.columns = cards.columns.str.strip()
    cards["Credit Limit"] = clean_dollar(cards["Credit Limit"])

    # Sum credit limits per user (a user may hold multiple cards)
    card_agg = (
        cards.groupby("User")
        .agg(Total_Credit_Limit=("Credit Limit", "sum"),
             Num_Cards=("CARD INDEX", "count"))
        .reset_index()
    )

    # Users are identified by their 0-based row index, which matches cards["User"]
    users["User"] = users.index
    df = users.merge(card_agg, on="User", how="left")

    # CUR = Total Debt / Total Credit Limit × 100, capped at 100 %
    # Note: in this synthetic dataset Total Debt is cumulative lifetime debt,
    # so values > 100 % are common.  We cap at 100 % to model the standard
    # credit-utilisation definition (0–100 %).
    df["CUR"] = (df["Total Debt"] / df["Total_Credit_Limit"]) * 100
    df["CUR"] = df["CUR"].clip(0, 100)   # standard utilisation range

    # Drop rows where CUR is undefined (no card matched)
    df = df.dropna(subset=["CUR"]).copy()

    print(f"  Users loaded : {len(users):,}")
    print(f"  Cards loaded : {len(cards):,}")
    print(f"  Merged rows  : {len(df):,}")
    print(f"  CUR — mean {df['CUR'].mean():.1f}%  median {df['CUR'].median():.1f}%  "
          f"std {df['CUR'].std():.1f}%")
    return df


# ── step 2 · sample transaction log, build spending features ──────────────────

def load_txn_features() -> pd.DataFrame:
    """
    Build per-user spending features from the transaction log.

    Strategy: read the file in 500 K-row chunks and accumulate per-user
    aggregates incrementally.  This covers all 2 000 users without loading
    the full 24 M rows into memory at once.  We stop after processing
    MAX_CHUNKS chunks (~5 M rows) to keep runtime under 2 minutes.
    """
    MAX_CHUNKS = 50          # 50 × 500 K = 25 M rows  (full file coverage)
    print(f"\n[2/7] Building txn features from {TXNS_CSV.name} …")
    t0 = time.time()

    accum: dict[int, dict] = {}   # user_id → running stats

    for i, chunk in enumerate(
        pd.read_csv(TXNS_CSV, chunksize=SAMPLE_ROWS, dtype=str, low_memory=False)
    ):
        if i >= MAX_CHUNKS:
            break

        chunk["Amount"] = clean_dollar(chunk["Amount"])
        chunk["User"]   = chunk["User"].astype(int)

        for user_id, grp in chunk.groupby("User"):
            if user_id not in accum:
                accum[user_id] = {"count": 0, "total": 0.0,
                                  "sq": 0.0, "max": 0.0}
            s = accum[user_id]
            s["count"] += len(grp)
            s["total"] += grp["Amount"].sum()
            s["sq"]    += (grp["Amount"] ** 2).sum()
            s["max"]    = max(s["max"], grp["Amount"].max())

    rows = []
    for uid, s in accum.items():
        n = s["count"]
        mean = s["total"] / n if n > 0 else 0.0
        var  = max(0.0, s["sq"] / n - mean ** 2) if n > 1 else 0.0
        rows.append({
            "User": uid,
            "Txn_Count":   n,
            "Total_Spend": s["total"],
            "Mean_Txn":    mean,
            "Std_Txn":     var ** 0.5,
            "Max_Txn":     s["max"],
        })

    feat = pd.DataFrame(rows)
    print(f"  Processed {MAX_CHUNKS * SAMPLE_ROWS:,} rows in {time.time()-t0:.1f}s")
    print(f"  Users with txn features: {len(feat):,}")
    return feat


# ── step 3 · merge into modelling frame ───────────────────────────────────────

def build_model_frame(users_df: pd.DataFrame,
                      txn_feat: pd.DataFrame) -> pd.DataFrame:
    print("\n[3/7] Building modelling frame …")

    # users_df already has a 'User' column (0-based row index) from load_users_cards
    # txn_feat also has 'User' (0-based integer from the transaction file)
    df = users_df.merge(txn_feat, on="User", how="left", suffixes=("", "_txn"))

    # Fill missing txn features with 0 (users not in the sample)
    for col in ["Txn_Count", "Total_Spend", "Mean_Txn", "Std_Txn", "Max_Txn"]:
        df[col] = df[col].fillna(0)

    # Credit-limit quintile (proxy for income group)
    df["CL_Quintile"] = pd.qcut(df["Total_Credit_Limit"], q=5,
                                 labels=[1, 2, 3, 4, 5])

    print(f"  Modelling frame: {df.shape[0]} rows × {df.shape[1]} cols")
    return df


# ── step 4 · baseline metric ──────────────────────────────────────────────────

def compute_baseline(df: pd.DataFrame) -> float:
    print("\n[4/7] Computing mean-prediction baseline …")

    y = df["CUR"].values
    _, y_test = train_test_split(y, test_size=TEST_SIZE, random_state=RANDOM_SEED)

    # Baseline: predict global training mean for every test observation
    y_train, _ = train_test_split(y, test_size=TEST_SIZE, random_state=RANDOM_SEED)
    baseline_pred = np.full_like(y_test, fill_value=y_train.mean())
    mae_baseline = mean_absolute_error(y_test, baseline_pred)

    result = {
        "metric_name": "MAE_baseline",
        "description": "Mean Absolute Error of the global-mean prediction baseline",
        "value": round(float(mae_baseline), 4),
        "threshold": MAE_THRESHOLD,
        "passed": bool(mae_baseline <= MAE_THRESHOLD),
        "n_test": int(len(y_test)),
        "train_mean_CUR": round(float(y_train.mean()), 4),
    }
    write_json(OUTPUTS / "baseline_metric.json", result)
    print(f"  Baseline MAE = {mae_baseline:.2f} pp")
    return mae_baseline


# ── step 5 · Ridge regression model ───────────────────────────────────────────

FEATURE_COLS = [
    "Yearly Income", "Total Debt", "FICO Score",
    "Total_Credit_Limit", "Num_Cards",
    "Txn_Count", "Total_Spend", "Mean_Txn", "Std_Txn", "Max_Txn",
    "Current Age", "Per Capita Inc",
]


def train_model(df: pd.DataFrame) -> float:
    print("\n[5/7] Training Ridge regression model …")

    # Add derived features
    df = df.copy()
    df["Debt_to_Income"]   = df["Total Debt"] / (df["Yearly Income"] + 1)
    df["Spend_to_Limit"]   = df["Total_Spend"] / (df["Total_Credit_Limit"] + 1)
    df["Income_per_Card"]  = df["Yearly Income"] / (df["Num_Cards"] + 1)

    feature_cols = FEATURE_COLS + ["Debt_to_Income", "Spend_to_Limit", "Income_per_Card"]

    X = df[feature_cols].fillna(0).values
    y = df["CUR"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_SEED
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    model = Ridge(alpha=1.0)
    model.fit(X_train_s, y_train)
    y_pred = np.clip(model.predict(X_test_s), 0, 100)

    mae_model = mean_absolute_error(y_test, y_pred)

    result = {
        "metric_name": "MAE_model",
        "description": "Mean Absolute Error of the Ridge regression model",
        "value": round(float(mae_model), 4),
        "threshold": MAE_THRESHOLD,
        "passed": bool(mae_model <= MAE_THRESHOLD),
        "n_test": int(len(y_test)),
        "model": "Ridge(alpha=1.0)",
        "features": feature_cols,
    }
    write_json(OUTPUTS / "primary_metric.json", result)
    # Save coefficients
    coeffs = dict(zip(feature_cols, model.coef_))
    write_json(OUTPUTS / "model_coefficients.json", {
        "intercept": float(model.intercept_),
        "coefficients": {k: float(v) for k, v in coeffs.items()}
    })

    # Save test results for accuracy plot
    test_results = pd.DataFrame({"actual": y_test, "predicted": y_pred})
    test_results.to_csv(OUTPUTS / "test_results.csv", index=False)

    print(f"  Model MAE    = {mae_model:.2f} pp")
    return mae_model


# ── step 6 · stratified estimates + hypothesis tests ──────────────────────────

def run_hypothesis_tests(df: pd.DataFrame) -> None:
    print("\n[6/7] Stratified estimates and hypothesis tests …")

    # ── stratified CUR by credit-limit quintile ──
    strat = (
        df.groupby("CL_Quintile", observed=True)["CUR"]
        .agg(n="count", mean="mean", se=lambda x: x.std() / np.sqrt(len(x)))
        .reset_index()
    )
    strat.to_csv(OUTPUTS / "stratified_cur.csv", index=False)
    print("  Stratified CUR by credit-limit quintile:")
    print(strat.to_string(index=False))

    # ── H1: bottom quintile CUR ≥ top quintile CUR + 20 pp ──
    q1 = df[df["CL_Quintile"] == 1]["CUR"].dropna()
    q5 = df[df["CL_Quintile"] == 5]["CUR"].dropna()
    t1, p1 = stats.ttest_ind(q1, q5, alternative="greater")
    h1_gap = float(q1.mean() - q5.mean())

    # ── H2: revolvers (spend > 60 % of limit) vs transactors (< 30 %) ──
    df["Spend_Ratio"] = df["Total_Spend"] / df["Total_Credit_Limit"].replace(0, np.nan)
    revolvers   = df[df["Spend_Ratio"] > 0.60]["CUR"].dropna()
    transactors = df[df["Spend_Ratio"] < 0.30]["CUR"].dropna()

    if len(revolvers) > 1 and len(transactors) > 1:
        t2, p2 = stats.ttest_ind(revolvers, transactors, alternative="greater")
        h2_result = {
            "revolver_mean_CUR": round(float(revolvers.mean()), 2),
            "transactor_mean_CUR": round(float(transactors.mean()), 2),
            "n_revolvers": int(len(revolvers)),
            "n_transactors": int(len(transactors)),
            "t_stat": round(float(t2), 4),
            "p_value": round(float(p2), 6),
            "h2_supported": bool(p2 < 0.05 and revolvers.mean() > 60),
        }
    else:
        h2_result = {"note": "Insufficient revolver/transactor observations in sample"}

    hyp = {
        "H1_utilisation_gradient": {
            "description": "Bottom CL quintile CUR ≥ top quintile CUR + 20 pp",
            "bottom_quintile_mean_CUR": round(float(q1.mean()), 2),
            "top_quintile_mean_CUR": round(float(q5.mean()), 2),
            "gap_pp": round(h1_gap, 2),
            "n_bottom": int(len(q1)),
            "n_top": int(len(q5)),
            "t_stat": round(float(t1), 4),
            "p_value": round(float(p1), 6),
            "h1_supported": bool(p1 < 0.05 and h1_gap >= 20),
        },
        "H2_revolver_threshold": h2_result,
    }
    write_json(OUTPUTS / "hypothesis_tests.json", hyp)
    print(f"  H1 gap = {h1_gap:.1f} pp  (p={p1:.4f})")


# ── step 7 · milestone manifest ───────────────────────────────────────────────

def write_manifest() -> None:
    print("\n[7/7] Writing milestone manifest …")

    artefacts = []
    for p in sorted(OUTPUTS.iterdir()):
        if p.is_file():
            artefacts.append({
                "file": p.name,
                "size_bytes": p.stat().st_size,
                "sha256": sha256_file(p),
            })

    manifest = {
        "project": "ECO 6810 — Credit Utilisation Prediction",
        "team": ["Sanya Mittal", "Astha Rawat", "Divya Mahendru",
                 "Harsh Lathwal", "Siddhanth Pandita"],
        "generated_at": pd.Timestamp.now().isoformat(),
        "charter": {
            "file": "CHARTER.md",
            "status": "approved",
            "primary_metric": "MAE (Mean Absolute Error) of Ridge regression on CUR",
            "threshold": "MAE <= 15 percentage points on 20% held-out test set",
            "baseline": "Global mean prediction (MAE ~30 pp)",
            "dataset": "IBM Credit Card Transactions (CC0 1.0)",
        },
        "sources": [
            {
                "file": "archive/sd254_users.csv",
                "description": "2,000 synthetic cardholders — demographics, income, debt, FICO",
                "committed": True,
                "licence": "CC0 1.0",
            },
            {
                "file": "archive/sd254_cards.csv",
                "description": "6,146 card records — credit limits",
                "committed": True,
                "licence": "CC0 1.0",
            },
            {
                "file": "archive/credit_card_transactions-ibm_v2.csv",
                "description": "24M transaction rows — too large for GitHub (2.2 GB)",
                "committed": False,
                "fallback": "archive/User0_credit_card_transactions.csv",
                "download_url": "https://www.kaggle.com/datasets/ealtman2019/credit-card-transactions",
                "licence": "CC0 1.0",
            },
        ],
        "artefacts": artefacts,
    }
    write_json(OUTPUTS / "milestone_manifest.json", manifest)


# ── entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 60)
    print("ECO 6810 — Credit Utilisation Prediction Pipeline")
    print("=" * 60)
    t_start = time.time()

    users_df  = load_users_cards()
    txn_feat  = load_txn_features()
    model_df  = build_model_frame(users_df, txn_feat)
    
    # Save processed data for visualization
    model_df.to_csv(OUTPUTS / "processed_data.csv", index=False)
    
    mae_base  = compute_baseline(model_df)
    mae_model = train_model(model_df)
    run_hypothesis_tests(model_df)
    write_manifest()

    elapsed = time.time() - t_start
    print("\n" + "=" * 60)
    print(f"Pipeline complete in {elapsed:.1f}s")
    print(f"  Baseline MAE : {mae_base:.2f} pp")
    print(f"  Model MAE    : {mae_model:.2f} pp")
    improvement = mae_base - mae_model
    print(f"  Improvement  : {improvement:.2f} pp  "
          f"({'[YES] beats baseline' if improvement > 0 else '[NO] does not beat baseline'})")
    print(f"  MAE <= {MAE_THRESHOLD} pp : {'[PASSED]' if mae_model <= MAE_THRESHOLD else '[FAILED]'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
