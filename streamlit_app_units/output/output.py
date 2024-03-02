from typing import Dict, Any

from streamlit_app_units.output.stats import display_stats
from streamlit_app_units.output.results import display_results
from streamlit_app_units.format import format_app_markdown


def display_output(
    *,
    params: Dict[str, Any],
    datasets: Dict[str, Any]
):
    display_stats(params=params, datasets=datasets)
    display_results(params=params, datasets=datasets)
    format_app_markdown()
