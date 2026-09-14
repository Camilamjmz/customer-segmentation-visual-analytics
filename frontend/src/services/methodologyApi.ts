import { getJson } from './api'
import type { MethodologyStage } from '../types/methodology'
export const getMethodology = (signal?:AbortSignal) => getJson<MethodologyStage[]>('/api/methodology',signal)
