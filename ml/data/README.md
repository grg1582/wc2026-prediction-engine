# ml/data — Data Ingestion

Loads the Kaggle martj42 international football results CSV and filters to competitive matches only.

Expected CSV columns: `date, home_team, away_team, home_score, away_score, tournament, city, country, neutral`

Public API: `load_results(csv_path) -> pd.DataFrame`
