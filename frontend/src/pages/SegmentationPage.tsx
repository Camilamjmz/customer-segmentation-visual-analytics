import { useCallback, useMemo, useState } from 'react'
import { AnalyticalFigure } from '../components/analysis/AnalyticalFigure'
import { CustomerScatter, ProfileHeatmap, QuartileRangeChart } from '../components/charts/SegmentationCharts'
import { SegmentDistributionChart } from '../components/charts/SegmentDistributionChart'
import { PageHeader } from '../components/layout/PageHeader'
import { DataState } from '../components/ui/DataState'
import { FeatureSelector } from '../components/ui/FeatureSelector'
import { Section } from '../components/ui/Section'
import { useApiResource } from '../hooks/useApiResource'
import { getSegments } from '../services/overviewApi'
import { getAllCustomers, getSegmentCustomers, getSegmentDetail, getSegmentDistributions } from '../services/segmentationApi'
import { formatCurrency, formatDecimal, formatInteger, formatPercent } from '../utils/formatters'

const profileFeatures = ['Recency', 'Frequency', 'MonetaryValue', 'UniqueProducts', 'CustomerLifetimeDays'] as const
const distributionFeatures = ['Recency', 'Frequency', 'MonetaryValue', 'TotalItems', 'UniqueProducts', 'AverageOrderValue', 'AverageItemsPerOrder', 'CustomerLifetimeDays'] as const
const displayName = (name: string) => name.replace(/([a-z])([A-Z])/g, '$1 $2')
const displayValue = (name: string, amount: number) => name.includes('Value') ? formatCurrency(amount) : formatDecimal(amount, 1)

