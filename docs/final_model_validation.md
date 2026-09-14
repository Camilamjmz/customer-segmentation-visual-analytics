# Final Model Validation

## Objective

This validation tests the two leading K-Means candidates before a final recommendation. Both use log-standard preprocessing and the primary features Recency, Frequency, MonetaryValue, UniqueProducts, and CustomerLifetimeDays. The analysis keeps every customer and does not remove outliers or alter existing processed data.

## Why subsampling stability matters

A useful segmentation should represent recurring structure rather than depend heavily on the exact customers used to fit it. For each candidate, a reference model was fitted to all 5,878 customers using `random_state=42` and `n_init=20`. Twenty deterministic samples then selected 80% of customers without replacement. Each sample contained 4,702 unique customers and used seeds 1000 through 1019.

Adjusted Rand Index (ARI) compares the sample assignments with reference assignments for those same customers. ARI is invariant to numeric cluster labels. For size and centroid comparisons, each sample's centroids were aligned one-to-one with reference centroids by minimizing total Euclidean distance across all possible label permutations. Cluster-size variation is the mean absolute percentage-point difference between aligned sample and reference shares. Centroid variation is Euclidean distance in the standardized five-feature space; lower values indicate less movement.

## Robustness results

| Candidate | Mean ARI | SD | Minimum | Maximum | Mean size variation | Mean centroid distance | Maximum centroid distance |
|---|---:|---:|---:|---:|---:|---:|---:|
| k=3 | 0.9801 | 0.0161 | 0.9441 | 0.9987 | 0.3995 pp | 0.0272 | 0.0850 |
| k=4 | 0.9614 | 0.0331 | 0.9183 | 0.9943 | 0.4440 pp | 0.0426 | 0.1163 |

Both candidates are robust. The k=3 solution is more stable under customer subsampling: it has higher mean and minimum ARI, roughly half the ARI standard deviation, and lower centroid movement. The k=4 solution remains strong but its additional boundary is more sensitive to sample composition.

Previous random-initialization testing reached a complementary result. Mean pairwise ARI was 0.9899 for k=3 and 0.9959 for k=4. Thus k=4 is slightly less affected by initialization on the full sample, while k=3 is more stable when the customer population changes.

## Why feature sensitivity matters

MonetaryValue and TotalItems are strongly correlated measures of purchase volume. Replacing MonetaryValue with TotalItems tests whether the solution depends on spending specifically or reflects broader purchase activity. The alternative matrix was generated only in memory for this experiment. It applies `log1p` to Frequency, TotalItems, and UniqueProducts, leaves Recency and CustomerLifetimeDays unchanged, and then applies StandardScaler. It contains no MonetaryValue column and was not saved over any preprocessing dataset.

| Feature set | k | Silhouette | Davies-Bouldin | Calinski-Harabasz | Smallest / largest cluster | ARI vs primary |
|---|---:|---:|---:|---:|---:|---:|
| MonetaryValue primary | 3 | 0.3110 | 1.1230 | 4856.59 | 25.86% / 37.87% | 1.0000 |
| TotalItems alternative | 3 | 0.3070 | 1.1441 | 4685.28 | 28.82% / 39.35% | 0.7750 |
| MonetaryValue primary | 4 | 0.2935 | 1.1303 | 4343.73 | 20.07% / 33.41% | 1.0000 |
| TotalItems alternative | 4 | 0.2838 | 1.1625 | 4125.21 | 19.85% / 33.16% | 0.8858 |

The primary MonetaryValue feature set has better internal metrics at both k values. The k=4 assignments are less sensitive to the volume-variable substitution, although k=3 still shows substantial agreement and retains clearer internal quality.

## Behavioral-profile comparison

Cluster numbers were not compared literally. The profiles were matched conceptually using medians in original units.

- **k=3 primary:** inactive/low activity has Recency 406, Frequency 1, and MonetaryValue 266.90; intermediate/developing has 72, 3, and 990.18; recent high activity has 25, 11, and 4,153.39.
- **k=3 TotalItems alternative:** inactive/low activity has 426, 1, and 252.50; intermediate/developing has 73, 3, and 855.71; recent high activity has 26, 11, and 3,754.95.
- **k=4 primary:** separates recent low-frequency customers (Recency 74.5, Frequency 1) from inactive low-frequency customers (475, 1), alongside intermediate customers (70, 4) and recent high-activity customers (23, 13).
- **k=4 TotalItems alternative:** repeats the same four-part pattern with corresponding medians of 73/1, 473/1, 68/4, and 22/13.

The same broad customer behaviors persist after substituting TotalItems. The k=4 extra segment is especially consistent: it distinguishes relatively recent one-order customers from long-lapsed one-order customers. The k=3 solution instead keeps a simpler three-level activity structure.

## Decision framework

The criteria are considered separately because a numerical average would mix metrics with different meanings.

| Criterion | k=3 | k=4 | Interpretation |
|---|---|---|---|
| Internal quality | Better on all three metrics | Slightly weaker | Favors k=3 |
| Cluster balance | 25.86% to 37.87% | 20.07% to 33.41% | Both acceptable; k=3 is simpler and balanced |
| Interpretability | Three clear activity levels | Adds recent one-order group | k=4 adds useful detail, but also complexity |
| Initialization stability | ARI 0.9899 | ARI 0.9959 | Slightly favors k=4 |
| Subsampling stability | ARI 0.9801, lower variation | ARI 0.9614, higher variation | Favors k=3 |
| Feature sensitivity | ARI 0.7750 | ARI 0.8858 | Favors k=4 |
| Customer coverage | 100% | 100% | Equal |
| Parsimony | Three segments | Four segments | Favors k=3 unless the extra group has a clear use |

## Final recommendation

The recommended final specification is **K-Means with log-standard preprocessing, the MonetaryValue-based five-feature set, and k=3**.

This recommendation uses all available evidence. K-Means k=3 previously outperformed hierarchical clustering among full-coverage methods and avoided DBSCAN's noise exclusions. It has stronger internal quality than k=4, balanced and behaviorally clear clusters, near-perfect initialization stability, stronger subsampling stability, full coverage, and greater parsimony. Replacing MonetaryValue with TotalItems changes some boundary assignments but preserves the inactive, intermediate, and high-activity interpretation.

K-Means k=4 remains a credible sensitivity model. Its main strengths are slightly higher initialization stability, higher feature-substitution ARI, and a consistent distinction between recent and inactive one-order customers. Its weaknesses are lower internal quality, greater subsampling variation, and the need to justify the operational value of the fourth segment.

## Limitations

- Subsampling tests use 20 deterministic 80% samples rather than bootstrap confidence intervals.
- Centroid distance is measured in the selected standardized space and does not have a direct business-unit interpretation.
- Feature sensitivity tests only one substitution and does not examine alternative weights or additional average-order features.
- Internal metrics do not demonstrate future stability, causal meaning, or business impact.
- Validation uses one historical dataset and should eventually be supplemented by temporal or holdout validation.

## Reproduction

From the project root in Windows PowerShell:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python scripts\run_final_model_validation.py
python -m unittest discover -s tests -v
```
