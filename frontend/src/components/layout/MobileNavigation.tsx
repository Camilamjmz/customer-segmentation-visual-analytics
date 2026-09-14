import { useEffect, useRef } from 'react'
import { SidebarNavigation } from './SidebarNavigation'

export function MobileNavigation({ open, onClose }: { open: boolean; onClose: () => void }) {
  const closeButton = useRef<HTMLButtonElement>(null)
  const navigationPanel = useRef<HTMLElement>(null)
  useEffect(() => {
    if (!open) return
    const handleKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
      if (event.key !== 'Tab') return
      const controls = navigationPanel.current?.querySelectorAll<HTMLElement>('button:not([disabled]), a[href]')
      if (!controls?.length) return
      const first = controls[0], last = controls[controls.length - 1]
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus() }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus() }
    }
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    closeButton.current?.focus()
    document.addEventListener('keydown', handleKey)
    return () => { document.removeEventListener('keydown', handleKey); document.body.style.overflow = previousOverflow }
  }, [open, onClose])
  if (!open) return null
  return <div className="mobile-nav-layer" role="dialog" aria-modal="true" aria-label="Mobile navigation"><button className="mobile-nav-backdrop" tabIndex={-1} onClick={onClose} aria-label="Close navigation" /><aside ref={navigationPanel} className="mobile-nav"><div className="mobile-nav__top"><span>Navigation</span><button ref={closeButton} className="text-button" onClick={onClose} aria-label="Close navigation">Close</button></div><SidebarNavigation onNavigate={onClose} /></aside></div>
}
