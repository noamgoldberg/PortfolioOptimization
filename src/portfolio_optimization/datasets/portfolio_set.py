import pandas as pd

class PortfolioSet:
    
    def __init__(self):
        self._portfolios = pd.DataFrame(columns=[
            "Method", "Return", "Volatility", "Sharpe Ratio", "Weights"
        ])
    
    @property
    def portfolios(self):
        return self._portfolios
    
    def add_portfolio(self, method, ret, volatility, sharpe_ratio, weights):
        # Directly assign the new row to the DataFrame using loc
        self._portfolios.loc[len(self._portfolios)] = [method, ret, volatility, sharpe_ratio, weights]

    