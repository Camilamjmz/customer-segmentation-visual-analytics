import { getJson } from './api'
import type { CustomersResponse, SegmentDetail, SegmentDistributionsResponse } from '../types/segmentation'
export const getAllCustomers = (signal?: AbortSignal) => getJson<CustomersResponse>('/api/customers?limit=10000&offset=0', signal)
export const getSegmentDetail = (segmentId: number, signal?: AbortSignal) => getJson<SegmentDetail>(`/api/segments/${segmentId}`, signal)
export const getSegmentCustomers = (segmentId: number, offset: number, signal?: AbortSignal) => getJson<CustomersResponse>(`/api/customers?segment_id=${segmentId}&limit=10&offset=${offset}`, signal)
export const getSegmentDistributions = (signal?: AbortSignal) => getJson<SegmentDistributionsResponse>('/api/segments/distributions', signal)
