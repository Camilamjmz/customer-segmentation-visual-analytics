# Controlled K-Means Preprocessing Experiment

## Objective

This experiment compares three existing preprocessing strategies while holding the clustering algorithm, feature set, candidate values of `k`, initialization count, and random seeds constant. It is an initial controlled comparison, not a final clustering system or model-selection decision.

## Experimental design

The clustering features are Recency, Frequency, MonetaryValue, UniqueProducts, and CustomerLifetimeDays. `CustomerID` is retained only for alignment and is never passed to K-Means.

The experiment evaluates `standard`, `log_standard`, and `log_robust` preprocessing for `k = 2` through `8`. Each combination is fitted with `n_init = 20` using random states 42, 7, 21, 84, and 123. This produces 105 model fits.

K-Means is used as a controlled comparison algorithm because it is reproducible, widely understood, and directly sensitive to the geometry created by transformation and scaling. Holding K-Means constant helps isolate the effect of preprocessing.

Values from 2 through 8 cover simple broad partitions and moderately detailed segmentations without introducing an unnecessarily wide search during the first experiment.

## Evaluation metrics

- **Silhouette Score:** compares within-cluster cohesion with separation from the nearest other cluster. Higher is better, with values near 1 indicating stronger separation.
- **Davies-Bouldin Index:** measures similarity between each cluster and its most similar neighbor. Lower is better.
- **Calinski-Harabasz Score:** compares between-cluster dispersion with within-cluster dispersion. Higher is better, but it often changes with `k` and should not be used alone.
- **Adjusted Rand Index (ARI):** compares two assignments while correcting for agreement expected by chance. Values near 1 indicate that different seeds found nearly the same partition, even if numeric cluster labels were permuted.

No metric alone establishes useful customer segments. Internal metrics evaluate geometric structure, not business meaning, actionability, or fairness.

## Stability

All combinations were highly stable across the five seeds. Mean pairwise ARI ranged from 0.953 to 1.000. The least stable tested combination was `log_robust`, `k = 7` (ARI 0.953). Exact agreement occurred for `standard`, `k = 3` and `log_robust`, `k = 2`.

Stability matters because an apparently strong solution is less trustworthy if small initialization changes produce substantially different customer assignments.

## Metric leaders within each strategy

| Strategy | Best mean silhouette | Lowest mean Davies-Bouldin | Highest mean Calinski-Harabasz |
| --- | --- | --- | --- |
| standard | k=6, 0.4198 | k=7, 0.8396 | k=7, 3,328.72 |
| log_standard | k=2, 0.4130 | k=2, 0.9126 | k=2, 5,989.93 |
| log_robust | k=2, 0.4055 | k=2, 0.9205 | k=2, 5,845.14 |

The transformed strategies agree on `k = 2` across all three metrics. The unlogged standard strategy has similar silhouette values for `k = 3`, `5`, `6`, and `7`, while Davies-Bouldin and Calinski-Harabasz favor `k = 7`.

## Cluster balance

Cluster balance is reported, not used as an automatic rejection rule. A small cluster can represent an important niche, an outlier group, or an unstable artifact. A dominant cluster can represent a genuine majority or insufficient separation.

- `log_standard`, `k = 2` averages 45.95% in the smaller cluster and 54.05% in the larger cluster.
- `log_robust`, `k = 2` averages 47.26% and 52.74%.
- `standard`, `k = 2` averages 41.38% and 58.62%.
- Unlogged `standard` solutions from `k = 3` onward isolate very small clusters. At `k = 3`, the smallest cluster averages 0.238% (14 customers). At `k = 7`, some runs contain a cluster of only 2 customers (0.034%).
- Across the transformed strategies, the smallest average cluster percentage stays above 7% for all tested values of `k`.

The tiny unlogged clusters are consistent with the EDA finding that extreme customers remain highly influential when StandardScaler is applied without a log transformation.

## Preliminary interpretation

Three combinations deserve later interpretation rather than automatic selection:

- `log_standard`, `k = 2` combines the strongest transformed-space internal metrics with high stability and balanced cluster sizes.
- `log_robust`, `k = 2` is exactly stable across seeds and similarly balanced, with slightly weaker internal metrics.
- `standard`, `k = 6` or `7` has the strongest silhouette or Davies-Bouldin result in the unlogged space, but creates extremely small clusters that may mainly isolate high-value outliers.

Scores computed in differently transformed feature spaces should be compared cautiously because preprocessing changes the geometry being evaluated. The next experiment should inspect cluster profiles and business interpretability for these candidate combinations before adding another algorithm or declaring a winner.

## Limitations

- K-Means assumes roughly compact clusters around means and is sensitive to Euclidean geometry.
- The experiment evaluates only one feature set and three preprocessing choices.
- Internal metrics do not measure customer-segment usefulness.
- Outliers are intentionally retained and may create tiny clusters in the unlogged data.
- Stability across five seeds tests initialization sensitivity, not stability across resampled customers or different time periods.
- ARI measures assignment agreement but does not determine whether the agreed solution is substantively meaningful.
- Comparing Calinski-Harabasz values across differently transformed spaces requires caution.
