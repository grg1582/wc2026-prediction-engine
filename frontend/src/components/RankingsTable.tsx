import type { RankingEntry } from '../lib/api';

interface RankingsTableProps {
  rankings: RankingEntry[];
}

export function RankingsTable({ rankings }: RankingsTableProps) {
  return (
    <table className="w-full border-collapse text-sm">
      <thead>
        <tr className="border-b" style={{ borderColor: 'var(--gridline)' }}>
          <th className="py-2 text-left font-medium" style={{ color: 'var(--text-muted)' }}>
            Rank
          </th>
          <th className="py-2 text-left font-medium" style={{ color: 'var(--text-muted)' }}>
            Team
          </th>
          <th className="py-2 text-right font-medium" style={{ color: 'var(--text-muted)' }}>
            Elo
          </th>
        </tr>
      </thead>
      <tbody>
        {rankings.map((entry) => (
          <tr key={entry.team} className="border-b" style={{ borderColor: 'var(--gridline)' }}>
            <td className="py-2 tabular-nums" style={{ color: 'var(--text-muted)' }}>
              {entry.rank}
            </td>
            <td className="py-2" style={{ color: 'var(--text-primary)' }}>
              {entry.team}
            </td>
            <td className="py-2 text-right font-semibold tabular-nums" style={{ color: 'var(--text-primary)' }}>
              {entry.elo.toFixed(1)}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
