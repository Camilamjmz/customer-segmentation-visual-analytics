export function FeatureSelector<T extends string>({ label, options, value, onChange }: { label: string; options: readonly T[]; value: T; onChange: (value: T) => void }) {
  return <fieldset className="feature-selector"><legend>{label}</legend><div className="feature-selector__options">{options.map((option) => <button key={option} type="button" className={value === option ? 'feature-option feature-option--active' : 'feature-option'} aria-pressed={value === option} onClick={() => onChange(option)}>{option}</button>)}</div></fieldset>
}
