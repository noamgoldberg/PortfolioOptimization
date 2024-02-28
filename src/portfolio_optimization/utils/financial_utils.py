import numpy as np
from numpy.typing import ArrayLike

from portfolio_optimization.utils.data_utils import verify_1D
from portfolio_optimization.consts import RISK_FREE_RATE, ANNUAL_TRADING_PERIODS


def get_num_trading_periods(period: str):
    try:
        return ANNUAL_TRADING_PERIODS[period]
    except KeyError:
        raise ValueError(f"{period}: Value of 'period' parameter invalid for calculation of sharpe ratio; choose from {list(ANNUAL_TRADING_PERIODS).keys()}")