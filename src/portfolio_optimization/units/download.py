from typing import Any, Dict, Callable

from portfolio_optimization.consts import DATE_FORMAT
from portfolio_optimization.datasets.stocks_data_loader import StocksDataLoader
from portfolio_optimization.utils.date_utils import format_date, get_end_date


def download_stock_prices(params: Dict[str, Any]) -> Dict[str, Callable]:
    symbols = params["data"]["stocks"]["symbols"]
    start_date = format_date(params["data"]["stocks"]["start_date"], format=DATE_FORMAT)
    end_date = get_end_date(params["data"]["stocks"].get("end_date"), format=DATE_FORMAT)
    loader = StocksDataLoader(symbols, start_date, end_date)
    data = loader.get_data(return_dict=True)
    return data
