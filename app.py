import os 
import sys
PROJECT_PATH = os.getcwd()
sys.path.append(f"{PROJECT_PATH}/src")

################################################################################

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from kedro.framework.session import KedroSession
from kedro.framework.project import configure_project

from portfolio_optimization.consts import CONF_ENV, DATE_FORMAT
from portfolio_optimization.units.visualize import plot_portfolios
from portfolio_optimization.utils.config_utils import write_yaml
from portfolio_optimization.utils.data_utils import concat_partitions, filter_stocks_df_for_agg
from portfolio_optimization.utils.kedro_utils import read_params


def run():    
    
    st.title("Portfolio Optimization")

    # (1) Establish (Local) Parameters
    symbols = st.text_input(
        "Enter stock tickers, separated by commas (e.g., AAPL, GOOG, MSFT)",
        "AAPL, GOOG, MSFT, BABA, META, V"
        )
    start_date = st.date_input(
        "Enter a 'Start Date' from which stock prices will be collected and analyzed",
        value=pd.to_datetime("2022-01-01"),
        min_value=pd.to_datetime("2020-01-01", format=DATE_FORMAT),
        max_value=datetime.today() - timedelta(weeks=8),
    )
    # params["optimize"]["methods"] = st.multiselect(
    #     "Select which optimization methods you would like to execute and visualize:",
    #     options=["Scipy", "Monty Carlo"],
    #     default=["Scipy", "Monty Carlo"]
    # )
    # selected_methods = [sm.lower() for sm in selected_methods]

    # (2) Launch App
    if st.button("Analyze & Plot Results"):
        if symbols:
            
            # Set (Local) Parameters
            params = read_params(conf=CONF_ENV)
            params["data"]["stocks"]["symbols"] = [s.strip() for s in symbols.split(',')]
            params["data"]["stocks"]["start_date"] = start_date.strftime(format=DATE_FORMAT)
            params["visualize"]["show"] = False
            write_yaml(params, f"{PROJECT_PATH}/{CONF_ENV}/local/parameters.yml")
            
            # Instantiate Kedro Session
            configure_project("portfolio_optimization")
            with KedroSession.create(project_path=PROJECT_PATH, conf_source="conf") as session:
                context = session.load_context()
                
                # (A) Run Pipeline
                datasets = session.run(pipeline_name="portfolio_optimization")
                
                # (B) Print Stock Stats & Plot Prices Over Time
                st.divider()
                st.write(f"Stocks: {symbols}")
                st.write(f"Start Date: {datasets['stock_prices_stats']['start_date']}")
                st.write(f"End Date: {datasets['stock_prices_stats']['end_date']}")
                st.write("Stock Prices Over Time:")
                st.write(datasets['stock_prices_stats']['stats'])
                stock_prices_fig = datasets["stock_prices_plot"]
                st.plotly_chart(stock_prices_fig)
                
                # (C) Print Portfolio Stats
                if 'portfolios_stats' in datasets and datasets['portfolios_stats']:
                    st.divider()
                    st.write("Portfolios Optimization Results:")

                    # Determine the number of columns based on the number of methods
                    methods_count = len(datasets['portfolios_stats'])
                    cols = st.columns(methods_count)

                    for i, (method, df) in enumerate(datasets['portfolios_stats'].items()):
                        with cols[i]:
                            st.write(f"Method: {method.title()}")
                            st.dataframe(df)  # Using st.dataframe to ensure the dataframe is displayed correctly

                # (C) Display Best Weights
                st.write("Optimal Portfolio Weights:")
                st.write(datasets["best_portfolio_weights"])
                
                # (D) Plot Portfolios
                portfolios_plot = datasets["portfolios_plot"]
                st.plotly_chart(portfolios_plot)
        else:
            st.error("Please enter tickers and select at least one method.")
        
if __name__ == "__main__":
    run()