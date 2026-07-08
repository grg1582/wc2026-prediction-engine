import type { Pairing, QuarterfinalResult } from '../lib/api';
import { SplitBar } from './SplitBar';

interface BracketBoardProps {
  quarterfinals: QuarterfinalResult[];
  mostLikelySemifinals: Pairing[];
  mostLikelyFinal: Pairing[];
}

function QuarterfinalCard({ match }: { match: QuarterfinalResult }) {
  return (
    <div
      className="rounded-lg border p-4"
      style={{ borderColor: 'var(--gridline)', background: 'var(--surface-1)' }}
    >
      <div className="mb-3 flex items-baseline justify-between text-sm">
        <span style={{ color: 'var(--text-primary)' }} className="font-semibold">
          {match.home}
        </span>
        <span style={{ color: 'var(--text-muted)' }} className="text-xs">
          xG {match.home_xg.toFixed(2)} – {match.away_xg.toFixed(2)}
        </span>
        <span style={{ color: 'var(--text-primary)' }} className="font-semibold">
          {match.away}
        </span>
      </div>
      <SplitBar
        segments={[
          { key: 'home', label: match.home, pct: match.home_win_pct, color: 'var(--series-home)' },
          { key: 'away', label: match.away, pct: match.away_win_pct, color: 'var(--series-away)' },
        ]}
      />
    </div>
  );
}

function PairingRow({ pairing }: { pairing: Pairing }) {
  return (
    <div className="flex items-center justify-between gap-4 py-2">
      <div className="flex-1">
        <div className="h-2 overflow-hidden rounded" style={{ background: 'var(--gridline)' }}>
          <div
            className="h-full rounded"
            style={{ width: `${pairing.probability_pct}%`, background: 'var(--series-home)' }}
          />
        </div>
      </div>
      <span className="whitespace-nowrap text-sm" style={{ color: 'var(--text-primary)' }}>
        {pairing.teams.join(' vs ')}
      </span>
      <span
        className="whitespace-nowrap text-sm font-semibold tabular-nums"
        style={{ color: 'var(--text-primary)' }}
      >
        {pairing.probability_pct.toFixed(1)}%
      </span>
    </div>
  );
}

export function BracketBoard({ quarterfinals, mostLikelySemifinals, mostLikelyFinal }: BracketBoardProps) {
  return (
    <div className="flex flex-col gap-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {quarterfinals.map((match) => (
          <QuarterfinalCard key={`${match.home}-${match.away}`} match={match} />
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <div>
          <h3 className="mb-1 text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
            Most likely semifinals
          </h3>
          <div className="divide-y" style={{ borderColor: 'var(--gridline)' }}>
            {mostLikelySemifinals.map((pairing) => (
              <PairingRow key={pairing.teams.join('-')} pairing={pairing} />
            ))}
          </div>
        </div>
        <div>
          <h3 className="mb-1 text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
            Most likely final
          </h3>
          <div className="divide-y" style={{ borderColor: 'var(--gridline)' }}>
            {mostLikelyFinal.map((pairing) => (
              <PairingRow key={pairing.teams.join('-')} pairing={pairing} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
