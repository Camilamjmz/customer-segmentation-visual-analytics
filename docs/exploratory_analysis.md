# Exploratory Analysis of Customer Features

## Scope

This analysis describes `data/processed/customer_features.csv` before clustering. It does not remove outliers, overwrite features, encode country, or make final modeling decisions.

## Dataset verification

The prepared table contains **5,878 customers and 10 columns**. It has no missing values and no duplicate `CustomerID` values.

The raw workbook date range was rechecked directly:

- Earliest transaction: **2009-12-01 07:45:00**
- Latest transaction: **2011-12-09 12:50:00**
- Invalid dates: **0**

The maximum transaction date is therefore 2011-12-09. The preparation pipeline uses 2011-12-10, one calendar day later, as its fixed Recency reference date. This makes a purchase on the final observed date have Recency 1 instead of 0.

## Numeric distributions

| Feature | Count | Mean | Std. dev. | Min | Q1 | Median | Q3 | Max | Skewness |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Recency | 5,878 | 201.87 | 209.35 | 1 | 26 | 96 | 380 | 739 | 0.887 |
| Frequency | 5,878 | 6.29 | 13.01 | 1 | 1 | 3 | 7 | 398 | 12.640 |
| MonetaryValue | 5,878 | 2,955.90 | 14,440.85 | 2.95 | 342.28 | 867.74 | 2,248.31 | 580,987.04 | 25.070 |
| TotalItems | 5,878 | 1,788.70 | 8,876.30 | 1 | 187 | 480 | 1,350 | 367,193 | 21.855 |
| UniqueProducts | 5,878 | 81.99 | 116.48 | 1 | 19 | 45 | 103 | 2,550 | 6.224 |
| AverageOrderValue | 5,878 | 385.18 | 1,214.29 | 2.95 | 176.68 | 279.24 | 414.90 | 84,236.25 | 57.133 |
| AverageItemsPerOrder | 5,878 | 247.56 | 1,424.48 | 1 | 91 | 153.58 | 256.93 | 87,167 | 47.907 |
| CustomerLifetimeDays | 5,878 | 273.39 | 258.96 | 0 | 0 | 221 | 512 | 738 | 0.388 |

Frequency, MonetaryValue, TotalItems, UniqueProducts, AverageOrderValue, and AverageItemsPerOrder are strongly right-skewed. Their means are pulled upward by a relatively small number of very large customers. Recency is moderately right-skewed, while CustomerLifetimeDays is only mildly skewed.

## IQR outlier assessment

The descriptive rule marks values below `Q1 - 1.5 * IQR` or above `Q3 + 1.5 * IQR`. A flag is not evidence that a record is erroneous.

| Feature | Q1 | Q3 | IQR | Lower bound | Upper bound | Outside bounds | Percent |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Recency | 26 | 380 | 354 | -505 | 911 | 0 | 0.00% |
| Frequency | 1 | 7 | 6 | -8 | 16 | 427 | 7.26% |
| MonetaryValue | 342.28 | 2,248.31 | 1,906.03 | -2,516.76 | 5,107.34 | 633 | 10.77% |
| TotalItems | 187 | 1,350 | 1,163 | -1,557.50 | 3,094.50 | 603 | 10.26% |
| UniqueProducts | 19 | 103 | 84 | -107 | 229 | 451 | 7.67% |
| AverageOrderValue | 176.68 | 414.90 | 238.22 | -180.64 | 772.23 | 387 | 6.58% |
| AverageItemsPerOrder | 91 | 256.93 | 165.93 | -157.89 | 505.81 | 359 | 6.11% |
| CustomerLifetimeDays | 0 | 512 | 512 | -768 | 1,280 | 0 | 0.00% |

The retailer serves wholesale as well as ordinary customers, so unusually large totals can be real business behavior. Customer 18102, for example, has MonetaryValue 580,987.04 across 145 invoices. Customer 14646 purchased 367,193 items across 151 invoices. These observations should remain available while their influence is controlled through transformations and scaling.

## Correlation analysis

The strongest Pearson correlation is **MonetaryValue versus TotalItems (r = 0.875)**. Both features measure overall purchasing magnitude and may partly duplicate the same signal.

Other notable relationships are:

