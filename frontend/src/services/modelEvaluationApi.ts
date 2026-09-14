import { getJson } from './api'
import type { ComparisonItem, ValidationResponse } from '../types/modelEvaluation'
export const getModelComparison = (signal?:AbortSignal) => getJson<ComparisonItem[]>('/api/model/comparison',signal)
export const getModelValidation = (signal?:AbortSignal) => getJson<ValidationResponse>('/api/model/validation',signal)
