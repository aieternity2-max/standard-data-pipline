import React, { useState } from 'react';
import {
  Sparkles,
  Send,
  Loader2,
  BookOpen,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  FileText,
  Bot,
  User,
  Lightbulb,
} from 'lucide-react';

export const AskAIPage = () => {
  const [query, setQuery] = useState('');
  const [nResults, setNResults] = useState(5);
  const [loading, setLoading] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [error, setError] = useState(null);
  const [copiedId, setCopiedId] = useState(null);
  const [expandedContextId, setExpandedContextId] = useState(null);

  const samplePrompts = [
    'What are the trending topics in Analytics according to the uploaded documents?',
    'Summarize our high value customer segment and their transactions',
    'What payment transaction anomalies were identified?',
    'Explain the data ingestion and validation pipeline steps',
  ];

  const handleAsk = async (userQuery = query) => {
    if (!userQuery.trim()) return;
    setLoading(true);
    setError(null);

    const questionText = userQuery.trim();
    setQuery('');

    try {
      const res = await fetch('/api/rag/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: questionText, n_results: nResults }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'RAG generation failed');
      }

      const data = await res.json();
      setConversations((prev) => [
        {
          id: Date.now(),
          query: data.query,
          answer: data.answer,
          context: data.context,
          sources: data.sources || [],
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
        ...prev,
      ]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Header */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
          <Sparkles size={24} color="#D97706" />
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-primary)' }}>
            Ask AI — Grounded RAG Assistant
          </h2>
        </div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
          Ask natural language questions. InsightSphere retrieves relevant vector embeddings and grounds its synthesized
          answers in your indexed documents and structured business records.
        </p>
      </div>

      {/* Query Input Card */}
      <div className="card" style={{ padding: '1.5rem' }}>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleAsk();
          }}
          style={{ display: 'flex', gap: '0.75rem', marginBottom: '1rem' }}
        >
          <input
            type="text"
            className="input"
            style={{ fontSize: '1rem', padding: '0.75rem 1rem' }}
            placeholder="Ask a question grounded in your data (e.g. 'What are the main insights in the documents?')..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />

          <select
            className="select"
            style={{ width: '130px', fontWeight: 600 }}
            value={nResults}
            onChange={(e) => setNResults(Number(e.target.value))}
            title="Number of Context Documents Retrieved"
          >
            <option value="3">Top 3 Context</option>
            <option value="5">Top 5 Context</option>
            <option value="8">Top 8 Context</option>
          </select>

          <button type="submit" className="btn btn-primary" disabled={loading || !query.trim()}>
            {loading ? <Loader2 size={16} className="pulse-indicator" /> : <Send size={16} />}
            <span>Ask</span>
          </button>
        </form>

        {/* Suggestion Chips */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
          <Lightbulb size={14} color="#D97706" />
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>Sample Prompts:</span>
          {samplePrompts.map((p, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                setQuery(p);
                handleAsk(p);
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
              {p}
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

      {/* Loading state indicator */}
      {loading && (
        <div className="card animate-fade-in" style={{ padding: '2rem', textAlign: 'center' }}>
          <Loader2 size={28} className="pulse-indicator" color="var(--primary-600)" style={{ margin: '0 auto 0.75rem' }} />
          <h4 style={{ color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
            Retrieving Context & Synthesizing Answer...
          </h4>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Searching vector space in ChromaDB and querying the LLM provider.
          </p>
        </div>
      )}

      {/* Conversation Thread */}
      {conversations.length === 0 && !loading && (
        <div
          className="card"
          style={{
            padding: '4rem 2rem',
            textAlign: 'center',
            color: 'var(--text-muted)',
            border: '2px dashed var(--border-main)',
          }}
        >
          <Bot size={44} style={{ margin: '0 auto 1rem', opacity: 0.5, color: 'var(--primary-600)' }} />
          <h3 style={{ fontSize: '1.2rem', color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
            No questions asked yet
          </h3>
          <p style={{ maxWidth: '460px', margin: '0 auto', fontSize: '0.9rem' }}>
            Enter a prompt above or click one of the suggested sample questions to get answers grounded in your ingested documents.
          </p>
        </div>
      )}

      {conversations.map((item) => {
        const isContextExpanded = expandedContextId === item.id;
        return (
          <div key={item.id} className="card animate-fade-in" style={{ padding: '1.75rem' }}>
            {/* User Question */}
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem', marginBottom: '1.25rem' }}>
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  background: 'var(--bg-muted)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                }}
              >
                <User size={16} color="var(--text-muted)" />
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>{item.query}</h4>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-light)' }}>{item.timestamp}</span>
                </div>
              </div>
            </div>

            {/* AI Response Card */}
            <div
              style={{
                backgroundColor: 'var(--bg-muted)',
                borderRadius: 'var(--radius-lg)',
                padding: '1.5rem',
                border: '1px solid var(--border-subtle)',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <div
                    style={{
                      width: '24px',
                      height: '24px',
                      borderRadius: 'var(--radius-sm)',
                      background: 'var(--primary-gradient)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'white',
                    }}
                  >
                    <Sparkles size={14} />
                  </div>
                  <strong style={{ fontSize: '0.85rem', color: 'var(--text-primary)' }}>InsightSphere AI</strong>
                </div>

                <button
                  className="btn btn-secondary btn-sm"
                  style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }}
                  onClick={() => handleCopy(item.id, item.answer)}
                >
                  {copiedId === item.id ? <Check size={12} color="#10B981" /> : <Copy size={12} />}
                  <span>{copiedId === item.id ? 'Copied' : 'Copy'}</span>
                </button>
              </div>

              {/* Answer Content */}
              <div
                style={{
                  color: 'var(--text-primary)',
                  fontSize: '0.95rem',
                  lineHeight: 1.65,
                  whiteSpace: 'pre-wrap',
                  marginBottom: '1.25rem',
                }}
              >
                {item.answer}
              </div>

              {/* Sources Chips */}
              {item.sources && item.sources.length > 0 && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '0.75rem' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>CITED SOURCES:</span>
                  {item.sources.map((src, sIdx) => (
                    <span key={sIdx} className="badge badge-primary">
                      <FileText size={11} />
                      <span>{src}</span>
                    </span>
                  ))}
                </div>
              )}

              {/* Retrieved Context Dropdown */}
              {item.context && (
                <div style={{ marginTop: '0.75rem' }}>
                  <button
                    style={{
                      background: 'transparent',
                      border: 'none',
                      color: 'var(--primary-600)',
                      fontSize: '0.8rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.35rem',
                    }}
                    onClick={() => setExpandedContextId(isContextExpanded ? null : item.id)}
                  >
                    <BookOpen size={13} />
                    <span>{isContextExpanded ? 'Hide Grounded Context' : 'Inspect Retrieved RAG Context'}</span>
                    {isContextExpanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
                  </button>

                  {isContextExpanded && (
                    <pre
                      style={{
                        backgroundColor: 'var(--bg-code)',
                        color: '#93C5FD',
                        borderRadius: 'var(--radius-md)',
                        padding: '1rem',
                        fontSize: '0.8rem',
                        fontFamily: 'var(--font-mono)',
                        whiteSpace: 'pre-wrap',
                        marginTop: '0.5rem',
                        maxHeight: '250px',
                        overflowY: 'auto',
                      }}
                    >
                      {item.context}
                    </pre>
                  )}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};
