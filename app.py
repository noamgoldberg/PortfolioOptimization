import os 
import sys
PROJECT_PATH = os.getcwd()
sys.path.append(f"{PROJECT_PATH}/src")

################################################################################

import streamlit as st

from streamlit_app_units.input.input import parse_symbols, gather_input
from streamlit_app_units.input.q_and_a import display_a_and_a
from streamlit_app_units.pipeline.pipeline import run_pipeline
from streamlit_app_units.output.output import display_output


def run():    
    
    # (1) Title
    st.title("Stocks Portfolio Optimization")
    
    # (2) Gather Input & Display Q&As
    symbols, start_date, end_date, optimize_for = gather_input()
    display_a_and_a()
    
    # (3) Launch App
    if st.button("Analyze & Plot Results"):
        # try:
        if parse_symbols(symbols):
            
            # (A) Run Pipeline
            params, datasets = run_pipeline(
                symbols=symbols,
                start_date=start_date,
                end_date=end_date,
                optimize_for=optimize_for
            )
            
            # (B) Display Stats & Results
            display_output(params=params, datasets=datasets)
            
        else:
            st.error("Please enter tickers and select at least one method.")
        # except:
        #     st.error("Input invalid. Please try again.")
            
        
if __name__ == "__main__":
    run()
    