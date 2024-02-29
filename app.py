import os 
import sys
PROJECT_PATH = os.getcwd()
sys.path.append(f"{PROJECT_PATH}/src")

################################################################################

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from kedro.framework.session import KedroSession
from kedro.framework.project import configure_project

from portfolio_optimization.consts import CONF_ENV, DATE_FORMAT
from portfolio_optimization.utils.config_utils import write_yaml
from portfolio_optimization.utils.kedro_utils import read_params
from portfolio_optimization.utils.plotly_utils import change_plotly_fig_title


def run():    
    
    st.title("Stock Portfolio Optimization")

    # (1) Establish (Local) Parameters
    def check_input():
        user_input = list(set([s.strip().upper() for s in st.session_state.symbols.split(',')]))
        if len(user_input) > 30:
            st.error('Input invalid, too many tickers. Please enter 30 stock tickers or less.')
        else:
            pass
    symbols = st.text_input(
        "Enter stock tickers, separated by commas (e.g., AAPL, GOOG, MSFT, BABA, META, V)",
        "AAPL, GOOG, MSFT, BABA, META, V",
        key="symbols",
        on_change=check_input
    )
    start_date = st.date_input(
        "Enter a 'Start Date' from which stock prices will be collected and analyzed",
        value=pd.to_datetime("2022-01-01"),
        min_value=pd.to_datetime("2018-01-01", format=DATE_FORMAT),
        max_value=datetime.today() - timedelta(weeks=8),
    )
    optimize_for = st.selectbox("Select a metric to optimize for", options=["Sharpe Ratio"], index=0)
    
    # (2) Collapsable Q&As
    with st.expander("What is portfolio optimization?"):
        st.write(
            "Portfolio optimization is a mathematical method used to select the best stocks and their allocations "
            "to maximize returns for a given level of risk, or alternatively, to minimize risk for a given level "
            "of expected return."
        )
    with st.expander("What is the Sharpe Ratio? Why is it useful?"):
        st.write("The Sharpe Ratio measures risk-adjusted returns by comparing the excess return of an investment to its volatility.")
        st.write("""Formula:
    
        Sharpe Ratio = (Portfolio Return - Risk Free Rate) / Portfolio Volatility"""
        )
        st.write(
            "Uses:\n- Risk-Adjusted Returns: Quantifies excess return per unit of risk.\n- Comparative "
            "Tool: Facilitates direct comparison between diverse investments.\n- Optimization: Aids in "
            "constructing portfolios with optimal risk-adjusted returns.\n- Performance Measure: Evaluates "
            "efficiency of investments or portfolios."
        )
        st.write(
            "Advantages:\n- Adjusts for risk, allowing investors to compare the performance of different "
            "investments on a level playing field\n- Its calculation is straightforward and universally "
            "understood, making it easy for investors of all levels to compare the risk-adjusted returns "
            "of different portfolios or assets\n- Its calculation is straightforward and universally "
            "understood, making it easy for investors of all levels to compare the risk-adjusted returns "
            "of different portfolios or assets\n- Rewards investments that provide stable returns with "
            "less volatility."
        )
        st.write(
            "Disadvantages:\n- Assumes returns are normally distributed, which is not always the case\n"
            "- Uses volatility (standard deviation) as its sole measure of risk, missing out on other "
            "external factors that could indicate different kinds of risk\n- Sensitives to the risk "
            "free rate; ratio can fluctuate can fluctuate due to factors unrelated to the investment's "
            "performance, potentially misleading in different interest rate environments."
        )
        
    # (3) Launch App
    if st.button("Analyze & Plot Results"):
        try:
            if symbols:
                
                # (4) Set (Local) Parameters
                params = read_params(conf=CONF_ENV)
                params["data"]["stocks"]["symbols"] = list(set([s.strip().upper() for s in symbols.split(',')]))
                params["data"]["stocks"]["start_date"] = start_date.strftime(format=DATE_FORMAT)
                params["visualize"]["show"] = False
                write_yaml(params, f"{PROJECT_PATH}/{CONF_ENV}/local/parameters.yml")
                
                # (5) Instantiate Kedro Session
                configure_project("portfolio_optimization")
                with KedroSession.create(project_path=PROJECT_PATH, conf_source="conf") as session:
                    context = session.load_context()
                    
                    # (6) Run Pipeline
                    datasets = session.run(pipeline_name="portfolio_optimization")
                    
                    # (7) Stocks Analysis
                    st.divider()
                    st.header(f"Stocks Analysis", anchor="stocks_analysis")
                    st.write(f"Stocks: {symbols}")
                    st.write(f"Start Date: {datasets['stock_prices_stats']['start_date']}")
                    st.write(f"End Date: {datasets['stock_prices_stats']['end_date']}")
                    st.divider()
                    
                    # (8) Stats: Stock Prices
                    st.subheader("Stats: Stock Prices")
                    st.write("This section analyzes the daily \"Adjusted Close\" price of each stock over time")
                    st.plotly_chart(datasets["stock_prices_plot"])
                    st.plotly_chart(datasets["stock_prices_box_plot"])
                    stock_prices_cov_matrix_plot = change_plotly_fig_title(datasets["stock_prices_cov_matrix_plot"], "Stock Prices Correlation Matrix")
                    st.plotly_chart(stock_prices_cov_matrix_plot)
                    st.divider()
                    
                    # (9) Stats: Stock Returns
                    st.subheader("Stats: Stock Returns")
                    st.write("This section analyzes the daily percentage increase/decrease of each stock over time")
                    st.plotly_chart(datasets["stock_returns_plot"])
                    st.plotly_chart(datasets["stock_returns_box_plot"])

                    # (10) Print Portfolio Stats
                    if 'portfolios_stats' in datasets and datasets['portfolios_stats']:
                        st.divider()
                        st.header("Portfolio Optimization Results", anchor="portfolios_optimization_results")
                        st.write(f"Chosen optimization metric: {optimize_for}")

                        with st.expander("What optimization methods are being used? How do they differ?"):
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
                                f"""SLSQP is typically much more effective than Monte Carlo simulations for portfolio optimization due to its 
                                precision in finding optimal solutions under complex constraints. You may notice this in the scatterplot below,
                                where SLSQP has most likely generated a set of portfolio weights that yield a signfiicantly higher {optimize_for}."""
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

                        # (11) Display Best Weights
                        st.plotly_chart(datasets["best_portfolio_weights_plot"])
    
                        # (12) Plot Portfolios
                        st.subheader("Scatterplot: All Portfolios Optimization Results", anchor="portfolios_optimization_results")
                        st.write(
                            f"""The portfolios plot visualizes the risk-return profile of various portfolio configurations. Each point represents a 
                            portfolio, with its position indicating the trade-off between risk (volatility) and expected return. This aids in 
                            visualizing the efficiency frontier and selecting an optimal portfolio."""
                        )
                        st.write(
                            f"NOTE: Pay attention to how the weights of different stocks in a single portfolio affect its return, volatility, and {optimize_for}"
                        )
                        portfolios_plot = change_plotly_fig_title(datasets["portfolios_plot"], "")
                        st.plotly_chart(portfolios_plot)
                        
                        # (13) Display Portfolio Stats by Method
                        st.subheader("Portfolio Stats by Method")
                        methods_count = len(datasets['portfolios_stats'])
                        cols = st.columns(methods_count)
                        for i, (method, df) in enumerate(datasets['portfolios_stats'].items()):
                            with cols[i]:
                                st.write(f"{method.title()}")
                                st.dataframe(df)  # Using st.dataframe to ensure the dataframe is displayed correctly

            else:
                st.error("Please enter tickers and select at least one method.")
        except:
            st.error("One or more tickers invalid. Please try again.")
            
        
if __name__ == "__main__":
    run()
    