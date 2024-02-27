from typing import Union, Callable, Optional, Iterable, Dict, Any
import pandas as pd
from numpy.typing import ArrayLike

from portfolio_optimization.consts import INDEX_COL
from portfolio_optimization.utils.formatting_utils import str2list


def callable2obj(obj: Any) -> Any:
    return obj() if callable(obj) else obj

def verify_1D(arr: ArrayLike, name: Optional[str] = None):
    error = ValueError(f"{arr.shape}: Shape of {name + ' ' if name else ''}array must be one dimensional")
    if len(arr.shape) == 0:
        raise error
    if len(arr.shape) != 1:
        if len(arr.shape) != 2:
            raise error
        elif arr.shape[1] != 1:
            raise error

def concat_partitions(dfs: Union[Dict[str, Union[Callable, pd.DataFrame]], Iterable[Union[Callable, pd.DataFrame]]]):
    if callable(dfs):
        dfs = dfs()
    if isinstance(dfs, pd.DataFrame):
        return dfs
    if isinstance(dfs, dict):
        dfs_list = []
        for title, df in dfs.items():
            df = pd.DataFrame(callable2obj(df))
            df.columns = [f"{title}_{col}" for col in df.columns] if df.shape[1] > 1 else [title]
            dfs_list += [df]
        return pd.concat(dfs_list, axis=1, ignore_index=False)
    raise TypeError(f"Expected one of types [Callable, pd.DataFrame, dict] for 'dfs' parameter, got '{type(dfs)}'")

def compute_pct_change(
    df: pd.DataFrame,
    *,
    compute_on: str,
    return_df: bool = False
):
    pct_change = df[compute_on].pct_change()
    return pd.DataFrame(pct_change) if return_df else pct_change

def filter_stocks_df_for_agg(
    df: pd.DataFrame,
    agg_col: str = "Adj Close",
):
    suffix = f"_{agg_col}"
    df = df[[f for f in df if f.endswith(suffix)]]
    df.columns = [f.rstrip(suffix) for f in df]
    return df

def set_index(df: Union[Callable, pd.DataFrame], col: str = INDEX_COL) -> pd.DataFrame:
    if not isinstance(col, str):
        raise TypeError(f"{col}: Expected type 'str', got {type(col)}")
    df = df() if callable(df) else df
    if df.index.name != col:
        if col in str2list(df.index.name or []):
            df = df.reset_index()
        df = df.set_index(col)
    return df

