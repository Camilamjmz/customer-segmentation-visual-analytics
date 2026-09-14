# Clustering Preprocessing Strategy

## Scope

This module prepares numeric customer behavior matrices for later controlled clustering experiments. It does not fit clustering algorithms, remove customers, alter `customer_features.csv`, or select a winning strategy.

## Primary feature set

The primary matrix contains five behavioral variables:

- `Recency`: time since the last purchase.
- `Frequency`: number of distinct valid invoices.
- `MonetaryValue`: total valid purchase value.
- `UniqueProducts`: number of distinct products purchased.
- `CustomerLifetimeDays`: time between first and last valid purchases.

Together they describe inactivity, repeat purchasing, spending, product breadth, and relationship duration.

## Excluded variables

- `Country` is categorical and highly imbalanced toward the United Kingdom. It requires a separately justified encoding and distance treatment.
- `TotalItems` is strongly correlated with `MonetaryValue` (`r = 0.875`) and could give overall customer size excessive influence if both are included.
- `AverageOrderValue` and `AverageItemsPerOrder` are reserved for later sensitivity analysis of order intensity.
- `CustomerID` is retained only as an identifier and is never used as a clustering variable.

## Strategies

### `standard`

The five original features are passed directly to `StandardScaler`. This provides an unlogged baseline for later comparison.

### `log_standard`

`log1p` is applied to `Frequency`, `MonetaryValue`, and `UniqueProducts`, followed by `StandardScaler` on all five features. EDA showed strong right skew in those three variables. `Recency` and `CustomerLifetimeDays` are left untransformed because their original skew was modest and logging was not clearly beneficial.

### `log_robust`

The same three variables receive `log1p`, followed by `RobustScaler` on all five features.

## Transformation behavior

`log1p(x)` calculates the natural logarithm of `1 + x`. It compresses large positive values while supporting zero. The module rejects negative values in variables selected for this transformation.

`StandardScaler` subtracts each feature's mean and divides by its standard deviation. Its outputs are centered near zero with unit variance, but its mean and standard deviation remain sensitive to extreme observations.

`RobustScaler` subtracts the median and divides by the interquartile range. It is less influenced by extreme observations, although it does not remove or correct them.

## Validation and alignment

The service verifies that requested columns exist, requested features are numeric, and inputs contain no missing or infinite values. It copies the selected data before transformation, checks that log inputs are nonnegative, and verifies the transformed matrix again for missing or infinite values. Row count and order are preserved, with `CustomerID` copied separately and restored as the first export column.

## Why outliers are retained

The retailer includes wholesale activity. Extreme customers may represent real high-value or high-volume behavior rather than data errors. Removing them before model comparison would silently change the research population. The three strategies instead allow later experiments to measure how transformations and scaler choice affect their influence.

## Why preserve three strategies

Keeping all three datasets makes later comparisons reproducible:

- `standard` isolates the effect of scaling without logging.
- `log_standard` tests skew reduction with conventional mean-based scaling.
- `log_robust` tests the same skew reduction with median- and IQR-based scaling.

No strategy is designated as best before clustering quality, stability, and interpretability are compared under controlled conditions.

## Known limitations

- Log transformation changes distances and reduces the relative separation of the largest values.
- Robust scaling reduces outlier influence but does not guarantee that outliers cannot affect a clustering algorithm.
- Scaling parameters are currently fitted to the complete historical customer table. A future predictive workflow would need training-only fitting to avoid leakage.
- The primary feature set may still contain moderate relationships, such as Frequency with UniqueProducts.
- Results remain specific to this historical retailer and its cleaning policy.
