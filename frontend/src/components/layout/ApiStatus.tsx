import { useEffect, useState } from 'react'
import { getHealth } from '../../services/api'

type Status = 'loading' | 'connected' | 'unavailable'

export function ApiStatus() {
  const [status, setStatus] = useState<Status>('loading')
  useEffect(() => {
    const controller = new AbortController()
    getHealth(controller.signal).then(() => setStatus('connected')).catch((error: unknown) => {
      if (!(error instanceof Error && error.name === 'AbortError')) setStatus('unavailable')
    })
    return () => controller.abort()
  }, [])
  const label = status === 'loading' ? 'Checking connection' : status === 'connected' ? 'Connected' : 'Unavailable'
  return <div className="api-status" aria-live="polite"><span className={`status-mark status-mark--${status}`} aria-hidden="true" /><div><p className="api-status__title">Analytics API</p><p className="api-status__value">{label}</p></div></div>
}
