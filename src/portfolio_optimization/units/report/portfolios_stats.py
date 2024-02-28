from typing import Dict, Any
import pandas as pd


def get_best_portfolio_weights(
    portfolios: pd.DataFrame,
) -> Dict[str, Any]:
    best_weights = pd.Series(portfolios.sort_values(
        "Sharpe Ratio", ascending=False
    ).iloc[0]["Weights"]).reset_index()
    best_weights.columns = ["Stock", "Weight"]
    return best_weights

def get_portfolios_stats(
    portfolios: pd.DataFrame,
) -> Dict[str, Any]:
    return {
        method: df.describe().loc[['mean', 'std', 'min', 'max', ]]
        for  method, df in portfolios.groupby("Method")
    }