from typing import List, Union, Dict, Optional
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Verify & establish alphas
def establish_alphas(alphas: Union[List[float], float]):
    if isinstance(alphas, float):
        alphas = [alphas]
    if not isinstance(alphas, list):
        raise TypeError(f"Type invalid for parameter 'alphas'. Expected one of types 'int', 'float', or 'list', got '{type(alphas)}'")
    for alpha in alphas:
        if isinstance(alpha, float):
            if not 0 < alpha < 1:
                raise ValueError(f"{alpha}: Value of risk threshold (alpha) must meet 0 < value < 1")
        else:
            raise TypeError(f"Expected one of types 'int', 'float', or 'list', got '{type(alphas)}'")
    return alphas

# VaR (Monte Carlo) - single alpha
def calculate_mcVaR(
    portfolio_returns: pd.Series,
    alpha: Union[List[float], float] = 0.05,
) -> float:
    VaR = np.percentile(portfolio_returns, alpha * 100)
    return VaR

# VaR (Monte Carlo) - many alphas
def calculate_mcVaR_for_each_alpha(
    portfolio_returns: pd.Series,
    alphas: Union[List[float], float] = 0.05,
) -> Dict[float, float]:
    alphas = establish_alphas(alphas)
    percentiles = [alpha * 100 for alpha in alphas]
    VaRs = np.percentile(portfolio_returns, percentiles)
    return dict(zip(alphas, VaRs))

# CVaR (Monte Carlo) - single alpha
def calculate_mcCVaR(
    portfolio_returns: pd.Series,
    alpha: float = 0.05,
    VaR: Optional[Union[float, int]] = None,
) -> float:
    if not isinstance(VaR, (float, int)):
        VaR = calculate_mcVaR(portfolio_returns, alpha)
    return portfolio_returns[portfolio_returns <= VaR].mean()

# CVaR (Monte Carlo) - many alphas
def calculate_mcCVaR_for_each_alpha(
    portfolio_returns: pd.Series,
    alphas: Union[List[float], float] = 0.05,
    VaR_series: Optional[Union[dict, pd.Series]] = None,
) -> Dict[float, float]:
    alphas = establish_alphas(alphas)
    if VaR_series:
        if not isinstance(VaR_series, (dict, pd.Series)):
            raise TypeError(f"Expected one of types 'dict' or 'pd.Series', got '{type(VaR_series)}'")
        elif len(VaR_series) != len(alphas):
            raise ValueError(f"Length of VaR_series parameter ({len(VaR_series)}) must match the number of alpha values ({len(alphas)}) for which to calculate CVaR")
        try:
            return {alpha: calculate_mcCVaR(portfolio_returns, alpha, VaR=dict(VaR_series)[alpha]) for alpha in alphas}
        except KeyError:
            raise ValueError(f"Values of alphas in VaR_series parameter ({list(dict(VaR_series).keys())}) must correspond exactly with those of parameter 'alphas ' ({alphas})")
    return {alpha: calculate_mcCVaR(portfolio_returns, alpha) for alpha in alphas}

# def plot_mcVaR_and_mcCVaR(
#     *,
#     VaR_series: pd.Series,
#     CVaR_series: pd.Series,
#     show: bool = True
# ):
    
#     VaR_series = pd.Series(VaR_series) if isinstance(VaR_series, dict) else VaR_series
#     CVaR_series = pd.Series(CVaR_series) if isinstance(CVaR_series, dict) else CVaR_series
    
#     # Create a bar chart to display the results
#     fig = go.Figure()

#     # Add VaR trace
#     fig.add_trace(go.Bar(
#         name='Value at Risk (VaR)',
#         x=VaR_series.index,
#         y=VaR_series.values,
#         text=VaR_series.values,
#         textposition='auto'
#     ))

#     # Add CVaR trace
#     fig.add_trace(go.Bar(
#         name='Conditional Value at Risk (CVaR)',
#         x=CVaR_series.index,
#         y=CVaR_series.values,
#         text=CVaR_series.values,
#         textposition='auto'
#     ))

#     # Update the layout of the bar chart
#     fig.update_layout(
#         barmode='group',
#         title="VaR and CVaR Evaluation",
#         xaxis_title="Alpha Values",
#         yaxis_title="Value"
#     )
    
#     if show:
#         fig.show()
    
#     return fig