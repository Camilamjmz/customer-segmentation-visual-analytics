"""Read-only routes for final segmentation analytics."""

import json

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from app.schemas import CorrelationsResponse, CustomersResponse, DatasetResponse, DistributionResponse, MethodologyStage, ModelComparisonItem, ModelResponse, ModelValidationResponse, OutliersResponse, OverviewResponse, SegmentDetail, SegmentDistributionsResponse, SegmentSummary
from app.services.analytics_data import correlations as correlation_summary
from app.services.analytics_data import dataset_summary, distribution, model_validation as validation_summary, outliers as outlier_summary, segment_distributions as segment_distribution_summary
from app.services.final_model import project_root, segment_analytics

router = APIRouter(prefix="/api")


def load_final() -> tuple[pd.DataFrame, dict]:
    root = project_root()
    customers = pd.read_csv(root / "data/final/final_customer_segments.csv")
    metadata = json.loads((root / "data/final/final_model_summary.json").read_text(encoding="utf-8"))
    return customers, metadata


@router.get("/overview", response_model=OverviewResponse)
def overview() -> dict:
    customers, model = load_final()
    return {"original_transaction_count": 1067371, "cleaned_transaction_count": 779425, "final_customer_count": len(customers), "country_count": int(customers["Country"].nunique()), "final_segment_count": int(customers["SegmentID"].nunique()), "selected_algorithm": model["algorithm"], "selected_k": model["k"], "preprocessing_strategy": model["preprocessing_strategy"], "clustering_features": model["clustering_features"]}


@router.get("/model", response_model=ModelResponse)
def model() -> dict:
    _, data = load_final()
    return {"algorithm": data["algorithm"], "k": data["k"], "preprocessing_strategy": data["preprocessing_strategy"], "clustering_features": data["clustering_features"], "random_state": data["random_state"], "n_init": data["n_init"], "evaluation_metrics": {"silhouette_score": data["silhouette_score"], "davies_bouldin_score": data["davies_bouldin_score"], "calinski_harabasz_score": data["calinski_harabasz_score"]}, "validation_summary": data["validation_summary"], "model_rationale": data["selected_model_rationale"], "sensitivity_model": data["sensitivity_model_information"]}


@router.get("/segments", response_model=list[SegmentSummary])
def segments() -> list[dict]:
    summaries, _ = segment_analytics(load_final()[0])
    return summaries


@router.get("/segments/distributions", response_model=SegmentDistributionsResponse)
def distributions_by_segment() -> dict:
    return segment_distribution_summary()


@router.get("/segments/{segment_id}", response_model=SegmentDetail)
def segment_detail(segment_id: int) -> dict:
    _, details = segment_analytics(load_final()[0])
    if segment_id not in details:
        raise HTTPException(status_code=404, detail=f"Segment {segment_id} was not found.")
    return details[segment_id]


@router.get("/customers", response_model=CustomersResponse)
def customers(segment_id: int | None = None, country: str | None = None, limit: int = Query(100, ge=1, le=10000), offset: int = Query(0, ge=0)) -> dict:
    data, _ = load_final()
    if segment_id is not None:
        data = data[data["SegmentID"] == segment_id]
    if country is not None:
        data = data[data["Country"].str.casefold() == country.casefold()]
    total = len(data)
    page = data.iloc[offset:offset + limit].copy()
    for column in ["CustomerID", "SegmentID", "Recency", "Frequency", "TotalItems", "UniqueProducts", "CustomerLifetimeDays"]:
        page[column] = page[column].astype(int)
    return {"total": total, "limit": limit, "offset": offset, "customers": page.to_dict(orient="records")}


@router.get("/model/comparison", response_model=list[ModelComparisonItem])
def model_comparison() -> list[dict]:
    data = pd.read_csv(project_root() / "data/experiments/algorithm_comparison/algorithm_comparison.csv")
    selected = data[((data["algorithm"] == "K-Means") & data["configuration"].isin(["k=3", "k=4"])) | ((data["algorithm"] == "Hierarchical") & data["configuration"].str.startswith(("k=3", "k=4"))) | ((data["algorithm"] == "DBSCAN") & (data["eps"] == 0.5) & (data["min_samples"] == 20))]
    return [{"algorithm": row.algorithm, "configuration": row.configuration, "silhouette_score": float(row.silhouette_score), "davies_bouldin": float(row.davies_bouldin), "calinski_harabasz": float(row.calinski_harabasz), "coverage_percentage": float(100 - row.noise_percentage), "cluster_count": int(row.n_clusters), "noise_percentage": float(row.noise_percentage)} for row in selected.itertuples(index=False)]


@router.get("/methodology", response_model=list[MethodologyStage])
def methodology() -> list[dict]:
    summaries = [
        ("Dataset", "UCI Online Retail II workbook with 1,067,371 transaction rows across two sheets."),
        ("Cleaning", "Exact duplicates, anonymous customers, cancellations, invalid dates, nonpositive quantities, and nonpositive prices were excluded; 779,425 transactions remained."),
        ("Feature engineering", "Transactions were aggregated into customer-level recency, frequency, value, item, product, order, and lifetime measures."),
        ("Exploratory analysis", "Distributions, skew, correlations, country imbalance, and retained extreme values informed feature selection."),
        ("Preprocessing", "Frequency, MonetaryValue, and UniqueProducts use log1p; five selected features then use StandardScaler."),
        ("K-Means experiments", "Controlled k and preprocessing comparisons used deterministic seeds and n_init=20."),
        ("Cluster profiling", "Assignments were interpreted through original-unit medians and means rather than scaled values."),
        ("Algorithm comparison", "K-Means, Ward hierarchical clustering, and DBSCAN were compared on the same matrix."),
        ("Final validation", "Twenty 80% subsamples and a TotalItems substitution tested stability and feature sensitivity."),
        ("Final model selection", "K-Means k=3 was selected for full coverage, internal quality, stability, interpretability, and parsimony; k=4 remains a sensitivity model."),
    ]
    return [{"stage": index, "name": name, "summary": summary} for index, (name, summary) in enumerate(summaries, 1)]


@router.get("/dataset", response_model=DatasetResponse)
def dataset() -> dict:
    return dataset_summary()


@router.get("/eda/distributions", response_model=DistributionResponse)
def eda_distributions(feature: str = Query(...)) -> dict:
    try:
        return distribution(feature)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.get("/eda/correlations", response_model=CorrelationsResponse)
def eda_correlations() -> dict:
    return correlation_summary()


@router.get("/eda/outliers", response_model=OutliersResponse)
def eda_outliers() -> dict:
    return outlier_summary()


@router.get("/model/validation", response_model=ModelValidationResponse)
def final_model_validation() -> dict:
    return validation_summary()
