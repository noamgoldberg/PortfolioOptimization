from typing import Any, Dict, Callable
import numpy as np
import pandas as pd


def simulate_portfolio_returns(
    stocks_data: Dict[str, Callable[[], pd.DataFrame]],
    weights_dict: Dict[str, float],
    params: Dict[str, Any],
    agg: str = "Adj Close"
):
    # Convert the weights dictionary to a numpy array
    weights = np.array(list(weights_dict.values()))
    
    # Get the stock tickers
    tickers = list(weights_dict.keys())

    # Extract the adjusted close prices for the selected tickers
    agg_data = {ticker: stocks_data[ticker]()[agg] for ticker in tickers}
    agg_df = pd.DataFrame(agg_data)
    
    # Calculate returns
    returns = agg_df.pct_change().dropna()
    mean_returns = returns.mean()
    cov_matrix = returns.cov()
    
    # Monte Carlo parameters
    mc_sims = params["simulate"].get("num_sims", 400)  # Number of simulations
    T = params["simulate"].get("timeframe", 90)  # Timeframe in days
    initial_investment = params["simulate"].get("initial_investment", 10000)

    # Initialize matrix to hold the simulation results
    portfolio_sims = np.full(shape=(T, mc_sims), fill_value=0.0)
    
    # Mean returns matrix
    meanM = np.full(shape=(T, len(weights)), fill_value=mean_returns.values).T

    # Cholesky decomposition
    L = np.linalg.cholesky(cov_matrix)
    
    for m in range(mc_sims):
        # Generate random noise
        Z = np.random.normal(size=(T, len(weights)))
        # Calculate daily returns with noise
        daily_returns = meanM + np.inner(L, Z)
        # Calculate cumulative returns
        portfolio_sims[:, m] = np.cumprod(np.inner(weights, daily_returns.T) + 1) * initial_investment

    # Convert the simulation results to a DataFrame
    portfolio_sims_df = pd.DataFrame(portfolio_sims, columns=[f"Simulation {i + 1}" for i in range(mc_sims)])
    
    return portfolio_sims_df

def calculate_simulated_portfolio_returns(
    portfolio_simulations: pd.DataFrame,
    initial_investment: int,
) -> pd.Series:
    return portfolio_simulations.iloc[-1] - initial_investment

def calculate_simulated_portfolio_returns_stats(
    simulated_portfolio_returns: pd.Series,
) -> pd.Series:
    return simulated_portfolio_returns.describe()
    
