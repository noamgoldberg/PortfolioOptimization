from portfolio_optimization.consts import ANNUAL_TRADING_PERIODS


def get_num_trading_periods(period: str):
    try:
        return ANNUAL_TRADING_PERIODS[period]
    except KeyError:
        raise ValueError(f"{period}: Value of 'period' parameter invalid for calculation of sharpe ratio; choose from {list(ANNUAL_TRADING_PERIODS).keys()}")