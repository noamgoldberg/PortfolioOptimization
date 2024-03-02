import pandas as pd
import yfinance
import streamlit as st
from datetime import datetime, timedelta

from portfolio_optimization.consts import DATE_FORMAT


def parse_symbols(symbols_input: str):
    return list(set([s.strip().upper() for s in symbols_input.split(',') if s.strip()]))

def check_input():
    NUM_SYMBOLS_LIMIT = 50
    symbols_input = parse_symbols(st.session_state.symbols)
    infos = {s: yfinance.ticker.Ticker(s).info for s in symbols_input}
    invalid_symbols = [s for s, info in infos.items() if len(info) < 10]
    if len(invalid_symbols) > 0:
        st.error(f"Input invalid. The following tickers could not be found: {', '.join(invalid_symbols)}")
    elif len(symbols_input) > NUM_SYMBOLS_LIMIT:
        st.error(f'Input invalid, too many tickers. Please enter {NUM_SYMBOLS_LIMIT} stock tickers or less.')

def gather_input():
    symbols = st.text_input(
        "Enter stock tickers, separated by commas (e.g. AAPL, GOOG, MSFT, ...)",
        "AAPL, GOOG, MSFT, BABA, META, V, C, XOM, OXY, SHEL, JPM, BAC, WFC, CVX, DE, CI",
        key="symbols",
        on_change=check_input,
    )
    start_date = st.date_input(
        "Enter a 'Start Date' from which stock prices will be collected and analyzed",
        value=pd.to_datetime("2020-01-01"),
        min_value=pd.to_datetime("2010-01-01", format=DATE_FORMAT),
        max_value=datetime.today() - timedelta(weeks=8),
    )
    end_date = datetime.today()
    optimize_for = st.selectbox("Select a metric for which to optimize", options=["Sharpe Ratio"], index=0)
    return symbols, start_date, end_date, optimize_for
