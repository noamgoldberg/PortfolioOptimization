from typing import Dict, Union, Callable, Any
import pandas as pd

from portfolio_optimization.consts import DATE_FORMAT
from portfolio_optimization.utils.data_utils import concat_partitions, filter_stocks_df_for_agg


def get_stock_prices_stats(
    stocks_data: Dict[str, Union[Callable, pd.DataFrame]],
    params: Dict[str, Any],
):
    stocks_data = filter_stocks_df_for_agg(concat_partitions(stocks_data), params["optimize"]["optimize_on"])
    start_date = stocks_data.index.min().strftime(DATE_FORMAT)
    end_date = stocks_data.index.max().strftime(DATE_FORMAT)
    stats = stocks_data.describe().loc[['mean', 'std', 'min', 'max']]
    return {
        "start_date": start_date,
        "end_date": end_date,
        "stats": stats,
    }