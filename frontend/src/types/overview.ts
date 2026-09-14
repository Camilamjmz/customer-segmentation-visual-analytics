export interface OverviewResponse {
  original_transaction_count: number
  cleaned_transaction_count: number
  final_customer_count: number
  country_count: number
  final_segment_count: number
  selected_algorithm: string
  selected_k: number
  preprocessing_strategy: string
  clustering_features: string[]
}

export interface ModelResponse {
  algorithm: string
  k: number
  preprocessing_strategy: string
  clustering_features: string[]
  random_state: number
  n_init: number
  evaluation_metrics: {
    silhouette_score: number
    davies_bouldin_score: number
    calinski_harabasz_score: number
  }
  validation_summary: Record<string, number | boolean>
  model_rationale: string
  sensitivity_model: { k?: number; role?: string; [key: string]: unknown }
}

export interface SegmentSummary {
  SegmentID: number
  SegmentName: string
  customer_count: number
  customer_percentage: number
  median_profile: Record<string, number>
  key_insights: string[]
}
