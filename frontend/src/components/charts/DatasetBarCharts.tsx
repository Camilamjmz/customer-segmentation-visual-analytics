import createPlotlyComponent from 'react-plotly.js/factory'
import Plotly from 'plotly.js-cartesian-dist-min'
import type { CountryCount } from '../../types/dataset'
import { formatInteger, formatPercent } from '../../utils/formatters'

const Plot = createPlotlyComponent(Plotly)

const cleanLabels: Record<string, string> = {
  exact_duplicates: 'Exact duplicates',
  missing_customer_id: 'Missing Customer ID',
  invalid_dates: 'Invalid dates',
  cancelled_invoices: 'Cancelled invoices',
  nonpositive_quantity: 'Nonpositive quantity',
  nonpositive_price: 'Nonpositive price',
}

const baseLayout = {
  autosize: true,
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  showlegend: false,
  font: { family: 'Inter, ui-sans-serif, system-ui, sans-serif', color: '#526071', size: 12 },
} as const

const config = { responsive: true, displaylogo: false, editable: false, scrollZoom: false, modeBarButtonsToRemove: ['lasso2d', 'select2d', 'autoScale2d', 'zoom2d', 'pan2d', 'zoomIn2d', 'zoomOut2d'] as never[] }

export function RemovalReasonsChart({ reasons }: { reasons: Record<string, number> }) {
  const rows = Object.entries(reasons).map(([key, count]) => ({ key, label: cleanLabels[key] ?? key, count })).sort((a, b) => b.count - a.count)
  return <Plot data={[{ type: 'bar', orientation: 'h', x: rows.map((row) => row.count), y: rows.map((row) => row.label), marker: { color: rows.map((row) => row.count === 0 ? '#CCD5DC' : '#607D94') }, text: rows.map((row) => formatInteger(row.count)), textposition: 'outside', cliponaxis: false, hovertemplate: '<b>%{y}</b><br>Records removed: %{x:,}<extra></extra>' }]} layout={{ ...baseLayout, height: 360, margin: { l: 150, r: 75, t: 10, b: 45 }, xaxis: { title: { text: 'Records removed' }, gridcolor: '#E7ECF0', zeroline: false, fixedrange: true }, yaxis: { autorange: 'reversed', fixedrange: true, automargin: true }, bargap: .3 }} config={config} useResizeHandler style={{ width: '100%', height: '360px' }} />
}

export function CountryDistributionChart({ countries }: { countries: CountryCount[] }) {
  const rows = [...countries].sort((a, b) => b.customer_count - a.customer_count)
  return <Plot data={[{ type: 'bar', orientation: 'h', x: rows.map((row) => row.customer_count), y: rows.map((row) => row.country), customdata: rows.map((row) => [row.customer_percentage]), marker: { color: '#526F86' }, text: rows.map((row) => `${formatInteger(row.customer_count)} · ${formatPercent(row.customer_percentage)}`), textposition: 'outside', cliponaxis: false, hovertemplate: '<b>%{y}</b><br>Customers: %{x:,}<br>Share of all customers: %{customdata[0]:.1f}%<extra></extra>' }]} layout={{ ...baseLayout, height: 430, margin: { l: 125, r: 100, t: 10, b: 45 }, xaxis: { title: { text: 'Customers' }, gridcolor: '#E7ECF0', zeroline: false, fixedrange: true }, yaxis: { autorange: 'reversed', fixedrange: true, automargin: true }, bargap: .28 }} config={config} useResizeHandler style={{ width: '100%', height: '430px' }} />
}
