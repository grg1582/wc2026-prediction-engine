import { useEffect, useState } from 'react';
import {
  ApiError,
  getRankings,
  predictTournament,
  type RankingEntry,
  type TournamentSimulation,
} from './lib/api';
import { BracketBoard } from './components/BracketBoard';
import { ChampionChart } from './components/ChampionChart';
import { TeamProbabilitiesTable } from './components/TeamProbabilitiesTable';
import { MatchPredictor } from './components/MatchPredictor';
import { RankingsTable } from './components/RankingsTable';

const cardClass = 'rounded-lg border p-5';
const cardStyle = { borderColor: 'var(--gridline)', background: 'var(--surface-1)' };

function SectionTitle({ children, subtitle }: { children: React.ReactNode; subtitle?: string }) {
  return (
    <div className="mb-4">
      <h2 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
        {children}
      </h2>
      {subtitle && (
        <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
          {subtitle}
        </p>
      )}
    </div>
  );
}

function App() {
  const [rankings, setRankings] = useState<RankingEntry[] | null>(null);
  const [simulation, setSimulation] = useState<TournamentSimulation | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getRankings(300), predictTournament(10_000, 42)])
      .then(([rankingsData, simulationData]) => {
        setRankings(rankingsData);
        setSimulation(simulationData);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : 'Failed to load data.'));
  }, []);

  return (
    <div className="py-8">
      <header className="mb-8">
        <h1 className="text-2xl font-semibold" style={{ color: 'var(--text-primary)' }}>
          WC2026 Prediction Engine
        </h1>
        <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
          Elo ratings, a Poisson xG model, and a Monte Carlo knockout simulation from the
          quarterfinal onward.
        </p>
      </header>

      {error && (
        <div
          className={cardClass}
          style={{ ...cardStyle, borderColor: 'var(--series-away)' }}
        >
          <p className="font-semibold" style={{ color: 'var(--text-primary)' }}>
            Couldn't load data
          </p>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            {error}
          </p>
        </div>
      )}

      {!error && (!rankings || !simulation) && (
        <p style={{ color: 'var(--text-muted)' }}>Loading predictions…</p>
      )}

      {rankings && simulation && (
        <div className="flex flex-col gap-8">
          <section>
            <SectionTitle subtitle={`Based on ${simulation.n_simulations.toLocaleString()} Monte Carlo simulations`}>
              Quarterfinals
            </SectionTitle>
            <BracketBoard
              quarterfinals={simulation.quarterfinals}
              mostLikelySemifinals={simulation.most_likely_semifinals}
              mostLikelyFinal={simulation.most_likely_final}
            />
          </section>

          <section className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className={cardClass} style={cardStyle}>
              <SectionTitle>Championship probability</SectionTitle>
              <ChampionChart teamProbabilities={simulation.team_probabilities} />
            </div>
            <div className={cardClass} style={cardStyle}>
              <SectionTitle>Advancement probabilities</SectionTitle>
              <TeamProbabilitiesTable teamProbabilities={simulation.team_probabilities} />
            </div>
          </section>

          <section className={cardClass} style={cardStyle}>
            <SectionTitle subtitle="Any two teams, using current Elo-conditioned expected goals">
              Head-to-head predictor
            </SectionTitle>
            <MatchPredictor teams={rankings} />
          </section>

          <section className={cardClass} style={cardStyle}>
            <SectionTitle>Elo rankings</SectionTitle>
            <RankingsTable rankings={rankings.slice(0, 20)} />
          </section>
        </div>
      )}
    </div>
  );
}

export default App;
