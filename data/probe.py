"""
data/probe.py
-------------
Quick sanity-check: loads the three core CSV files, prints one usable row from
each, and reports basic shape / column info.

Run with:
    python data/probe.py
"""

import pathlib
import pandas as pd

ARCHIVE = pathlib.Path(__file__).parent.parent / "archive"


def probe(name: str, path: pathlib.Path, nrows: int = 5) -> pd.DataFrame:
    df = pd.read_csv(path, nrows=nrows)
    print(f"\n{'='*60}")
    print(f"FILE : {path.name}")
    print(f"COLS : {list(df.columns)}")
    print(f"SHAPE (first {nrows} rows shown): {df.shape}")
    print("SAMPLE ROW:")
    print(df.iloc[0].to_string())
    return df


if __name__ == "__main__":
    probe("users",  ARCHIVE / "sd254_users.csv")
    probe("cards",  ARCHIVE / "sd254_cards.csv")
    # Fall back to the committed single-user sample if the full file is absent
    txns_full  = ARCHIVE / "credit_card_transactions-ibm_v2.csv"
    txns_small = ARCHIVE / "User0_credit_card_transactions.csv"
    txns_path  = txns_full if txns_full.exists() else txns_small
    probe("txns", txns_path)
    print("\n[DONE] Probe complete - all files are readable.")
    if not txns_full.exists():
        print(f"NOTE: full transactions file not present; used fallback {txns_small.name}")
        print("      Download full file from: https://www.kaggle.com/datasets/ealtman2019/credit-card-transactions")
