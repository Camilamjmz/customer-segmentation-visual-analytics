# Data Preparation

## Dataset source

This project uses the **Online Retail II** dataset from the UCI Machine Learning Repository:

- Daqing Chen (2012), *Online Retail II*.
- UCI dataset page: https://archive.ics.uci.edu/dataset/502/online+retail+ii
- DOI: https://doi.org/10.24432/C5CG6D

The dataset contains transactions from a UK-based non-store retailer. The original workbook is preserved at `data/online_retail_II.xlsx` and copied to `data/raw/online_retail_II.xlsx` for the preparation pipeline.

## Original workbook structure

The workbook has two sheets with the same eight columns:

`Invoice`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `Price`, `Customer ID`, and `Country`.

| Sheet | Rows | Date range | Unique customers | Unique countries | Exact duplicates |
| --- | ---: | --- | ---: | ---: | ---: |
| Year 2009-2010 | 525,461 | 2009-12-01 07:45 to 2010-12-09 20:01 | 4,383 | 40 | 6,865 |
| Year 2010-2011 | 541,910 | 2010-12-01 08:26 to 2011-12-09 12:50 | 4,372 | 38 | 5,268 |
| Combined before cleaning | 1,067,371 | 2009-12-01 07:45 to 2011-12-09 12:50 | 5,942 | 43 | 34,335 |

The combined duplicate count is greater than the sum of within-sheet duplicates because the sheet date ranges overlap from December 1 through December 9, 2010. There are 2,813 identified customers present in both sheets, so combining the sheets preserves useful longitudinal history.

### Data types

Both sheets were read with the same inferred types:

| Column | Pandas type | Meaning |
| --- | --- | --- |
| Invoice | object | Invoice identifier; values beginning with `C` indicate cancellation |
| StockCode | object | Product identifier |
| Description | object | Product description |
| Quantity | int64 | Units on the transaction line |
| InvoiceDate | datetime64 | Transaction timestamp |
| Price | float64 | Unit price in pounds sterling |
| Customer ID | float64 | Customer identifier stored as numeric because missing values exist |
| Country | string | Customer or transaction country |

### Missing values

| Column | Year 2009-2010 | Year 2010-2011 | Combined |
| --- | ---: | ---: | ---: |
| Description | 2,928 | 1,454 | 4,382 |
| Customer ID | 107,927 | 135,080 | 243,007 |
| All other columns | 0 | 0 | 0 |

There were no invalid or unparseable invoice dates. Missing descriptions do not directly prevent aggregation because product identity comes from `StockCode`. Rows without a Customer ID cannot be assigned to a customer and therefore cannot contribute to customer segmentation.

## Data-quality findings and segmentation impact

- **Missing Customer IDs:** 243,007 raw rows have no customer identifier. Keeping them would mix anonymous activity into an unassignable pseudo-customer.
- **Cancelled transactions:** 19,494 raw rows have invoice identifiers beginning with `C`. These represent reversals rather than completed purchasing behavior and would reduce monetary and quantity totals if mixed with sales.
- **Negative quantities:** 22,950 raw rows have negative quantities. In the sequential cleaning pipeline, all such identified-customer rows are already removed as duplicates, missing-customer activity, or cancellations, leaving zero additional rows for the nonpositive-quantity rule.
- **Zero quantities:** None were found.
- **Zero or negative prices:** The raw sheets contain 6,202 zero-price rows and 5 negative-price rows. Most do not survive the earlier identity and cancellation rules; 70 additional rows are removed by the final nonpositive-price rule. Free or accounting-only lines do not represent comparable customer spending.
- **Exact duplicates:** 34,335 rows are duplicates after the sheets are combined. Keeping them would inflate purchase counts, item totals, and spending.
- **Invalid dates:** None were found. Invalid dates would make recency and customer lifetime impossible to calculate reliably.
- **Extreme values:** Quantity ranges from -80,995 to 80,995 and price ranges from -53,594.36 to 38,970 in the raw workbook. The cleaned customer table remains strongly right-skewed: maximum MonetaryValue is 580,987.04 compared with a median of 867.74. These values may reflect legitimate wholesale customers, data-entry problems, or special accounting lines and can strongly influence distance-based clustering.
- **Cross-sheet customers:** 2,813 customers occur in both sheets. Treating each sheet separately would split their histories and understate lifetime, frequency, and value.

