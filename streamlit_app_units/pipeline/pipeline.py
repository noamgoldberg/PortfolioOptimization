from typing import Union, List
import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from kedro.framework.session import KedroSession
from kedro.framework.project import configure_project
import yfinance

from streamlit_app_units.input.input import parse_symbols, gather_input
from streamlit_app_units.input.q_and_a import display_q_and_a

from portfolio_optimization.consts import CONF_ENV, DATE_FORMAT
from portfolio_optimization.utils.config_utils import write_yaml
from portfolio_optimization.utils.kedro_utils import read_params
from portfolio_optimization.utils.plotly_utils import change_plotly_fig_title
from portfolio_optimization.utils.formatting_utils import strip_stock_symbol


PROJECT_PATH = os.getcwd()

def set_local_params(
    *,
    symbols: Union[List[str], str],
    start_date: Union[pd.Timestamp, datetime],
    optimize_for: str,
):
    # (1)Erase Current Local Params
    write_yaml({}, f"{PROJECT_PATH}/{CONF_ENV}/local/parameters.yml")
    
    # (2) Set New Local Params
    params = read_params(conf=CONF_ENV)
    symbols = parse_symbols(symbols) if isinstance(symbols, str) else symbols
    params["data"]["stocks"]["symbols"] = list(map(strip_stock_symbol, symbols))
    params["data"]["stocks"]["start_date"] = start_date.strftime(format=DATE_FORMAT)
    params["visualize"]["show"] = False
    write_yaml(params, f"{PROJECT_PATH}/{CONF_ENV}/local/parameters.yml")
    return params


def run_pipeline(
    *,
    symbols: Union[List[str], str],
    start_date: Union[pd.Timestamp, datetime],
    end_date: Union[pd.Timestamp, datetime],
    optimize_for: str,
    project_name: str = "portfolio_optimization",
    project_path: str = PROJECT_PATH,
    conf_source: str = "conf",
    pipeline_name: str = "portfolio_optimization"
):
    # (1) Establish (Local) Params
    params = set_local_params(symbols=symbols, start_date=start_date, optimize_for=optimize_for)
    
    # (2) Instantiate Kedro Session
    configure_project(project_name)

    with KedroSession.create(project_path=project_path, conf_source=conf_source) as session:
        
        # (3) Run Pipeline & 
        datasets = session.run(pipeline_name=pipeline_name)
    
    # (4) Return Params & (Non-Input, Output-Only) Datasets
    return params, datasets