from typing import Dict, Union, Callable, Any, Optional
import pandas as pd
import numpy as np
from numpy.typing import ArrayLike
import scipy.optimize as sco

from portfolio_optimization.datasets.portfolio_set import PortfolioSet
from portfolio_optimization.utils.data_utils import get_stock_returns
from portfolio_optimization.utils.financial_utils import get_num_trading_periods
from portfolio_optimization.utils.formatting_utils import str2list
from portfolio_optimization.consts import RISK_FREE_RATE


def optimize_weights(
    stocks_data: Dict[str, Union[Callable, pd.DataFrame]],
    params: Dict[str, Any],
) -> pd.DataFrame:
    portfolio_set = PortfolioSet()
    solvers = str2list(params["optimize"]["solvers"])
    agg = params["optimize"]["optimize_on"]
    period = params["data"]["stocks"]["period"]
    subtract_risk_free =  params["optimize"].get("subtract_risk_free", True)
    for solver in solvers:
        opt_results = optimize_scipy(
            stocks_data,
            portfolio_set,
            agg=agg,
            period=period,
            solver=solver,
            subtract_risk_free=subtract_risk_free,
        )
    return portfolio_set.portfolios
    
            
def optimize_scipy(
    stocks_data: Dict[str, Union[Callable, pd.DataFrame]],
    portfolio_set: PortfolioSet,
    *,
    agg: str = "Close",
    period: str = "daily",
    solver: str = "SLSQP",  # default: Sequential Least Squares Programming (SLSQP)
    subtract_risk_free: bool = True
) -> pd.DataFrame:
        
    # (1) Concat Partitions of Returns Data    
    returns = get_stock_returns(stocks_data, agg)
    symbols = returns.columns
    
    mean_annualized = returns.mean() * get_num_trading_periods(period)
    cov_annualized = returns.cov() * get_num_trading_periods(period)
    
    # (2) Write Negate Function (scipy only has optimize.minimize, not optimize.maximize)
    def _neg_sharpe(weights):
        return get_ret_vol_sr(
            portfolio_set=portfolio_set,
            symbols=symbols,
            weights=weights,
            mean_annualized=mean_annualized,
            cov_annualized=cov_annualized,
            solver=solver,
            subtract_risk_free=subtract_risk_free
        )[2] * -1
        
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
        method=solver,
        bounds=bounds,
        constraints=constraints
    )
    
    return opt_results


def get_ret_vol_sr(
    portfolio_set: PortfolioSet,
    symbols: ArrayLike,
    weights: ArrayLike,
    mean_annualized: ArrayLike,
    cov_annualized: ArrayLike,
    solver: str,
    subtract_risk_free: bool = True
) -> np.ndarray:
    risk_free_rate = RISK_FREE_RATE if subtract_risk_free else 0
    weights = np.array(weights)
    ret = np.sum(mean_annualized * weights) - risk_free_rate
    vol = np.sqrt(np.dot(weights.T, np.dot(cov_annualized, weights)))
    sharpe_ratio = ret / vol
    weights_dict = dict(zip(symbols, weights))
    portfolio_set.add_portfolio(
        solver=solver,
        ret=ret,
        vol=vol,
        sharpe_ratio=sharpe_ratio,
        weights=weights_dict
    )
    return np.array([ret, vol, sharpe_ratio])

def extract_best_portfolio_weights(
    *,
    portfolios: pd.DataFrame,
    min_weight: Optional[float] = 1e-04
):
    weights_dict = portfolios.sort_values(by="Sharpe Ratio", ascending=False).iloc[0]["Weights"]
    if isinstance(min_weight, float):
        weights_dict = {ticker: weight for ticker, weight in weights_dict.items() if weight > min_weight}
    return weights_dict