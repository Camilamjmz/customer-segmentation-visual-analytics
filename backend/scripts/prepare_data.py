"""Prepare customer-level behavioral features from Online Retail II."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "Invoice",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "Price",
    "Customer ID",
    "Country",
}


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(
        description="Create customer features from the Online Retail II workbook."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=project_root / "data" / "raw" / "online_retail_II.xlsx",
        help="Path to the source workbook.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=project_root / "data" / "processed" / "customer_features.csv",
        help="Path for the prepared customer CSV.",
    )
    return parser.parse_args()


def load_workbook(path: Path) -> tuple[pd.DataFrame, dict[str, int]]:
    workbook = pd.ExcelFile(path, engine="openpyxl")
    frames: list[pd.DataFrame] = []
    sheet_rows: dict[str, int] = {}

    for sheet_name in workbook.sheet_names:
        sheet = pd.read_excel(workbook, sheet_name=sheet_name)
        missing_columns = REQUIRED_COLUMNS.difference(sheet.columns)
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"Sheet '{sheet_name}' is missing columns: {missing}")

        sheet_rows[sheet_name] = len(sheet)
        frames.append(sheet)

    return pd.concat(frames, ignore_index=True), sheet_rows


def clean_transactions(
    transactions: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, int]]:
    cleaned = transactions.copy()
    removed: dict[str, int] = {}

    duplicate_mask = cleaned.duplicated(keep="first")
    removed["exact_duplicates"] = int(duplicate_mask.sum())
    cleaned = cleaned.loc[~duplicate_mask].copy()

    missing_customer_mask = cleaned["Customer ID"].isna()
    removed["missing_customer_id"] = int(missing_customer_mask.sum())
    cleaned = cleaned.loc[~missing_customer_mask].copy()

    cleaned["InvoiceDate"] = pd.to_datetime(cleaned["InvoiceDate"], errors="coerce")
    invalid_date_mask = cleaned["InvoiceDate"].isna()
    removed["invalid_dates"] = int(invalid_date_mask.sum())
    cleaned = cleaned.loc[~invalid_date_mask].copy()

    cancelled_mask = cleaned["Invoice"].astype("string").str.startswith("C", na=False)
    removed["cancelled_invoices"] = int(cancelled_mask.sum())
    cleaned = cleaned.loc[~cancelled_mask].copy()

    nonpositive_quantity_mask = cleaned["Quantity"] <= 0
    removed["nonpositive_quantity"] = int(nonpositive_quantity_mask.sum())
    cleaned = cleaned.loc[~nonpositive_quantity_mask].copy()

    nonpositive_price_mask = cleaned["Price"] <= 0
    removed["nonpositive_price"] = int(nonpositive_price_mask.sum())
    cleaned = cleaned.loc[~nonpositive_price_mask].copy()

    cleaned["CustomerID"] = cleaned["Customer ID"].astype("int64")
    cleaned["TotalPrice"] = cleaned["Quantity"] * cleaned["Price"]

    return cleaned, removed


def most_frequent_country(transactions: pd.DataFrame) -> pd.Series:
    country_counts = (
        transactions.groupby(["CustomerID", "Country"], as_index=False)
        .size()
        .sort_values(
            ["CustomerID", "size", "Country"],
            ascending=[True, False, True],
        )
    )
    return country_counts.drop_duplicates("CustomerID").set_index("CustomerID")[
        "Country"
    ]


def build_customer_features(transactions: pd.DataFrame) -> pd.DataFrame:
    reference_date = transactions["InvoiceDate"].max().normalize() + pd.Timedelta(days=1)

    customers = transactions.groupby("CustomerID").agg(
        LastPurchase=("InvoiceDate", "max"),
        FirstPurchase=("InvoiceDate", "min"),
        Frequency=("Invoice", "nunique"),
        MonetaryValue=("TotalPrice", "sum"),
        TotalItems=("Quantity", "sum"),
        UniqueProducts=("StockCode", "nunique"),
    )
    customers.insert(0, "Country", most_frequent_country(transactions))
    customers["Recency"] = (
        reference_date - customers["LastPurchase"].dt.normalize()
    ).dt.days
    customers["AverageOrderValue"] = (
        customers["MonetaryValue"] / customers["Frequency"]
    )
    customers["AverageItemsPerOrder"] = (
        customers["TotalItems"] / customers["Frequency"]
    )
    customers["CustomerLifetimeDays"] = (
        customers["LastPurchase"].dt.normalize()
        - customers["FirstPurchase"].dt.normalize()
    ).dt.days

    return (
        customers.reset_index()[
            [
                "CustomerID",
                "Country",
                "Recency",
                "Frequency",
                "MonetaryValue",
                "TotalItems",
                "UniqueProducts",
                "AverageOrderValue",
                "AverageItemsPerOrder",
                "CustomerLifetimeDays",
            ]
        ]
        .sort_values("CustomerID")
        .reset_index(drop=True)
    )


def main() -> None:
    args = parse_args()
    transactions, sheet_rows = load_workbook(args.input)
    cleaned, removed = clean_transactions(transactions)
    customer_features = build_customer_features(cleaned)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    customer_features.to_csv(args.output, index=False, float_format="%.2f")

    report = {
        "input": str(args.input.resolve()),
        "output": str(args.output.resolve()),
        "sheet_rows": sheet_rows,
        "original_rows": len(transactions),
        "removed_by_reason": removed,
        "cleaned_rows": len(cleaned),
        "customers": len(customer_features),
        "output_columns": len(customer_features.columns),
        "reference_date": str(
            cleaned["InvoiceDate"].max().normalize() + pd.Timedelta(days=1)
        ).split()[0],
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
