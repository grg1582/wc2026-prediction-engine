export interface BarSegment {
  key: string;
  label: string;
  pct: number;
  color: string;
  textColor?: string;
}

interface SplitBarProps {
  segments: BarSegment[];
}

// legend below always shows the exact numbers, so precision doesn't depend on hover/fit
export function SplitBar({ segments }: SplitBarProps) {
  return (
    <div>
      <div
        className="flex h-6 overflow-hidden rounded"
        style={{ gap: '2px', background: 'var(--surface-1)' }}
      >
        {segments.map((segment) => (
          <div
            key={segment.key}
            className="flex items-center justify-center text-xs font-medium whitespace-nowrap"
            style={{
              flexBasis: `${segment.pct}%`,
              background: segment.color,
              color: segment.textColor ?? '#fff',
            }}
            title={`${segment.label}: ${segment.pct.toFixed(1)}%`}
          >
            {segment.pct >= 14 ? `${segment.pct.toFixed(0)}%` : ''}
          </div>
        ))}
      </div>
      <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs">
        {segments.map((segment) => (
          <span key={segment.key} className="inline-flex items-center gap-1.5">
            <span
              className="inline-block h-2.5 w-2.5 rounded-sm"
              style={{ background: segment.color }}
            />
            <span style={{ color: 'var(--text-secondary)' }}>{segment.label}</span>
            <span className="font-semibold tabular-nums" style={{ color: 'var(--text-primary)' }}>
              {segment.pct.toFixed(1)}%
            </span>
          </span>
        ))}
      </div>
    </div>
  );
}