export function SegmentationPage() {
  const segments = useApiResource(getSegments)
  const customers = useApiResource(getAllCustomers)
  const distributions = useApiResource(getSegmentDistributions)
  const [scatterView, setScatterView] = useState<'frequency' | 'recency'>('frequency')
  const [segmentFilter, setSegmentFilter] = useState('all')
  const [country, setCountry] = useState('all')
  const [feature, setFeature] = useState<(typeof distributionFeatures)[number]>('MonetaryValue')
  const [selectedSegment, setSelectedSegment] = useState(0)
  const [offset, setOffset] = useState(0)
  const detail = useApiResource(useCallback((signal?: AbortSignal) => getSegmentDetail(selectedSegment, signal), [selectedSegment]))
  const examples = useApiResource(useCallback((signal?: AbortSignal) => getSegmentCustomers(selectedSegment, offset, signal), [selectedSegment, offset]))
  const countries = useMemo(() => [...new Set(customers.data?.customers.map(row => row.Country) ?? [])].sort(), [customers.data])
  const visible = useMemo(() => (customers.data?.customers ?? []).filter(row => (segmentFilter === 'all' || row.SegmentID === Number(segmentFilter)) && (country === 'all' || row.Country === country)), [customers.data, segmentFilter, country])
  const chooseSegment = (id: number) => { setSelectedSegment(id); setOffset(0) }
  return <>
    <PageHeader eyebrow="Final segmentation" title="Customer Segment Analysis" description={`The final K-Means model divides ${segments.data ? formatInteger(segments.data.reduce((sum, item) => sum + item.customer_count, 0)) : 'the complete population of'} customers into three behaviorally distinct segments based on purchasing activity, value, product diversity, and customer lifetime.`} />
    <div className="segmentation-page">
      {segments.loading && <DataState state="loading" message="Loading final segment summaries." />}
      {segments.error && <DataState state="error" message="Segment summaries are unavailable." onRetry={segments.retry} />}
      {segments.data && <div className="segment-summary-grid">{[...segments.data].sort((a,b)=>a.SegmentID-b.SegmentID).map(segment => <article className={`segment-summary segment-summary--${segment.SegmentID}`} key={segment.SegmentID}><h2>{segment.SegmentName}</h2><strong>{formatInteger(segment.customer_count)}</strong><span>{formatPercent(segment.customer_percentage)} of customers</span><dl><div><dt>Median recency</dt><dd>{formatInteger(segment.median_profile.Recency)} days</dd></div><div><dt>Median frequency</dt><dd>{formatInteger(segment.median_profile.Frequency)}</dd></div><div><dt>Median value</dt><dd>{formatCurrency(segment.median_profile.MonetaryValue)}</dd></div></dl></article>)}</div>}

      <div className="segmentation-two-column">
        {segments.data && <AnalyticalFigure id="segment-share" title="Customer distribution" description="Count and share of the complete segmented population." keyFinding="The three final groups retain meaningful customer coverage without a very small residual segment." interpretation="The final partition represents every customer in one of three substantial behavioral groups." howToRead="Longer bars represent more customers; direct labels show count and share." limitation="Size describes prevalence, not customer quality or profitability."><SegmentDistributionChart segments={segments.data}/></AnalyticalFigure>}
        {segments.data && detail.data && <AnalyticalFigure id="relative-profile" title="Relative median profile" description="Segment median divided by the complete-population median." keyFinding="Recent High-Activity has the strongest frequency, value, product breadth, and lifetime profile, alongside the lowest recency." interpretation="The ratios make behavioral differences comparable while preserving each feature's direction." howToRead="Values above 1 exceed the population median. For Recency, lower means more recent." limitation="A ratio is unavailable when the population median is zero."><ProfileHeatmap segments={segments.data} population={detail.data.population_medians}/></AnalyticalFigure>}
        {(detail.loading || detail.error) && <DataState state={detail.error ? 'error' : 'loading'} message={detail.error ? 'Relative profiles are unavailable.' : 'Loading population medians.'} onRetry={detail.error ? detail.retry : undefined}/>}
      </div>

      <Section title="Customer relationship explorer" description="Explore all customer assignments with local segment and country filters.">
        <div className="segmentation-controls"><FeatureSelector label="Relationship" options={['frequency','recency'] as const} value={scatterView} onChange={setScatterView}/><label className="select-label">Segment<select value={segmentFilter} onChange={e=>setSegmentFilter(e.target.value)}><option value="all">All segments</option>{segments.data?.map(s=><option key={s.SegmentID} value={s.SegmentID}>{s.SegmentName}</option>)}</select></label><label className="select-label">Country<select value={country} onChange={e=>setCountry(e.target.value)}><option value="all">All countries</option>{countries.map(item=><option key={item}>{item}</option>)}</select></label><button className="secondary-button" disabled={segmentFilter === 'all' && country === 'all'} onClick={()=>{setSegmentFilter('all');setCountry('all')}}>Clear filters</button></div>
        {customers.loading && <DataState state="loading" message="Loading customer assignments once for local exploration."/>}{customers.error && <DataState state="error" message="Customer assignments are unavailable." onRetry={customers.retry}/>}{customers.data && <><p className="result-count">{segmentFilter === 'all' && country === 'all' ? `Showing ${formatInteger(visible.length)} of ${formatInteger(customers.data.total)} customers` : `Showing ${formatInteger(visible.length)} matching customers`}</p>{visible.length ? <CustomerScatter customers={visible} view={scatterView}/> : <DataState state="empty" message="No customers match these filters."/>}<div className="profile-finding"><p className="key-finding__label">Full-population finding</p><p>{scatterView === 'frequency' ? 'The segment medians progress from lower-frequency, lower-value customers toward higher-frequency, higher-value customers.' : 'Recent High-Activity customers occupy the lower-Recency and higher-value region more strongly; lower Recency means more recent purchasing.'}</p></div></>}
      </Section>

      <Section title="Within-segment distribution" description="Verified quartiles, medians, whisker-compatible bounds, and outlier counts.">
        <FeatureSelector label="Feature" options={distributionFeatures} value={feature} onChange={setFeature}/>
        {distributions.loading && <DataState state="loading" message="Loading segment distributions."/>}{distributions.error && <DataState state="error" message="Distribution summaries are unavailable." onRetry={distributions.retry}/>} {distributions.data && <><QuartileRangeChart segments={distributions.data.segments} feature={feature}/><p className="table-note">Whisker method: {distributions.data.whisker_method}. No synthetic observations are created.</p></>}
      </Section>

      <Section title="Segment detail" description="Review one segment at a time in original business units.">
        <FeatureSelector label="Segment" options={(segments.data ?? []).map(s=>String(s.SegmentID))} value={String(selectedSegment)} onChange={v=>chooseSegment(Number(v))}/>
        {detail.loading && <DataState state="loading" message="Loading the selected profile."/>}{detail.error && <DataState state="error" message="The selected profile is unavailable." onRetry={detail.retry}/>} {detail.data && <div className="segment-detail"><div><h3>{detail.data.SegmentName}</h3><p>{formatInteger(detail.data.customer_count)} customers · {formatPercent(detail.data.customer_percentage)}</p></div><div className="profile-table-wrap"><table className="profile-table segment-detail-table"><thead><tr><th>Feature</th><th>Median</th><th>Mean</th><th>Population median</th><th>Comparison</th></tr></thead><tbody>{profileFeatures.map(item=><tr key={item}><th>{displayName(item)}</th><td>{displayValue(item,detail.data!.median_profile[item])}</td><td>{displayValue(item,detail.data!.mean_profile[item])}</td><td>{displayValue(item,detail.data!.population_medians[item])}</td><td>{detail.data!.comparison_with_population[item]}</td></tr>)}</tbody></table></div><div className="detail-notes"><div><h4>Key characteristics</h4><ul>{detail.data.key_characteristics.map(x=><li key={x}>{x}</li>)}</ul></div><div><h4>Interpretation notes</h4><ul>{detail.data.interpretation_notes.map(x=><li key={x}>{x}</li>)}</ul></div><div><h4>Limitations</h4><ul>{detail.data.limitations.map(x=><li key={x}>{x}</li>)}</ul></div></div></div>}
        <div className="customer-examples"><h3>Customer examples</h3>{examples.loading && <DataState state="loading" message="Loading customer examples."/>}{examples.error && <DataState state="error" message="Customer examples are unavailable." onRetry={examples.retry}/>} {examples.data && <><div className="research-table-wrap"><table className="research-table"><thead><tr><th>Customer ID</th><th>Country</th><th>Recency</th><th>Frequency</th><th>Monetary value</th><th>Products</th><th>Lifetime</th></tr></thead><tbody>{examples.data.customers.map(row=><tr key={row.CustomerID}><th>{row.CustomerID}</th><td>{row.Country}</td><td>{formatInteger(row.Recency)} days</td><td>{formatInteger(row.Frequency)}</td><td>{formatCurrency(row.MonetaryValue)}</td><td>{formatInteger(row.UniqueProducts)}</td><td>{formatInteger(row.CustomerLifetimeDays)} days</td></tr>)}</tbody></table></div><div className="pagination"><button className="secondary-button" disabled={!offset} onClick={()=>setOffset(Math.max(0,offset-10))}>Previous</button><span>{formatInteger(offset+1)}–{formatInteger(Math.min(offset+10,examples.data.total))} of {formatInteger(examples.data.total)}</span><button className="secondary-button" disabled={offset+10>=examples.data.total} onClick={()=>setOffset(offset+10)}>Next</button></div></>}
        </div>
      </Section>
    </div>
  </>
}
