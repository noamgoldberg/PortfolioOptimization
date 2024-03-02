from typing import Dict, Any, Union
import pandas as pd
import streamlit as st
from datetime import datetime

from portfolio_optimization.consts import DATE_FORMAT
from portfolio_optimization.utils.plotly_utils import change_plotly_fig_title


def display_stats(
    *,
    params: Dict[str, Any],
    datasets: Dict[str, Any]
):
    st.divider()
    
    # (7) Stocks Statistics
    st.header(f"Stocks Statistics", anchor="stocks_statistics")
    st.write(f"Stocks: {', '.join(params['data']['stocks']['symbols'])}")
    st.write(f"Start Date: {datasets['stock_prices_stats']['start_date']}")
    st.write(f"End Date: {datasets['stock_prices_stats']['end_date']}")
    
    # (8) Stats: Stock Prices or Returns
    stocks_data_type_options = ["Stock Prices (Adjusted Close)", "Daily Stock Returns (%)"]
    selected_stocks_data_type = st.selectbox(
        "Select the type of stocks data for which you'd like to see statistics",
        options=stocks_data_type_options, index=0
    )
    if selected_stocks_data_type == stocks_data_type_options[0]:
        st.subheader("Stats: Stock Prices (Adjusted Close)")
        st.write("This section analyzes the daily \"Adjusted Close\" price of each stock over time")
        st.plotly_chart(datasets["stock_prices_plot"])
        st.plotly_chart(datasets["stock_prices_box_plot"])
        stock_prices_corr_matrix_plot = change_plotly_fig_title(
            datasets["stock_prices_corr_matrix_plot"], "Stock Prices Correlation Matrix"
        )
        st.plotly_chart(stock_prices_corr_matrix_plot)
        st.write("How do these stocks move with one anothe?")
        st.write(
            "This heatmap shows the correlation, or strength of the linear relationship, between each pair of stocks:\n"
            "- Blue means a strong POSITIVE correlation, meaning the pair of stocks move up and down together\n"
            "- Red means a strong NEGATIVE correlation, meaning the pair of stocks are inversely related - when one stock increases in value, the other decreases\n"
            "- White indicates a WEAK correlation (or no correlation), meaning the pair of stocks have little or no linear relationship\n"
        )
    elif selected_stocks_data_type == stocks_data_type_options[1]:
        st.subheader("Stats: Daily Stock Returns (%)")
        st.write("This section analyzes the daily percentage increase/decrease of each stock over time")
        st.plotly_chart(datasets["stock_returns_plot"])
        st.plotly_chart(datasets["stock_returns_box_plot"])