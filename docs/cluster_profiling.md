# Candidate Cluster Profiling

## Objective and method

Seven K-Means candidates were refitted with `random_state=42` and `n_init=20`. Clustering uses the five transformed features, while interpretation joins each assignment back to `customer_features.csv`. `CustomerID` is preserved for alignment and never enters the clustering matrix.

Transformed values are appropriate for fitting because they keep different units and highly skewed variables from dominating Euclidean distance. Original values are appropriate for interpretation because statements such as “median spending is 4,153” are meaningful, while a scaled value such as 1.2 is not directly actionable.

Medians are emphasized because retained wholesale-scale customers make several feature distributions strongly right-skewed. Means are also included in each candidate CSV but can be pulled upward by a few extreme customers.

## Relative-profile rule

Each cluster median is divided by the overall customer median for the same feature:

- Ratio at or below 0.50: substantially below overall median
- Above 0.50 and below 0.80: below overall median
- From 0.80 through 1.25: near overall median
- Above 1.25 through 2.00: above overall median
- Above 2.00: substantially above overall median

The overall medians are Recency 96 days, Frequency 3, MonetaryValue 867.74, TotalItems 480, UniqueProducts 45, AverageOrderValue 279.24, AverageItemsPerOrder 153.59, and CustomerLifetimeDays 221. These indicators describe numerical level only. For Recency, a lower value means a more recent purchase.

## Cluster profiles and candidate labels

Labels are descriptive proposals made after numerical profiling. They are not fixed marketing categories.

