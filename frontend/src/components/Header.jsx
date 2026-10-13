import React from 'react';
import {
  RotateCw,
  Search,
  Database,
  CheckCircle2,
  AlertTriangle,
  Radio,
} from 'lucide-react';

export const Header = ({
  pageTitle,
  pageSubtitle,
  health,
  onRefresh,
  loading,
}) => {
  const isMysqlConnected = health?.mysql?.status === 'connected';
  const chromaCount = health?.chromadb?.count ?? 0;

  return (
    <header className="app-topbar">
      <div className="topbar-left">
        <div>
          <h1 className="page-title">{pageTitle}</h1>
          {pageSubtitle && (
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              {pageSubtitle}
            </p>
          )}
        </div>
      </div>

      <div className="topbar-right">
        {/* ChromaDB Status Pill */}
        <div
          className="badge badge-primary"
          style={{ padding: '0.35rem 0.75rem', gap: '0.45rem' }}
          title="ChromaDB Indexed Vector Documents"
        >
          <Database size={13} />
          <span>Chroma: <strong>{chromaCount} docs</strong></span>
        </div>

        {/* MySQL Status Pill */}
        <div
          className={`badge ${isMysqlConnected ? 'badge-success' : 'badge-warning'}`}
          style={{ padding: '0.35rem 0.75rem', gap: '0.45rem' }}
          title={isMysqlConnected ? 'MySQL Database Connected' : 'MySQL Unavailable'}
        >
          {isMysqlConnected ? <CheckCircle2 size={13} /> : <AlertTriangle size={13} />}
          <span>MySQL: <strong>{isMysqlConnected ? 'Live' : 'Offline'}</strong></span>
        </div>

        {/* Refresh button */}
        <button
          className="btn btn-secondary btn-sm"
          onClick={onRefresh}
          disabled={loading}
          title="Refresh All System Analytics"
        >
          <RotateCw size={14} className={loading ? 'pulse-indicator' : ''} />
          <span>Sync</span>
        </button>
      </div>
    </header>
  );
};
