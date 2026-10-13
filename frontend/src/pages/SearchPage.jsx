import React, { useState } from 'react';
import {
  Search,
  SlidersHorizontal,
  FileText,
  ChevronDown,
  ChevronUp,
  Sparkles,
  Loader2,
  Filter,
  CheckCircle2,
} from 'lucide-react';

export const SearchPage = () => {
  const [query, setQuery] = useState('');
  const [numResults, setNumResults] = useState(10);
  const [loading, setLoading] = useState(false);
  const [searchResponse, setSearchResponse] = useState(null);
  const [error, setError] = useState(null);

  // Filters
  const [selectedSources, setSelectedSources] = useState([]);
  const [selectedTypes, setSelectedTypes] = useState([]);
  const [expandedIndex, setExpandedIndex] = useState(null);

  const sampleQueries = [
    'Augmented Analytics',
    'Customer transactions and revenue',
    'Alice',
    'Machine learning pipeline',
    'Data quality and validation',
  ];

  const handleSearch = async (searchQuery = query) => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    setError(null);
    setExpandedIndex(null);

    try {
      const res = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchQuery.trim(), n_results: numResults }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Search failed');
      }

      const data = await res.json();
      setSearchResponse(data);
      setSelectedSources(data.available_sources || []);
      setSelectedTypes(data.available_types || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const results = searchResponse?.results || [];
  const filteredResults = results.filter(
    (r) =>
      selectedSources.includes(String(r.source)) &&
      selectedTypes.includes(String(r.source_type))
  );

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Header */}
      <div>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
          Semantic Vector Search
        </h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
          Query across all ingested text and document chunks using dense vector embeddings in ChromaDB.
        </p>
      </div>

      {/* Search Input Box */}
      <div className="card" style={{ padding: '1.75rem' }}>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSearch();
          }}
          style={{ display: 'flex', gap: '0.75rem', marginBottom: '1rem' }}
        >
          <div style={{ position: 'relative', flex: 1 }}>
            <Search
              size={18}
              style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }}
            />
            <input
              type="text"
              className="input"
              style={{ paddingLeft: '2.6rem', fontSize: '1rem', padding: '0.75rem 0.85rem 0.75rem 2.6rem' }}
              placeholder="What are you looking for? (e.g. topics, claims, users)..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>

          <select
            className="select"
            style={{ width: '130px', fontWeight: 600 }}
            value={numResults}
            onChange={(e) => setNumResults(Number(e.target.value))}
          >
            <option value="5">Top 5</option>
            <option value="10">Top 10</option>
            <option value="20">Top 20</option>
          </select>

          <button type="submit" className="btn btn-primary" disabled={loading || !query.trim()}>
            {loading ? <Loader2 size={16} className="pulse-indicator" /> : <Search size={16} />}
            <span>Search</span>
          </button>
        </form>

        {/* Quick query chips */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>Try queries:</span>
          {sampleQueries.map((q, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                setQuery(q);
                handleSearch(q);
              }}
              style={{
                background: 'var(--bg-muted)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-full)',
                padding: '0.25rem 0.65rem',
                fontSize: '0.75rem',
                color: 'var(--text-secondary)',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="card" style={{ background: 'var(--danger-bg)', borderColor: 'var(--danger-border)' }}>
          <p style={{ color: 'var(--danger-text)', fontSize: '0.9rem', fontWeight: 600 }}>{error}</p>
        </div>
      )}

      {/* Filter and Results Section */}
      {searchResponse && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Active filters */}
          <div
            className="card"
            style={{ padding: '1rem 1.25rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.825rem', fontWeight: 700, color: 'var(--text-muted)' }}>
                <Filter size={14} />
                <span>FILTER RESULTS:</span>
              </div>

              {/* Source filter */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', flexWrap: 'wrap' }}>
                {searchResponse.available_sources.map((s, idx) => {
                  const isChecked = selectedSources.includes(s);
                  return (
                    <button
                      key={idx}
                      className={`badge ${isChecked ? 'badge-primary' : 'badge-info'}`}
                      style={{ cursor: 'pointer', opacity: isChecked ? 1 : 0.4 }}
                      onClick={() =>
                        setSelectedSources((prev) =>
                          isChecked ? prev.filter((item) => item !== s) : [...prev, s]
                        )
                      }
                    >
                      {s}
                    </button>
                  );
                })}
              </div>

              {/* Type filter */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', flexWrap: 'wrap' }}>
                {searchResponse.available_types.map((t, idx) => {
                  const isChecked = selectedTypes.includes(t);
                  return (
                    <button
                      key={idx}
                      className={`badge ${isChecked ? 'badge-success' : 'badge-info'}`}
                      style={{ cursor: 'pointer', opacity: isChecked ? 1 : 0.4 }}
                      onClick={() =>
                        setSelectedTypes((prev) =>
                          isChecked ? prev.filter((item) => item !== t) : [...prev, t]
                        )
                      }
                    >
                      .{t}
                    </button>
                  );
                })}
              </div>
            </div>

            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Showing {filteredResults.length} of {searchResponse.count} matches
            </span>
          </div>

          {/* Results list */}
          {filteredResults.length === 0 ? (
            <div className="card" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              <p>No results match the selected source and format filters.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {filteredResults.map((result, idx) => {
                const isExpanded = expandedIndex === idx;
                return (
                  <div key={result.id || idx} className="card" style={{ padding: '1.25rem 1.5rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.25rem' }}>
                          <span style={{ fontWeight: 700, fontSize: '0.85rem', color: 'var(--primary-600)' }}>
                            #{idx + 1}
                          </span>
                          <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{result.source}</span>
                          <span className="badge badge-info">{result.source_type}</span>
                        </div>
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-light)' }}>
                          ID: {result.id}
                        </span>
                      </div>

                      {result.distance !== null && (
                        <div style={{ textAlign: 'right' }}>
                          <span className="badge badge-success">
                            Distance: {Number(result.distance).toFixed(4)}
                          </span>
                        </div>
                      )}
                    </div>

                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.6, marginBottom: '0.75rem' }}>
                      {result.preview}
                    </p>

                    <button
                      className="btn btn-secondary btn-sm"
                      style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                      onClick={() => setExpandedIndex(isExpanded ? null : idx)}
                    >
                      <span>{isExpanded ? 'Hide Raw Details' : 'View Full Content & Metadata'}</span>
                      {isExpanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
                    </button>

                    {isExpanded && (
                      <div className="animate-fade-in" style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border-subtle)' }}>
                        <div style={{ marginBottom: '0.75rem' }}>
                          <strong style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>FULL CHUNK:</strong>
                          <pre
                            style={{
                              backgroundColor: 'var(--bg-muted)',
                              padding: '0.75rem',
                              borderRadius: 'var(--radius-sm)',
                              fontSize: '0.825rem',
                              fontFamily: 'var(--font-mono)',
                              marginTop: '0.35rem',
                              whiteSpace: 'pre-wrap',
                            }}
                          >
                            {result.content}
                          </pre>
                        </div>
                        <div>
                          <strong style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>METADATA:</strong>
                          <pre
                            style={{
                              backgroundColor: 'var(--bg-code)',
                              color: '#93C5FD',
                              padding: '0.75rem',
                              borderRadius: 'var(--radius-sm)',
                              fontSize: '0.75rem',
                              fontFamily: 'var(--font-mono)',
                              marginTop: '0.35rem',
                            }}
                          >
                            {JSON.stringify(result.metadata || {}, null, 2)}
                          </pre>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
