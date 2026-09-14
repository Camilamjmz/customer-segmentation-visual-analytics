import { getJson } from './api'
import type { CorrelationsResponse, DistributionResponse, EdaFeature, OutliersResponse } from '../types/eda'
export const getDistribution = (feature: EdaFeature, signal?: AbortSignal) => getJson<DistributionResponse>(`/api/eda/distributions?feature=${encodeURIComponent(feature)}`, signal)
export const getCorrelations = (signal?: AbortSignal) => getJson<CorrelationsResponse>('/api/eda/correlations', signal)
export const getOutliers = (signal?: AbortSignal) => getJson<OutliersResponse>('/api/eda/outliers', signal)
