import React, { useState } from 'react';

/**
 * Beautiful, dependency-free interactive SVG Line/Area Chart with hover tooltips
 */
export const LineTrendChart = ({
  data = [],
  xKey = 'period',
  yKey = 'value',
  label = 'Value',
  height = 220,
  color = '#2563EB',
  formatValue = (v) => v,
}) => {
  const [hoverIndex, setHoverIndex] = useState(null);

  if (!data || data.length === 0) {
    return (
      <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
        No trend data available
      </div>
    );
  }

  const values = data.map((d) => Number(d[yKey]) || 0);
  const minVal = Math.min(0, ...values);
  const maxVal = Math.max(1, ...values);
  const paddingX = 40;
  const paddingY = 25;
  const chartWidth = 500;
  const chartHeight = height;

  const getX = (index) => paddingX + (index / (data.length - 1 || 1)) * (chartWidth - paddingX * 2);
  const getY = (val) => chartHeight - paddingY - ((val - minVal) / (maxVal - minVal || 1)) * (chartHeight - paddingY * 2);

  const points = data.map((d, i) => `${getX(i)},${getY(Number(d[yKey]) || 0)}`).join(' ');
  const areaPoints = `${getX(0)},${chartHeight - paddingY} ${points} ${getX(data.length - 1)},${chartHeight - paddingY}`;

  return (
    <div style={{ position: 'relative', width: '100%', overflow: 'hidden' }}>
      <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} style={{ width: '100%', height: 'auto', overflow: 'visible' }}>
        <defs>
          <linearGradient id={`gradient-${color.replace('#', '')}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.25" />
            <stop offset="100%" stopColor={color} stopOpacity="0.0" />
          </linearGradient>
        </defs>

        {/* Horizontal gridlines */}
        {[0, 0.5, 1].map((pct, idx) => {
          const y = paddingY + pct * (chartHeight - paddingY * 2);
          const val = maxVal - pct * (maxVal - minVal);
          return (
            <g key={idx}>
              <line x1={paddingX} y1={y} x2={chartWidth - paddingX} y2={y} stroke="var(--border-subtle)" strokeDasharray="3 3" />
              <text x={paddingX - 8} y={y + 4} textAnchor="end" fill="var(--text-light)" fontSize="10" fontFamily="var(--font-sans)">
                {formatValue(Math.round(val))}
              </text>
            </g>
          );
        })}

        {/* Area fill */}
        <polygon points={areaPoints} fill={`url(#gradient-${color.replace('#', '')})`} />

        {/* Line */}
        <polyline
          fill="none"
          stroke={color}
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          points={points}
        />

        {/* Data points */}
        {data.map((d, i) => {
          const cx = getX(i);
          const cy = getY(Number(d[yKey]) || 0);
          const isHovered = hoverIndex === i;

          return (
            <g key={i} onMouseEnter={() => setHoverIndex(i)} onMouseLeave={() => setHoverIndex(null)} style={{ cursor: 'pointer' }}>
              <circle
                cx={cx}
                cy={cy}
                r={isHovered ? 6 : 4}
                fill={isHovered ? color : '#FFFFFF'}
                stroke={color}
                strokeWidth={isHovered ? 3 : 2}
                style={{ transition: 'all 0.15s ease' }}
              />
              {/* Invisible larger hit target */}
              <circle cx={cx} cy={cy} r="18" fill="transparent" />
            </g>
          );
        })}

        {/* X labels */}
        {data.map((d, i) => {
          if (data.length > 8 && i % Math.ceil(data.length / 6) !== 0 && i !== data.length - 1) return null;
          return (
            <text
              key={i}
              x={getX(i)}
              y={chartHeight - 6}
              textAnchor="middle"
              fill="var(--text-muted)"
              fontSize="10.5"
              fontFamily="var(--font-sans)"
              fontWeight="500"
            >
              {d[xKey]}
            </text>
          );
        })}
      </svg>

      {/* Floating Tooltip */}
      {hoverIndex !== null && data[hoverIndex] && (
        <div
          style={{
            position: 'absolute',
            top: '8px',
            left: '50%',
            transform: 'translateX(-50%)',
            background: 'var(--text-primary)',
            color: 'var(--text-inverse)',
            padding: '4px 10px',
            borderRadius: 'var(--radius-sm)',
            fontSize: '0.75rem',
            fontWeight: 600,
            boxShadow: 'var(--shadow-md)',
            pointerEvents: 'none',
            zIndex: 10,
          }}
        >
          {data[hoverIndex][xKey]}: {formatValue(data[hoverIndex][yKey])}
        </div>
      )}
    </div>
  );
};

/**
 * Modern Interactive Bar Chart for categorical data
 */
export const BarDistributionChart = ({
  data = [],
  xKey = 'category',
  yKey = 'count',
  height = 200,
  color = '#3B82F6',
  formatValue = (v) => v,
}) => {
  const [hoverIndex, setHoverIndex] = useState(null);

  if (!data || data.length === 0) {
    return (
      <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
        No distribution data available
      </div>
    );
  }

  const values = data.map((d) => Number(d[yKey]) || 0);
  const maxVal = Math.max(1, ...values);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', padding: '0.5rem 0' }}>
      {data.map((item, idx) => {
        const val = Number(item[yKey]) || 0;
        const pct = Math.min(100, (val / maxVal) * 100);
        const isHovered = hoverIndex === idx;

        return (
          <div
            key={idx}
            onMouseEnter={() => setHoverIndex(idx)}
            onMouseLeave={() => setHoverIndex(null)}
            style={{
              cursor: 'pointer',
              transition: 'background 0.15s ease',
              borderRadius: 'var(--radius-sm)',
              padding: '0.2rem 0.4rem',
              background: isHovered ? 'var(--bg-muted)' : 'transparent',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.825rem', marginBottom: '4px' }}>
              <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{item[xKey] || 'Unknown'}</span>
              <span style={{ fontWeight: 700, color: isHovered ? color : 'var(--text-secondary)', fontFamily: 'var(--font-mono)' }}>
                {formatValue(val)}
              </span>
            </div>
            <div
              style={{
                width: '100%',
                height: '8px',
                backgroundColor: 'var(--border-subtle)',
                borderRadius: 'var(--radius-full)',
                overflow: 'hidden',
              }}
            >
              <div
                style={{
                  width: `${pct}%`,
                  height: '100%',
                  background: isHovered ? `linear-gradient(90deg, ${color}, #8B5CF6)` : color,
                  borderRadius: 'var(--radius-full)',
                  transition: 'width 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
};

/**
 * Donut / Status Ratio Component
 */
export const DonutBreakdown = ({
  items = [
    { label: 'Completed', value: 3, color: '#10B981' },
    { label: 'Pending', value: 1, color: '#F59E0B' },
    { label: 'Failed', value: 1, color: '#EF4444' },
  ],
}) => {
  const total = items.reduce((acc, curr) => acc + curr.value, 0) || 1;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {/* Progress segmented bar */}
      <div style={{ display: 'flex', height: '14px', borderRadius: 'var(--radius-full)', overflow: 'hidden', backgroundColor: 'var(--border-subtle)' }}>
        {items.map((item, idx) => {
          const widthPct = (item.value / total) * 100;
          if (widthPct === 0) return null;
          return (
            <div
              key={idx}
              title={`${item.label}: ${item.value}`}
              style={{
                width: `${widthPct}%`,
                backgroundColor: item.color,
                transition: 'width 0.3s ease',
              }}
            />
          );
        })}
      </div>

      {/* Legend list */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', justifyContent: 'space-between' }}>
        {items.map((item, idx) => {
          const pct = Math.round((item.value / total) * 100);
          return (
            <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.825rem' }}>
              <span style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: item.color }} />
              <span style={{ color: 'var(--text-secondary)', fontWeight: 500 }}>{item.label}:</span>
              <strong style={{ color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>{item.value} ({pct}%)</strong>
            </div>
          );
        })}
      </div>
    </div>
  );
};
