export type EdaFeature = 'Recency' | 'Frequency' | 'MonetaryValue' | 'UniqueProducts' | 'CustomerLifetimeDays'
export interface Histogram { bin_edges: number[]; counts: number[] }
export interface DistributionResponse { feature: EdaFeature; count: number; minimum: number; maximum: number; mean: number; median: number; standard_deviation: number; quartiles: { q1: number; q2: number; q3: number }; histogram: Histogram; skewness: number; log_display_recommended: boolean; log1p_histogram: Histogram | null }
export interface CorrelationPair { feature_a: string; feature_b: string; correlation: number; absolute_correlation: number }
export interface CorrelationsResponse { features: string[]; matrix: number[][]; strongest_correlation_pairs: CorrelationPair[]; interpretation: { method: string; guidance: string; primary_feature_note: string } }
export interface ExtremeCustomer { CustomerID: number; value: number }
export interface OutlierFeature { feature: string; q1: number; q3: number; iqr: number; lower_bound: number; upper_bound: number; outlier_count: number; outlier_percentage: number; representative_extreme_customers: ExtremeCustomer[] }
export interface OutliersResponse { method: string; features: OutlierFeature[]; interpretation: string }
