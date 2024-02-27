from typing import Dict, Union, Callable, Any
import pandas as pd
import numpy as np
from numpy.typing import ArrayLike
import scipy.optimize as sco
from tqdm import tqdm

from portfolio_optimization.datasets.portfolio_set import PortfolioSet
from portfolio_optimization.utils.data_utils import concat_partitions, filter_stocks_df_for_agg
from portfolio_optimization.utils.financial_utils import get_num_trading_periods
from portfolio_optimization.utils.formatting_utils import str2list
from portfolio_optimization.consts import RISK_FREE_RATE


def optimize_weights(
    stocks_data: Dict[str, Union[Callable, pd.DataFrame]],
    params: Dict[str, Any],
) -> pd.DataFrame:
    ALL_METHODS = ["scipy", "monte carlo"]
    portfolio_set = PortfolioSet()
    methods = str2list(params["optimize"]["methods"])
    if not all([m in ALL_METHODS for m in methods]):
        raise NotImplementedError(
            f"Optimization methods '{[m for m in methods if m not in ALL_METHODS]}' for not yet implemented"
        )
    agg_col = params["optimize"]["optimize_on"]
    period = params["data"]["stocks"]["period"]
    subtract_risk_free =  params["optimize"].get("subtract_risk_free", True)
    for method in methods:
        if method.split(":")[0] == "scipy":
            scipy_solver = method.split(":")[1] or "SLSQP"
            optimize_scipy(
                stocks_data,
                portfolio_set,
                agg_col=agg_col,
                period=period,
                scipy_solver=scipy_solver,
                subtract_risk_free=subtract_risk_free,
            )
        elif method.split(":")[0] == "monte carlo":
            n_iters = method.split(":")[1] or 10000
            optimize_monte_carlo(
                stocks_data,
                portfolio_set,
                agg_col=agg_col,
                period=period,
                n_iters=n_iters,
                subtract_risk_free=subtract_risk_free,
            )
    return portfolio_set.portfolios
    
            
def optimize_scipy(
    stocks_data: Dict[str, Union[Callable, pd.DataFrame]],
    portfolio_set: PortfolioSet,
    *,
    agg_col: str = "Adj Close",
    period: str = "daily",
    scipy_solver: str = "SLSQP",  # default: Sequential Least Squares Programming (SLSQP)
    subtract_risk_free: bool = True
) -> pd.DataFrame:
        
    # (1) Concat Partitions of Log Returns Data    
    stocks_data = concat_partitions(stocks_data)
    stocks_data = filter_stocks_df_for_agg(stocks_data, agg_col)
    symbols = list(stocks_data.columns)
    returns = stocks_data.pct_change().dropna()
    
    mean_annualized = returns.mean() * get_num_trading_periods(period)
    cov_annualized = returns.cov() * get_num_trading_periods(period)
    
    # (2) Write Negate Function (scipy only has optimize.minimize, not optimize.maximize)
    def _neg_sharpe(weights):
        return get_ret_vol_sr(portfolio_set, symbols, weights, mean_annualized, cov_annualized, "scipy", subtract_risk_free)[2] * -1
        
    # (3) Establish Constraint(s): weights must add to 1 (by convention of sco.minimize, condition functions should return zero)
    constraints = ({'type':'eq','fun': lambda weights: np.sum(weights) - 1})

    # (4) Establish Bound(s): each weights must be btw. 0 and 1 (by convention of sco.minimize, bounds should be iterable of tuples)
    bounds = ((0, 1) for _ in returns.columns)

    # (5) Generate Initial Guess: equal distribution
    init_guess = [1 / len(returns.columns) for _ in returns.columns]

    # (6) Optimize & Save Each Portfolio!
    opt_results = sco.minimize(
        _neg_sharpe,
        init_guess,
        method=scipy_solver,
        bounds=bounds,
        constraints=constraints
    )

def optimize_monte_carlo(
    stocks_data: Dict[str, Union[Callable, pd.DataFrame]],
    portfolio_set: PortfolioSet,
    *,
    agg_col: str = "Adj Close",
    period: str = "daily",
    n_iters: int = 20000,
    subtract_risk_free: bool = True,
) -> pd.DataFrame:
    
    # (1) Calculate Stock Returns by Single Period
    stocks_data = concat_partitions(stocks_data)
    stocks_data = filter_stocks_df_for_agg(stocks_data, agg_col)
    symbols = list(stocks_data.columns)
    returns = stocks_data.pct_change().dropna()

    # (2) Initialize Arrays
    # all_weights = np.zeros((n_iters, stocks_data.shape[1]))
    return_arr = np.zeros(n_iters)
    volatility_arr = np.zeros(n_iters)
    sharpe_arr = np.zeros(n_iters)

    # (3) Optimize! (Monte Carlo Simulation)
    num_trading_periods = get_num_trading_periods(period)
    mean_annualized = returns.mean() * num_trading_periods
    cov_annualized = returns.cov() * num_trading_periods
    for i in tqdm(range(n_iters)):
        
        # a. Create Random Weights
        weights = np.array(np.random.random(stocks_data.shape[1]))
        weights = weights / np.sum(weights)
        
        # b. Get Expected Return, Expected Variance & Sharpe Ratio & Save Portfolio
        (
            return_arr[i], 
            volatility_arr[i], 
            sharpe_arr[i]
        ) = get_ret_vol_sr(portfolio_set, symbols, weights, mean_annualized, cov_annualized, "monte carlo", subtract_risk_free)
        
def get_ret_vol_sr(
    portfolio_set: PortfolioSet,
    symbols: ArrayLike,
    weights: ArrayLike,
    mean_annualized: ArrayLike,
    cov_annualized: ArrayLike,
    method: str,
    subtract_risk_free: bool = True
) -> np.ndarray:
    risk_free_rate = RISK_FREE_RATE if subtract_risk_free else 0
    weights = np.array(weights)
    ret = np.sum(mean_annualized * weights) - risk_free_rate
    vol = np.sqrt(np.dot(weights.T, np.dot(cov_annualized, weights)))
    sr = ret / vol
    weights_dict = dict(zip(symbols, weights))
    portfolio_set.add_portfolio(method, ret, vol, sr, weights_dict)
    return np.array([ret, vol, sr])
