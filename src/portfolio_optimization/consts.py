from portfolio_optimization.datasets.risk_free_rate_dataset import RiskFreeRateDataSet


CONF_ENV = "conf"
INDEX_COL = "Date"
DATE_FORMAT = "%Y-%m-%d"

# RISK_FREE_RATE = RiskFreeRateDataSet().rate  # Source <https://ycharts.com/indicators/10_year_treasury_rate>
RISK_FREE_RATE = 0.0443  # Source <https://ycharts.com/indicators/10_year_treasury_rate> (May 23, 2024)
ANNUAL_TRADING_PERIODS = {
    "daily": 252,
    "weekly": 52,
    "monthly": 12,
    "yearly": 1
}
