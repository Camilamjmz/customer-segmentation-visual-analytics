import type { ReactNode } from 'react'

export function Section({ title, description, children, tone = 'default' }: { title: string; description?: string; children?: ReactNode; tone?: 'default' | 'quiet' }) {
  return <section className={`section-panel section-panel--${tone}`}><div className="section-panel__header"><h2>{title}</h2>{description && <p>{description}</p>}</div>{children && <div className="section-panel__body">{children}</div>}</section>
}
