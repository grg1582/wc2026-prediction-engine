# ml/models — Poisson xG Model (Future Session)

Will use Poisson regression to estimate expected goals (xG) per team per match,
conditioned on Elo ratings and recent form.

Note: apply time-decay or a rolling training window before fitting — goals/match
has declined from ~3.0 (1950s) to ~2.4 (2020s) and naive full-history fitting
will overpredict modern match scores.
