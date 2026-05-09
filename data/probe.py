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
    probe("txns",   ARCHIVE / "credit_card_transactions-ibm_v2.csv")
    print("\n[DONE] Probe complete - all three files are readable.")
