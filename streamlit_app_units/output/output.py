from typing import Dict, Any
import streamlit as st

from streamlit_app_units.output.stats import display_stats
from streamlit_app_units.output.results import display_results
from streamlit_app_units.format import format_app_markdown


def display_output(
    *,
    params: Dict[str, Any],
    datasets: Dict[str, Any]
):
    (
        tab1,
        tab3,
    ) = st.tabs([
        "Monte Carlo Simulation",
        "Analyze Historical Stocks Data"
    ])
    display_stats(tab=tab3, params=params, datasets=datasets)
    display_results(tab=tab1, datasets=datasets, params=params)
    format_app_markdown()

