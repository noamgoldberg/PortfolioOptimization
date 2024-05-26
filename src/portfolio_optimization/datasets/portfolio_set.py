from typing import Dict
import pandas as pd

class PortfolioSet:
    
    def __init__(self):
        self._portfolios = pd.DataFrame(columns=[
            "Solver", "Return", "Volatility", "Sharpe Ratio", "Weights"
        ])
    
    @property
    def portfolios(self):
        return self._portfolios
    
    def add_portfolio(
        self,
        *,
        solver: str,  # scipy solver
        ret: float,  # return
        vol: float,  # volatility
        sharpe_ratio: float,
        weights: Dict[str, float]  # weights dict
    ) -> None:
        # Directly assign the new row to the DataFrame using loc
        self._portfolios.loc[len(self._portfolios)] = [solver, ret, vol, sharpe_ratio, weights]

    