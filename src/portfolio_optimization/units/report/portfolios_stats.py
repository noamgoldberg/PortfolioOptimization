from typing import Dict, Any
import pandas as pd


def get_best_portfolio(
    portfolios: pd.DataFrame,
    metric: str = "Sharpe Ratio"
) -> Dict[str, Any]:
    return portfolios.sort_values(
        metric, ascending=False
    ).iloc[0].to_dict()

def get_portfolios_stats(
    portfolios: pd.DataFrame,
) -> Dict[str, Any]:
    return {
        method: df.describe().loc[['mean', 'std', 'min', 'max', ]]
        for  method, df in portfolios.groupby("Method")
    }