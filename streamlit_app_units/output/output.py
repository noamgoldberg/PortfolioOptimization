from typing import Dict, Any
import streamlit as st

from streamlit_app_units.output.stats import display_stats
from streamlit_app_units.output.results import display_optimize, display_simulation_and_evaluation
from streamlit_app_units.format import format_app_markdown


def display_output(
    *,
    params: Dict[str, Any],
    datasets: Dict[str, Any]
):
    # Display Output Elements
    (
        tab1,
        # tab2, 
        tab3,
    ) = st.tabs([
        "Monte Carlo Simulation",
        # "Optimize Portfolio Weights",
        "Analyze Historical Stocks Data"
    ])
    display_stats(tab=tab3, params=params, datasets=datasets)
    # display_optimize(tab=tab2, datasets=datasets, params=params)
    display_simulation_and_evaluation(tab=tab1, datasets=datasets, params=params)
    
    # Write a concise description of the resulting VaR and CVaR, and what that means in terms of an assessment of the portfolio with the gievn % percent confidence.
    
    # Format
    format_app_markdown()

