# Final Segmentation Model

The frozen primary model is K-Means with k=3, `random_state=42`, and `n_init=20`. It uses log-standard preprocessing on Recency, Frequency, MonetaryValue, UniqueProducts, and CustomerLifetimeDays. Frequency, MonetaryValue, and UniqueProducts receive `log1p`; all five features then receive StandardScaler.

Stable segment IDs are assigned from original-unit medians, not arbitrary K-Means labels. The cluster with highest median Frequency is Segment 2, **Recent High-Activity**. Of the remaining clusters, the one with highest median Recency is Segment 0, **Inactive Low-Activity**. The remaining cluster is Segment 1, **Developing / Moderate**. The exact raw-label mapping is recorded in `data/final/final_model_summary.json`.

The selected model has silhouette 0.311049, Davies-Bouldin 1.122967, and Calinski-Harabasz 4856.588. It covers all 5,878 customers. The three segments represent inactive one-order customers, intermediate/developing customers, and recent high-activity customers.

K-Means k=3 was selected because it had the strongest full-coverage internal metrics in the algorithm comparison, balanced profiles, mean initialization ARI 0.9899, mean subsampling ARI 0.9801, clear interpretation, and greater parsimony. K-Means k=4 remains documented as a sensitivity model because it consistently separates recent one-order customers, but it has weaker internal metrics and greater subsampling variation.

Limitations include historical data ending in 2011, retained positive outliers, internal rather than outcome-based validation, and segment descriptions that do not establish intent or causality.

Reproduce the frozen files from the backend directory with:

```powershell
python scripts\freeze_final_model.py
```
