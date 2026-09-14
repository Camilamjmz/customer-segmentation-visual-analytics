type Kind = 'loading' | 'error' | 'empty'
export function DataState({ state, title, message, onRetry }: { state: Kind; title?: string; message: string; onRetry?: () => void }) {
  return <div className={`data-state data-state--${state}`} role={state === 'error' ? 'alert' : 'status'}>{state === 'loading' && <span className="data-state__line" aria-hidden="true" />}<div><p className="data-state__title">{title ?? (state === 'loading' ? 'Loading data' : state === 'error' ? 'Data unavailable' : 'No results')}</p><p className="data-state__message">{message}</p></div>{state === 'error' && onRetry && <button className="secondary-button" onClick={onRetry}>Try again</button>}</div>
}
