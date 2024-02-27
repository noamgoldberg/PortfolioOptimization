from typing import Iterable, Any
import pandas as pd
import numpy as np

def strip_stock_symbol(symbol: str):
    return symbol.split(":")[-1]

def iterable2list(obj: Iterable):
    if isinstance(obj, (list, tuple, set, pd.Index, np.ndarray)):
        return list(obj)
    raise TypeError(f"{obj}: Expected one of types [list, tuple, set, pd.Index], got {type(obj)}")

def str2list(obj: str):
    if isinstance(obj, str):
        return [obj]
    try:
        return iterable2list(obj)
    except TypeError:
        raise TypeError(f"{obj}: Expected one of types [str, list, tuple, set, pd.Index], got {type(obj)}")
        