"""Pydantic response models for the read-only analytics API."""

from typing import Any

from pydantic import BaseModel


class OverviewResponse(BaseModel):
    original_transaction_count: int
    cleaned_transaction_count: int
    final_customer_count: int
    country_count: int
    final_segment_count: int
    selected_algorithm: str
    selected_k: int
    preprocessing_strategy: str
    clustering_features: list[str]


class ModelResponse(BaseModel):
    algorithm: str
    k: int
    preprocessing_strategy: str
    clustering_features: list[str]
    random_state: int
    n_init: int
    evaluation_metrics: dict[str, float]
    validation_summary: dict[str, float | bool]
    model_rationale: str
    sensitivity_model: dict[str, Any]


class SegmentSummary(BaseModel):
    SegmentID: int
    SegmentName: str
    customer_count: int
    customer_percentage: float
    median_profile: dict[str, float]
    key_insights: list[str]


class SegmentDetail(SegmentSummary):
    mean_profile: dict[str, float]
    population_medians: dict[str, float]
    comparison_with_population: dict[str, str]
    key_characteristics: list[str]
    interpretation_notes: list[str]
    limitations: list[str]


class CustomerRecord(BaseModel):
    CustomerID: int
    SegmentID: int
    SegmentName: str
    Country: str
    Recency: int
    Frequency: int
    MonetaryValue: float
    TotalItems: int
    UniqueProducts: int
    AverageOrderValue: float
    AverageItemsPerOrder: float
    CustomerLifetimeDays: int


class CustomersResponse(BaseModel):
    total: int
    limit: int
    offset: int
    customers: list[CustomerRecord]


class ModelComparisonItem(BaseModel):
    algorithm: str
    configuration: str
    silhouette_score: float
    davies_bouldin: float
    calinski_harabasz: float
    coverage_percentage: float
    cluster_count: int
    noise_percentage: float


class MethodologyStage(BaseModel):
    stage: int
    name: str
    summary: str


class DatasetResponse(BaseModel):
    raw_transaction_count: int
    cleaned_transaction_count: int
    removed_records_by_reason: dict[str, int]
    raw_minimum_transaction_date: str
    raw_maximum_transaction_date: str
    workbook_sheet_summary: list[dict[str, Any]]
    final_customer_count: int
    country_count: int
    top_country_counts: list[dict[str, Any]]
    customer_feature_dictionary: list[dict[str, Any]]


class DistributionResponse(BaseModel):
    feature: str
    count: int
    minimum: float
    maximum: float
    mean: float
    median: float
    standard_deviation: float
    quartiles: dict[str, float]
    histogram: dict[str, list[float] | list[int]]
    skewness: float
    log_display_recommended: bool
    log1p_histogram: dict[str, list[float] | list[int]] | None


class CorrelationsResponse(BaseModel):
    features: list[str]
    matrix: list[list[float]]
    strongest_correlation_pairs: list[dict[str, Any]]
    interpretation: dict[str, str]


class OutliersResponse(BaseModel):
    method: str
    features: list[dict[str, Any]]
    interpretation: str


class SegmentDistributionsResponse(BaseModel):
    whisker_method: str
    segments: list[dict[str, Any]]


class ModelValidationResponse(BaseModel):
    candidates: list[dict[str, Any]]
    recommended_k: int
    recommendation_rationale: str
