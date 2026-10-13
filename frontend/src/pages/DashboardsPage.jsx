import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  TrendingUp,
  AlertTriangle,
  Users,
  ShoppingBag,
  DollarSign,
  RotateCw,
  Globe,
  ShieldAlert,
  Loader2,
  CheckCircle2,
  Layers,
} from 'lucide-react';
import { LineTrendChart, BarDistributionChart, DonutBreakdown } from '../components/Charts';

export const DashboardsPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboards = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/dashboards');
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Failed to load dashboards');
      }
      const analyticsData = await res.json();
      setData(analyticsData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboards();
  }, []);

  const formatCurrency = (val) => {
    try {
      return `₹${Number(val || 0).toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })}`;
    } catch {
      return `₹0.00`;
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '5rem 0', textAlign: 'center' }}>
        <Loader2 size={32} className="pulse-indicator" color="var(--primary-600)" style={{ margin: '0 auto 1rem' }} />
        <h3 style={{ color: 'var(--text-primary)', marginBottom: '0.25rem' }}>Loading Business Analytics</h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
          Querying MySQL database and calculating metrics...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card" style={{ borderColor: 'var(--danger-border)', background: 'var(--danger-bg)' }}>
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start', color: 'var(--danger-text)' }}>
          <AlertTriangle size={24} style={{ flexShrink: 0 }} />
          <div>
            <h3 style={{ fontWeight: 800, marginBottom: '0.25rem' }}>Unable to Load Business Analytics</h3>
            <p style={{ fontSize: '0.9rem', marginBottom: '1rem' }}>{error}</p>
            <button className="btn btn-primary btn-sm" onClick={fetchDashboards}>
              <RotateCw size={14} />
              <span>Retry</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  const revenue = data?.revenue || {};
  const payments = data?.payments || {};
  const customers = data?.customers || {};
  const segmentation = data?.segmentation || {};
  const anomalies = data?.anomalies || {};
  const products = data?.products || {};

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
            Business Analytics & Intelligence Dashboards
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
            Real-time financial performance, payment completion rates, customer segmentation, and transaction anomaly indicators.
          </p>
        </div>
        <button className="btn btn-secondary btn-sm" onClick={fetchDashboards}>
          <RotateCw size={14} />
          <span>Refresh Analytics</span>
        </button>
      </div>

      {/* ====================================================================
          1. PAYMENT & TRANSACTION ANALYSIS
          ==================================================================== */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
          <DollarSign size={20} color="var(--primary-600)" />
          <h3 style={{ fontSize: '1.25rem', color: 'var(--text-primary)' }}>
            Payment & Transaction Performance
          </h3>
        </div>

        {/* Payment Metrics */}
        <div className="grid-5" style={{ marginBottom: '1.5rem' }}>
          <div className="stat-card">
            <span className="stat-label">Completed Value</span>
            <div className="stat-value" style={{ color: 'var(--success-solid)' }}>
              {formatCurrency(revenue.completed_transaction_value)}
            </div>
            <div className="stat-footer">Gross settled revenue</div>
          </div>

          <div className="stat-card">
            <span className="stat-label">Total Transactions</span>
            <div className="stat-value">{Number(payments.total_transactions || 0).toLocaleString()}</div>
            <div className="stat-footer">Logged in pipeline</div>
          </div>

          <div className="stat-card">
            <span className="stat-label">Completion Rate</span>
            <div className="stat-value" style={{ color: 'var(--primary-600)' }}>
              {Number(payments.completion_rate_pct || 0).toFixed(1)}%
            </div>
            <div className="stat-footer">Success conversion</div>
          </div>

          <div className="stat-card">
            <span className="stat-label">Failed Transactions</span>
            <div className="stat-value" style={{ color: 'var(--danger-solid)' }}>
              {Number(payments.failed_transactions || 0).toLocaleString()}
            </div>
            <div className="stat-footer">Potential leakage</div>
          </div>

          <div className="stat-card">
            <span className="stat-label">Pending Transactions</span>
            <div className="stat-value" style={{ color: 'var(--warning-solid)' }}>
              {Number(payments.pending_transactions || 0).toLocaleString()}
            </div>
            <div className="stat-footer">Awaiting settlement</div>
          </div>
        </div>

        <div className="grid-2">
          {/* Monthly Completed Value Trend */}
          <div className="card">
            <div className="card-header">
              <div>
                <h4 className="card-title">Monthly Completed Transaction Value</h4>
                <p className="card-subtitle">Revenue trend aggregated over billing periods</p>
              </div>
            </div>
            <LineTrendChart
              data={revenue.revenue_trend || []}
              xKey="period"
              yKey="completed_transaction_value"
              formatValue={(val) => `₹${Number(val).toLocaleString()}`}
            />
          </div>

          {/* Transaction Status Breakdown */}
          <div className="card">
            <div className="card-header">
              <div>
                <h4 className="card-title">Transaction Status & Value Distribution</h4>
                <p className="card-subtitle">Completed vs Pending vs Failed volume</p>
              </div>
            </div>
            <DonutBreakdown
              items={[
                { label: 'Completed', value: Number(payments.completed_transactions || 0), color: '#10B981' },
                { label: 'Pending', value: Number(payments.pending_transactions || 0), color: '#F59E0B' },
                { label: 'Failed', value: Number(payments.failed_transactions || 0), color: '#EF4444' },
                ...(Number(payments.refunded_transactions || 0) > 0 ? [
                  { label: 'Refunded', value: Number(payments.refunded_transactions), color: '#8B5CF6' }
                ] : []),
              ]}
            />
            <div style={{ marginTop: '1.5rem', borderTop: '1px solid var(--border-subtle)', paddingTop: '1rem' }}>
              <BarDistributionChart
                data={[
                  { category: 'Completed Value', amount: Number(revenue.completed_transaction_value || 0) },
                  { category: 'Pending Value', amount: Number(payments.pending_transaction_value || 0) },
                  { category: 'Failed Value', amount: Number(payments.failed_transaction_value || 0) },
                  ...(Number(payments.refunded_transaction_value || 0) > 0 ? [
                    { category: 'Refunded Value', amount: Number(payments.refunded_transaction_value) }
                  ] : []),
                ]}
                xKey="category"
                yKey="amount"
                color="#2563EB"
                formatValue={(val) => formatCurrency(val)}
              />
            </div>
          </div>
        </div>
      </div>

      {/* ====================================================================
          2. CUSTOMER ANALYTICS & GEOGRAPHY
          ==================================================================== */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
          <Users size={20} color="#059669" />
          <h3 style={{ fontSize: '1.25rem', color: 'var(--text-primary)' }}>
            Customer Analytics & Demographic Reach
          </h3>
        </div>

        <div className="grid-4" style={{ marginBottom: '1.5rem' }}>
          <div className="stat-card">
            <span className="stat-label">Total Customers</span>
            <div className="stat-value">{Number(customers.total_customers || 0).toLocaleString()}</div>
            <div className="stat-footer">Registered in system</div>
          </div>

          <div className="stat-card">
            <span className="stat-label">Active Transacting</span>
            <div className="stat-value" style={{ color: 'var(--success-solid)' }}>
              {Number(customers.customers_with_transactions || 0).toLocaleString()}
            </div>
            <div className="stat-footer">Made at least 1 purchase</div>
          </div>

          <div className="stat-card">
            <span className="stat-label">Without Transactions</span>
            <div className="stat-value" style={{ color: 'var(--text-muted)' }}>
              {Number(customers.customers_without_transactions || 0).toLocaleString()}
            </div>
            <div className="stat-footer">Onboarding prospects</div>
          </div>

          <div className="stat-card">
            <span className="stat-label">Countries Represented</span>
            <div className="stat-value">{Number(customers.countries_represented || 0).toLocaleString()}</div>
            <div className="stat-footer">Global footprint</div>
          </div>
        </div>

        <div className="grid-2">
          {/* Country Distribution Chart */}
          <div className="card">
            <div className="card-header">
              <div>
                <h4 className="card-title">Customers by Country</h4>
                <p className="card-subtitle">Demographic customer dispersion</p>
              </div>
            </div>
            <BarDistributionChart
              data={customers.country_distribution || []}
              xKey="country"
              yKey="customer_count"
              color="#059669"
              formatValue={(v) => `${v} users`}
            />
          </div>

          {/* Country Ranked Table */}
          <div className="card">
            <div className="card-header">
              <div>
                <h4 className="card-title">Country Details</h4>
                <p className="card-subtitle">Active country market breakdown</p>
              </div>
            </div>
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Country</th>
                    <th style={{ textAlign: 'right' }}>Customers</th>
                  </tr>
                </thead>
                <tbody>
                  {(customers.country_distribution || []).map((c, i) => (
                    <tr key={i}>
                      <td style={{ fontWeight: 600, textTransform: 'capitalize' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                          <Globe size={14} color="var(--primary-600)" />
                          <span>{c.country}</span>
                        </div>
                      </td>
                      <td style={{ textAlign: 'right', fontFamily: 'var(--font-mono)', fontWeight: 700 }}>
                        {c.customer_count}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      {/* ====================================================================
          3. CUSTOMER VALUE SEGMENTATION (RFM)
          ==================================================================== */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
          <Layers size={20} color="#7C3AED" />
          <h3 style={{ fontSize: '1.25rem', color: 'var(--text-primary)' }}>
            Customer Value Segmentation
          </h3>
        </div>

        <div className="grid-3" style={{ marginBottom: '1.5rem' }}>
          <div className="stat-card">
            <span className="stat-label">Customers Analysed</span>
            <div className="stat-value">{Number(segmentation.customer_count || 0).toLocaleString()}</div>
            <div className="stat-footer">Segmented by spend thresholds</div>
          </div>

          <div className="stat-card">
            <span className="stat-label">Total Segmented Value</span>
            <div className="stat-value" style={{ color: 'var(--primary-600)' }}>
              {formatCurrency(segmentation.total_completed_transaction_value)}
            </div>
            <div className="stat-footer">Completed transaction base</div>
          </div>

          <div className="stat-card">
            <span className="stat-label">Segmentation Date</span>
            <div className="stat-value" style={{ fontSize: '1.4rem' }}>
              {segmentation.as_of_date || 'Current'}
            </div>
            <div className="stat-footer">Thresholds: High (₹200+), Reg (₹50+)</div>
          </div>
        </div>

        <div className="grid-2">
          {/* Segment by Count */}
          <div className="card">
            <div className="card-header">
              <h4 className="card-title">Customers by Segment</h4>
            </div>
            <BarDistributionChart
              data={segmentation.segment_summary || []}
              xKey="customer_segment"
              yKey="customer_count"
              color="#7C3AED"
              formatValue={(v) => `${v} users`}
            />
          </div>

          {/* Segment by Value */}
          <div className="card">
            <div className="card-header">
              <h4 className="card-title">Completed Value by Segment</h4>
            </div>
            <BarDistributionChart
              data={segmentation.segment_summary || []}
              xKey="customer_segment"
              yKey="total_completed_value"
              color="#2563EB"
              formatValue={(v) => formatCurrency(v)}
            />
          </div>
        </div>
      </div>

      {/* ====================================================================
          4. TRANSACTION ANOMALY INDICATORS
          ==================================================================== */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
          <ShieldAlert size={20} color="#EF4444" />
          <h3 style={{ fontSize: '1.25rem', color: 'var(--text-primary)' }}>
            Transaction Anomaly Indicators
          </h3>
        </div>

        <div className="grid-3" style={{ marginBottom: '1.5rem' }}>
          <div className="stat-card">
            <span className="stat-label">Transactions Analysed</span>
            <div className="stat-value">{Number(anomalies.transaction_count || 0).toLocaleString()}</div>
            <div className="stat-footer">Rule-based auditing</div>
          </div>

          <div className="stat-card">
            <span className="stat-label">Anomaly Flags</span>
            <div className="stat-value" style={{ color: anomalies.anomaly_count > 0 ? '#EF4444' : '#10B981' }}>
              {Number(anomalies.anomaly_count || 0).toLocaleString()}
            </div>
            <div className="stat-footer">Triggered flag events</div>
          </div>

          <div className="stat-card">
            <span className="stat-label">Affected Customers</span>
            <div className="stat-value">{Number(anomalies.affected_customer_count || 0).toLocaleString()}</div>
            <div className="stat-footer">Requiring verification</div>
          </div>
        </div>

        {anomalies.anomaly_count === 0 ? (
          <div className="card" style={{ padding: '2rem', textAlign: 'center', background: 'var(--success-bg)', borderColor: 'var(--success-border)' }}>
            <CheckCircle2 size={32} color="var(--success-solid)" style={{ margin: '0 auto 0.5rem' }} />
            <h4 style={{ color: 'var(--success-text)', marginBottom: '0.25rem' }}>No Anomaly Flags Detected</h4>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              All checked transactions passed automated velocity and amount validation rules.
            </p>
          </div>
        ) : (
          <div className="card">
            <div className="card-header">
              <h4 className="card-title">Flagged Transactions</h4>
            </div>
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Transaction ID</th>
                    <th>User ID</th>
                    <th>Rule Triggered</th>
                    <th>Amount</th>
                    <th>Reason</th>
                  </tr>
                </thead>
                <tbody>
                  {(anomalies.anomalies || []).map((a, i) => (
                    <tr key={i}>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>{a.transaction_id}</td>
                      <td>{a.user_id}</td>
                      <td><span className="badge badge-danger">{a.rule}</span></td>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>{formatCurrency(a.amount)}</td>
                      <td style={{ color: 'var(--text-secondary)' }}>{a.description}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* ====================================================================
          5. PRODUCT CATALOGUE HEALTH
          ==================================================================== */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
          <ShoppingBag size={20} color="#D97706" />
          <h3 style={{ fontSize: '1.25rem', color: 'var(--text-primary)' }}>
            Product Catalogue Health
          </h3>
        </div>

        <div className="grid-4">
          <div className="stat-card">
            <span className="stat-label">Total Products</span>
            <div className="stat-value">{Number(products.total_products || 0).toLocaleString()}</div>
            <div className="stat-footer">Active catalogue SKUs</div>
          </div>

          <div className="stat-card">
            <span className="stat-label">Minimum Price</span>
            <div className="stat-value">
              {products.price_statistics ? formatCurrency(products.price_statistics.minimum) : 'N/A'}
            </div>
            <div className="stat-footer">Lowest SKU pricing</div>
          </div>

          <div className="stat-card">
            <span className="stat-label">Average Price</span>
            <div className="stat-value">
              {products.price_statistics ? formatCurrency(products.price_statistics.average) : 'N/A'}
            </div>
            <div className="stat-footer">Mean catalogue value</div>
          </div>

          <div className="stat-card">
            <span className="stat-label">Maximum Price</span>
            <div className="stat-value">
              {products.price_statistics ? formatCurrency(products.price_statistics.maximum) : 'N/A'}
            </div>
            <div className="stat-footer">Peak SKU pricing</div>
          </div>
        </div>
      </div>
    </div>
  );
};
