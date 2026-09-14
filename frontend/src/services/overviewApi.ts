import { getJson } from './api'
import type { ModelResponse, OverviewResponse, SegmentSummary } from '../types/overview'

export const getOverview = (signal?: AbortSignal) => getJson<OverviewResponse>('/api/overview', signal)
export const getModel = (signal?: AbortSignal) => getJson<ModelResponse>('/api/model', signal)
export const getSegments = (signal?: AbortSignal) => getJson<SegmentSummary[]>('/api/segments', signal)
