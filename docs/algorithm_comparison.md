# Controlled Algorithm Comparison

## Objective and shared preprocessing

This experiment compares K-Means, Ward hierarchical agglomerative clustering, and DBSCAN on exactly the same 5,878-customer `log_standard` matrix. Its five inputs are Recency, Frequency, MonetaryValue, UniqueProducts, and CustomerLifetimeDays. CustomerID is retained only for alignment. Holding preprocessing fixed makes differences attributable to the algorithms rather than to different feature transformations.

Frequency, MonetaryValue, and UniqueProducts were transformed with `log1p`; Recency and CustomerLifetimeDays were not. All five variables were then standardized. Outliers were retained. The experiment is reproducible: K-Means uses `random_state=42` and `n_init=20`; hierarchical clustering uses Ward linkage and Euclidean distance; DBSCAN evaluates the complete requested 8-by-4 parameter grid.

## Conceptual differences

- **K-Means** partitions every customer around a centroid. It is efficient and produces compact, easy-to-profile segments, but assumes roughly convex groups and is sensitive to extreme observations.
- **Hierarchical clustering** successively merges customers and does not require centroid-based assignments. Ward linkage favors compact groups and exposes a nested grouping interpretation, but can be computationally expensive and still assigns every outlier to a cluster.
- **DBSCAN** defines dense regions and labels sparse observations as noise. It can discover non-spherical groups and isolate unusual customers, but its result is highly sensitive to `eps` and `min_samples`, particularly in five dimensions with varying customer density.

## Quantitative results

| Algorithm | Configuration | Silhouette | Davies-Bouldin | Calinski-Harabasz | Smallest / largest cluster |
|---|---|---:|---:|---:|---:|
| K-Means | k=3 | 0.3110 | 1.1230 | 4856.59 | 25.86% / 37.87% |
| K-Means | k=4 | 0.2935 | 1.1303 | 4343.73 | 20.07% / 33.41% |
| Hierarchical | k=3 | 0.2639 | 1.2312 | 4099.31 | 23.70% / 42.45% |
| Hierarchical | k=4 | 0.2449 | 1.1873 | 3568.17 | 14.94% / 42.45% |
| DBSCAN | eps=0.5, min_samples=20 | 0.3473* | 0.9555* | 3436.58* | 24.91% / 57.18% |

`*` DBSCAN metrics use only the 4,825 non-noise customers and therefore are not directly equivalent to metrics computed on all 5,878 customers. This solution marks 1,053 customers (17.91%) as noise.

The Adjusted Rand Index (ARI) is 0.5790 for K-Means k=3 versus hierarchical k=3, and 0.5568 for the k=4 pair. These moderate values show meaningful shared structure alongside substantial assignment differences.

## DBSCAN exploration and noise

Noise means that a customer did not belong to a sufficiently dense neighborhood for the selected parameters; it does not mean the customer or record is invalid. Of the 32 configurations, 13 produced only one non-noise cluster and therefore have no internal metrics. Many configurations with high silhouette scores contain a cluster below 1% of customers—for example, `eps=1.0, min_samples=5` has silhouette 0.5591 but splits only seven customers from a 5,841-customer cluster. Such a result is statistically separated but not a useful broad segmentation.

The strongest DBSCAN candidate passing all three stated quality filters is `eps=0.5, min_samples=20`: two clusters of 3,361 (57.18%) and 1,464 (24.91%) customers, plus 1,053 noise customers (17.91%). It provides a plausible active-versus-lapsed density split, but leaves nearly one in five customers without a segment.

## Behavioral interpretation

K-Means k=3 gives three balanced and distinct behavioral levels: high-value active customers (median Recency 25, Frequency 11, MonetaryValue 4,153.39), lapsed one-order customers (406, 1, 266.90), and an intermediate group (72, 3, 990.18). K-Means k=4 retains the high-value and intermediate groups while separating recent one-order customers from more lapsed one-order customers.

Hierarchical k=3 tells a similar three-level story. Its active group has median Recency 25, Frequency 12, and MonetaryValue 4,452.71; its lapsed group has 313, 1, and 250.13; and its intermediate group has 106, 3, and 983.10. Its clusters are less balanced than K-Means k=3, but the behavioral interpretation is coherent.

DBSCAN's selected solution yields an active/repeat cluster (median Recency 51, Frequency 5, MonetaryValue 1,352.00) and a lapsed/one-order cluster (387, 1, 226.67). Noise is intentionally excluded from segment profiles. This coarser result loses the high-value tier visible in the three- and four-cluster solutions.

## Why metrics are not sufficient

Silhouette rewards separation and cohesion, Davies-Bouldin rewards compact, separated clusters, and Calinski-Harabasz compares between- and within-cluster dispersion. None measures business usefulness, stability under new samples, actionability, or whether excluding many customers as noise is acceptable. DBSCAN scores are additionally computed on a reduced population. Cluster balance and original-unit profiles must therefore be considered alongside internal metrics.

## Limitations and preliminary recommendation

The study uses one preprocessing strategy, one fixed observation window, internal validation only, and no resampling or external business outcome. Ward hierarchical clustering can also be sensitive to unusual observations, while DBSCAN has one global density threshold and may struggle with variable-density structure.

Statistically, K-Means k=3 is strongest among methods that segment every customer: it has the best silhouette and Calinski-Harabasz score, the lowest Davies-Bouldin value, and the most balanced sizes. Hierarchical k=3 is interpretable but weaker on all three internal metrics. The quality-filtered DBSCAN candidate has an attractive non-noise silhouette, but the restricted scoring population and 17.91% noise prevent a direct win.

The preliminary recommendation is to carry **K-Means k=3** forward as the leading full-coverage solution, with **K-Means k=4** retained as an interpretability sensitivity case. This is evidence for the next decision—not an automatic final model selection.

## Reproduction

From the project root in Windows PowerShell:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python scripts\run_algorithm_comparison.py
python -m unittest discover -s tests -v
```
