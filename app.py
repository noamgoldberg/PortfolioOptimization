import os 
import sys
PROJECT_PATH = os.getcwd()
sys.path.append(f"{PROJECT_PATH}/src")

################################################################################

import yfinance as yf
import streamlit as st

from streamlit_app_units.input.input import parse_symbols, gather_input
from streamlit_app_units.input.q_and_a import display_q_and_a
from streamlit_app_units.pipeline.pipeline import run_pipeline
from streamlit_app_units.output.output import display_output
from portfolio_optimization.utils.formatting_utils import strip_stock_symbol


def is_ticker_valid(ticker: str) -> bool:
    """
    Checks if an ticker is available via the Yahoo Finance API.
    """
    info = yf.Ticker(ticker).history(
        period='7d',
        interval='1d'
    )
    return len(info) > 0

def run():    
    
    # (1) Title
    st.title("Stock Portfolio Performance Simulator")
    
    # (2) Gather Input & Display Q&As
    symbols, start_date, end_date, optimize_for = gather_input()
    display_q_and_a()
    
    # (3) Launch App
    if 'datasets' in st.session_state:
        display_output(
            params=st.session_state.params,
            datasets=st.session_state.datasets
        )
    else:
        # Run Analysis and Store Results in Session State
        if st.button("Optimize Portfolio & Simulate"):
            symbols = list(map(strip_stock_symbol, parse_symbols(symbols)))
            if symbols:
                invalid_tickers = [symbol for symbol in symbols if not is_ticker_valid(symbol)]
                
                # Validate tickers
                if len(invalid_tickers) > 0:
                    error = f"The following tickers are invalid: {invalid_tickers}"
                    st.error(error)
                else:
                    placeholder_1 = st.empty()
                    placeholder_2 = st.empty()
                    with placeholder_1:
                        st.markdown("<h4 style='text-align: center;'>...Analyzing</h4>", unsafe_allow_html=True)
                    with placeholder_2:
                        st.image(
                            "images/doing_science.gif",
                            caption="...Patience...He's Doing Science",
                            use_column_width=True
                        )

                    # Generate Results
                    params, datasets = run_pipeline(
                        symbols=symbols,
                        start_date=start_date,
                        end_date=end_date,
                        optimize_for=optimize_for
                    )
                    st.session_state.params = params
                    st.session_state.datasets = datasets
                    
                    # Clear Placeholder & Display Results
                    placeholder_1.empty()
                    placeholder_2.empty()
                    display_output(params=params, datasets=datasets)
            else:
                st.error("Please enter tickers and select at least one method.")

        
if __name__ == "__main__":
    run()
    