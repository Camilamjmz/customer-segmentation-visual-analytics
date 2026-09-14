import { lazy, Suspense } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from './components/layout/AppShell'
import { DataState } from './components/ui/DataState'

const OverviewPage = lazy(() => import('./pages/OverviewPage').then((module) => ({ default: module.OverviewPage })))
const DatasetPage = lazy(() => import('./pages/DatasetPage').then((module) => ({ default: module.DatasetPage })))
const ExploratoryAnalysisPage = lazy(() => import('./pages/ExploratoryAnalysisPage').then((module) => ({ default: module.ExploratoryAnalysisPage })))
const SegmentationPage = lazy(() => import('./pages/SegmentationPage').then((module) => ({ default: module.SegmentationPage })))
const ModelEvaluationPage = lazy(() => import('./pages/ModelEvaluationPage').then((module) => ({ default: module.ModelEvaluationPage })))
const MethodologyPage = lazy(() => import('./pages/MethodologyPage').then((module) => ({ default: module.MethodologyPage })))

function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<Navigate to="/overview" replace />} />
        <Route path="overview" element={<Suspense fallback={<DataState state="loading" message="Loading the overview."/>}><OverviewPage /></Suspense>} />
        <Route path="dataset" element={<Suspense fallback={<DataState state="loading" message="Loading the dataset page."/>}><DatasetPage /></Suspense>} />
        <Route path="exploratory-analysis" element={<Suspense fallback={<DataState state="loading" message="Loading exploratory analysis."/>}><ExploratoryAnalysisPage /></Suspense>} />
        <Route path="segmentation" element={<Suspense fallback={<DataState state="loading" message="Loading segmentation analysis."/>}><SegmentationPage /></Suspense>} />
        <Route path="model-evaluation" element={<Suspense fallback={<DataState state="loading" message="Loading model evaluation."/>}><ModelEvaluationPage /></Suspense>} />
        <Route path="methodology" element={<Suspense fallback={<DataState state="loading" message="Loading methodology."/>}><MethodologyPage /></Suspense>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}

export default App
