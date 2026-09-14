# Read-Only Analytics API

The API serves frozen segmentation artifacts and calculated descriptive analytics. It does not fit models during requests, write customer data, or generate charts.

| Endpoint | Purpose | Main response |
|---|---|---|
| `GET /health` | Service availability | Status and service name |
| `GET /api/overview` | Dashboard headline totals | Transaction, customer, country, segment, algorithm, and feature metadata |
| `GET /api/model` | Final model panel | Configuration, metrics, validation, rationale, and k=4 sensitivity information |
| `GET /api/segments` | Segment summary charts and cards | Counts, percentages, median profiles, and deterministic insights |
| `GET /api/segments/{segment_id}` | Segment detail view | Medians, means, population comparison, insights, notes, and limitations |
| `GET /api/customers` | Customer table and Plotly tooltips | Complete customer behavior records with pagination |
| `GET /api/model/comparison` | Algorithm comparison view | Verified metrics, coverage, clusters, and DBSCAN noise |
| `GET /api/methodology` | Methodology page | Ten concise research stages |
| `GET /api/dataset` | Dataset and preparation page | Verified counts, dates, sheet summaries, removal reasons, countries, and feature definitions |
| `GET /api/eda/distributions?feature=...` | Feature distribution explorer | Descriptive statistics, histogram bins, skewness, and applicable log1p histogram |
| `GET /api/eda/correlations` | Feature relationship analysis | Pearson matrix, strongest pairs, and deterministic interpretation metadata |
| `GET /api/eda/outliers` | Outlier analysis | Tukey bounds, counts, percentages, and representative extreme customers |
| `GET /api/segments/distributions` | Segment boxplots | Original-unit quartiles, means, observed ranges, whiskers, and outlier counts |
| `GET /api/model/validation` | Final-model validation view | k=3 and k=4 initialization, subsampling, sensitivity, quality, balance, coverage, and parsimony evidence |

`/api/customers` accepts `segment_id`, case-insensitive exact `country`, `limit`, and `offset`. The default limit is 100 and the explicit maximum is 10,000, allowing the future frontend to request full visualization data deliberately.

The frontend should use overview and model responses for summary panels, segments for comparison charts, segment detail for explanatory sections, and customers for tables or interactive Plotly traces. All insight text comes from deterministic comparisons with calculated population medians. Responses do not expose file paths, NaN, infinity, or Python-specific objects.

The distribution endpoint accepts only `Recency`, `Frequency`, `MonetaryValue`, `UniqueProducts`, or `CustomerLifetimeDays`. Invalid feature names receive HTTP 422. Histogram counts are computed from the complete verified customer table; no arbitrary customer sample is returned. Outlier and segment-distribution endpoints use the Tukey 1.5 × IQR convention, with whiskers defined as the most extreme observed values inside those bounds.
