export function Placeholder({ label, height = 'medium' }: { label: string; height?: 'small' | 'medium' | 'large' }) {
  return <div className={`placeholder placeholder--${height}`}><span>{label}</span><div className="placeholder__lines" aria-hidden="true"><i /><i /><i /></div></div>
}