| Strategy | k | Cluster | Customers | Share | Median R | F | Monetary | Items | Products | AOV | Items/order | Lifetime | Candidate label and numeric rationale |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| standard | 6 | 0 | 1,570 | 26.71% | 61 | 2 | 507.75 | 298 | 28 | 258.75 | 150.00 | 32 | Recent low-activity, short-history: F=2, value=508, lifetime=32 |
| standard | 6 | 1 | 492 | 8.37% | 15 | 20 | 8,089.15 | 4,584 | 295 | 395.74 | 232.28 | 677 | Recent high-activity established: F=20, value=8,089, lifetime=677 |
| standard | 6 | 2 | 1,999 | 34.01% | 48 | 6 | 1,821.90 | 1,010 | 81 | 298.09 | 167.75 | 521 | Active established mid-value: F=6, value=1,822, lifetime=521 |
| standard | 6 | 3 | 20 | 0.34% | 3.5 | 114 | 102,305.70 | 59,735 | 530 | 626.90 | 473.47 | 733 | Extreme high-activity long-history: F=114 and value=102,306 |
| standard | 6 | 4 | 4 | 0.07% | 2 | 153.5 | 421,020.07 | 172,985 | 1,203.5 | 2,754.95 | 1,153.04 | 736.5 | Extreme wholesale-scale: four customers with median value=421,020 |
| standard | 6 | 5 | 1,793 | 30.50% | 446 | 1 | 359.40 | 194 | 22 | 229.20 | 122.00 | 0 | Inactive one-date customers: R=446, F=1, lifetime=0 |
| standard | 7 | 0 | 1,862 | 31.68% | 51 | 6 | 1,708.98 | 947 | 74 | 294.48 | 165.10 | 511 | Active established mid-value: F=6, value=1,709, lifetime=511 |
| standard | 7 | 1 | 1,790 | 30.45% | 446 | 1 | 359.38 | 194 | 22 | 229.08 | 122.00 | 0 | Inactive one-date customers: R=446, F=1, lifetime=0 |
| standard | 7 | 2 | 8 | 0.14% | 2 | 205.5 | 114,191.66 | 64,541 | 1,354 | 555.71 | 313.78 | 735 | Extreme frequent broad-product: F=206 and 1,354 products |
| standard | 7 | 3 | 611 | 10.39% | 19 | 15 | 6,452.99 | 3,555 | 262 | 378.14 | 222.93 | 656 | Recent high-activity established: F=15, value=6,453, lifetime=656 |
| standard | 7 | 4 | 1,552 | 26.40% | 61 | 2 | 499.87 | 295 | 28 | 258.67 | 150.00 | 30.5 | Recent low-activity, short-history: F=2, value=500, lifetime=31 |
| standard | 7 | 5 | 2 | 0.03% | 1.5 | 148 | 554,794.78 | 274,419 | 671.5 | 3,753.74 | 1,842.23 | 737 | Extreme value/volume pair: two customers above 528,000 value |
| standard | 7 | 6 | 53 | 0.90% | 5 | 58 | 45,179.10 | 20,921 | 280 | 667.60 | 378.02 | 727 | High-value long-history: F=58, value=45,179, lifetime=727 |
| log_standard | 2 | 0 | 3,181 | 54.12% | 332 | 1 | 373.01 | 206 | 22 | 228.18 | 125.50 | 0 | Inactive low-activity: R=332, F=1, lifetime=0 |
| log_standard | 2 | 1 | 2,697 | 45.88% | 33 | 7 | 2,399.82 | 1,401 | 107 | 326.00 | 190.00 | 533 | Recent established repeat: R=33, F=7, lifetime=533 |
| log_standard | 3 | 0 | 1,520 | 25.86% | 25 | 11 | 4,153.39 | 2,350 | 155.5 | 351.22 | 202.54 | 622 | Recent high-activity established: F=11, value=4,153, lifetime=622 |
| log_standard | 3 | 1 | 2,132 | 36.27% | 406 | 1 | 266.90 | 144 | 16 | 206.12 | 109.75 | 0 | Inactive low-activity: R=406, F=1, value=267 |
| log_standard | 3 | 2 | 2,226 | 37.87% | 72 | 3 | 990.18 | 550 | 52 | 285.20 | 164.22 | 287.5 | Moderate developing: R=72, F=3, value=990, lifetime=288 |
| log_standard | 4 | 0 | 1,180 | 20.07% | 74.5 | 1 | 338.20 | 195 | 19 | 216.63 | 126.00 | 0 | Recent one-date low-activity: R=75, F=1, lifetime=0 |
| log_standard | 4 | 1 | 1,223 | 20.81% | 23 | 13 | 4,921.53 | 2,860 | 175 | 368.32 | 213.40 | 643 | Recent high-activity established: F=13, value=4,922, lifetime=643 |
| log_standard | 4 | 2 | 1,511 | 25.71% | 475 | 1 | 311.77 | 159 | 19 | 219.85 | 114.00 | 0 | Long-inactive one-date: R=475, F=1, lifetime=0 |
| log_standard | 4 | 3 | 1,964 | 33.41% | 70 | 4 | 1,248.35 | 707 | 64 | 287.80 | 166.00 | 374 | Established moderate: F=4, value=1,248, lifetime=374 |
| log_standard | 5 | 0 | 1,035 | 17.61% | 510 | 1 | 200.10 | 102 | 12 | 171.81 | 90.50 | 0 | Long-inactive one-date low-value: R=510 and value=200 |
| log_standard | 5 | 1 | 1,661 | 28.26% | 51 | 5 | 1,376.87 | 791 | 69 | 289.85 | 167.60 | 433 | Active established moderate: R=51, F=5, lifetime=433 |
| log_standard | 5 | 2 | 1,195 | 20.33% | 65 | 1 | 362.71 | 210 | 20 | 228.86 | 135.00 | 0 | Recent one-date low-value: R=65, F=1, lifetime=0 |
| log_standard | 5 | 3 | 1,094 | 18.61% | 20 | 14 | 5,472.16 | 3,085 | 184 | 375.26 | 217.68 | 649 | Recent high-activity long-history: F=14, value=5,472, lifetime=649 |
| log_standard | 5 | 4 | 893 | 15.19% | 401 | 3 | 794.41 | 429 | 47 | 303.50 | 165.50 | 139 | Inactive occasional: R=401, F=3, lifetime=139 |
| log_robust | 2 | 0 | 2,778 | 47.26% | 34 | 7 | 2,346.23 | 1,387 | 106.5 | 332.10 | 194.00 | 518 | Recent established repeat: R=34, F=7, lifetime=518 |
| log_robust | 2 | 1 | 3,100 | 52.74% | 325.5 | 1 | 360.73 | 198 | 21 | 219.50 | 121.00 | 0 | Inactive low-activity: R=326, F=1, lifetime=0 |

## Standard-strategy micro-cluster audit

### Standard, k=6

