export interface WorkbookSheetSummary {
  sheet_name: string
  row_count: number
  minimum_date: string
  maximum_date: string
  unique_customer_count: number
  unique_country_count: number
}

export interface CountryCount {
  country: string
  customer_count: number
  customer_percentage: number
}

export interface CustomerFeatureDefinition {
  feature: string
  definition: string
  unit: string
  used_for_clustering: boolean
  transformation: string
}

export interface DatasetResponse {
  raw_transaction_count: number
  cleaned_transaction_count: number
  removed_records_by_reason: Record<string, number>
  raw_minimum_transaction_date: string
  raw_maximum_transaction_date: string
  workbook_sheet_summary: WorkbookSheetSummary[]
  final_customer_count: number
  country_count: number
  top_country_counts: CountryCount[]
  customer_feature_dictionary: CustomerFeatureDefinition[]
}
