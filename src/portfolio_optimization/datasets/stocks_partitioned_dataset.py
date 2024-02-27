# from typing import Any, Dict, Union, Iterable, Optional
# import pandas as pd
# from kedro.io import PartitionedDataSet
# from kedro.io.core import DataSetError
# from copy import deepcopy
# from datetime import datetime
# from portfolio_optimization.datasets.stocks_data_loader import StocksDataLoader
# from portfolio_optimization.consts import DATE_FORMAT


# class StocksPartitionedDataSet(PartitionedDataSet):
#     def __init__(
#         self,
#         path: str,
#         dataset,
#         symbols: Union[str, Iterable[str]],
#         start_date: str,
#         end_date: Optional[str] = None,
#         **kwargs
#     ):
#         super().__init__(path, dataset, **kwargs)
#         self.symbols = [symbols] if isinstance(symbols, str) else list(symbols)
#         self.start_date = pd.to_datetime(start_date).strftime(DATE_FORMAT)
#         end_date = datetime.today() if end_date is None else pd.to_datetime(end_date)
#         self.end_date = end_date.strftime(DATE_FORMAT)
        # self.loader = StocksDataLoader(self.symbols, self.start_date, self.end_date)

    # def _load(self) -> Dict[str, Dict[str, pd.Series]]:
    #     """
    #     Custom load method to organize data into a nested dictionary structure
    #     where the first level keys are stock tickers and the second level keys are dates.
    #     """
        # try:
        #     partitions = super()._load() # Load using the base class's load method
        #     partitions = {f"{k.split('.')[0]}": v for k, v in partitions.items()}
        # except DataSetError:
        #     partitions = self.loader.get_data(return_dict=True)
        #     self._save(partitions)
        # return partitions