"""Constants for economic resilience / hyperinflation analysis."""
COL_GDP = "gdp_change_pct"
COL_INFLATION = "inflation_rate_pct"
COL_DEVAL = "currency_devaluation_pct"
COL_CONFLICT_TYPE = "Conflict_Type"
COL_UNEMPLOYMENT_SPIKE = "unemployment_spike_pp"

# Inflation threshold considered high (%)
INFLATION_HIGH_THRESHOLD_PCT = 50.0

# GDP drop intervals (%) for the bar chart
GDP_BIN_EDGES = [-90, -80, -70, -60, -50, -40, -30, -20, -10, 0]

ANALYSIS_NAME = "economic_resilience_hyperinflation"
