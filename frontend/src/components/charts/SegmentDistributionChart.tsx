import createPlotlyComponent from 'react-plotly.js/factory'
import Plotly from 'plotly.js-cartesian-dist-min'
import { segmentColors } from '../../constants/design'
import type { SegmentSummary } from '../../types/overview'
import { formatInteger, formatPercent } from '../../utils/formatters'

const colorsById = [segmentColors.inactive, segmentColors.developing, segmentColors.recent]
const Plot = createPlotlyComponent(Plotly)

export function SegmentDistributionChart({ segments }: { segments: SegmentSummary[] }) {
  const ordered = [...segments].sort((a, b) => a.SegmentID - b.SegmentID)
  return <Plot
    data={[{
      type: 'bar', orientation: 'h',
      x: ordered.map((segment) => segment.customer_count),
      y: ordered.map((segment) => segment.SegmentName),
      marker: { color: ordered.map((segment) => colorsById[segment.SegmentID]), line: { color: '#ffffff', width: 1 } },
      customdata: ordered.map((segment) => [segment.customer_percentage]),
      text: ordered.map((segment) => `${formatInteger(segment.customer_count)} · ${formatPercent(segment.customer_percentage)}`),
      textposition: 'outside', cliponaxis: false,
      hovertemplate: '<b>%{y}</b><br>Customers: %{x:,}<br>Share: %{customdata[0]:.1f}%<extra></extra>',
    }]}
    layout={{
      autosize: true, height: 300, margin: { l: 160, r: 95, t: 12, b: 45 },
      paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)', showlegend: false,
      font: { family: 'Inter, ui-sans-serif, system-ui, sans-serif', color: '#526071', size: 12 },
      xaxis: { title: { text: 'Customers', font: { size: 12 } }, gridcolor: '#E7ECF0', zeroline: false, fixedrange: true },
      yaxis: { autorange: 'reversed', fixedrange: true, automargin: true }, bargap: 0.34,
    }}
    config={{ responsive: true, displaylogo: false, editable: false, scrollZoom: false, modeBarButtonsToRemove: ['lasso2d', 'select2d', 'autoScale2d', 'zoom2d', 'pan2d', 'zoomIn2d', 'zoomOut2d'] }}
    useResizeHandler
    style={{ width: '100%', height: '300px' }}
  />
}
