"""Reusable preprocessing for customer clustering experiments."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Sequence

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype
from sklearn.preprocessing import RobustScaler, StandardScaler


PRIMARY_FEATURES = (
    "Recency",
    "Frequency",
    "MonetaryValue",
    "UniqueProducts",
    "CustomerLifetimeDays",
)
LOG_FEATURES = frozenset({"Frequency", "MonetaryValue", "UniqueProducts"})
Strategy = Literal["standard", "log_standard", "log_robust"]


class PreprocessingValidationError(ValueError):
    """Raised when input data cannot be safely preprocessed."""


@dataclass(frozen=True)
class PreprocessingResult:
    """Customer identifiers and their aligned transformed feature matrix."""

    customer_ids: pd.Series
    matrix: pd.DataFrame
    strategy: Strategy

    def to_dataframe(self) -> pd.DataFrame:
        """Return an export-ready copy with CustomerID as the first column."""
        output = self.matrix.copy(deep=True)
        output.insert(0, "CustomerID", self.customer_ids.to_numpy(copy=True))
        return output


def load_customer_features(path: str | Path) -> pd.DataFrame:
    """Load customer features without changing the source file."""
    return pd.read_csv(Path(path))


def preprocess_customer_features(
    customers: pd.DataFrame,
    strategy: Strategy,
    features: Sequence[str] = PRIMARY_FEATURES,
    log_features: Sequence[str] | None = None,
) -> PreprocessingResult:
    """Validate and transform customer features for a future clustering run."""
    if strategy not in {"standard", "log_standard", "log_robust"}:
        raise PreprocessingValidationError(f"Unknown preprocessing strategy: {strategy}")

    requested = list(features)
    requested_log_features = (
        set(LOG_FEATURES).intersection(requested)
        if log_features is None
        else set(log_features)
    )
    if not requested:
        raise PreprocessingValidationError("At least one clustering feature is required.")
    if len(requested) != len(set(requested)):
        raise PreprocessingValidationError("Clustering feature names must be unique.")
    invalid_log_features = sorted(requested_log_features.difference(requested))
    if invalid_log_features:
        raise PreprocessingValidationError(
            "Log-transformed features must be requested clustering features: "
            + ", ".join(invalid_log_features)
        )

    required = ["CustomerID", *requested]
    missing_columns = [name for name in required if name not in customers.columns]
    if missing_columns:
        names = ", ".join(missing_columns)
        raise PreprocessingValidationError(f"Missing required columns: {names}")

    nonnumeric = [name for name in requested if not is_numeric_dtype(customers[name])]
    if nonnumeric:
        names = ", ".join(nonnumeric)
        raise PreprocessingValidationError(
            f"Clustering features must be numeric. Invalid columns: {names}"
        )

    customer_ids = customers["CustomerID"].copy(deep=True).reset_index(drop=True)
    matrix = (
        customers.loc[:, requested]
        .copy(deep=True)
        .reset_index(drop=True)
        .astype(float)
    )

    if customer_ids.isna().any():
        raise PreprocessingValidationError("CustomerID contains missing values.")
    if matrix.isna().any().any():
        bad = matrix.columns[matrix.isna().any()].tolist()
        raise PreprocessingValidationError(
            f"Clustering features contain missing values: {', '.join(bad)}"
        )
    if not np.isfinite(matrix.to_numpy(dtype=float)).all():
        raise PreprocessingValidationError(
            "Clustering features contain infinite values."
        )

    if strategy in {"log_standard", "log_robust"}:
        log_columns = [name for name in requested if name in requested_log_features]
        negative_columns = [name for name in log_columns if (matrix[name] < 0).any()]
        if negative_columns:
            names = ", ".join(negative_columns)
            raise PreprocessingValidationError(
                f"log1p features must be nonnegative. Invalid columns: {names}"
            )
        matrix.loc[:, log_columns] = np.log1p(matrix.loc[:, log_columns])

    scaler = RobustScaler() if strategy == "log_robust" else StandardScaler()
    transformed = pd.DataFrame(
        scaler.fit_transform(matrix),
        columns=requested,
        index=matrix.index,
    )

    if len(transformed) != len(customers):
        raise RuntimeError("Preprocessing unexpectedly changed the row count.")
    if transformed.isna().any().any():
        raise RuntimeError("Preprocessing produced missing values.")
    if not np.isfinite(transformed.to_numpy()).all():
        raise RuntimeError("Preprocessing produced infinite values.")

    return PreprocessingResult(
        customer_ids=customer_ids,
        matrix=transformed,
        strategy=strategy,
    )
