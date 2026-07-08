const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';

export interface RankingEntry {
  rank: number;
  team: string;
  elo: number;
}

export interface MatchPrediction {
  home_team: string;
  away_team: string;
  home_elo: number;
  away_elo: number;
  home_xg: number;
  away_xg: number;
  home_win_pct: number;
  draw_pct: number;
  away_win_pct: number;
}

export interface QuarterfinalResult {
  home: string;
  away: string;
  home_xg: number;
  away_xg: number;
  home_win_pct: number;
  away_win_pct: number;
}

export interface TeamProbabilities {
  reach_semifinal: number;
  reach_final: number;
  champion: number;
  third_place: number;
}

export interface Pairing {
  teams: [string, string];
  probability_pct: number;
}

export interface TournamentSimulation {
  n_simulations: number;
  quarterfinals: QuarterfinalResult[];
  team_probabilities: Record<string, TeamProbabilities>;
  most_likely_semifinals: Pairing[];
  most_likely_final: Pairing[];
}

class ApiError extends Error {}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...init,
    });
  } catch {
    throw new ApiError(
      `Could not reach the API at ${API_BASE_URL}. Is "uvicorn api.main:app" running?`,
    );
  }
  if (!response.ok) {
    const detail = await response.json().catch(() => null);
    throw new ApiError(detail?.detail ?? `Request to ${path} failed (${response.status}).`);
  }
  return response.json() as Promise<T>;
}

export function getRankings(top = 20): Promise<RankingEntry[]> {
  return request(`/rankings?top=${top}`);
}

export function predictMatch(homeTeam: string, awayTeam: string): Promise<MatchPrediction> {
  return request('/predict/match', {
    method: 'POST',
    body: JSON.stringify({ home_team: homeTeam, away_team: awayTeam }),
  });
}

export function predictTournament(sims = 10_000, seed?: number): Promise<TournamentSimulation> {
  const params = new URLSearchParams({ sims: String(sims) });
  if (seed !== undefined) params.set('seed', String(seed));
  return request(`/predict/tournament?${params.toString()}`);
}

export { ApiError };
