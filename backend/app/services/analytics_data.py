"""Deterministic dataset and EDA summaries for the analytics API."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from app.services.final_model import BEHAVIORAL_FEATURES, project_root

EDA_FEATURES = ["Recency", "Frequency", "MonetaryValue", "UniqueProducts", "CustomerLifetimeDays"]
LOG_FEATURES = {"Frequency", "MonetaryValue", "UniqueProducts"}
REMOVED = {"exact_duplicates": 34335, "missing_customer_id": 235151, "invalid_dates": 0, "cancelled_invoices": 18390, "nonpositive_quantity": 0, "nonpositive_price": 70}
FEATURE_DICTIONARY = [
    {"feature": "CustomerID", "definition": "Unique customer identifier.", "unit": "identifier", "used_for_clustering": False, "transformation": "Excluded from model input"},
    {"feature": "Country", "definition": "Most frequent valid transaction country for the customer; alphabetical order resolves ties.", "unit": "category", "used_for_clustering": False, "transformation": "Excluded because it is categorical and imbalanced"},
    {"feature": "Recency", "definition": "Days from the last valid purchase to 2011-12-10.", "unit": "days", "used_for_clustering": True, "transformation": "StandardScaler"},
    {"feature": "Frequency", "definition": "Number of distinct valid invoices.", "unit": "orders", "used_for_clustering": True, "transformation": "log1p, then StandardScaler"},
    {"feature": "MonetaryValue", "definition": "Total valid Quantity multiplied by Price.", "unit": "GBP", "used_for_clustering": True, "transformation": "log1p, then StandardScaler"},
    {"feature": "TotalItems", "definition": "Total valid quantity purchased.", "unit": "items", "used_for_clustering": False, "transformation": "Excluded from primary model because of strong MonetaryValue correlation"},
    {"feature": "UniqueProducts", "definition": "Number of distinct purchased StockCode values.", "unit": "products", "used_for_clustering": True, "transformation": "log1p, then StandardScaler"},
    {"feature": "AverageOrderValue", "definition": "MonetaryValue divided by Frequency.", "unit": "GBP per order", "used_for_clustering": False, "transformation": "Sensitivity-analysis feature only"},
    {"feature": "AverageItemsPerOrder", "definition": "TotalItems divided by Frequency.", "unit": "items per order", "used_for_clustering": False, "transformation": "Sensitivity-analysis feature only"},
    {"feature": "CustomerLifetimeDays", "definition": "Days between first and last valid purchase.", "unit": "days", "used_for_clustering": True, "transformation": "StandardScaler"},
]


def load_customers() -> pd.DataFrame:
    return pd.read_csv(project_root() / "data/processed/customer_features.csv")


def dataset_summary() -> dict:
    customers = load_customers()
    countries = customers["Country"].value_counts().head(10)
    return {
        "raw_transaction_count": 1067371, "cleaned_transaction_count": 779425,
        "removed_records_by_reason": REMOVED,
        "raw_minimum_transaction_date": "2009-12-01T07:45:00",
        "raw_maximum_transaction_date": "2011-12-09T12:50:00",
        "workbook_sheet_summary": [
            {"sheet_name": "Year 2009-2010", "row_count": 525461, "minimum_date": "2009-12-01T07:45:00", "maximum_date": "2010-12-09T20:01:00", "unique_customer_count": 4383, "unique_country_count": 40},
            {"sheet_name": "Year 2010-2011", "row_count": 541910, "minimum_date": "2010-12-01T08:26:00", "maximum_date": "2011-12-09T12:50:00", "unique_customer_count": 4372, "unique_country_count": 38},
        ],
        "final_customer_count": len(customers), "country_count": int(customers["Country"].nunique()),
        "top_country_counts": [{"country": name, "customer_count": int(count), "customer_percentage": float(count / len(customers) * 100)} for name, count in countries.items()],
        "customer_feature_dictionary": FEATURE_DICTIONARY,
    }


def distribution(feature: str) -> dict:
    if feature not in EDA_FEATURES:
        raise ValueError(f"Unsupported EDA feature: {feature}")
    series = load_customers()[feature].astype(float)
    counts, edges = np.histogram(series, bins="fd")
    result = {
        "feature": feature, "count": len(series), "minimum": float(series.min()), "maximum": float(series.max()),
        "mean": float(series.mean()), "median": float(series.median()), "standard_deviation": float(series.std()),
        "quartiles": {"q1": float(series.quantile(.25)), "q2": float(series.quantile(.5)), "q3": float(series.quantile(.75))},
        "histogram": {"bin_edges": edges.tolist(), "counts": counts.astype(int).tolist()},
        "skewness": float(series.skew()), "log_display_recommended": bool(feature in LOG_FEATURES), "log1p_histogram": None,
    }
    if feature in LOG_FEATURES:
        log_counts, log_edges = np.histogram(np.log1p(series), bins="fd")
        result["log1p_histogram"] = {"bin_edges": log_edges.tolist(), "counts": log_counts.astype(int).tolist()}
    return result


def correlations() -> dict:
    matrix = load_customers()[BEHAVIORAL_FEATURES].corr(method="pearson")
    pairs = []
    for left_index, left in enumerate(BEHAVIORAL_FEATURES):
        for right in BEHAVIORAL_FEATURES[left_index + 1:]:
            value = float(matrix.loc[left, right])
            pairs.append({"feature_a": left, "feature_b": right, "correlation": value, "absolute_correlation": abs(value)})
    strongest = sorted(pairs, key=lambda row: row["absolute_correlation"], reverse=True)[:8]
    return {"features": BEHAVIORAL_FEATURES, "matrix": matrix.to_numpy(float).tolist(), "strongest_correlation_pairs": strongest, "interpretation": {"method": "Pearson correlation on customer-level original values.", "guidance": "Values near 1 or -1 indicate strong linear association; correlation does not establish causation.", "primary_feature_note": "MonetaryValue was retained while strongly related TotalItems was excluded from the primary clustering matrix to reduce redundant volume information."}}


def outliers() -> dict:
    customers = load_customers(); results = []
    for feature in BEHAVIORAL_FEATURES:
        values = customers[feature].astype(float); q1, q3 = values.quantile([.25, .75]); iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        mask = (values < lower) | (values > upper)
        examples = customers.loc[mask, ["CustomerID", feature]].assign(_distance=lambda frame: np.maximum(lower - frame[feature], frame[feature] - upper)).nlargest(3, "_distance")
        results.append({"feature": feature, "q1": float(q1), "q3": float(q3), "iqr": float(iqr), "lower_bound": float(lower), "upper_bound": float(upper), "outlier_count": int(mask.sum()), "outlier_percentage": float(mask.mean() * 100), "representative_extreme_customers": [{"CustomerID": int(row.CustomerID), "value": float(getattr(row, feature))} for row in examples.itertuples(index=False)]})
    return {"method": "Tukey 1.5 × IQR rule on original customer-level values.", "features": results, "interpretation": "Outliers are flagged descriptively and were retained in the research datasets and final model."}


def segment_distributions() -> dict:
    customers = pd.read_csv(project_root() / "data/final/final_customer_segments.csv"); rows = []
    for (segment_id, segment_name), group in customers.groupby(["SegmentID", "SegmentName"], sort=True):
        features = []
        for feature in BEHAVIORAL_FEATURES:
            values = group[feature].astype(float); q1, q3 = values.quantile([.25, .75]); iqr = q3 - q1; lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            within = values[(values >= lower) & (values <= upper)]
            features.append({"feature": feature, "minimum": float(values.min()), "q1": float(q1), "median": float(values.median()), "q3": float(q3), "maximum": float(values.max()), "mean": float(values.mean()), "whisker_low": float(within.min()), "whisker_high": float(within.max()), "outlier_count": int(((values < lower) | (values > upper)).sum())})
        rows.append({"SegmentID": int(segment_id), "SegmentName": segment_name, "customer_count": len(group), "features": features})
    return {"whisker_method": "Most extreme observed values within the Tukey 1.5 × IQR bounds.", "segments": rows}


def model_validation() -> dict:
    root = project_root(); subsamples = pd.read_csv(root / "data/experiments/final_validation/subsampling_stability.csv")
    sensitivity = pd.read_csv(root / "data/experiments/final_validation/feature_sensitivity.csv")
    comparison = pd.read_csv(root / "data/experiments/algorithm_comparison/algorithm_comparison.csv")
    initialization = pd.read_csv(root / "data/experiments/kmeans_preprocessing_summary.csv")
    candidates = []
    for k in (3, 4):
        sub = subsamples[subsamples.k == k]; primary = sensitivity[(sensitivity.k == k) & sensitivity.feature_specification.str.startswith("MonetaryValue")].iloc[0]; alt = sensitivity[(sensitivity.k == k) & sensitivity.feature_specification.str.startswith("TotalItems")].iloc[0]
        init = initialization[(initialization.k == k) & (initialization.preprocessing_strategy == "log_standard")].iloc[0]
        metric = comparison[(comparison.algorithm == "K-Means") & (comparison.configuration == f"k={k}")].iloc[0]
        candidates.append({"k": k, "initialization_stability": {"mean_pairwise_ari": float(init.mean_pairwise_ari)}, "subsampling_stability": {"iterations": len(sub), "sample_proportion": float(sub.sample_proportion.iloc[0]), "mean_ari": float(sub.adjusted_rand_index.mean()), "standard_deviation_ari": float(sub.adjusted_rand_index.std()), "minimum_ari": float(sub.adjusted_rand_index.min()), "maximum_ari": float(sub.adjusted_rand_index.max()), "mean_cluster_percentage_variation": float(sub.mean_absolute_cluster_percentage_difference.mean()), "mean_centroid_distance": float(sub.mean_centroid_distance.mean())}, "feature_sensitivity": {"alternative_feature": "TotalItems replaces MonetaryValue", "ari_vs_primary": float(alt.ari_vs_primary), "primary_silhouette": float(primary.silhouette_score), "alternative_silhouette": float(alt.silhouette_score)}, "internal_quality": {"silhouette_score": float(metric.silhouette_score), "davies_bouldin": float(metric.davies_bouldin), "calinski_harabasz": float(metric.calinski_harabasz)}, "cluster_balance": {"smallest_cluster_percentage": float(metric.smallest_cluster_percentage), "largest_cluster_percentage": float(metric.largest_cluster_percentage)}, "customer_coverage_percentage": 100.0, "parsimony_note": "Three broad behavioral groups with fewer boundaries." if k == 3 else "Adds a recent low-frequency group but requires a fourth boundary."})
    return {"candidates": candidates, "recommended_k": 3, "recommendation_rationale": "K-Means k=3 combines stronger full-coverage internal metrics, balanced interpretable groups, stronger subsampling stability, and greater parsimony. K-Means k=4 remains a sensitivity model."}
