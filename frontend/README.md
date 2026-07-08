# frontend — React Dashboard

Vite + React + TypeScript + Tailwind CSS v4 + Recharts.

Screens (single page, `src/App.tsx`):
- Quarterfinal bracket cards with win-probability bars
- Most likely semifinal / final matchups
- Championship probability chart + advancement-probability table
- Head-to-head predictor (any two teams)
- Elo rankings table

## Run

Requires the API running first (see `../api/README.md`):

```bash
npm install
npm run dev
```

Opens on `http://localhost:5173`, talking to the API at
`http://127.0.0.1:8000` by default. Override with a `.env` file:

```
VITE_API_BASE_URL=http://127.0.0.1:8000
```
