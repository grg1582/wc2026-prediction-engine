import type { TeamProbabilities } from '../lib/api';

interface TeamProbabilitiesTableProps {
  teamProbabilities: Record<string, TeamProbabilities>;
}

const COLUMNS: Array<{ key: keyof TeamProbabilities; label: string }> = [
  { key: 'reach_semifinal', label: 'Reach SF' },
  { key: 'reach_final', label: 'Reach final' },
  { key: 'champion', label: 'Champion' },
  { key: 'third_place', label: '3rd place' },
];

export function TeamProbabilitiesTable({ teamProbabilities }: TeamProbabilitiesTableProps) {
  const rows = Object.entries(teamProbabilities).sort((a, b) => b[1].champion - a[1].champion);

  return (
    <table className="w-full border-collapse text-sm">
      <thead>
        <tr className="border-b" style={{ borderColor: 'var(--gridline)' }}>
          <th className="py-2 text-left font-medium" style={{ color: 'var(--text-muted)' }}>
            Team
          </th>
          {COLUMNS.map((col) => (
            <th
              key={col.key}
              className="py-2 text-right font-medium"
              style={{ color: 'var(--text-muted)' }}
            >
              {col.label}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map(([team, p]) => (
          <tr key={team} className="border-b" style={{ borderColor: 'var(--gridline)' }}>
            <td className="py-2 text-left" style={{ color: 'var(--text-primary)' }}>
              {team}
            </td>
            {COLUMNS.map((col) => (
              <td
                key={col.key}
                className="py-2 text-right tabular-nums"
                style={{ color: 'var(--text-primary)' }}
              >
                {p[col.key].toFixed(1)}%
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
