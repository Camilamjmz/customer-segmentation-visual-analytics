import { Link } from 'react-router-dom'
import { AnalyticalFigure } from '../components/analysis/AnalyticalFigure'
import { SegmentDistributionChart } from '../components/charts/SegmentDistributionChart'
import { PageHeader } from '../components/layout/PageHeader'
import { DataState } from '../components/ui/DataState'
import { MetricCard } from '../components/ui/MetricCard'
import { Section } from '../components/ui/Section'
import { useApiResource } from '../hooks/useApiResource'
import { getModel, getOverview, getSegments } from '../services/overviewApi'
import type { SegmentSummary } from '../types/overview'
import { formatCurrency, formatDecimal, formatInteger, formatPercent } from '../utils/formatters'

function distributionFinding(segments: SegmentSummary[]) {
  const largest = [...segments].sort((a, b) => b.customer_percentage - a.customer_percentage)[0]
  const smallest = [...segments].sort((a, b) => a.customer_percentage - b.customer_percentage)[0]
  const difference = largest.customer_percentage - smallest.customer_percentage
  return `${largest.SegmentName} is the largest segment at ${formatPercent(largest.customer_percentage)}; it exceeds ${smallest.SegmentName}, the smallest segment, by ${difference.toFixed(1)} percentage points.`
}

function profileFinding(segments: SegmentSummary[]) {
  const inactive = segments.find((segment) => segment.SegmentName === 'Inactive Low-Activity')
  const recent = segments.find((segment) => segment.SegmentName === 'Recent High-Activity')
  if (!inactive || !recent) return 'The segment medians describe distinct levels of customer recency, frequency, value, product breadth, and lifetime.'
  return `${recent.SegmentName} customers have a median frequency of ${formatInteger(recent.median_profile.Frequency)} orders and median Recency of ${formatInteger(recent.median_profile.Recency)} days, compared with ${formatInteger(inactive.median_profile.Frequency)} order and ${formatInteger(inactive.median_profile.Recency)} days for ${inactive.SegmentName}.`
}

