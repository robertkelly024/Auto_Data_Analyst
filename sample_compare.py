#!/usr/bin/env python3
"""
compare_tables.py – Reusable SQLite table-comparison utility (no CLI)
-------------------------------------------------------------------
Edit **one small config block** in `main()` and run the script. It will:

* Locate the correct mapping columns in your Excel workbook (exact or
  prefix match, case-insensitive).
* Pull the mapped columns plus the primary key (default **Employee ID**).
* Produce three comparison sheets:
    1. Rows present only in Table A.
    2. Rows present only in Table B.
    3. Field-level differences on common rows.
* Save everything to an Excel file alongside a one-row *Summary* sheet.

Dependencies
~~~~~~~~~~~~
```bash
pip install pandas openpyxl
```
Python ≥3.8 recommended.

How to use
~~~~~~~~~~
1. Open the file.
2. Scroll to `main()` – **edit the paths/table names** in the clearly
   marked block.
3. Run:
   ```bash
   python compare_tables.py
   ```

The mapping workbook must contain at least two columns whose headers are
source table names *or prefixes* (e.g. `HC_asof`, `employee_main`). New
"HC_asof_YYYYMMDD" tables are picked up automatically.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
import sys
from typing import List, Tuple

import pandas as pd

PRIMARY_KEY = "Employee ID"  # Change here if your PK differs

###############################################################################
# Mapping helpers
###############################################################################

def _match_mapping_column(columns: List[str], table_name: str) -> str:
    """Return the mapping column header matching *table_name*.

    * Exact (case-insensitive) match first.
    * Otherwise the **longest unique prefix** of *table_name* in the
      available headers.
    """
    lowered = [c.lower() for c in columns]
    table_lower = table_name.lower()

    # Exact match
    if table_lower in lowered:
        return columns[lowered.index(table_lower)]

    # Longest unique prefix
    candidates = [c for c in columns if table_lower.startswith(c.lower())]
    if not candidates:
        raise ValueError(f"No mapping column matches '{table_name}'.")
    longest = max(candidates, key=len)
    if candidates.count(longest) > 1:
        raise ValueError(f"Ambiguous mapping columns for '{table_name}': {candidates}")
    return longest


def load_mapping(mapping_path: Path, sheet: str, table_a: str, table_b: str) -> Tuple[List[str], List[str]]:
    """Return two aligned field lists (fields_a, fields_b)."""
    df_map = pd.read_excel(mapping_path, sheet_name=sheet)
    if df_map.shape[1] < 2:
        raise ValueError("Mapping sheet must contain at least two columns.")

    col_a = _match_mapping_column(df_map.columns.tolist(), table_a)
    col_b = _match_mapping_column(df_map.columns.tolist(), table_b)

    mapping_df = df_map[[col_a, col_b]].dropna(how="all")
    fields_a = mapping_df[col_a].astype(str).str.strip().tolist()
    fields_b = mapping_df[col_b].astype(str).str.strip().tolist()

    # Ensure PK is included
    if PRIMARY_KEY not in fields_a:
        fields_a.insert(0, PRIMARY_KEY)
    if PRIMARY_KEY not in fields_b:
        fields_b.insert(0, PRIMARY_KEY)

    if len(fields_a) != len(fields_b):
        raise ValueError("Mapping columns are of unequal length after dropping blanks.")

    return fields_a, fields_b

###############################################################################
# SQLite helpers
###############################################################################

def fetch_table(conn: sqlite3.Connection, table: str, columns: List[str]) -> pd.DataFrame:
    quoted_cols = ", ".join(f'"{c}"' for c in columns)
    query = f'SELECT {quoted_cols} FROM "{table}"'
    return pd.read_sql_query(query, conn)

###############################################################################
# Comparison logic
###############################################################################

def compare_dataframes(
    df_a: pd.DataFrame,
    df_b: pd.DataFrame,
    fields_a: List[str],
    fields_b: List[str],
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return (only_in_a, only_in_b, diffs)."""
    df_a = df_a.copy().set_index(PRIMARY_KEY)
    df_b = df_b.copy().set_index(PRIMARY_KEY)

    only_in_a = df_a.loc[df_a.index.difference(df_b.index)].reset_index()
    only_in_b = df_b.loc[df_b.index.difference(df_a.index)].reset_index()

    common_ids = df_a.index.intersection(df_b.index)
    diffs_frames: List[pd.DataFrame] = []

    for col_a, col_b in zip(fields_a, fields_b):
        if col_a == PRIMARY_KEY and col_b == PRIMARY_KEY:
            continue
        series_a = df_a.loc[common_ids, col_a]
        series_b = df_b.loc[common_ids, col_b]
        unequal = ~(series_a.fillna("__NA__") == series_b.fillna("__NA__"))
        if unequal.any():
            diffs_frames.append(
                pd.DataFrame({
                    PRIMARY_KEY: common_ids[unequal],
                    "Field": col_a,
                    "Value in A": series_a[unequal].values,
                    "Value in B": series_b[unequal].values,
                })
            )

    diffs = pd.concat(diffs_frames, ignore_index=True) if diffs_frames else pd.DataFrame()
    return only_in_a, only_in_b, diffs

###############################################################################
# Main
###############################################################################

def main() -> None:  # noqa: C901 – main intentionally verbose for clarity
    # ------------------------------------------------------------------
    # EDIT THESE VARIABLES ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
    db_path = "./mydatabase.sqlite"
    table_a = "HC_asof_20250131"
    table_b = "employee_main"
    mapping_path = "./column_mapping.xlsx"
    mapping_sheet = "Mappings"  # Sheet name in the Excel workbook
    output_path = "./HC_vs_main_diff.xlsx"
    # ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
    # ------------------------------------------------------------------

    db_path = Path(db_path).expanduser().resolve()
    mapping_path = Path(mapping_path).expanduser().resolve()
    output_path = Path(output_path).expanduser().resolve()

    if not db_path.exists():
        sys.exit(f"SQLite DB not found: {db_path}")
    if not mapping_path.exists():
        sys.exit(f"Mapping file not found: {mapping_path}")

    try:
        fields_a, fields_b = load_mapping(mapping_path, mapping_sheet, table_a, table_b)
    except Exception as exc:
        sys.exit(f"Error loading mapping – {exc}")

    with sqlite3.connect(str(db_path)) as conn:
        try:
            df_a = fetch_table(conn, table_a, fields_a)
            df_b = fetch_table(conn, table_b, fields_b)
        except Exception as exc:
            sys.exit(f"Error querying tables – {exc}")

    only_a, only_b, diffs = compare_dataframes(df_a, df_b, fields_a, fields_b)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        only_a.to_excel(writer, sheet_name=f"{table_a}_only", index=False)
        only_b.to_excel(writer, sheet_name=f"{table_b}_only", index=False)
        if not diffs.empty:
            diffs.to_excel(writer, sheet_name="Differences", index=False)
        pd.DataFrame({
            "Sheet": [f"{table_a}_only", f"{table_b}_only", "Differences"],
            "Rows": [len(only_a), len(only_b), len(diffs)],
        }).to_excel(writer, sheet_name="Summary", index=False)

    print(f"Comparison complete – results saved to {output_path}")


if __name__ == "__main__":
    main()