## Cleaning policy

Rules are applied sequentially so each removed row is counted once:

1. Combine both worksheets to create one longitudinal transaction table.
2. Remove exact duplicate rows, keeping the first occurrence. This also resolves duplicated records in the overlapping sheet dates.
3. Exclude rows with missing Customer IDs because they cannot be assigned to a customer.
4. Parse `InvoiceDate` and exclude invalid dates. No rows were removed by this rule in the current workbook.
5. Exclude invoices whose identifier begins with `C` because they are cancellations.
6. Exclude nonpositive quantities because the customer features represent completed purchases.
7. Exclude zero or negative prices because they do not represent comparable paid sales.
8. Calculate `TotalPrice = Quantity * Price` after cleaning.
9. Preserve positive extreme values. No winsorization, trimming, or log transformation is performed at this stage. Outlier treatment should be evaluated transparently during later modeling rather than silently changing the prepared observations.

### Removed records

| Sequential reason | Rows removed |
| --- | ---: |
| Exact duplicate | 34,335 |
| Missing Customer ID | 235,151 |
| Invalid InvoiceDate | 0 |
| Cancelled invoice | 18,390 |
| Nonpositive Quantity | 0 |
| Nonpositive Price | 70 |
| **Total removed** | **287,946** |

The sequential counts differ from raw issue counts because one row can have more than one issue. For example, a duplicate cancellation is counted only as a duplicate, not again as a cancellation.

The resulting clean transaction table contains **779,425 rows** and produces **5,878 unique customers**.

## Customer-level feature definitions

The reference date is fixed at **2011-12-10**, one calendar day after the latest valid transaction date. Adding one day makes the most recent possible recency equal to 1 rather than 0.

| Feature | Definition |
| --- | --- |
| CustomerID | Original customer identifier, converted to an integer after missing IDs are removed |
| Country | Country with the greatest number of valid transaction lines for the customer; alphabetical order resolves ties |
| Recency | Calendar days from the customer's last valid purchase date to 2011-12-10 |
| Frequency | Number of distinct valid invoice identifiers |
| MonetaryValue | Sum of `Quantity * Price` across valid transaction lines |
| TotalItems | Total valid quantity purchased |
| UniqueProducts | Number of distinct `StockCode` values purchased |
| AverageOrderValue | `MonetaryValue / Frequency` |
| AverageItemsPerOrder | `TotalItems / Frequency` |
| CustomerLifetimeDays | Calendar days between the first and last valid purchase dates; one-day customers have a value of 0 |

## Assumptions

- Customer IDs consistently identify the same customer across both sheets.
- An invoice beginning with uppercase `C` is a cancellation, consistent with the UCI description.
- Distinct invoice identifiers represent distinct orders.
- Prices are interpreted as pounds sterling, as documented by UCI.
- The most frequent valid transaction-line country is a reasonable single country label when a customer has activity in more than one country.
- Exact duplicates are accidental repeated records rather than intentional repeated identical line items.

## Limitations

- Removing cancellations creates gross valid-purchase behavior rather than net behavior after returns. A future analysis may model returns separately.
- Positive extreme values are retained and may dominate clustering unless later scaling or robust transformations are used.
- The workbook includes stock codes that may represent postage, adjustments, or other non-product lines. They are preserved because this milestone does not introduce undocumented product-code exclusions.
- Country is reduced to one modal label and therefore does not preserve customer movement or cross-border purchasing history.
- Frequency relies on invoice identifiers and does not attempt to infer household relationships or merge customer IDs.
- The data ends in December 2011, so findings describe the historical retailer and may not generalize to current commerce behavior.

## Reproducibility

From the project root, activate the backend environment and run:

```powershell
.\backend\.venv\Scripts\Activate.ps1
python .\backend\scripts\prepare_data.py
```

The script reads `data/raw/online_retail_II.xlsx` and overwrites only the reproducible output `data/processed/customer_features.csv`.
