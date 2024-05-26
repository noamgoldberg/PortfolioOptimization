import os 
import sys
PROJECT_PATH = os.getcwd()
sys.path.append(f"{PROJECT_PATH}/src")

################################################################################

import streamlit as st

from streamlit_app_units.input.input import parse_symbols, gather_input
from streamlit_app_units.input.q_and_a import display_q_and_a
from streamlit_app_units.pipeline.pipeline import run_pipeline
from streamlit_app_units.output.output import display_output


def run():    
    
    # (1) Title
    st.title("Portfolio Optimization & Monte Carlo Simulation")
    
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
            if parse_symbols(symbols):
                
                # Placeholder GIF
                placeholder = st.empty()
                with placeholder:
                    st.image(
                        "images/doing_science.gif",
                        caption="...Doing Science",
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
                placeholder.empty()
                display_output(params=params, datasets=datasets)
                
            else:
                st.error("Please enter tickers and select at least one method.")

        
if __name__ == "__main__":
    run()
    