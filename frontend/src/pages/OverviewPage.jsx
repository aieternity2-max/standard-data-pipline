import React from 'react';
import {
  UploadCloud,
  Database,
  Search,
  Sparkles,
  BarChart3,
  Server,
  ArrowRight,
  ShieldCheck,
  Cpu,
  FileText,
  Activity,
  CheckCircle2,
} from 'lucide-react';

export const OverviewPage = ({ stats, health, onNavigate }) => {
  const docCount = health?.chromadb?.count ?? stats?.document_count ?? 0;
  const mysqlLive = health?.mysql?.status === 'connected';

  const cards = [
    {
      id: 'upload',
      title: 'Upload Data',
      icon: UploadCloud,
      color: '#2563EB',
      description:
        'Load CSV, Excel, JSON, PDF, DOCX, and other supported sources into the standardized ingestion pipeline.',
      action: 'Open Upload Data',
    },
    {
      id: 'explore',
      title: 'Explore Data',
      icon: Database,
      color: '#059669',
      description:
        'Inspect ingested data, review its structure, and inspect full text and metadata for analysis and visualization.',
      action: 'Open Explore Data',
    },
    {
      id: 'search',
      title: 'Semantic Search',
      icon: Search,
      color: '#7C3AED',
      description:
        'Find relevant information across indexed documents with vector embeddings and similarity scoring.',
      action: 'Open Search',
    },
    {
      id: 'ask-ai',
      title: 'Ask AI (RAG)',
      icon: Sparkles,
      color: '#D97706',
      description:
        'Ask questions about your documents and receive accurate answers grounded in retrieved context with source citations.',
      action: 'Open Ask AI',
    },
    {
      id: 'dashboards',
      title: 'Dashboards',
      icon: BarChart3,
      color: '#2563EB',
      description:
        'Connect analytical outputs to reporting and business intelligence: revenue, payments, customer RFM, and anomaly rules.',
      action: 'Open Dashboards',
    },
    {
      id: 'settings',
      title: 'Activity & Status',
      icon: Activity,
      color: '#0891B2',
      description:
        'Review pipeline activity, storage connectivity, and runtime settings across MySQL and ChromaDB.',
      action: 'Open Pipeline Config',
    },
  ];

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Hero Welcome Banner */}
      <div
        className="card"
        style={{
          background: 'linear-gradient(135deg, #1E293B 0%, #0F172A 100%)',
          color: 'white',
          border: 'none',
          padding: '2.5rem',
          position: 'relative',
          overflow: 'hidden',
          boxShadow: 'var(--shadow-lg)',
        }}
      >
        <div
          style={{
            position: 'absolute',
            top: '-40px',
            right: '-40px',
            width: '260px',
            height: '260px',
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(59, 130, 246, 0.3) 0%, rgba(59, 130, 246, 0) 70%)',
            pointerEvents: 'none',
          }}
        />

        <div style={{ position: 'relative', zIndex: 1, maxWidth: '780px' }}>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.25rem 0.75rem',
              borderRadius: 'var(--radius-full)',
              background: 'rgba(59, 130, 246, 0.2)',
              border: '1px solid rgba(96, 165, 250, 0.3)',
              color: '#93C5FD',
              fontSize: '0.75rem',
              fontWeight: 700,
              letterSpacing: '0.06em',
              textTransform: 'uppercase',
              marginBottom: '1rem',
            }}
          >
            <span>Standard Ingestion & Analytics Platform</span>
          </div>

          <h2 style={{ fontSize: '2.25rem', fontWeight: 800, color: 'white', marginBottom: '0.75rem', lineHeight: 1.2 }}>
            Welcome to InsightSphere
          </h2>
          <p style={{ color: '#CBD5E1', fontSize: '1.05rem', lineHeight: 1.6, marginBottom: '2rem' }}>
            Your data workspace for exploration, search, AI, and reporting. Bring structured files and unstructured
            documents into a unified pipeline with vector embeddings, semantic retrieval, and deep business analytics.
          </p>

          {/* Workflow Stepper */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
            {[
              { step: '01', label: 'Upload Data', action: 'upload' },
              { step: '02', label: 'Validate & Parse', action: 'upload' },
              { step: '03', label: 'Explore & Search', action: 'explore' },
              { step: '04', label: 'Ask AI & Reports', action: 'ask-ai' },
            ].map((item, idx) => (
              <button
                key={idx}
                onClick={() => onNavigate(item.action)}
                style={{
                  background: 'rgba(255, 255, 255, 0.08)',
                  backdropFilter: 'blur(8px)',
                  border: '1px solid rgba(255, 255, 255, 0.15)',
                  borderRadius: 'var(--radius-md)',
                  padding: '0.6rem 1rem',
                  color: 'white',
                  fontWeight: 600,
                  fontSize: '0.85rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.65rem',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.18)';
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.3)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.08)';
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.15)';
                }}
              >
                <span style={{ color: '#60A5FA', fontWeight: 800 }}>{item.step}</span>
                <span>{item.label}</span>
                <ArrowRight size={13} style={{ opacity: 0.7 }} />
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Real-time KPI Stats */}
      <div className="grid-4">
        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Vector Storage</span>
            <div className="stat-icon" style={{ background: '#EFF6FF', color: '#2563EB' }}>
              <Database size={18} />
            </div>
          </div>
          <div className="stat-value">{docCount.toLocaleString()}</div>
          <div className="stat-footer">
            <CheckCircle2 size={13} color="#10B981" />
            <span>Indexed in ChromaDB collection</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Relational Storage</span>
            <div className="stat-icon" style={{ background: '#ECFDF5', color: '#059669' }}>
              <Server size={18} />
            </div>
          </div>
          <div className="stat-value" style={{ fontSize: '1.4rem' }}>
            {mysqlLive ? 'Connected' : 'Offline'}
          </div>
          <div className="stat-footer">
            <span>MySQL: localhost:3306</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">AI / LLM Engine</span>
            <div className="stat-icon" style={{ background: '#FFFBEB', color: '#D97706' }}>
              <Sparkles size={18} />
            </div>
          </div>
          <div className="stat-value" style={{ fontSize: '1.4rem' }}>
            Active
          </div>
          <div className="stat-footer">
            <Cpu size={13} />
            <span>ChromaDB + RAG Enabled</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Supported Loaders</span>
            <div className="stat-icon" style={{ background: '#F5F3FF', color: '#7C3AED' }}>
              <FileText size={18} />
            </div>
          </div>
          <div className="stat-value">8 Formats</div>
          <div className="stat-footer">
            <span>CSV, XLSX, PDF, DOCX, JSON...</span>
          </div>
        </div>
      </div>

      {/* Your Workspace Cards Section */}
      <div>
        <div style={{ marginBottom: '1.25rem' }}>
          <h3 style={{ fontSize: '1.35rem', color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
            Your Workspace
          </h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            Choose how you want to work with your data.
          </p>
        </div>

        <div className="grid-3">
          {cards.map((card) => {
            const Icon = card.icon;
            return (
              <div
                key={card.id}
                className="card"
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  cursor: 'pointer',
                }}
                onClick={() => onNavigate(card.id)}
              >
                <div>
                  <div
                    style={{
                      width: '42px',
                      height: '42px',
                      borderRadius: 'var(--radius-md)',
                      backgroundColor: 'var(--bg-muted)',
                      color: card.color,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      marginBottom: '1rem',
                    }}
                  >
                    <Icon size={22} strokeWidth={2.2} />
                  </div>
                  <h4 style={{ fontSize: '1.1rem', marginBottom: '0.5rem', color: 'var(--text-primary)' }}>
                    {card.title}
                  </h4>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', lineHeight: 1.5, marginBottom: '1.5rem' }}>
                    {card.description}
                  </p>
                </div>

                <button
                  className="btn btn-secondary btn-sm"
                  style={{ width: '100%', justifyContent: 'space-between' }}
                  onClick={(e) => {
                    e.stopPropagation();
                    onNavigate(card.id);
                  }}
                >
                  <span>{card.action}</span>
                  <ArrowRight size={14} />
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {/* Approved Closing Banner */}
      <div
        className="card"
        style={{
          background: 'var(--bg-muted)',
          border: '1px solid var(--border-main)',
          padding: '1.5rem 2rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '1rem',
        }}
      >
        <div>
          <h4 style={{ fontSize: '1.1rem', color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
            One platform. Multiple ways to work.
          </h4>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            Your data supports exploration, search, AI, and reporting.
          </p>
        </div>
        <button className="btn btn-primary btn-sm" onClick={() => onNavigate('upload')}>
          <UploadCloud size={15} />
          <span>Start Ingestion Workflow</span>
        </button>
      </div>
    </div>
  );
};
