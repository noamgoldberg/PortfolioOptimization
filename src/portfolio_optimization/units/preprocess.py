from typing import Dict, Callable, Union, Any, Optional, Iterable
import pandas as pd
import numpy as np

from portfolio_optimization.utils.data_utils import compute_pct_change
from portfolio_optimization.utils.formatting_utils import str2list
from portfolio_optimization.utils.wrapper_utils import wrapper


def preprocess(
    prices_data: Dict[str, Union[Callable, pd.DataFrame]],
    params: Dict[str, Any],
):
    compute_on = params["data"]["stocks"]["compute_pct_change_on"]
    if params["data"]["stocks"].get("normalize", False):
        prices_data = normalize_prices(prices_data, compute_on=compute_on)
    returns_data = convert_prices_to_returns(prices_data, compute_on=compute_on)
    log_returns_data = log_data(returns_data)
    return returns_data, log_returns_data

def normalize_prices(
    prices_data: Dict[str, Union[Callable, pd.DataFrame]],
    *,
    compute_on: str,
):
    def _normalize_features(df: pd.DataFrame, columns: Optional[Union[Iterable[str], str]] = None):
        columns = str2list(columns) if columns else df.columns
        for col in columns:
            df[col] = df[col] / df.iloc[0][col]  # normalize stock prices by initial price
        return df
    prices_norm_data = {
        ticker: wrapper(_normalize_features, df, columns=compute_on)
        for ticker, df in prices_data.items()
    }
    return prices_norm_data

def convert_prices_to_returns(
    prices_data: Dict[str, Union[Callable, pd.DataFrame]],
    *,
    compute_on: str,
):
    returns_data = {
        stock: wrapper(compute_pct_change, df, compute_on=compute_on, return_df=True)
        for stock, df in prices_data.items()
    }
    return returns_data

def log_data(
    data: Dict[str, Union[Callable, pd.DataFrame]],
):
    log_data = {
        ticker: wrapper(lambda df: pd.DataFrame(np.log1p(df), index=df.index, columns=df.columns), df)
        for ticker, df in data.items()
    }
    return log_data