| Pair | Pearson r |
| --- | ---: |
| Frequency and UniqueProducts | 0.693 |
| Frequency and MonetaryValue | 0.628 |
| Frequency and TotalItems | 0.572 |
| Recency and CustomerLifetimeDays | -0.564 |
| AverageOrderValue and AverageItemsPerOrder | 0.529 |
| UniqueProducts and CustomerLifetimeDays | 0.499 |
| Frequency and CustomerLifetimeDays | 0.442 |
| TotalItems and AverageItemsPerOrder | 0.358 |
| MonetaryValue and AverageOrderValue | 0.269 |

Using several strongly related variables can give one behavioral dimension extra weight in Euclidean distance. For example, including both MonetaryValue and TotalItems may make overall customer size count twice relative to Recency.

## Log-transformation assessment

`log1p(x)` was assessed in memory only. It was not written back to the source CSV.

| Feature | Original skewness | After log1p |
| --- | ---: | ---: |
| Recency | 0.887 | -0.449 |
| Frequency | 12.640 | 1.001 |
| MonetaryValue | 25.070 | 0.269 |
| TotalItems | 21.855 | -0.095 |
| UniqueProducts | 6.224 | -0.281 |
| AverageOrderValue | 57.133 | 0.063 |
| AverageItemsPerOrder | 47.907 | -0.629 |
| CustomerLifetimeDays | 0.388 | -0.676 |

Frequency, MonetaryValue, TotalItems, UniqueProducts, AverageOrderValue, and AverageItemsPerOrder benefit substantially from `log1p`. Recency improves less and becomes moderately left-skewed. CustomerLifetimeDays becomes more skewed in absolute terms, so the evidence does not support automatically logging it.

## Country analysis

The prepared customer table contains 41 countries. The United Kingdom accounts for **5,350 customers, or 91.02%** of the table.

| Rank | Country | Customers |
| ---: | --- | ---: |
| 1 | United Kingdom | 5,350 |
| 2 | Germany | 106 |
| 3 | France | 95 |
| 4 | Spain | 38 |
| 5 | Belgium | 28 |
| 6 | Portugal | 24 |
| 7 | Switzerland | 22 |
| 8 | Netherlands | 22 |
| 9 | Sweden | 19 |
| 10 | Italy | 17 |

Country is not numerically ordered. Integer labels would create artificial distances, while one-hot encoding would add many sparse dimensions dominated by the United Kingdom imbalance. Country should remain descriptive until the segmentation objective and categorical-distance strategy are defined.

## Customer behavior checks

- **1,623 customers (27.61%)** have Frequency equal to 1.
- **1,689 customers (28.73%)** have CustomerLifetimeDays equal to 0.
- The highest MonetaryValue customers include 18102 (580,987.04), 14646 (528,602.52), 14156 (313,437.62), 14911 (291,420.81), and 17450 (244,784.25).
- The highest TotalItems customers include 14646 (367,193), 13902 (220,600), 13694 (188,201), 18102 (181,645), and 14156 (164,325).

A zero lifetime is expected when a customer has purchases on only one calendar date. It is not automatically a data-quality error.

## Preliminary preprocessing recommendations

For a first behavioral clustering experiment, a defensible candidate set is Recency, Frequency, MonetaryValue, UniqueProducts, and CustomerLifetimeDays. This retains inactivity, repeat purchasing, spending, product breadth, and relationship duration. TotalItems could be compared with MonetaryValue rather than automatically included alongside it because their correlation is 0.875. The two average-order features are useful for a separate order-intensity sensitivity analysis but may overlap conceptually with total activity measures.

Apply `log1p` to the strongly right-skewed selected variables before scaling. Keep Recency and CustomerLifetimeDays in their original forms initially, then standardize every selected feature. StandardScaler alone equalizes variance but does not correct extreme skew, so extreme customers could still dominate distances.

These are candidate choices for later testing, not final clustering decisions.

## Limitations

- IQR flags are sensitive to skew and identify unusual values, not confirmed errors.
- Pearson correlation measures linear relationships and can be strongly affected by extreme observations.
- The results describe one historical retailer and are dominated by UK customers.
- Removing cancellations during preparation describes gross completed purchasing behavior rather than net behavior after returns.
- Country is a modal label and does not preserve changes in customer location.
- Alternative feature subsets and transformations must be compared during later model evaluation.
