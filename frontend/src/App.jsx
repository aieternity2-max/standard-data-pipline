import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { OverviewPage } from './pages/OverviewPage';
import { UploadPage } from './pages/UploadPage';
import { ExplorePage } from './pages/ExplorePage';
import { SearchPage } from './pages/SearchPage';
import { AskAIPage } from './pages/AskAIPage';
import { DashboardsPage } from './pages/DashboardsPage';
import { SettingsPage } from './pages/SettingsPage';

export function App() {
  const [activePage, setActivePage] = useState('overview');
  const [stats, setStats] = useState({});
  const [health, setHealth] = useState({});
  const [loading, setLoading] = useState(false);
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('insightsphere_theme') || 'light';
  });

  // Apply Theme
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('insightsphere_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  // Fetch overview & health stats
  const fetchSystemData = async () => {
    setLoading(true);
    try {
      const [healthRes, overviewRes] = await Promise.all([
        fetch('/api/health'),
        fetch('/api/overview'),
      ]);

      if (healthRes.ok) {
        const healthData = await healthRes.json();
        setHealth(healthData);
      }
      if (overviewRes.ok) {
        const overviewData = await overviewRes.json();
        setStats(overviewData);
      }
    } catch (err) {
      console.error('Failed to sync system status:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSystemData();
  }, []);

  const pageTitles = {
    overview: { title: 'Overview', subtitle: 'Standard Ingestion Pipeline & Analytics Workspace' },
    upload: { title: 'Upload Data', subtitle: 'Staged file parsing, previewing, and pipeline ingestion' },
    explore: { title: 'Explore Data', subtitle: 'Browse vector document chunks and verify metadata' },
    search: { title: 'Semantic Search', subtitle: 'Dense vector retrieval and similarity scoring' },
    'ask-ai': { title: 'Ask AI (RAG)', subtitle: 'Retrieval-Augmented Generation grounded in indexed records' },
    dashboards: { title: 'Business Dashboards', subtitle: 'Financial KPIs, payment metrics, and customer segmentation' },
    settings: { title: 'Pipeline Config', subtitle: 'MySQL database, ChromaDB vector store, and runtime settings' },
  };

  const currentMeta = pageTitles[activePage] || { title: 'InsightSphere', subtitle: '' };

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <Sidebar
        activePage={activePage}
        onNavigate={setActivePage}
        stats={stats}
        health={health}
        theme={theme}
        onToggleTheme={toggleTheme}
      />

      {/* Main Content Area */}
      <div className="app-main">
        <Header
          pageTitle={currentMeta.title}
          pageSubtitle={currentMeta.subtitle}
          health={health}
          loading={loading}
          onRefresh={fetchSystemData}
        />

        <main className="content-viewport">
          {activePage === 'overview' && (
            <OverviewPage
              stats={stats}
              health={health}
              onNavigate={setActivePage}
            />
          )}

          {activePage === 'upload' && (
            <UploadPage onIngestionSuccess={fetchSystemData} />
          )}

          {activePage === 'explore' && (
            <ExplorePage health={health} onDocumentDeleted={fetchSystemData} />
          )}

          {activePage === 'search' && <SearchPage />}

          {activePage === 'ask-ai' && <AskAIPage />}

          {activePage === 'dashboards' && <DashboardsPage />}

          {activePage === 'settings' && (
            <SettingsPage health={health} onRefreshHealth={fetchSystemData} />
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
