import type { SegmentSummary } from './overview'

export interface CustomerRecord { CustomerID: number; SegmentID: number; SegmentName: string; Country: string; Recency: number; Frequency: number; MonetaryValue: number; TotalItems: number; UniqueProducts: number; AverageOrderValue: number; AverageItemsPerOrder: number; CustomerLifetimeDays: number }
export interface CustomersResponse { total: number; limit: number; offset: number; customers: CustomerRecord[] }
export interface SegmentDetail extends SegmentSummary { mean_profile: Record<string, number>; population_medians: Record<string, number>; comparison_with_population: Record<string, string>; key_characteristics: string[]; interpretation_notes: string[]; limitations: string[] }
export interface FeatureDistribution { feature: string; minimum: number; q1: number; median: number; q3: number; maximum: number; mean: number; whisker_low: number; whisker_high: number; outlier_count: number }
export interface SegmentDistribution { SegmentID: number; SegmentName: string; customer_count: number; features: FeatureDistribution[] }
export interface SegmentDistributionsResponse { whisker_method: string; segments: SegmentDistribution[] }
