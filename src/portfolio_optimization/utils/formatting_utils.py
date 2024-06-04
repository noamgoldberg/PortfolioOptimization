from typing import Iterable, Union
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

def format_currency_str(
    value: Union[int, float],
    currency = "$",
    decimals: Union[int, float] = 0,
    escape_seq: bool = False
) -> str:
    formatted = f"{['', '-'][int(value < 0)]}"
    formatted += f"\{currency}" if escape_seq else f"{currency}"
    decimals_dict = {
        0: f"{np.abs(value):,.0f}",
        1: f"{np.abs(value):,.1f}",
        2: f"{np.abs(value):,.2f}",
    }
    try:
        return f"{formatted}{decimals_dict[decimals]}"
    except KeyError:
        raise ValueError(f"Invalid value for 'decimals' parameter; choose from {decimals_dict.keys()}")