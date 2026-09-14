import { PageHeader } from '../components/layout/PageHeader'
import { DataState } from '../components/ui/DataState'
import { Section } from '../components/ui/Section'
import { useApiResource } from '../hooks/useApiResource'
import { getMethodology } from '../services/methodologyApi'
import { getModel } from '../services/overviewApi'
import { formatDecimal } from '../utils/formatters'

const phases=[
  {name:'Data foundation',range:[1,2]},
  {name:'Feature development',range:[3,5]},
  {name:'Modeling experiments',range:[6,8]},
  {name:'Validation & selection',range:[9,10]},
]
const features=[
  ['Recency','Time since the most recent purchase','Separates recently active customers from customers whose activity is older.'],
  ['Frequency','Number of distinct valid orders','Represents repeat-purchase activity.'],
  ['MonetaryValue','Total valid transaction value','Represents the financial scale of observed purchasing.'],
  ['UniqueProducts','Number of distinct products purchased','Captures product breadth and variety.'],
  ['CustomerLifetimeDays','Time between first and last valid purchase','Represents the duration of the observed customer relationship.'],
]

export function MethodologyPage(){
 const methodology=useApiResource(getMethodology), model=useApiResource(getModel)
 return <><PageHeader eyebrow="Research methodology" title="Methodology & Research Process" description="The project followed a reproducible sequence from raw transaction preparation through feature engineering, clustering comparison, robustness validation, and final model selection."/><div className="methodology-page">
  <Section title="Research pipeline" description="Ten backend-documented stages grouped into four phases of the study.">
   {methodology.loading&&<DataState state="loading" message="Loading the documented research workflow."/>}
   {methodology.error&&<DataState state="error" message="The research workflow is unavailable." onRetry={methodology.retry}/>}
   {methodology.data&&<div className="methodology-phases">{phases.map(phase=><section key={phase.name} className="methodology-phase"><h3>{phase.name}</h3><ol start={phase.range[0]}>{methodology.data!.filter(item=>item.stage>=phase.range[0]&&item.stage<=phase.range[1]).map(item=><li key={item.stage}><span aria-hidden="true">{String(item.stage).padStart(2,'0')}</span><div><h4>{item.name}</h4><p>{item.summary}</p></div></li>)}</ol></section>)}</div>}
  </Section>

  <div className="methodology-grid">
   <Section title="Feature engineering" description="The final matrix represents five complementary dimensions of customer behavior."><div className="research-table-wrap"><table className="research-table methodology-feature-table"><thead><tr><th>Feature</th><th>Behavioral meaning</th><th>Why useful for clustering</th></tr></thead><tbody>{features.map(row=><tr key={row[0]}><th>{row[0]}</th><td>{row[1]}</td><td>{row[2]}</td></tr>)}</tbody></table></div></Section>
   <Section title="Feature-selection decisions" description="Engineered variables remained available for interpretation even when excluded from the primary distance matrix."><dl className="decision-list"><div><dt>TotalItems</dt><dd>Strongly correlated with MonetaryValue (Pearson correlation 0.875), so it was excluded from the primary set to reduce redundant volume information.</dd></div><div><dt>AverageOrderValue</dt><dd>Retained for behavioral interpretation and later sensitivity analysis, but not primary clustering.</dd></div><div><dt>AverageItemsPerOrder</dt><dd>Retained for interpretation and order-intensity sensitivity analysis, but not primary clustering.</dd></div><div><dt>Country</dt><dd>Categorical and highly imbalanced, making it unsuitable for direct inclusion in this Euclidean-distance feature matrix.</dd></div></dl></Section>
  </div>

  <Section title="Preprocessing decisions" description="Transformations made differently scaled behavioral measures suitable for distance-based comparison."><div className="methodology-decision-grid"><article><p className="eyebrow">Transformation</p><h3>log1p for skewed measures</h3><p>Frequency, MonetaryValue, and UniqueProducts were strongly right-skewed. log1p compresses extreme magnitudes while preserving customer ordering, reducing domination by very large observations. It does not remove outliers.</p></article><article><p className="eyebrow">Comparable scale</p><h3>StandardScaler</h3><p>The five features use different units and magnitudes. StandardScaler centers and scales them so Euclidean distance in K-Means is not dominated merely by the largest numerical unit.</p></article><article><p className="eyebrow">Preserved dimensions</p><h3>No logarithm for time measures</h3><p>Recency and CustomerLifetimeDays remained untransformed before standardization, preserving the chosen temporal representation.</p></article></div></Section>

  <Section title="Outlier strategy" description="Extreme observations were investigated and retained rather than automatically deleted."><div className="outlier-method"><div className="outlier-evidence"><strong>10.8%</strong><span>MonetaryValue Tukey-rule outliers</span></div><div className="outlier-evidence"><strong>10.3%</strong><span>TotalItems Tukey-rule outliers</span></div><div><p>Some extreme customers had long, repeated purchasing histories, and wholesale-scale behavior may be legitimate. This does not establish that every outlier is valid.</p><p>The study managed their influence through transformation, alternative preprocessing tests, algorithm comparison, and robustness validation instead of blind deletion.</p></div></div></Section>

  <Section title="Modeling experiments" description="A controlled progression narrowed preprocessing, cluster-count, and algorithm choices without repeating the full evaluation report."><div className="experiment-grid"><article><span>01</span><h3>K-Means preprocessing</h3><p>Three strategies × seven values from k=2 through k=8 × five seeds produced 105 controlled runs.</p></article><article><span>02</span><h3>Candidate profiling</h3><p>k=3 and k=4 emerged as the most interpretable logged solutions and were profiled in original units.</p></article><article><span>03</span><h3>Algorithm comparison</h3><p>K-Means, Ward hierarchical agglomerative clustering, and DBSCAN were evaluated on the shared matrix.</p></article><article><span>04</span><h3>Robustness validation</h3><p>Random initialization, twenty 80% subsamples, and a TotalItems-for-MonetaryValue substitution tested stability and sensitivity.</p></article></div></Section>

  <div className="methodology-grid">
   <Section title="Why k=3" description="The selection balances multiple forms of evidence rather than optimizing a single metric.">{model.loading&&<DataState state="loading" message="Loading final selection evidence."/>}{model.error&&<DataState state="error" message="Final-model evidence is unavailable; the documented pipeline remains available above." onRetry={model.retry}/>} {model.data&&<div className="selection-rationale"><p>{model.data.model_rationale}</p><ul><li>Strongest verified full-coverage internal metrics</li><li>Balanced, behaviorally clear segments</li><li>Initialization ARI {formatDecimal(Number(model.data.validation_summary.random_initialization_stability_ari),4)}</li><li>Mean subsampling ARI {formatDecimal(Number(model.data.validation_summary.subsampling_mean_ari),4)}</li><li>Complete customer coverage and fewer segment boundaries</li></ul><details><summary>Why retain k=4?</summary><p>{String(model.data.sensitivity_model.role)} It preserved meaningful structure, had stronger feature-substitution agreement, and separated a recent low-frequency group. Its internal metrics and subsampling stability were weaker, and interpretation required an additional boundary.</p></details></div>}</Section>
   <Section title="Final model configuration" description="Frozen configuration exposed by the analytics API.">{model.loading&&<DataState state="loading" message="Loading configuration."/>}{model.error&&<DataState state="error" message="Configuration evidence is unavailable." onRetry={model.retry}/>} {model.data&&<dl className="configuration-list"><div><dt>Algorithm</dt><dd>{model.data.algorithm}</dd></div><div><dt>Clusters</dt><dd>{model.data.k}</dd></div><div><dt>Preprocessing</dt><dd>log1p + StandardScaler</dd></div><div><dt>Features</dt><dd>{model.data.clustering_features.join(', ')}</dd></div><div><dt>Coverage</dt><dd>{model.data.validation_summary.full_customer_coverage?'100%':'Partial'}</dd></div><div><dt>Customers</dt><dd>5,878</dd></div></dl>}</Section>
  </div>

  <Section title="Study limitations" description="Boundaries on what can be concluded from this segmentation."><div className="limitations-grid"><p>The dataset is dominated by United Kingdom customers and may not generalize geographically.</p><p>Historical retail data ending in 2011 may not represent current purchasing behavior.</p><p>Interpretation depends on the engineered behavioral features and observation window.</p><p>K-Means favors compact structure defined through Euclidean distance.</p><p>The segmentation is descriptive and does not establish intent or causality.</p><p>No external business outcome was used to validate segment value.</p><p>Customer behavior and resulting assignments may change over time.</p><p>The model uses historical transaction behavior rather than broader customer context.</p></div></Section>

  <Section title="Reproducibility" description="The analytical result remains traceable from source preparation to the application."><ul className="reproducibility-list"><li>Deterministic preparation scripts</li><li>Documented preprocessing rules</li><li>Fixed random states</li><li>Saved experiment outputs</li><li>Automated backend tests</li><li>Frozen final segmentation</li><li>API-exposed final analytics</li></ul></Section>
 </div></>}
