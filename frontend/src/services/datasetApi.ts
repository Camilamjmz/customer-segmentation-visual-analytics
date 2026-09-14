import { getJson } from './api'
import type { DatasetResponse } from '../types/dataset'

export const getDataset = (signal?: AbortSignal) => getJson<DatasetResponse>('/api/dataset', signal)
