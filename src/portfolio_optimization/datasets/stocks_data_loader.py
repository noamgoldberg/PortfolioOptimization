from typing import Union, Iterable, Optional, Callable, Any, Dict
import yfinance as yf
import pandas as pd

from portfolio_optimization.utils.formatting_utils import strip_stock_symbol
from portfolio_optimization.utils.kedro_utils import read_catalog
from portfolio_optimization.utils.wrapper_utils import wrapper

class StocksDataLoader:
    def __init__(
        self,
        symbols: Union[str, Iterable[str]],
        start_date: str,
        end_date: Optional[str] = None,
    ):
        self.symbols = self.obj2list(symbols)
        [symbols] if isinstance(symbols, str) else list(symbols)
        self.symbols = list(map(strip_stock_symbol, self.symbols))
        self.start_date = start_date
        self.end_date = end_date
        self._data = None
        self._test_yf_download()
    
    @staticmethod
    def obj2list(obj: Any) -> list:
        return [obj] if isinstance(obj, str) else list(obj)
    
    def _test_yf_download(self):
        test_symbols = self.symbols
        stocks_data = self._download_and_clean_data(self.symbols, self.start_date, end_date=self.end_date)
        shape_msg = f"Shape of data: {stocks_data.shape}"
        print("TEST:", shape_msg)
        print("HEAD rows:", stocks_data.iloc[:5, 0])
        print("HEAD cols:", stocks_data.columns[:5])
        if stocks_data.shape[0] == 0 or stocks_data.shape[1] == 0:
            msg = f"{test_symbols}: Failed to download stocks data from Yahoo Finance. {shape_msg}"
            raise Exception(msg)
        return stocks_data
        
    def _download_and_clean_data(
        self,
        symbols: Union[str, Iterable[str]],
        start_date: str,
        end_date: Optional[str] = None,
        batch_size: Optional[int] = 10,
    ) -> pd.DataFrame:
        symbols = self.obj2list(symbols)
        all_data = []
        for i in range(0, len(symbols), batch_size):
            batch_symbols = symbols[i:i + batch_size]
            data: pd.DataFrame = yf.download(batch_symbols, start=start_date, end=end_date)
            data.columns = data.columns.swaplevel(0, 1)
            data.sort_index(axis=1, level=0, inplace=True)
            all_data.append(data)
        
        return pd.concat(all_data, axis=1) if all_data else pd.DataFrame()
    
    @property
    def data(self) -> pd.DataFrame:
        if self._data is None:
            self._data = self._download_and_clean_data(self.symbols, self.start_date, end_date=self.end_date)
        return self._data

    def get_data(
        self,
        return_dict: bool = True,
        _callable: bool = False
    ) -> Union[Dict[str, Callable], pd.DataFrame]:
        if return_dict:
            def _get_ticker_data(ticker: str) -> Callable:
                return self.data[ticker]
            partitions = {
                ticker: (wrapper(_get_ticker_data, ticker) if _callable else _get_ticker_data(ticker))
                for ticker in self.data.columns.get_level_values('Ticker').unique()
            }
            return partitions
        return self.data