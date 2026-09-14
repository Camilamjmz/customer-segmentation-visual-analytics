import { NavLink } from 'react-router-dom'
import { navigationItems } from '../../app/navigation'
import { ApiStatus } from './ApiStatus'

export function SidebarNavigation({ onNavigate }: { onNavigate?: () => void }) {
  return <div className="sidebar__inner">
    <div className="brand-block"><span className="brand-mark" aria-hidden="true">CS</span><div><p className="brand-name">Customer Segmentation</p><p className="brand-descriptor">Research analytics platform</p></div></div>
    <nav className="primary-nav" aria-label="Primary navigation"><p className="nav-label">Research workspace</p><ul>{navigationItems.map((item) => <li key={item.path}><NavLink to={item.path} onClick={onNavigate} className={({ isActive }) => `nav-link${isActive ? ' nav-link--active' : ''}`}><span className="nav-index" aria-hidden="true">{item.index}</span><span>{item.label}</span></NavLink></li>)}</ul></nav>
    <div className="sidebar__footer"><ApiStatus /><p className="sidebar__meta">UCI Online Retail II</p></div>
  </div>
}
