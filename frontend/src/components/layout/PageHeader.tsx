import type { ReactNode } from 'react'

export function PageHeader({ eyebrow, title, description, controls }: { eyebrow: string; title: string; description: string; controls?: ReactNode }) {
  return <header className="page-header"><div className="page-header__copy"><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p className="page-description">{description}</p></div>{controls && <div className="page-header__controls">{controls}</div>}</header>
}
