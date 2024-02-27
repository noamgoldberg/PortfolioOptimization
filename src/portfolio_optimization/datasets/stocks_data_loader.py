from typing import Union, Iterable, Optional, Callable
import yfinance as yf

from portfolio_optimization.utils.wrapper_utils import wrapper
from portfolio_optimization.utils.formatting_utils import strip_stock_symbol

class StocksDataLoader:
    def __init__(
        self,
        symbols: Union[str, Iterable[str]],
        start_date: str,
        end_date: Optional[str] = None,
    ):
        self.symbols = [symbols] if isinstance(symbols, str) else list(symbols)
        self.symbols = list(map(strip_stock_symbol, self.symbols))
        self.start_date = start_date
        self.end_date = end_date
        self._data = None
    
    @property
    def data(self):
        if self._data is None:
            self._data = yf.download(self.symbols, start=self.start_date, end=self.end_date)
            self._data.columns = self._data.columns.swaplevel(0, 1)
            self._data.sort_index(axis=1, level=0, inplace=True)
        return self._data

    
    def get_data(self, return_dict: bool = True):
        if return_dict:
            def _helper(ticker: str) -> Callable:
                return self.data[ticker]
            partitions = {
                ticker: wrapper(_helper, ticker)
                for ticker in self.data.columns.get_level_values('Ticker').unique()
            }
            return partitions
        return self.data