export function OverviewPage() {
  const overview = useApiResource(getOverview)
  const model = useApiResource(getModel)
  const segments = useApiResource(getSegments)

  return <>
    <PageHeader eyebrow="Research overview" title="Customer Segmentation Overview" description="Retail transaction data was transformed into customer-level behavioral profiles and segmented using a validated K-Means model." />

    <section className="overview-kpis" aria-labelledby="overview-kpis-title">
      <h2 id="overview-kpis-title" className="sr-only">Dataset summary</h2>
      {overview.loading && <DataState state="loading" message="Loading dataset summary from the analytics API." />}
      {overview.error && <DataState state="error" message="The dataset summary could not be loaded." onRetry={overview.retry} />}
      {overview.data && <div className="metric-grid"><MetricCard label="Original transactions" value={formatInteger(overview.data.original_transaction_count)} /><MetricCard label="Cleaned transactions" value={formatInteger(overview.data.cleaned_transaction_count)} /><MetricCard label="Customers" value={formatInteger(overview.data.final_customer_count)} /><MetricCard label="Final segments" value={formatInteger(overview.data.final_segment_count)} /></div>}
    </section>

    <div className="overview-primary-grid">
      <div>{segments.loading && <Section title="Segment distribution"><DataState state="loading" message="Loading segment counts and percentages." /></Section>}{segments.error && <Section title="Segment distribution"><DataState state="error" message="Segment distribution data is unavailable." onRetry={segments.retry} /></Section>}{segments.data && <AnalyticalFigure id="segment-distribution" title="Segment distribution" description="Customer count and share of the complete segmented population." keyFinding={distributionFinding(segments.data)} interpretation="The three groups are reasonably balanced, so the final model does not depend on a very small customer segment." howToRead="Bar length represents customer count. Each direct label also shows the segment's share of all customers." limitation="Segment size describes prevalence, not customer quality or business value."><SegmentDistributionChart segments={segments.data} /></AnalyticalFigure>}</div>

      <Section title="Final model" description="Frozen model configuration and evaluation evidence.">
        {model.loading && <DataState state="loading" message="Loading final model details." />}
        {model.error && <DataState state="error" message="The final model summary is unavailable." onRetry={model.retry} />}
        {model.data && <div className="model-summary"><dl className="model-definition-list"><div><dt>Algorithm</dt><dd>{model.data.algorithm}</dd></div><div><dt>Clusters</dt><dd>k = {model.data.k}</dd></div><div><dt>Preprocessing</dt><dd>{model.data.preprocessing_strategy}</dd></div><div><dt>Customer coverage</dt><dd>{model.data.validation_summary.full_customer_coverage ? '100%' : 'Partial'}</dd></div></dl><div className="model-metrics"><div><span>Silhouette Score <small>higher is better</small></span><strong>{formatDecimal(model.data.evaluation_metrics.silhouette_score)}</strong></div><div><span>Davies-Bouldin Index <small>lower is better</small></span><strong>{formatDecimal(model.data.evaluation_metrics.davies_bouldin_score)}</strong></div><div><span>Calinski-Harabasz Score <small>higher is better</small></span><strong>{formatDecimal(model.data.evaluation_metrics.calinski_harabasz_score, 1)}</strong></div></div><div className="evidence-note"><p className="evidence-note__label">Selection evidence</p><p>{model.data.model_rationale}</p>{model.data.sensitivity_model.k && <p className="sensitivity-note">k={model.data.sensitivity_model.k} was retained as a sensitivity model. {model.data.sensitivity_model.role}</p>}</div></div>}
      </Section>
    </div>

    <Section title="Segment profile summary" description="Original-unit medians provide a concise behavioral comparison without combining incompatible measures on one axis.">
      {segments.loading && <DataState state="loading" message="Loading behavioral profiles." />}
      {segments.error && <DataState state="error" message="Behavioral profiles are unavailable." onRetry={segments.retry} />}
      {segments.data && <><div className="profile-table-wrap"><table className="profile-table"><thead><tr><th scope="col">Segment</th><th scope="col">Customers</th><th scope="col">Recency</th><th scope="col">Frequency</th><th scope="col">Monetary value</th><th scope="col">Unique products</th><th scope="col">Lifetime</th></tr></thead><tbody>{[...segments.data].sort((a, b) => a.SegmentID - b.SegmentID).map((segment) => <tr key={segment.SegmentID} className={`segment-row segment-row--${segment.SegmentID}`}><th scope="row"><span className="segment-key"><i aria-hidden="true" />{segment.SegmentName}</span></th><td>{formatInteger(segment.customer_count)} <small>{formatPercent(segment.customer_percentage)}</small></td><td>{formatInteger(segment.median_profile.Recency)} days</td><td>{formatInteger(segment.median_profile.Frequency)}</td><td>{formatCurrency(segment.median_profile.MonetaryValue)}</td><td>{formatInteger(segment.median_profile.UniqueProducts)}</td><td>{formatInteger(segment.median_profile.CustomerLifetimeDays)} days</td></tr>)}</tbody></table></div><div className="profile-finding"><p className="key-finding__label">Key finding</p><p>{profileFinding(segments.data)}</p></div></>}
    </Section>

    <Section title="Research conclusion" description="Evidence from the frozen model and final customer assignments." tone="quiet">
      {model.data && segments.data ? <div className="research-conclusion"><p>{model.data.algorithm} with k={model.data.k} separates the complete customer population into {segments.data.length} interpretable behavioral groups. The profiles distinguish inactive low-activity, developing or moderate, and recent high-activity customers, supporting comparison of purchasing behavior while retaining full customer coverage.</p><Link className="navigation-action" to="/segmentation">Explore customer segments</Link></div> : <DataState state={model.error || segments.error ? 'error' : 'loading'} message={model.error || segments.error ? 'The conclusion requires both model and segment evidence.' : 'Loading supporting research evidence.'} />}
    </Section>
  </>
}
