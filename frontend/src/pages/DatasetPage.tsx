import { AnalyticalFigure } from '../components/analysis/AnalyticalFigure'
import { CountryDistributionChart, RemovalReasonsChart } from '../components/charts/DatasetBarCharts'
import { PageHeader } from '../components/layout/PageHeader'
import { DataState } from '../components/ui/DataState'
import { MetricCard } from '../components/ui/MetricCard'
import { Section } from '../components/ui/Section'
import { useApiResource } from '../hooks/useApiResource'
import { getDataset } from '../services/datasetApi'
import type { DatasetResponse } from '../types/dataset'
import { formatDate, formatInteger, formatPercent } from '../utils/formatters'

const readableReason = (key: string) => key === 'missing_customer_id' ? 'Missing Customer ID' : key.replaceAll('_', ' ')

function removalEvidence(data: DatasetResponse) {
  const rows = Object.entries(data.removed_records_by_reason).sort((a, b) => b[1] - a[1])
  const total = rows.reduce((sum, [, count]) => sum + count, 0)
  const [largest, second] = rows
  return {
    total,
    finding: `${readableReason(largest[0])} was the largest source of removed records, accounting for ${formatPercent(largest[1] / total * 100)} of all ${formatInteger(total)} removals.`,
    interpretation: `${formatPercent(total / data.raw_transaction_count * 100)} of raw transaction rows were removed by the sequential cleaning pipeline. ${formatInteger(second[1])} records were removed at the ${readableReason(second[0]).toLowerCase()} stage.`,
  }
}

function countryFinding(data: DatasetResponse) {
  const largest = [...data.top_country_counts].sort((a, b) => b.customer_count - a.customer_count)[0]
  return `${largest.country} is the largest represented customer country with ${formatInteger(largest.customer_count)} customers, or ${formatPercent(largest.customer_percentage)} of final customer profiles.`
}

export function DatasetPage() {
  const dataset = useApiResource(getDataset)
  return <><PageHeader eyebrow="Data foundation" title="Dataset & Preparation" description="The original retail transaction data was validated, cleaned, and aggregated into one behavioral profile per customer." />{dataset.loading && <div className="dataset-page-state"><DataState state="loading" message="Loading verified dataset and preparation metadata." /></div>}{dataset.error && <div className="dataset-page-state"><DataState state="error" message="The dataset preparation summary could not be loaded." onRetry={dataset.retry} /></div>}{dataset.data && <DatasetContent data={dataset.data} />}</>
}

