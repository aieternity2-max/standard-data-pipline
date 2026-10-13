import React from 'react';
import {
  LayoutDashboard,
  UploadCloud,
  Database,
  Search,
  Sparkles,
  BarChart3,
  Settings,
  Server,
  Layers,
  ChevronRight,
  Sun,
  Moon,
} from 'lucide-react';

export const Sidebar = ({
  activePage,
  onNavigate,
  stats = {},
  health = {},
  theme,
  onToggleTheme,
}) => {
  const navItems = [
    {
      id: 'overview',
      label: 'Overview',
      icon: LayoutDashboard,
      badge: null,
    },
    {
      id: 'upload',
      label: 'Upload & Ingest',
      icon: UploadCloud,
      badge: 'ETL',
    },
    {
      id: 'explore',
      label: 'Explore Data',
      icon: Database,
      badge: stats.document_count ? `${stats.document_count}` : null,
    },
    {
      id: 'search',
      label: 'Semantic Search',
      icon: Search,
      badge: 'Vector',
    },
    {
      id: 'ask-ai',
      label: 'Ask AI (RAG)',
      icon: Sparkles,
      badge: 'AI',
    },
    {
      id: 'dashboards',
      label: 'Dashboards',
      icon: BarChart3,
      badge: 'Analytics',
    },
    {
      id: 'settings',
      label: 'Pipeline Config',
      icon: Settings,
      badge: null,
    },
  ];

  const isHealthy = health?.status === 'healthy';
  const isDegraded = health?.status === 'degraded';

  return (
    <aside className="app-sidebar">
      {/* Brand Header */}
      <div className="sidebar-header">
        <div className="brand-wrapper">
          <div className="brand-icon">
            <Layers size={20} strokeWidth={2.5} />
          </div>
          <div>
            <div className="brand-title">InsightSphere</div>
            <div className="brand-tag">Data Pipeline Platform</div>
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="sidebar-nav">
        <div className="nav-section-title">Workspace</div>
        {navItems.slice(0, 6).map((item) => {
          const Icon = item.icon;
          const isActive = activePage === item.id;
          return (
            <button
              key={item.id}
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => onNavigate(item.id)}
            >
              <div className="nav-item-content">
                <Icon size={18} strokeWidth={isActive ? 2.2 : 1.8} />
                <span>{item.label}</span>
              </div>
              {item.badge && <span className="nav-badge">{item.badge}</span>}
            </button>
          );
        })}

        <div className="nav-section-title">System & Ops</div>
        <button
          className={`nav-item ${activePage === 'settings' ? 'active' : ''}`}
          onClick={() => onNavigate('settings')}
        >
          <div className="nav-item-content">
            <Settings size={18} strokeWidth={activePage === 'settings' ? 2.2 : 1.8} />
            <span>Pipeline Config</span>
          </div>
        </button>
      </nav>

      {/* Sidebar Footer & System Status */}
      <div className="sidebar-footer">
        <div className="system-status-indicator">
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <span
              className={`status-dot ${
                isHealthy ? 'healthy' : isDegraded ? 'degraded' : 'error'
              }`}
            />
            <span style={{ color: 'var(--text-secondary)' }}>
              {isHealthy ? 'All Systems Online' : isDegraded ? 'Degraded Ops' : 'Connecting...'}
            </span>
          </div>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            v0.1.0
          </span>
        </div>

        {/* Theme Toggle */}
        <button
          className="btn btn-secondary btn-sm"
          style={{ width: '100%', justifyContent: 'space-between' }}
          onClick={onToggleTheme}
        >
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            {theme === 'dark' ? <Moon size={15} /> : <Sun size={15} />}
            <span>{theme === 'dark' ? 'Dark Mode' : 'Light Mode'}</span>
          </span>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Toggle</span>
        </button>
      </div>
    </aside>
  );
};
