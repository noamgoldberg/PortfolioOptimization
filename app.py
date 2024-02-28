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
                st.header(f"Stocks Information", anchor="stocks_information")
                st.write(f"Stocks: {symbols}")
                st.write(f"Start Date: {datasets['stock_prices_stats']['start_date']}")
                st.write(f"End Date: {datasets['stock_prices_stats']['end_date']}")
                st.divider()
                stock_prices_fig = datasets["stock_prices_plot"]
                st.plotly_chart(stock_prices_fig)
                st.write(datasets['stock_prices_stats']['stats'])
                
                # (C) Print Portfolio Stats
                if 'portfolios_stats' in datasets and datasets['portfolios_stats']:
                    st.divider()
                    st.header("Portfolios Optimization Results", anchor="portfolios_optimization_results")
                    st.write(
                        "Portfolio optimization is a mathematical method used to select the best stocks and their allocations "
                        "to maximize returns for a given level of risk, or alternatively, to minimize risk for a given level "
                        "of expected return."
                    )
                    st.write("This project compares 2 investment portfolio optimization techniques:")
                    st.markdown(
                        "1. Sequential Least Squares Programming, or SLSQP (administered by the SciPy python library), an "
                        "optimization technique ideal for handling multivariate problems with constraints, and"
                    )
                    st.markdown(
                        "2. Monte Carlo simulation, a computational algorithm that uses repeated random sampling to obtain "
                        "the likelihood of a range of results of occurring. In this case, Monte Carlo simulations are useful "
                        "for estimating the probability of various investment outcomes"
                    )
                    st.write(
                        "SLSQP is typically much more effective than Monte Carlo simulations for portfolio optimization due to its precision in finding optimal solutions under complex constraints. "
                        "You may notice this in the scatterplot below, where SLSQP has most likely generated a set of portfolio weights that "
                        "yield a signfiicantly higher Sharpe Ratio."
                    )
                    st.markdown(
                        '''
                        <style>
                        [data-testid="stMarkdownContainer"] ul{
                            padding-left:40px;
                        }
                        </style>
                        ''', 
                        unsafe_allow_html=True
                    )
                    
                    # Determine the number of columns based on the number of methods
                    methods_count = len(datasets['portfolios_stats'])
                    cols = st.columns(methods_count)

                    for i, (method, df) in enumerate(datasets['portfolios_stats'].items()):
                        with cols[i]:
                            st.write(f"Method: {method.title()}")
                            st.dataframe(df)  # Using st.dataframe to ensure the dataframe is displayed correctly

                # (C) Display Best Weights
                st.write("Optimal Portfolio Weights")
                st.write(datasets["best_portfolio_weights"])
                
                # (D) Plot Portfolios
                
                portfolios_plot = datasets["portfolios_plot"]
                st.plotly_chart(portfolios_plot)
                st.write(
                    "The portfolios plot visualizes the risk-return profile of various portfolio configurations. Each point represents a "
                    "portfolio, with its position indicating the trade-off between risk (volatility) and expected return. This aids in "
                    "visualizing the efficiency frontier and selecting an optimal portfolio."
                )

        else:
            st.error("Please enter tickers and select at least one method.")
        
        
if __name__ == "__main__":
    run()