- Cluster 3 contains 20 customers (0.34%): `12415, 12748, 13089, 13408, 13694, 13798, 14298, 14527, 14606, 15039, 15061, 15311, 16029, 16422, 16684, 17450, 17511, 17841, 17850, 17949`. Countries are United Kingdom (19) and Australia (1). MonetaryValue ranges from 27,246.88 to 244,784.25; Frequency from 28 to 336; TotalItems from 6,647 to 188,201; UniqueProducts from 57 to 2,286; and lifetime from 362 to 738 days.
- Cluster 4 contains customers `14156, 14646, 14911, 18102` (0.07%). Countries are EIRE (2), Netherlands (1), and United Kingdom (1). MonetaryValue ranges from 291,420.81 to 580,987.04; TotalItems from 147,972 to 367,193; Frequency from 145 to 398; UniqueProducts from 382 to 2,550; AverageOrderValue from 732.21 to 4,006.81; AverageItemsPerOrder from 371.79 to 2,431.74; and lifetime from 729 to 738 days.

### Standard, k=7

- Cluster 2 contains `12748, 13089, 13694, 14156, 14606, 14911, 15311, 17841` (0.14%). Six are from the United Kingdom and two from EIRE. Median Frequency is 205.5, MonetaryValue 114,191.66, UniqueProducts 1,354, and lifetime 735 days.
- Cluster 5 contains `14646, 18102` (0.03%), one customer from the Netherlands and one from the United Kingdom. Both have more than 528,000 in MonetaryValue, more than 181,000 items, at least 145 invoices, and lifetimes of at least 736 days.
- Cluster 6 contains 53 customers (0.90%): `12346, 12415, 12471, 12681, 12682, 12921, 12931, 12971, 13078, 13081, 13093, 13199, 13319, 13408, 13468, 13767, 13777, 13798, 13881, 14031, 14088, 14096, 14298, 14527, 14667, 14680, 15039, 15061, 15769, 15838, 15856, 16013, 16029, 16133, 16168, 16422, 16446, 16684, 16705, 16754, 16779, 17243, 17377, 17389, 17428, 17450, 17511, 17675, 17677, 17850, 17920, 17949, 17961`. Countries are United Kingdom (49), France (2), Australia (1), and Germany (1). This cluster is heterogeneous: Frequency ranges from 2 to 155 and AverageOrderValue from 28.67 to 84,236.25.

These records contain positive purchases, identifiable customers, and generally substantial or repeated activity. The longest-lived micro-cluster customers transact across nearly the full dataset period. This supports interpretation as legitimate extreme or wholesale-scale behavior rather than obvious missing-value, negative-value, or single-line errors. Customer 16446 remains a notable concentration case: only two invoices but AverageOrderValue 84,236.25. It should be reviewed against raw transactions in a future audit, not deleted here.

## Interpretability comparison

- **Log-standard k=2 is too coarse for detailed segmentation.** It cleanly separates inactive low-activity customers from recent established repeat customers, but combines substantial variation within each broad group.
- **Log-standard k=3 is useful and interpretable.** It adds a moderate/developing group between inactive and high-activity customers, with balanced shares of 25.86%, 36.27%, and 37.87%.
- **Log-standard k=4 is useful and more nuanced.** It distinguishes recent one-date customers from long-inactive one-date customers while retaining moderate and high-activity groups. Shares remain between 20.07% and 33.41%.
- **Log-standard k=5 is plausibly interpretable but begins to fragment low-activity behavior.** It divides low-frequency customers into long-inactive one-date, recent one-date, and inactive occasional groups. This may be useful if lifecycle detail matters, but it requires more business justification than k=3 or k=4.
- **Log-robust k=2 is also too coarse.** Its two profiles closely resemble log-standard k=2, so robust scaling does not create a new behavioral interpretation at this level.
- **Standard k=6 and k=7 are too fragmented for a primary customer typology.** Their large clusters are interpretable, but multiple clusters below 1% mostly isolate extreme-scale customers. Standard k=7 also contains a heterogeneous 53-customer micro-cluster.

## Preliminary recommendation

Advance **log-standard k=3** and **log-standard k=4** to later comparison with other algorithms. They provide distinct behavioral profiles without micro-clusters, maintain reasonable size balance, and represent two useful levels of detail. K=3 offers a simpler broad lifecycle structure; k=4 tests whether separating recent and long-inactive one-date customers adds meaningful information.

This recommendation reduces the candidate set. It does not choose a final clustering model.

## Limitations

- Cluster numbers are arbitrary identifiers, not ordered performance grades.
- Candidate labels summarize medians and do not describe every customer in a cluster.
- Means and medians cannot show the full within-cluster distribution.
- Original-unit scatterplots remain affected by skew; monetary axes use a logarithmic scale in the notebook.
- The micro-cluster assessment indicates plausibility, not independent transaction-level validation.
- Business usefulness and temporal robustness remain untested.
