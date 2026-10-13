import React, { useState } from 'react';
import {
  Settings,
  Server,
  Database,
  Cpu,
  Layers,
  CheckCircle2,
  AlertTriangle,
  RotateCw,
  Terminal,
} from 'lucide-react';

export const SettingsPage = ({ health, onRefreshHealth }) => {
  const [testing, setTesting] = useState(false);

  const handleTest = async () => {
    setTesting(true);
    await onRefreshHealth();
    setTimeout(() => setTesting(false), 500);
  };

  const isMysqlConnected = health?.mysql?.status === 'connected';
  const chromaCount = health?.chromadb?.count ?? 0;

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
            Pipeline & Environment Settings
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
            Review real-time configuration parameters, storage connection pools, vector settings, and LLM providers.
          </p>
        </div>
        <button className="btn btn-secondary btn-sm" onClick={handleTest} disabled={testing}>
          <RotateCw size={14} className={testing ? 'pulse-indicator' : ''} />
          <span>Ping Storage Connections</span>
        </button>
      </div>

      {/* Storage Connectivity Status */}
      <div className="grid-2">
        {/* MySQL */}
        <div className="card">
          <div className="card-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              <div
                style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: 'var(--radius-md)',
                  background: isMysqlConnected ? 'var(--success-bg)' : 'var(--warning-bg)',
                  color: isMysqlConnected ? 'var(--success-solid)' : 'var(--warning-solid)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Server size={20} />
              </div>
              <div>
                <h4 className="card-title">MySQL Relational Database</h4>
                <p className="card-subtitle">SQLAlchemy Engine with Connection Pooling</p>
              </div>
            </div>
            <span className={`badge ${isMysqlConnected ? 'badge-success' : 'badge-warning'}`}>
              {isMysqlConnected ? 'Connected' : 'Offline'}
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.85rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
              <span style={{ color: 'var(--text-muted)' }}>Host / Port:</span>
              <strong style={{ fontFamily: 'var(--font-mono)' }}>localhost:3306</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
              <span style={{ color: 'var(--text-muted)' }}>Database Name:</span>
              <strong style={{ fontFamily: 'var(--font-mono)' }}>big_data_demo</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
              <span style={{ color: 'var(--text-muted)' }}>Connection Pool Size:</span>
              <strong style={{ fontFamily: 'var(--font-mono)' }}>5 (Max Overflow: 10)</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0' }}>
              <span style={{ color: 'var(--text-muted)' }}>Driver:</span>
              <strong style={{ fontFamily: 'var(--font-mono)' }}>PyMySQL / SQLAlchemy 2.1</strong>
            </div>
          </div>
        </div>

        {/* ChromaDB */}
        <div className="card">
          <div className="card-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              <div
                style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: 'var(--radius-md)',
                  background: 'var(--primary-50)',
                  color: 'var(--primary-600)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Database size={20} />
              </div>
              <div>
                <h4 className="card-title">ChromaDB Vector Store</h4>
                <p className="card-subtitle">Persistent Dense Vector Index</p>
              </div>
            </div>
            <span className="badge badge-success">Active</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.85rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
              <span style={{ color: 'var(--text-muted)' }}>Collection Name:</span>
              <strong style={{ fontFamily: 'var(--font-mono)' }}>documents</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
              <span style={{ color: 'var(--text-muted)' }}>Storage Path:</span>
              <strong style={{ fontFamily: 'var(--font-mono)' }}>data/chroma</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
              <span style={{ color: 'var(--text-muted)' }}>Indexed Documents:</span>
              <strong style={{ fontFamily: 'var(--font-mono)' }}>{chromaCount} records</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0' }}>
              <span style={{ color: 'var(--text-muted)' }}>Distance Metric:</span>
              <strong style={{ fontFamily: 'var(--font-mono)' }}>Cosine Similarity</strong>
            </div>
          </div>
        </div>
      </div>

      {/* AI & Pipeline Config Card */}
      <div className="card">
        <div className="card-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
            <Cpu size={20} color="var(--primary-600)" />
            <h4 className="card-title">AI Engine & Ingestion Pipeline Settings</h4>
          </div>
        </div>

        <div className="grid-3" style={{ fontSize: '0.85rem' }}>
          <div style={{ padding: '1rem', background: 'var(--bg-muted)', borderRadius: 'var(--radius-md)' }}>
            <strong style={{ color: 'var(--text-primary)', display: 'block', marginBottom: '0.5rem' }}>
              Embedding Provider
            </strong>
            <p style={{ color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Provider: ChromaDB Native</p>
            <p style={{ color: 'var(--text-muted)' }}>ONNX Runtime / Tokenizers enabled</p>
          </div>

          <div style={{ padding: '1rem', background: 'var(--bg-muted)', borderRadius: 'var(--radius-md)' }}>
            <strong style={{ color: 'var(--text-primary)', display: 'block', marginBottom: '0.5rem' }}>
              LLM Provider (RAG)
            </strong>
            <p style={{ color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Provider: Mock / OpenAI</p>
            <p style={{ color: 'var(--text-muted)' }}>Model: gpt-6-luna (configurable)</p>
          </div>

          <div style={{ padding: '1rem', background: 'var(--bg-muted)', borderRadius: 'var(--radius-md)' }}>
            <strong style={{ color: 'var(--text-primary)', display: 'block', marginBottom: '0.5rem' }}>
              Pipeline Batch Size
            </strong>
            <p style={{ color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Chunk size: 1,000 records</p>
            <p style={{ color: 'var(--text-muted)' }}>Data validation: Pydantic v2</p>
          </div>
        </div>
      </div>
    </div>
  );
};
