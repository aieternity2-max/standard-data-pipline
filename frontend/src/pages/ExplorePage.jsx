import React, { useState, useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import {
  Database,
  Search,
  ChevronLeft,
  ChevronRight,
  Eye,
  Trash2,
  Copy,
  Check,
  X,
  FileText,
  Server,
  CheckCircle2,
  AlertTriangle,
  AlertCircle,
  Loader2,
  CheckSquare,
} from 'lucide-react';

/**
 * Helper to parse structured records (JSON or Python dict string) into key-value summary
 */
const parseContentSummary = (content) => {
  if (!content || typeof content !== 'string') return null;

  // Attempt JSON parse
  try {
    const parsed = JSON.parse(content);
    if (typeof parsed === 'object' && parsed !== null && !Array.isArray(parsed)) {
      return Object.entries(parsed);
    }
  } catch {}

  // Attempt Python dict string parse (e.g. {'EMPID': 1001, 'EMP_NAME': 'Rahul', ...})
  const trimmed = content.trim();
  if (trimmed.startsWith('{') && trimmed.endsWith('}')) {
    try {
      const regex = /['"]?([a-zA-Z0-9_]+)['"]?\s*:\s*(?:datetime\.[a-zA-Z0-9_]+\([^)]*\)|'([^']*)'|"([^"]*)"|([0-9.]+)|([a-zA-Z0-9_]+))/g;
      const entries = [];
      let match;
      while ((match = regex.exec(trimmed)) !== null) {
        const key = match[1];
        const val = match[2] ?? match[3] ?? match[4] ?? match[5] ?? match[0].split(':')[1]?.trim();
        entries.push([key, String(val).trim()]);
      }
      if (entries.length > 0) return entries;
    } catch {}
  }

  return null;
};

export const ExplorePage = ({ health, onDocumentDeleted }) => {
  const [documents, setDocuments] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [copied, setCopied] = useState(false);

  // Deletion modal state
  const [docToDelete, setDocToDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);
  const [feedback, setFeedback] = useState(null);

  // Multiple selection state
  const [selectedDocIds, setSelectedDocIds] = useState([]);
  const [batchDeleteModalOpen, setBatchDeleteModalOpen] = useState(false);
  const headerCheckboxRef = useRef(null);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const offset = (page - 1) * pageSize;
      let url = `/api/documents?limit=${pageSize}&offset=${offset}`;
      if (searchQuery.trim()) {
        url += `&query=${encodeURIComponent(searchQuery.trim())}`;
      }

      const res = await fetch(url);
      if (!res.ok) throw new Error('Failed to load documents');
      const data = await res.json();
      setDocuments(data.items || []);
      setTotalCount(data.total || 0);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [page, pageSize]);

  // Multiple selection helpers
  const isAllCurrentPageSelected =
    documents.length > 0 && documents.every((doc) => selectedDocIds.includes(doc.id));

  const isSomeCurrentPageSelected =
    documents.some((doc) => selectedDocIds.includes(doc.id)) && !isAllCurrentPageSelected;

  useEffect(() => {
    if (headerCheckboxRef.current) {
      headerCheckboxRef.current.indeterminate = isSomeCurrentPageSelected;
    }
  }, [isSomeCurrentPageSelected]);

  // Reset selection when page, pageSize, or search changes
  useEffect(() => {
    setSelectedDocIds([]);
  }, [page, pageSize, searchQuery]);

  const handleToggleSelectAll = () => {
    if (isAllCurrentPageSelected) {
      const pageDocIds = new Set(documents.map((d) => d.id));
      setSelectedDocIds((prev) => prev.filter((id) => !pageDocIds.has(id)));
    } else {
      const currentIds = new Set(selectedDocIds);
      documents.forEach((d) => currentIds.add(d.id));
      setSelectedDocIds(Array.from(currentIds));
    }
  };

  const handleToggleSelectDoc = (docId) => {
    setSelectedDocIds((prev) =>
      prev.includes(docId) ? prev.filter((id) => id !== docId) : [...prev, docId]
    );
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchDocuments();
  };

  const handleCopyContent = () => {
    if (!selectedDoc) return;
    navigator.clipboard.writeText(selectedDoc.content || '');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDeleteConfirm = async () => {
    if (!docToDelete) return;
    setDeleting(true);
    try {
      const res = await fetch(`/api/documents/${encodeURIComponent(docToDelete.id)}`, {
        method: 'DELETE',
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Failed to delete document');
      }

      const deletedDocId = docToDelete.id;
      setDocToDelete(null);
      if (selectedDoc?.id === deletedDocId) {
        setSelectedDoc(null);
      }
      // Also remove from multi-selection if present
      setSelectedDocIds((prev) => prev.filter((id) => id !== deletedDocId));

      setFeedback({
        type: 'success',
        message: `Document "${deletedDocId}" successfully deleted from storage.`,
      });
      setTimeout(() => setFeedback(null), 4000);

      await fetchDocuments();
      if (onDocumentDeleted) {
        onDocumentDeleted();
      }
    } catch (err) {
      setFeedback({
        type: 'error',
        message: err.message,
      });
    } finally {
      setDeleting(false);
    }
  };

  const handleBatchDeleteConfirm = async () => {
    if (selectedDocIds.length === 0) return;
    setDeleting(true);
    try {
      const res = await fetch('/api/documents/batch-delete', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ids: selectedDocIds }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Failed to delete selected documents');
      }

      const deletedCount = selectedDocIds.length;
      const deletedIdsSet = new Set(selectedDocIds);

      setSelectedDocIds([]);
      setBatchDeleteModalOpen(false);

      if (selectedDoc && deletedIdsSet.has(selectedDoc.id)) {
        setSelectedDoc(null);
      }

      setFeedback({
        type: 'success',
        message: `Successfully deleted ${deletedCount} document${deletedCount > 1 ? 's' : ''} from storage.`,
      });
      setTimeout(() => setFeedback(null), 4000);

      await fetchDocuments();
      if (onDocumentDeleted) {
        onDocumentDeleted();
      }
    } catch (err) {
      setFeedback({
        type: 'error',
        message: err.message,
      });
    } finally {
      setDeleting(false);
    }
  };

  const totalPages = Math.max(1, Math.ceil(totalCount / pageSize));
  const isMysqlConnected = health?.mysql?.status === 'connected';

  // Calculate content metrics for selected document
  const contentWordCount = selectedDoc?.content
    ? selectedDoc.content.trim().split(/\s+/).filter(Boolean).length
    : 0;
  const contentCharCount = selectedDoc?.content ? selectedDoc.content.length : 0;
  const parsedSummary = selectedDoc ? parseContentSummary(selectedDoc.content) : null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Page Header */}
      <div>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
          Explore Data
        </h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
          Browse vector document chunks, inspect metadata, review chunk content, or delete documents as per your wish.
        </p>
      </div>

      {/* Storage Overview Banner */}
      <div className="grid-2">
        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Vector Storage (ChromaDB)</span>
            <div className="stat-icon">
              <Database size={18} />
            </div>
          </div>
          <div className="stat-value">{totalCount.toLocaleString()} Indexed Documents</div>
          <div className="stat-footer">
            <CheckCircle2 size={13} color="#10B981" />
            <span>Ready for semantic retrieval and RAG</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Relational Storage (MySQL)</span>
            <div className="stat-icon" style={{ background: '#ECFDF5', color: '#059669' }}>
              <Server size={18} />
            </div>
          </div>
          <div className="stat-value" style={{ fontSize: '1.5rem' }}>
            {isMysqlConnected ? 'Connected & Healthy' : 'Offline / Degraded'}
          </div>
          <div className="stat-footer">
            {isMysqlConnected ? (
              <CheckCircle2 size={13} color="#10B981" />
            ) : (
              <AlertTriangle size={13} color="#F59E0B" />
            )}
            <span>Database: big_data_demo (localhost:3306)</span>
          </div>
        </div>
      </div>

      {/* Notification Feedback Toast */}
      {feedback && (
        <div
          className="card"
          style={{
            padding: '1rem 1.25rem',
            background: feedback.type === 'success' ? 'var(--success-bg)' : 'var(--danger-bg)',
            borderColor: feedback.type === 'success' ? 'var(--success-border)' : 'var(--danger-border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
            {feedback.type === 'success' ? (
              <CheckCircle2 size={18} color="var(--success-solid)" />
            ) : (
              <AlertCircle size={18} color="var(--danger-solid)" />
            )}
            <span
              style={{
                fontSize: '0.875rem',
                fontWeight: 600,
                color: feedback.type === 'success' ? 'var(--success-text)' : 'var(--danger-text)',
              }}
            >
              {feedback.message}
            </span>
          </div>
          <button
            style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}
            onClick={() => setFeedback(null)}
          >
            <X size={16} />
          </button>
        </div>
      )}

      {/* Search & Filter Bar */}
      <div className="card" style={{ padding: '1.25rem' }}>
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <Search
              size={16}
              style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }}
            />
            <input
              type="text"
              className="input"
              style={{ paddingLeft: '2.4rem' }}
              placeholder="Filter by keyword across document chunks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <button type="submit" className="btn btn-primary btn-sm">
            Search
          </button>
          {searchQuery && (
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => {
                setSearchQuery('');
                setPage(1);
                fetchDocuments();
              }}
            >
              Reset
            </button>
          )}
        </form>
      </div>

      {/* Documents Table */}
      <div className="card">
        <div className="card-header" style={{ flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h3 className="card-title">Document Explorer</h3>
            <p className="card-subtitle">
              Showing page {page} of {totalPages} · {totalCount} total documents
            </p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
            {/* Multiple Selection Action Button */}
            <button
              type="button"
              className={`btn btn-sm ${selectedDocIds.length > 0 ? 'btn-primary' : 'btn-secondary'}`}
              onClick={handleToggleSelectAll}
              disabled={documents.length === 0 || loading}
              title={
                isAllCurrentPageSelected
                  ? 'Deselect all documents on this page'
                  : 'Select all documents on this page for batch operations'
              }
              style={{ gap: '0.4rem' }}
            >
              <CheckSquare size={14} />
              <span>
                {isAllCurrentPageSelected
                  ? 'Deselect All'
                  : selectedDocIds.length > 0
                  ? `Select All (${documents.length})`
                  : 'Multiple Selection'}
              </span>
            </button>

            {/* Batch Delete Trigger Button in Header */}
            {selectedDocIds.length > 0 && (
              <button
                type="button"
                className="btn btn-danger btn-sm"
                onClick={() => setBatchDeleteModalOpen(true)}
                disabled={deleting}
                title="Delete selected documents"
                style={{ gap: '0.4rem' }}
              >
                <Trash2 size={14} />
                <span>Delete Selected ({selectedDocIds.length})</span>
              </button>
            )}

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginLeft: '0.25rem' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Page Size:</span>
              <select
                className="select"
                style={{ width: '80px', padding: '0.35rem 0.5rem', fontSize: '0.8rem' }}
                value={pageSize}
                onChange={(e) => {
                  setPageSize(Number(e.target.value));
                  setPage(1);
                }}
              >
                <option value="10">10</option>
                <option value="20">20</option>
                <option value="50">50</option>
              </select>
            </div>
          </div>
        </div>

        {/* Selection Toolbar Banner */}
        {selectedDocIds.length > 0 && (
          <div className="selection-bar">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <div
                style={{
                  width: '30px',
                  height: '30px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--primary-600)',
                  color: 'white',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                }}
              >
                <CheckSquare size={16} />
              </div>
              <div>
                <span style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                  {selectedDocIds.length} {selectedDocIds.length === 1 ? 'document' : 'documents'} selected
                </span>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginLeft: '0.4rem' }}>
                  on page {page}
                </span>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', flexWrap: 'wrap' }}>
              {!isAllCurrentPageSelected && (
                <button
                  type="button"
                  className="btn btn-secondary btn-sm"
                  onClick={handleToggleSelectAll}
                  style={{ padding: '0.35rem 0.65rem', fontSize: '0.8rem' }}
                >
                  Select All on Page ({documents.length})
                </button>
              )}
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => setSelectedDocIds([])}
                style={{ padding: '0.35rem 0.65rem', fontSize: '0.8rem' }}
              >
                <X size={13} />
                <span>Clear Selection</span>
              </button>
              <button
                type="button"
                className="btn btn-danger btn-sm"
                onClick={() => setBatchDeleteModalOpen(true)}
                style={{ padding: '0.4rem 0.9rem', fontWeight: 700, gap: '0.4rem' }}
              >
                <Trash2 size={14} />
                <span>Delete Selected ({selectedDocIds.length})</span>
              </button>
            </div>
          </div>
        )}

        {loading ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            <Loader2 size={24} className="pulse-indicator" style={{ margin: '0 auto 0.5rem' }} />
            <p style={{ fontSize: '0.875rem' }}>Loading document chunks from vector storage...</p>
          </div>
        ) : documents.length === 0 ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            <FileText size={32} style={{ margin: '0 auto 0.75rem', opacity: 0.5 }} />
            <h4 style={{ color: 'var(--text-primary)', marginBottom: '0.25rem' }}>No documents found</h4>
            <p style={{ fontSize: '0.85rem' }}>
              Upload files or refine your search query to explore indexed records.
            </p>
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th style={{ width: '44px', textAlign: 'center', padding: '0.75rem 0.5rem' }}>
                    <input
                      type="checkbox"
                      className="custom-checkbox"
                      ref={headerCheckboxRef}
                      checked={isAllCurrentPageSelected}
                      onChange={handleToggleSelectAll}
                      aria-label="Select all documents on current page"
                      title={isAllCurrentPageSelected ? 'Deselect all' : 'Select all documents on this page'}
                    />
                  </th>
                  <th style={{ width: '180px' }}>Document ID</th>
                  <th>Source File</th>
                  <th>Type</th>
                  <th>Content Preview</th>
                  <th style={{ textAlign: 'right', minWidth: '170px' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {documents.map((doc, idx) => {
                  const isSelected = selectedDocIds.includes(doc.id);
                  return (
                    <tr
                      key={doc.id || idx}
                      className={isSelected ? 'selected' : ''}
                      onClick={() => handleToggleSelectDoc(doc.id)}
                      style={{ cursor: 'pointer' }}
                    >
                      <td
                        style={{ textAlign: 'center', padding: '0.875rem 0.5rem' }}
                        onClick={(e) => e.stopPropagation()}
                      >
                        <input
                          type="checkbox"
                          className="custom-checkbox"
                          checked={isSelected}
                          onChange={() => handleToggleSelectDoc(doc.id)}
                          aria-label={`Select document ${doc.id}`}
                        />
                      </td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.775rem', color: 'var(--text-muted)' }}>
                        {doc.id}
                      </td>
                      <td style={{ fontWeight: 600 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                          <FileText size={15} color="var(--primary-600)" />
                          <span>{doc.source}</span>
                        </div>
                      </td>
                      <td>
                        <span className="badge badge-info">{doc.source_type}</span>
                      </td>
                      <td style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                        {doc.content_preview || doc.content?.slice(0, 160)}
                      </td>
                      <td style={{ textAlign: 'right' }} onClick={(e) => e.stopPropagation()}>
                        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', justifyContent: 'flex-end' }}>
                          <button
                            className="btn btn-secondary btn-sm"
                            onClick={() => setSelectedDoc(doc)}
                            style={{ padding: '0.25rem 0.6rem' }}
                            title="Inspect Document Summary & Details"
                          >
                            <Eye size={13} />
                            <span>Inspect</span>
                          </button>
                          <button
                            className="btn btn-danger btn-sm"
                            onClick={() => setDocToDelete(doc)}
                            style={{ padding: '0.25rem 0.6rem' }}
                            title="Delete Document"
                          >
                            <Trash2 size={13} />
                            <span>Delete</span>
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination controls */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginTop: '1.25rem',
            paddingTop: '1rem',
            borderTop: '1px solid var(--border-subtle)',
          }}
        >
          <span style={{ fontSize: '0.825rem', color: 'var(--text-muted)' }}>
            Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, totalCount)} of {totalCount}
          </span>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              className="btn btn-secondary btn-sm"
              disabled={page <= 1 || loading}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            >
              <ChevronLeft size={15} />
              <span>Previous</span>
            </button>
            <button
              className="btn btn-secondary btn-sm"
              disabled={page >= totalPages || loading}
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            >
              <span>Next</span>
              <ChevronRight size={15} />
            </button>
          </div>
        </div>
      </div>

      {/* ====================================================================
          PORTAL MODAL: DELETE CONFIRMATION POPUP
          Mounted directly to document.body to ensure absolute centering on screen
          ==================================================================== */}
      {docToDelete &&
        createPortal(
          <div
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              width: '100vw',
              height: '100vh',
              backgroundColor: 'rgba(15, 23, 42, 0.75)',
              backdropFilter: 'blur(6px)',
              zIndex: 99999,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '1.5rem',
              overflowY: 'auto',
            }}
            onClick={() => !deleting && setDocToDelete(null)}
          >
            <div
              className="card"
              style={{
                width: '100%',
                maxWidth: '520px',
                padding: '2rem',
                backgroundColor: 'var(--bg-surface)',
                boxShadow: 'var(--shadow-xl)',
                border: '1px solid var(--danger-border)',
                borderRadius: 'var(--radius-xl)',
                position: 'relative',
              }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header Icon & Title */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.25rem' }}>
                <div
                  style={{
                    width: '46px',
                    height: '46px',
                    borderRadius: '50%',
                    backgroundColor: 'var(--danger-bg)',
                    color: 'var(--danger-solid)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                    border: '1px solid var(--danger-border)',
                  }}
                >
                  <Trash2 size={22} />
                </div>
                <div>
                  <h3 style={{ fontSize: '1.25rem', color: 'var(--text-primary)', fontWeight: 800 }}>
                    Are you sure you want to delete this?
                  </h3>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    Confirm deletion of this indexed document chunk
                  </p>
                </div>
              </div>

              {/* Target Document Details */}
              <div
                style={{
                  background: 'var(--bg-muted)',
                  borderRadius: 'var(--radius-md)',
                  padding: '1rem',
                  marginBottom: '1.25rem',
                  border: '1px solid var(--border-subtle)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem', fontSize: '0.85rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Document ID:</span>
                  <strong style={{ fontFamily: 'var(--font-mono)', color: 'var(--primary-600)' }}>
                    {docToDelete.id}
                  </strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem', fontSize: '0.85rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Source File:</span>
                  <strong style={{ color: 'var(--text-primary)' }}>{docToDelete.source}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Format Type:</span>
                  <span className="badge badge-info">{docToDelete.source_type}</span>
                </div>
              </div>

              {/* Warning Notice */}
              <div
                style={{
                  padding: '0.85rem 1rem',
                  backgroundColor: 'var(--warning-bg)',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--warning-border)',
                  fontSize: '0.825rem',
                  color: 'var(--warning-text)',
                  marginBottom: '1.75rem',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '0.5rem',
                }}
              >
                <AlertTriangle size={16} style={{ flexShrink: 0, marginTop: '2px' }} />
                <span>
                  This action cannot be undone. The document chunk and its dense embeddings will be permanently removed
                  from the ChromaDB vector database.
                </span>
              </div>

              {/* Modal Buttons */}
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button
                  className="btn btn-secondary btn-sm"
                  style={{ padding: '0.5rem 1rem' }}
                  disabled={deleting}
                  onClick={() => setDocToDelete(null)}
                >
                  Cancel
                </button>
                <button
                  className="btn btn-danger btn-sm"
                  style={{ padding: '0.5rem 1.25rem' }}
                  disabled={deleting}
                  onClick={handleDeleteConfirm}
                >
                  {deleting ? <Loader2 size={15} className="pulse-indicator" /> : <Trash2 size={15} />}
                  <span>{deleting ? 'Deleting Document...' : 'Delete'}</span>
                </button>
              </div>
            </div>
          </div>,
          document.body
        )}

      {/* ====================================================================
          PORTAL MODAL: BATCH DELETE CONFIRMATION POPUP
          Mounted directly to document.body to ensure absolute centering on screen
          ==================================================================== */}
      {batchDeleteModalOpen &&
        createPortal(
          <div
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              width: '100vw',
              height: '100vh',
              backgroundColor: 'rgba(15, 23, 42, 0.75)',
              backdropFilter: 'blur(6px)',
              zIndex: 99999,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '1.5rem',
              overflowY: 'auto',
            }}
            onClick={() => !deleting && setBatchDeleteModalOpen(false)}
          >
            <div
              className="card"
              style={{
                width: '100%',
                maxWidth: '560px',
                padding: '2rem',
                backgroundColor: 'var(--bg-surface)',
                boxShadow: 'var(--shadow-xl)',
                border: '1px solid var(--danger-border)',
                borderRadius: 'var(--radius-xl)',
                position: 'relative',
              }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header Icon & Title */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.25rem' }}>
                <div
                  style={{
                    width: '46px',
                    height: '46px',
                    borderRadius: '50%',
                    backgroundColor: 'var(--danger-bg)',
                    color: 'var(--danger-solid)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                    border: '1px solid var(--danger-border)',
                  }}
                >
                  <Trash2 size={22} />
                </div>
                <div>
                  <h3 style={{ fontSize: '1.25rem', color: 'var(--text-primary)', fontWeight: 800 }}>
                    Delete {selectedDocIds.length} Selected {selectedDocIds.length === 1 ? 'Document' : 'Documents'}?
                  </h3>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    Confirm permanent deletion of multiple indexed document chunks
                  </p>
                </div>
              </div>

              {/* Target Documents List Preview */}
              <div
                style={{
                  background: 'var(--bg-muted)',
                  borderRadius: 'var(--radius-md)',
                  padding: '1rem',
                  marginBottom: '1.25rem',
                  border: '1px solid var(--border-subtle)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                    Selected Documents List
                  </span>
                  <span className="badge badge-danger">
                    {selectedDocIds.length} {selectedDocIds.length === 1 ? 'document' : 'documents'}
                  </span>
                </div>

                <div
                  style={{
                    maxHeight: '180px',
                    overflowY: 'auto',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.4rem',
                    paddingRight: '0.25rem',
                  }}
                >
                  {selectedDocIds.map((id) => {
                    const docItem = documents.find((d) => d.id === id);
                    return (
                      <div
                        key={id}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          padding: '0.5rem 0.75rem',
                          backgroundColor: 'var(--bg-surface)',
                          borderRadius: 'var(--radius-sm)',
                          border: '1px solid var(--border-subtle)',
                          fontSize: '0.825rem',
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', overflow: 'hidden' }}>
                          <FileText size={14} color="var(--primary-600)" style={{ flexShrink: 0 }} />
                          <span
                            style={{
                              fontFamily: 'var(--font-mono)',
                              fontSize: '0.775rem',
                              color: 'var(--text-muted)',
                              textOverflow: 'ellipsis',
                              overflow: 'hidden',
                              whiteSpace: 'nowrap',
                              maxWidth: '180px',
                            }}
                          >
                            {id}
                          </span>
                          {docItem?.source && (
                            <span
                              style={{
                                fontWeight: 600,
                                color: 'var(--text-primary)',
                                textOverflow: 'ellipsis',
                                overflow: 'hidden',
                                whiteSpace: 'nowrap',
                                maxWidth: '160px',
                              }}
                            >
                              ({docItem.source})
                            </span>
                          )}
                        </div>
                        {docItem?.source_type && (
                          <span className="badge badge-info" style={{ fontSize: '0.7rem' }}>
                            {docItem.source_type}
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Warning Notice */}
              <div
                style={{
                  padding: '0.85rem 1rem',
                  backgroundColor: 'var(--warning-bg)',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--warning-border)',
                  fontSize: '0.825rem',
                  color: 'var(--warning-text)',
                  marginBottom: '1.75rem',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '0.5rem',
                }}
              >
                <AlertTriangle size={16} style={{ flexShrink: 0, marginTop: '2px' }} />
                <span>
                  This action cannot be undone. All {selectedDocIds.length} selected document chunks and their vector embeddings
                  will be permanently removed from the ChromaDB vector database.
                </span>
              </div>

              {/* Modal Buttons */}
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button
                  type="button"
                  className="btn btn-secondary btn-sm"
                  style={{ padding: '0.5rem 1rem' }}
                  disabled={deleting}
                  onClick={() => setBatchDeleteModalOpen(false)}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  className="btn btn-danger btn-sm"
                  style={{ padding: '0.5rem 1.25rem' }}
                  disabled={deleting}
                  onClick={handleBatchDeleteConfirm}
                >
                  {deleting ? <Loader2 size={15} className="pulse-indicator" /> : <Trash2 size={15} />}
                  <span>{deleting ? `Deleting ${selectedDocIds.length} Documents...` : `Delete ${selectedDocIds.length} Documents`}</span>
                </button>
              </div>
            </div>
          </div>,
          document.body
        )}

      {/* ====================================================================
          PORTAL MODAL: INSPECT DOCUMENT SUMMARY & DETAILS
          Mounted directly to document.body to ensure absolute centering on screen
          ==================================================================== */}
      {selectedDoc &&
        createPortal(
          <div
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              width: '100vw',
              height: '100vh',
              backgroundColor: 'rgba(15, 23, 42, 0.75)',
              backdropFilter: 'blur(6px)',
              zIndex: 99999,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '1.5rem',
              overflowY: 'auto',
            }}
            onClick={() => setSelectedDoc(null)}
          >
            <div
              className="card"
              style={{
                width: '100%',
                maxWidth: '820px',
                maxHeight: '90vh',
                overflowY: 'auto',
                padding: '2rem',
                backgroundColor: 'var(--bg-surface)',
                boxShadow: 'var(--shadow-xl)',
                borderRadius: 'var(--radius-xl)',
                position: 'relative',
              }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Modal Top Header */}
              <div className="card-header" style={{ marginBottom: '1.5rem', alignItems: 'flex-start' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
                    <span className="badge badge-primary">{selectedDoc.source_type}</span>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      ID: {selectedDoc.id}
                    </span>
                  </div>
                  <h3 className="card-title" style={{ fontSize: '1.35rem' }}>
                    {selectedDoc.source}
                  </h3>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    Document Details & Parsed Summary
                  </p>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <button
                    type="button"
                    className={`btn btn-sm ${selectedDocIds.includes(selectedDoc.id) ? 'btn-primary' : 'btn-secondary'}`}
                    style={{ padding: '0.35rem 0.75rem' }}
                    onClick={() => handleToggleSelectDoc(selectedDoc.id)}
                    title={selectedDocIds.includes(selectedDoc.id) ? 'Remove from multiple selection' : 'Add to multiple selection'}
                  >
                    <CheckSquare size={14} />
                    <span>{selectedDocIds.includes(selectedDoc.id) ? 'Selected' : 'Select'}</span>
                  </button>
                  <button
                    className="btn btn-danger btn-sm"
                    style={{ padding: '0.35rem 0.75rem' }}
                    onClick={() => setDocToDelete(selectedDoc)}
                    title="Delete Document"
                  >
                    <Trash2 size={14} />
                    <span>Delete</span>
                  </button>
                  <button
                    style={{
                      background: 'var(--bg-muted)',
                      border: 'none',
                      borderRadius: '50%',
                      width: '32px',
                      height: '32px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      cursor: 'pointer',
                      color: 'var(--text-muted)',
                    }}
                    onClick={() => setSelectedDoc(null)}
                    title="Close"
                  >
                    <X size={18} />
                  </button>
                </div>
              </div>

              {/* Document Overview Metrics Pills */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(3, 1fr)',
                  gap: '1rem',
                  marginBottom: '1.5rem',
                }}
              >
                <div style={{ padding: '0.75rem 1rem', background: 'var(--bg-muted)', borderRadius: 'var(--radius-md)' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Total Words</span>
                  <strong style={{ fontSize: '1.15rem', color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>
                    {contentWordCount.toLocaleString()}
                  </strong>
                </div>
                <div style={{ padding: '0.75rem 1rem', background: 'var(--bg-muted)', borderRadius: 'var(--radius-md)' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Characters</span>
                  <strong style={{ fontSize: '1.15rem', color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>
                    {contentCharCount.toLocaleString()}
                  </strong>
                </div>
                <div style={{ padding: '0.75rem 1rem', background: 'var(--bg-muted)', borderRadius: 'var(--radius-md)' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Source Format</span>
                  <strong style={{ fontSize: '1.15rem', color: 'var(--primary-600)', textTransform: 'uppercase' }}>
                    {selectedDoc.source_type}
                  </strong>
                </div>
              </div>

              {/* Parsed Structured Fields Summary (if available) */}
              {parsedSummary && parsedSummary.length > 0 && (
                <div style={{ marginBottom: '1.5rem' }}>
                  <h4 style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: '0.65rem' }}>
                    Structured Record Summary
                  </h4>
                  <div
                    style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
                      gap: '0.65rem',
                      background: 'var(--bg-muted)',
                      padding: '1rem',
                      borderRadius: 'var(--radius-lg)',
                      border: '1px solid var(--border-subtle)',
                    }}
                  >
                    {parsedSummary.map(([field, value], idx) => (
                      <div
                        key={idx}
                        style={{
                          background: 'var(--bg-surface)',
                          padding: '0.5rem 0.75rem',
                          borderRadius: 'var(--radius-sm)',
                          border: '1px solid var(--border-main)',
                        }}
                      >
                        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', textTransform: 'uppercase' }}>
                          {field}
                        </span>
                        <strong style={{ fontSize: '0.85rem', color: 'var(--text-primary)', wordBreak: 'break-all' }}>
                          {value || '—'}
                        </strong>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Full Document Content */}
              <div style={{ marginBottom: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <h4 style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)' }}>
                    Document Content Text
                  </h4>
                  <button className="btn btn-secondary btn-sm" onClick={handleCopyContent}>
                    {copied ? <Check size={13} color="#10B981" /> : <Copy size={13} />}
                    <span>{copied ? 'Copied' : 'Copy Content'}</span>
                  </button>
                </div>
                <pre
                  style={{
                    backgroundColor: 'var(--bg-muted)',
                    border: '1px solid var(--border-main)',
                    borderRadius: 'var(--radius-md)',
                    padding: '1.25rem',
                    fontSize: '0.875rem',
                    fontFamily: 'var(--font-mono)',
                    color: 'var(--text-primary)',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                    maxHeight: '260px',
                    overflowY: 'auto',
                    lineHeight: 1.6,
                  }}
                >
                  {selectedDoc.content || 'No text content available'}
                </pre>
              </div>

              {/* Document Metadata */}
              <div>
                <h4 style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                  Vector Metadata JSON
                </h4>
                <pre
                  style={{
                    backgroundColor: 'var(--bg-code)',
                    borderRadius: 'var(--radius-md)',
                    padding: '1rem',
                    fontSize: '0.8rem',
                    fontFamily: 'var(--font-mono)',
                    color: '#93C5FD',
                    maxHeight: '180px',
                    overflowY: 'auto',
                  }}
                >
                  {JSON.stringify(selectedDoc.metadata || {}, null, 2)}
                </pre>
              </div>

              {/* Close Button in Footer */}
              <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1.5rem' }}>
                <button className="btn btn-secondary btn-sm" onClick={() => setSelectedDoc(null)}>
                  Close
                </button>
              </div>
            </div>
          </div>,
          document.body
        )}
    </div>
  );
};
