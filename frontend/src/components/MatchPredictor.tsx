import { useState } from 'react';
import { ApiError, predictMatch, type MatchPrediction, type RankingEntry } from '../lib/api';
import { SplitBar } from './SplitBar';

interface MatchPredictorProps {
  teams: RankingEntry[];
}

export function MatchPredictor({ teams }: MatchPredictorProps) {
  const [homeTeam, setHomeTeam] = useState(teams[0]?.team ?? '');
  const [awayTeam, setAwayTeam] = useState(teams[1]?.team ?? '');
  const [result, setResult] = useState<MatchPrediction | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      setResult(await predictMatch(homeTeam, awayTeam));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Prediction failed.');
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  const selectClass =
    'w-full rounded-md border px-3 py-2 text-sm';
  const selectStyle = {
    borderColor: 'var(--border)',
    background: 'var(--surface-1)',
    color: 'var(--text-primary)',
  };

  return (
    <div>
      <form onSubmit={handleSubmit} className="flex flex-wrap items-end gap-3">
        <label className="flex-1 min-w-[10rem] text-sm">
          <span className="mb-1 block" style={{ color: 'var(--text-muted)' }}>
            Home team
          </span>
          <select
            className={selectClass}
            style={selectStyle}
            value={homeTeam}
            onChange={(e) => setHomeTeam(e.target.value)}
          >
            {teams.map((t) => (
              <option key={t.team} value={t.team}>
                {t.team}
              </option>
            ))}
          </select>
        </label>
        <label className="flex-1 min-w-[10rem] text-sm">
          <span className="mb-1 block" style={{ color: 'var(--text-muted)' }}>
            Away team
          </span>
          <select
            className={selectClass}
            style={selectStyle}
            value={awayTeam}
            onChange={(e) => setAwayTeam(e.target.value)}
          >
            {teams.map((t) => (
              <option key={t.team} value={t.team}>
                {t.team}
              </option>
            ))}
          </select>
        </label>
        <button
          type="submit"
          disabled={loading || homeTeam === awayTeam}
          className="rounded-md px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
          style={{ background: 'var(--series-home)' }}
        >
          {loading ? 'Predicting…' : 'Predict'}
        </button>
      </form>

      {homeTeam === awayTeam && (
        <p className="mt-2 text-xs" style={{ color: 'var(--text-muted)' }}>
          Pick two different teams.
        </p>
      )}
      {error && (
        <p className="mt-3 text-sm" style={{ color: 'var(--series-away)' }}>
          {error}
        </p>
      )}

      {result && (
        <div className="mt-4">
          <div className="mb-2 flex justify-between text-xs" style={{ color: 'var(--text-muted)' }}>
            <span>
              {result.home_team} · Elo {result.home_elo.toFixed(0)} · xG {result.home_xg.toFixed(2)}
            </span>
            <span>
              {result.away_team} · Elo {result.away_elo.toFixed(0)} · xG {result.away_xg.toFixed(2)}
            </span>
          </div>
          <SplitBar
            segments={[
              {
                key: 'home',
                label: `${result.home_team} win`,
                pct: result.home_win_pct,
                color: 'var(--series-home)',
              },
              {
                key: 'draw',
                label: 'Draw',
                pct: result.draw_pct,
                color: 'var(--series-draw)',
                textColor: 'var(--text-primary)',
              },
              {
                key: 'away',
                label: `${result.away_team} win`,
                pct: result.away_win_pct,
                color: 'var(--series-away)',
              },
            ]}
          />
        </div>
      )}
    </div>
  );
}
