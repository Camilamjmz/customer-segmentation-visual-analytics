import { useCallback, useEffect, useState } from 'react'

export function useApiResource<T>(loader: (signal?: AbortSignal) => Promise<T>) {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState(false)
  const [requestKey, setRequestKey] = useState(0)
  const retry = useCallback(() => setRequestKey((value) => value + 1), [])

  useEffect(() => {
    const controller = new AbortController()
    setError(false)
    setData(null)
    loader(controller.signal).then(setData).catch((reason: unknown) => {
      if (!(reason instanceof Error && reason.name === 'AbortError')) setError(true)
    })
    return () => controller.abort()
  }, [loader, requestKey])

  return { data, error, loading: !data && !error, retry }
}
