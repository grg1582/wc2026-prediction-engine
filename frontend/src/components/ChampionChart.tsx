import { Bar, BarChart, CartesianGrid, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { TeamProbabilities } from '../lib/api';

interface ChampionChartProps {
  teamProbabilities: Record<string, TeamProbabilities>;
}

interface ChartRow {
  team: string;
  champion: number;
}

function ChampionTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload: ChartRow }> }) {
  if (!active || !payload?.length) return null;
  const row = payload[0].payload;
  return (
    <div
      className="rounded-md border px-3 py-2 text-sm shadow-sm"
      style={{ background: 'var(--surface-1)', borderColor: 'var(--border)' }}
    >
      <div className="font-semibold" style={{ color: 'var(--text-primary)' }}>
        {row.champion.toFixed(1)}%
      </div>
      <div style={{ color: 'var(--text-secondary)' }}>{row.team} to win it all</div>
    </div>
  );
}

export function ChampionChart({ teamProbabilities }: ChampionChartProps) {
  const data: ChartRow[] = Object.entries(teamProbabilities)
    .map(([team, p]) => ({ team, champion: p.champion }))
    .sort((a, b) => b.champion - a.champion);

  const height = Math.max(220, data.length * 40);

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} layout="vertical" margin={{ top: 8, right: 40, bottom: 8, left: 8 }}>
        <CartesianGrid
          horizontal={false}
          stroke="var(--gridline)"
          strokeDasharray="0"
        />
        <XAxis
          type="number"
          domain={[0, 100]}
          ticks={[0, 25, 50, 75, 100]}
          tickFormatter={(v) => `${v}%`}
          tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
          axisLine={{ stroke: 'var(--border)' }}
          tickLine={false}
        />
        <YAxis
          type="category"
          dataKey="team"
          width={100}
          tick={{ fill: 'var(--text-primary)', fontSize: 13 }}
          axisLine={{ stroke: 'var(--border)' }}
          tickLine={false}
        />
        <Tooltip content={<ChampionTooltip />} cursor={{ fill: 'var(--gridline)', opacity: 0.4 }} />
        <Bar
          dataKey="champion"
          fill="var(--series-home)"
          radius={[0, 4, 4, 0]}
          maxBarSize={22}
          isAnimationActive={false}
        >
          <LabelList
            dataKey="champion"
            position="right"
            formatter={(value: unknown) => `${Number(value).toFixed(1)}%`}
            fill="var(--text-secondary)"
            fontSize={12}
          />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
