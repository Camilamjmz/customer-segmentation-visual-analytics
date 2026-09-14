import { useCallback, useRef, useState } from 'react'
import { Outlet } from 'react-router-dom'
import { MobileNavigation } from './MobileNavigation'
import { SidebarNavigation } from './SidebarNavigation'

export function AppShell() {
  const [mobileOpen, setMobileOpen] = useState(false)
  const menuButton = useRef<HTMLButtonElement>(null)
  const closeMobile = useCallback(() => { setMobileOpen(false); window.requestAnimationFrame(() => menuButton.current?.focus()) }, [])
  return <div className="app-shell">
    <a className="skip-link" href="#main-content">Skip to main content</a>
    <aside className="desktop-sidebar"><SidebarNavigation /></aside>
    <div className="app-frame"><header className="mobile-header"><button ref={menuButton} className="menu-button" onClick={() => setMobileOpen(true)} aria-expanded={mobileOpen} aria-controls="mobile-navigation">Menu</button><span className="mobile-header__title">Customer Segmentation</span></header><main id="main-content" className="main-content" tabIndex={-1}><div className="content-container"><Outlet /></div></main></div>
    <div id="mobile-navigation"><MobileNavigation open={mobileOpen} onClose={closeMobile} /></div>
  </div>
}
