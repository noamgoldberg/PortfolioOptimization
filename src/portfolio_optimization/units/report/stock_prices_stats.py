from typing import Dict, Union, Callable, Any
import pandas as pd
import streamlit as st

from portfolio_optimization.consts import DATE_FORMAT
from portfolio_optimization.utils.data_utils import concat_partitions, filter_stocks_df_for_agg, get_stock_returns
from portfolio_optimization.utils.financial_utils import get_num_trading_periods


def get_stock_prices_stats(
    stocks_data: Dict[str, Union[Callable, pd.DataFrame]],
    agg: str = "Close",
) -> Dict[str, Any]:
    stocks_data: pd.DataFrame = filter_stocks_df_for_agg(concat_partitions(stocks_data), agg)
    start_date = stocks_data.index.min().strftime(DATE_FORMAT)
    end_date = stocks_data.index.max().strftime(DATE_FORMAT)
    if stocks_data.empty:
        st.error(f"Failed to retrieve 'stocks_data' dataset (shape: {stocks_data.shape}, columns: {stocks_data.columns})")
        raise Exception(f"Failed to retrieve 'stocks_data' dataset (shape: {stocks_data.shape}, columns: {stocks_data.columns})")
    stats = stocks_data.describe().loc[['mean', 'std', 'min', 'max']]
    return {
        "start_date": start_date,
        "end_date": end_date,
        "stats": stats,
    }

def get_stock_prices_corr_matrix(
    stocks_data: Dict[str, Union[Callable, pd.DataFrame]],
    agg: str = "Close",
) -> pd.DataFrame:
    stocks_data: pd.DataFrame = filter_stocks_df_for_agg(concat_partitions(stocks_data), agg)
    return stocks_data.corr()

def get_stock_returns_cov_matrix(
    stocks_data: Dict[str, Union[Callable, pd.DataFrame]],
    agg: str = "Close",
    period: str = "daily"
) -> pd.DataFrame:
    returns = get_stock_returns(stocks_data, agg)
    return returns.cov() * get_num_trading_periods(period)