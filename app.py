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
import yfinance

from portfolio_optimization.consts import CONF_ENV, DATE_FORMAT
from portfolio_optimization.utils.config_utils import write_yaml
from portfolio_optimization.utils.kedro_utils import read_params
from portfolio_optimization.utils.plotly_utils import change_plotly_fig_title


def run():    
    
    st.title("Stocks Portfolio Optimization")

    # (1) Establish (Local) Parameters
    parse_symbols = lambda symbols_input: list(set([s.strip().upper() for s in symbols_input.split(',') if s.strip()]))
    def check_input():
        NUM_SYMBOLS_LIMIT = 50
        symbols_input = parse_symbols(st.session_state.symbols)
        infos = {s: yfinance.ticker.Ticker(s).info for s in symbols_input}
        invalid_symbols = [s for s, info in infos.items() if len(info) < 10]
        if len(invalid_symbols) > 0:
            st.error(f"Input invalid. The following tickers could not be found: {', '.join(invalid_symbols)}")
        elif len(symbols_input) > NUM_SYMBOLS_LIMIT:
            st.error(f'Input invalid, too many tickers. Please enter {NUM_SYMBOLS_LIMIT} stock tickers or less.')
    symbols = st.text_input(
        "Enter stock tickers, separated by commas (e.g., AAPL, GOOG, MSFT, ...)",
        "AAPL, GOOG, MSFT, BABA, META, V, C, XOM, OXY, SHEL, JPM, BAC, WFC, CVX, DE, CI",
        key="symbols",
        on_change=check_input,
    )
    start_date = st.date_input(
        "Enter a 'Start Date' from which stock prices will be collected and analyzed",
        value=pd.to_datetime("2020-01-01"),
        min_value=pd.to_datetime("2010-01-01", format=DATE_FORMAT),
        max_value=datetime.today() - timedelta(weeks=8),
    )
    end_date = datetime.today().strftime(DATE_FORMAT)
    optimize_for = st.selectbox("Select a metric to optimize for", options=["Sharpe Ratio"], index=0)
    
    # (2) Collapsable Q&As
    with st.expander("What is portfolio optimization?"):
        st.write(
            "Portfolio optimization is a mathematical method used to select the best stocks and their allocations "
            "to maximize returns for a given level of risk, or alternatively, to minimize risk for a given level "
            "of expected return."
        )
    with st.expander("What is the Sharpe Ratio? Why is it useful?"):
        st.write(
            "The Sharpe Ratio measures risk-adjusted returns by comparing the excess return of an investment to "
            "its volatility."
        )
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
                write_yaml({}, f"{PROJECT_PATH}/{CONF_ENV}/local/parameters.yml")
                params = read_params(conf=CONF_ENV)
                params["data"]["stocks"]["symbols"] = parse_symbols(symbols)
                params["data"]["stocks"]["start_date"] = start_date.strftime(format=DATE_FORMAT)
                params["visualize"]["show"] = False
                write_yaml(params, f"{PROJECT_PATH}/{CONF_ENV}/local/parameters.yml")
                
                # (5) Instantiate Kedro Session
                configure_project("portfolio_optimization")
                with KedroSession.create(project_path=PROJECT_PATH, conf_source="conf") as session:
                    
                    # (6) Run Pipeline
                    datasets = session.run(pipeline_name="portfolio_optimization")
                    
                    # (7) Stocks Statistics
                    st.divider()
                    st.header(f"Stocks Statistics", anchor="stocks_statistics")
                    st.write(f"Stocks: {params['data']['stocks']['symbols']}")
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
                        st.write(
                            "How do these stocks move with one another? This heatmap shows how stongly each "
                            "stock is related each of the other stocks. The lighter the color, the more the "
                            "two stocks are correlated!"
                        )
                    elif selected_stocks_data_type == stocks_data_type_options[1]:
                        st.subheader("Stats: Daily Stock Returns (%)")
                        st.write("This section analyzes the daily percentage increase/decrease of each stock over time")
                        st.plotly_chart(datasets["stock_returns_plot"])
                        st.plotly_chart(datasets["stock_returns_box_plot"])

                    # (10) Print Portfolio Stats
                    if 'portfolios_stats' in datasets and datasets['portfolios_stats']:
                        st.divider()
                        st.header("Portfolio Optimization Results", anchor="portfolios_optimization_results")
                        
                        # (11) Display Optimization Info
                        st.subheader("Optimization Information", anchor="optimization_information")
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
                                f"""SLSQP excels in cases like these where the task is to finding an optimal solutions under well-defined
                                constraints. For example, (a) all weights must be between 0 and 1 and (b) all weights must add up to 1.
                                Unlike Monte Carlo simulations, which relies mainly on randomness, SLQSP uses math to compute the set of
                                optimal weights, rather than attempting to generate among a sea of random iterations.
                                You may notice this in the scatterplot below, where SLSQP has most likely generated a set of portfolio 
                                weights that yield a signfiicantly higher {optimize_for}."""
                            )


                        # (12) Display Best Weights
                        st.subheader("Optimal Portfolio: Weights", anchor="optimal_portfolio")
                        initial_investment = datasets["best_portfolio_forecast_plot"]["data"][2]["y"][0]
                        best_portfolio_return = datasets['best_portfolio']['Return']
                        first_year_return = initial_investment * (1 + best_portfolio_return)
                        fifth_year_return = initial_investment * ((1 + best_portfolio_return) ** 5)
                        st.plotly_chart(datasets["best_portfolio_weights_plot"])
                        st.plotly_chart(datasets["best_portfolio_forecast_plot"])
                        st.write(
                            "This chart presents a forecast for your portfolio, which was optimized using historical data to achieve the highest "
                            f"possible {optimize_for}."
                        )
                        st.write(f"This portfolio has an expected annual return of {best_portfolio_return:.1%}")
                        st.write(f"If you invested ${int(initial_investment):,.0f}, you would be expected to make:")
                        st.write(f"- ${int(first_year_return):,.0f} over your first year")
                        st.write(f"- ${int(fifth_year_return):,.0f} over your first 5 years")
                        st.write(
                            "This metric is based on the assumption that investment returns follow a normal distribution, implying a predictable "
                            "pattern of returns. While useful for planning, it's important to remember that actual market behavior can be unpredictable."
                        )
                        st.write("Understanding Your Forecast:")
                        st.write(
                            f"- Solid Line: Represents the expected growth of your investment, based on the portfolio's average return of {datasets['best_portfolio']['Return']:.1%} and a "
                            f"spread of {datasets['best_portfolio']['Volatility']:.1%} from {start_date} to {end_date}."
                        )
                        st.write("- Darker Shaded Area: 68% confidence interval. A broader set of outcomes (1 standard deviation), showing the range of valuations where your investment will land 68% of the time, statistically speaking (assuming a normal distribution).")
                        st.write("- Lighter Shaded Area: 95% confidence interval. An even broader (and therefore more confident) set of outcomes (2 standard deviations), showing the range of valuations where your investment will land 95% of the time, statistically speaking (assuming a normal distribution).")
                        st.write(
                            "This visualization is designed to help you grasp the potential range of returns for your optimized portfolio over the "
                            "coming years, giving you insight into both likely and less likely financial outcomes."
                        )

                        # (13) Plot Portfolios
                        st.subheader("All Portfolios", anchor="all_portfolios")
                        portfolios_plot = change_plotly_fig_title(datasets["portfolios_plot"], "")
                        st.plotly_chart(portfolios_plot)
                        st.write(
                            """This scatterplot visualizes the risk-return profile of various portfolio configurations generated during optimization. 
                            Each point represents a portfolio, with its position indicating the trade-off between risk (volatility) and expected return.
                            In addition to visualizing different optimization methods, this plot efficiency frontier - the set of optimal portfolios 
                            that offer the highest expected return for a defined level of risk or the lowest risk for a given level of expected return."""
                        )
                        st.write(
                            f"Pay attention to how the weights of different stocks in a the portfolios' returns, volatilities, and {optimize_for}s"
                        )
                        
                        # (14) Display Portfolio Stats by Method
                        st.subheader("Portfolio Stats by Method")
                        methods_count = len(datasets['portfolios_stats'])
                        stats_by_method_cols = st.columns(methods_count)
                        for i, (method, df) in enumerate(datasets['portfolios_stats'].items()):
                            with stats_by_method_cols[i]:
                                st.write(f"{method.title()}")
                                st.dataframe(df)  # Using st.dataframe to ensure the dataframe is displayed correctly
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
            else:
                st.error("Please enter tickers and select at least one method.")
        except:
            st.error("Input invalid. Please try again.")
            
        
if __name__ == "__main__":
    run()
    