function DatasetContent({ data }: { data: DatasetResponse }) {
  const removal = removalEvidence(data)
  return <div className="dataset-content">
    <section className="dataset-summary" aria-labelledby="dataset-summary-title"><h2 id="dataset-summary-title" className="sr-only">Dataset summary</h2><div className="metric-grid"><MetricCard label="Raw transactions" value={formatInteger(data.raw_transaction_count)} /><MetricCard label="Cleaned transactions" value={formatInteger(data.cleaned_transaction_count)} /><MetricCard label="Final customers" value={formatInteger(data.final_customer_count)} /><MetricCard label="Countries" value={formatInteger(data.country_count)} /></div><div className="date-range"><div><span>Observation period</span><strong>{formatDate(data.raw_minimum_transaction_date)} – {formatDate(data.raw_maximum_transaction_date)}</strong></div><p>Raw transaction coverage across both workbook sheets.</p></div></section>
    <Section title="Transaction-to-customer preparation" description="A conceptual view of how transaction records became comparable customer-level observations."><ol className="preparation-flow"><li><span>01</span><div><p>Raw transaction rows</p><strong>{formatInteger(data.raw_transaction_count)}</strong><small>Purchase-line records from the two source sheets.</small></div></li><li><span>02</span><div><p>Cleaning and validation</p><strong>{formatInteger(removal.total)} removed</strong><small>Duplicates, anonymous customers, cancellations, invalid dates, and unusable values were checked sequentially.</small></div></li><li><span>03</span><div><p>Valid transaction rows</p><strong>{formatInteger(data.cleaned_transaction_count)}</strong><small>Positive, identified, non-cancelled purchases retained for analysis.</small></div></li><li><span>04</span><div><p>Customer aggregation</p><strong>One row per customer</strong><small>Transactions were grouped into behavioral summaries.</small></div></li><li><span>05</span><div><p>Customer profiles</p><strong>{formatInteger(data.final_customer_count)}</strong><small>Comparable observations prepared for clustering.</small></div></li></ol></Section>
    <AnalyticalFigure id="removal-reasons" title="Records removed by cleaning reason" description="Sequential removal counts document how the raw workbook was converted into valid purchase activity." keyFinding={removal.finding} interpretation={removal.interpretation} howToRead="Bars are ordered by records removed. Zero-length categories remain listed because they document checks that were applied but removed no additional records at that stage." limitation="Removal counts follow the sequential cleaning pipeline. A row may satisfy multiple invalid conditions, but it is counted only at the first stage where it was removed."><RemovalReasonsChart reasons={data.removed_records_by_reason} /></AnalyticalFigure>
    <Section title="Workbook source summary" description="The original workbook contains two transaction sheets with overlapping time coverage.">{data.workbook_sheet_summary.length ? <div className="research-table-wrap"><table className="research-table"><thead><tr><th scope="col">Sheet</th><th scope="col">Transaction rows</th><th scope="col">Date range</th><th scope="col">Customers</th><th scope="col">Countries</th></tr></thead><tbody>{data.workbook_sheet_summary.map((sheet) => <tr key={sheet.sheet_name}><th scope="row">{sheet.sheet_name}</th><td>{formatInteger(sheet.row_count)}</td><td>{formatDate(sheet.minimum_date)} – {formatDate(sheet.maximum_date)}</td><td>{formatInteger(sheet.unique_customer_count)}</td><td>{formatInteger(sheet.unique_country_count)}</td></tr>)}</tbody></table></div> : <DataState state="empty" message="Workbook sheet metadata is not available." />}</Section>
    {data.top_country_counts.length ? <AnalyticalFigure id="country-distribution" title="Leading customer countries" description="Customer counts for the countries returned by the dataset summary, ranked from largest to smallest." keyFinding={countryFinding(data)} interpretation="The customer population is geographically concentrated. Country was therefore retained for descriptive filtering but excluded from the numerical clustering feature space." howToRead="Bar length represents customer count. Direct labels and tooltips show each country's percentage of all final customer profiles." limitation={`The endpoint returns the leading ${data.top_country_counts.length} countries rather than a complete ranked list. The chart does not construct an Other category from unreturned country rows.`}><CountryDistributionChart countries={data.top_country_counts} /></AnalyticalFigure> : <Section title="Leading customer countries"><DataState state="empty" message="Country distribution data is not available." /></Section>}
    <Section title="Customer feature dictionary" description="All engineered customer variables remain documented, including those not selected for the final clustering model.">{data.customer_feature_dictionary.length ? <div className="research-table-wrap"><table className="research-table feature-table"><thead><tr><th scope="col">Feature</th><th scope="col">Definition</th><th scope="col">Unit</th><th scope="col">Used in final clustering</th><th scope="col">Transformation</th></tr></thead><tbody>{data.customer_feature_dictionary.map((feature) => <tr key={feature.feature} className={feature.used_for_clustering ? 'feature-selected' : undefined}><th scope="row">{feature.feature}</th><td>{feature.definition}</td><td>{feature.unit}</td><td><span className="selection-status">{feature.used_for_clustering ? 'Selected' : 'Not selected'}</span></td><td>{feature.transformation}</td></tr>)}</tbody></table></div> : <DataState state="empty" message="Customer feature definitions are not available." />}</Section>
    <Section title="Why customer aggregation matters" description="The unit of analysis must match the segmentation question." tone="quiet"><div className="method-note"><p>Transaction rows are purchase events rather than independent customers. Customers who purchase frequently appear in many rows, so clustering raw transactions would give their behavior disproportionate influence and would describe transaction patterns instead of customer groups.</p><p>Aggregation creates one observation per customer. Recency, frequency, value, product breadth, order behavior, and lifetime can then be compared consistently across the full customer population.</p></div></Section>
  </div>
}
