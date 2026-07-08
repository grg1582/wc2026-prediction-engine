# ml/simulator — Monte Carlo Simulator (Future Session)

Will simulate the full WC 2026 group stage and knockout rounds N times
using match probabilities from the Poisson xG model.

Performance target: 10k simulations in < 5s — requires NumPy vectorisation,
not per-match Python loops.
