import React, { useState, useRef } from 'react';
import {
  UploadCloud,
  FileText,
  CheckCircle2,
  AlertCircle,
  Eye,
  Play,
  Trash2,
  FileSpreadsheet,
  FileCheck,
  AlertTriangle,
  Loader2,
  Sparkles,
} from 'lucide-react';

export const UploadPage = ({ onIngestionSuccess }) => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewData, setPreviewData] = useState(null);
  const [previewError, setPreviewError] = useState(null);

  const [ingestLoading, setIngestLoading] = useState(false);
  const [ingestResult, setIngestResult] = useState(null);
  const [ingestError, setIngestError] = useState(null);

  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const handleFiles = (files) => {
    const validFiles = Array.from(files);
    setSelectedFiles((prev) => [...prev, ...validFiles]);
    setPreviewData(null);
    setIngestResult(null);
    setPreviewError(null);
    setIngestError(null);
  };

  const removeFile = (index) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
    setPreviewData(null);
    setIngestResult(null);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  };

  // 1. Run File Preview
  const handlePreview = async () => {
    if (selectedFiles.length === 0) return;
    setPreviewLoading(true);
    setPreviewError(null);

    const formData = new FormData();
    selectedFiles.forEach((file) => {
      formData.append('files', file);
    });

    try {
      const response = await fetch('/api/upload/preview', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Preview generation failed.');
      }

      const data = await response.json();
      setPreviewData(data);
    } catch (err) {
      setPreviewError(err.message);
    } finally {
      setPreviewLoading(false);
    }
  };

  // 2. Run Pipeline Ingestion
  const handleIngest = async () => {
    if (selectedFiles.length === 0) return;
    setIngestLoading(true);
    setIngestError(null);

    const formData = new FormData();
    selectedFiles.forEach((file) => {
      formData.append('files', file);
    });

    try {
      const response = await fetch('/api/upload/ingest', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ingestion pipeline execution failed.');
      }

      const result = await response.json();
      setIngestResult(result);
      if (onIngestionSuccess) onIngestionSuccess();
    } catch (err) {
      setIngestError(err.message);
    } finally {
      setIngestLoading(false);
    }
  };

  const totalSizeMB = (
    selectedFiles.reduce((acc, f) => acc + f.size, 0) / (1024 * 1024)
  ).toFixed(2);

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Page Header */}
      <div>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
          Upload & Standardized Ingestion Pipeline
        </h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
          Upload structured files and raw documents, inspect parsed document chunks in preview, and run validation &
          vector embedding into MySQL and ChromaDB storage.
        </p>
      </div>

      {/* Supported Formats Card */}
      <div className="card" style={{ padding: '1.25rem 1.5rem', background: 'var(--bg-muted)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
          <FileCheck size={18} color="var(--primary-600)" />
          <h4 style={{ fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--text-primary)' }}>
            Supported File Formats
          </h4>
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1.5rem', fontSize: '0.85rem' }}>
          <div>
            <strong style={{ color: 'var(--text-secondary)' }}>Structured Data:</strong>{' '}
            <span style={{ color: 'var(--text-muted)' }}>CSV, Excel (.xlsx, .xls), JSON, JSONL</span>
          </div>
          <div style={{ borderLeft: '1px solid var(--border-main)', paddingLeft: '1.5rem' }}>
            <strong style={{ color: 'var(--text-secondary)' }}>Unstructured Documents:</strong>{' '}
            <span style={{ color: 'var(--text-muted)' }}>PDF, Word (.docx), Plain Text (.txt)</span>
          </div>
        </div>
      </div>

      {/* Drag & Drop Upload Zone */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        style={{
          border: `2px dashed ${dragActive ? 'var(--primary-500)' : 'var(--border-main)'}`,
          backgroundColor: dragActive ? 'var(--primary-50)' : 'var(--bg-surface)',
          borderRadius: 'var(--radius-xl)',
          padding: '3rem 2rem',
          textAlign: 'center',
          cursor: 'pointer',
          transition: 'all 0.2s ease',
        }}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".csv,.xlsx,.xls,.json,.jsonl,.pdf,.docx,.txt"
          style={{ display: 'none' }}
          onChange={(e) => handleFiles(e.target.files)}
        />
        <div
          style={{
            width: '56px',
            height: '56px',
            borderRadius: 'var(--radius-full)',
            backgroundColor: 'var(--primary-50)',
            color: 'var(--primary-600)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '1rem',
          }}
        >
          <UploadCloud size={28} />
        </div>
        <h3 style={{ fontSize: '1.15rem', color: 'var(--text-primary)', marginBottom: '0.35rem' }}>
          Drag and drop files here, or browse
        </h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
          Select CSV, Excel, JSON, JSONL, PDF, DOCX, or TXT files to process
        </p>
      </div>

      {/* Selected Files List & Actions */}
      {selectedFiles.length > 0 && (
        <div className="card">
          <div className="card-header">
            <div>
              <h3 className="card-title">Selected Files ({selectedFiles.length})</h3>
              <p className="card-subtitle">Total upload size: {totalSizeMB} MB</p>
            </div>
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => setSelectedFiles([])}
              >
                Clear All
              </button>
              <button
                className="btn btn-secondary btn-sm"
                onClick={handlePreview}
                disabled={previewLoading || ingestLoading}
              >
                {previewLoading ? <Loader2 size={15} className="pulse-indicator" /> : <Eye size={15} />}
                <span>{previewLoading ? 'Parsing...' : 'Preview Files'}</span>
              </button>
              <button
                className="btn btn-primary btn-sm"
                onClick={handleIngest}
                disabled={ingestLoading || previewLoading}
              >
                {ingestLoading ? <Loader2 size={15} className="pulse-indicator" /> : <Play size={15} />}
                <span>{ingestLoading ? 'Ingesting Pipeline...' : 'Ingest Data'}</span>
              </button>
            </div>
          </div>

          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>File Name</th>
                  <th>Format</th>
                  <th>Size</th>
                  <th style={{ textAlign: 'right' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {selectedFiles.map((file, idx) => {
                  const ext = file.name.split('.').pop()?.toUpperCase() || 'FILE';
                  return (
                    <tr key={idx}>
                      <td style={{ fontWeight: 600 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <FileText size={16} color="var(--primary-600)" />
                          <span>{file.name}</span>
                        </div>
                      </td>
                      <td>
                        <span className="badge badge-primary">{ext}</span>
                      </td>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>
                        {(file.size / 1024).toFixed(1)} KB
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <button
                          style={{
                            background: 'transparent',
                            border: 'none',
                            color: 'var(--text-light)',
                            cursor: 'pointer',
                          }}
                          onClick={() => removeFile(idx)}
                          title="Remove file"
                        >
                          <Trash2 size={16} />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Preview Error */}
      {previewError && (
        <div className="card" style={{ borderColor: 'var(--danger-border)', background: 'var(--danger-bg)' }}>
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start', color: 'var(--danger-text)' }}>
            <AlertCircle size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <h4 style={{ fontWeight: 700, marginBottom: '0.25rem' }}>File Preview Error</h4>
              <p style={{ fontSize: '0.875rem' }}>{previewError}</p>
            </div>
          </div>
        </div>
      )}

      {/* Preview Results Table */}
      {previewData && (
        <div className="card animate-fade-in">
          <div className="card-header">
            <div>
              <h3 className="card-title">Parsed Documents Preview</h3>
              <p className="card-subtitle">
                {previewData.total_documents} document(s) loaded. Review parsed chunks prior to pipeline storage.
              </p>
            </div>
            <div className="badge badge-success">
              <CheckCircle2 size={13} />
              <span>{previewData.file_results.length} Files Processed</span>
            </div>
          </div>

          {/* File Results summary pills */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1.25rem' }}>
            {previewData.file_results.map((fr, idx) => (
              <div key={idx} className="badge badge-primary" style={{ padding: '0.35rem 0.75rem' }}>
                <span>{fr.file}:</span>
                <strong>{fr.documents} docs</strong>
              </div>
            ))}
          </div>

          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Doc ID</th>
                  <th>Source</th>
                  <th>Type</th>
                  <th>Content Preview</th>
                </tr>
              </thead>
              <tbody>
                {previewData.preview.map((doc, idx) => (
                  <tr key={idx}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {doc.id}
                    </td>
                    <td style={{ fontWeight: 600 }}>{doc.source}</td>
                    <td>
                      <span className="badge badge-info">{doc.source_type}</span>
                    </td>
                    <td style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                      {doc.content_preview}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div
            style={{
              marginTop: '1.5rem',
              padding: '1rem',
              backgroundColor: 'var(--warning-bg)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--warning-border)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <AlertTriangle size={18} color="var(--warning-solid)" />
              <span style={{ fontSize: '0.875rem', color: 'var(--warning-text)', fontWeight: 500 }}>
                This is a preview stage. Click <strong>Ingest Data</strong> to clean, validate, generate embeddings,
                and persist to SQL and ChromaDB.
              </span>
            </div>
            <button className="btn btn-primary btn-sm" onClick={handleIngest} disabled={ingestLoading}>
              {ingestLoading ? <Loader2 size={14} className="pulse-indicator" /> : <Play size={14} />}
              <span>Execute Ingestion</span>
            </button>
          </div>
        </div>
      )}

      {/* Ingestion Pipeline Execution Results */}
      {ingestResult && (
        <div className="card animate-fade-in" style={{ border: '2px solid var(--success-border)' }}>
          <div className="card-header">
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--success-solid)' }}>
                <CheckCircle2 size={20} />
                <h3 className="card-title" style={{ color: 'var(--success-text)' }}>
                  Ingestion Pipeline Completed Successfully
                </h3>
              </div>
              <p className="card-subtitle">
                All records validated, embedded, and synchronized across persistence stores.
              </p>
            </div>
          </div>

          {/* Ingestion Metric Cards */}
          <div className="grid-4" style={{ marginBottom: '1.5rem' }}>
            <div className="stat-card" style={{ padding: '1rem' }}>
              <span className="stat-label">Input Documents</span>
              <div className="stat-value">{ingestResult.input_documents}</div>
            </div>
            <div className="stat-card" style={{ padding: '1rem' }}>
              <span className="stat-label">Processed Chunks</span>
              <div className="stat-value">{ingestResult.processed_documents}</div>
            </div>
            <div className="stat-card" style={{ padding: '1rem' }}>
              <span className="stat-label">SQL Records Written</span>
              <div className="stat-value">{ingestResult.sql_records}</div>
            </div>
            <div className="stat-card" style={{ padding: '1rem' }}>
              <span className="stat-label">Vector Embeddings</span>
              <div className="stat-value">{ingestResult.vector_records}</div>
            </div>
          </div>

          {/* Quality Summary Gauge */}
          {ingestResult.quality_summary && (
            <div
              style={{
                background: 'var(--bg-muted)',
                borderRadius: 'var(--radius-md)',
                padding: '1.25rem',
                marginBottom: '1rem',
              }}
            >
              <h4 style={{ fontSize: '0.95rem', marginBottom: '0.75rem', color: 'var(--text-primary)' }}>
                Data Quality Assessment
              </h4>
              <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Quality Score</span>
                  <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--primary-600)' }}>
                    {ingestResult.quality_summary.quality_score?.toFixed(2)}
                  </div>
                </div>
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Valid Records</span>
                  <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--success-solid)' }}>
                    {ingestResult.quality_summary.valid_records}
                  </div>
                </div>
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Invalid Records</span>
                  <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--danger-solid)' }}>
                    {ingestResult.quality_summary.invalid_records}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Invalid documents table if any */}
          {ingestResult.invalid_count > 0 && (
            <div style={{ marginTop: '1rem' }}>
              <h4 style={{ color: 'var(--warning-text)', fontSize: '0.9rem', marginBottom: '0.5rem' }}>
                Invalid Documents ({ingestResult.invalid_count})
              </h4>
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Document ID</th>
                      <th>Source</th>
                      <th>Type</th>
                    </tr>
                  </thead>
                  <tbody>
                    {ingestResult.invalid_documents.map((d, i) => (
                      <tr key={i}>
                        <td style={{ fontFamily: 'var(--font-mono)' }}>{d.id}</td>
                        <td>{d.source}</td>
                        <td>{d.source_type}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Ingestion Error Display */}
      {ingestError && (
        <div className="card" style={{ borderColor: 'var(--danger-border)', background: 'var(--danger-bg)' }}>
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start', color: 'var(--danger-text)' }}>
            <AlertCircle size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <h4 style={{ fontWeight: 700, marginBottom: '0.25rem' }}>Pipeline Ingestion Failed</h4>
              <p style={{ fontSize: '0.875rem' }}>{ingestError}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
