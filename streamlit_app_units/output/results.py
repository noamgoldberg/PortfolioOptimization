from typing import Dict, Any
import streamlit as st

from portfolio_optimization.utils.plotly_utils import change_plotly_fig_title


def display_results(
    *,
    params: Dict[str, Any],
    datasets: Dict[str, Any]
):
    # (10) Display Results
    if 'portfolios_stats' in datasets and datasets['portfolios_stats']:
        st.divider()
        st.header("Portfolio Optimization Results", anchor="portfolios_optimization_results")
        
        # (11) Display Optimization Info
        st.subheader("Optimization Information", anchor="optimization_information")
        st.write(f"Chosen optimization metric: {params['optimize']['optimize_for']}")
        
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
                weights that yield a signfiicantly higher {params['optimize']['optimize_for']}."""
            )

        # (12) Display Best Weights
        st.subheader("Optimal Portfolio: Weights", anchor="optimal_portfolio_weights")
        initial_investment = datasets["best_portfolio_forecast_plot"]["data"][2]["y"][0]
        best_portfolio_return = datasets['best_portfolio']['Return']
        first_year_return = initial_investment * (1 + best_portfolio_return)
        fifth_year_return = initial_investment * ((1 + best_portfolio_return) ** 5)
        st.plotly_chart(datasets["best_portfolio_weights_plot"])
        st.subheader("Optimal Portfolio: Return Forecast", anchor="optimal_portfolio_return_plot")
        st.plotly_chart(datasets["best_portfolio_forecast_plot"])
        st.write(
            "This chart presents a forecast for your portfolio, which was optimized using historical data to achieve the highest "
            f"possible {params['optimize']['optimize_for']}."
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
            f"spread of {datasets['best_portfolio']['Volatility']:.1%} from {params['data']['stocks']['start_date']} to {params['data']['stocks']['end_date']}."
        )
        st.write("- Darker Shaded Area: 68% confidence interval. A broader set of outcomes (1 standard deviation), showing the range of valuations where your investment will land 68% of the time, statistically speaking (assuming a normal distribution).")
        st.write("- Lighter Shaded Area: 95% confidence interval. An even broader (and therefore more confident) set of outcomes (2 standard deviations), showing the range of valuations where your investment will land 95% of the time, statistically speaking (assuming a normal distribution).")
        st.write(
            "This visualization is designed to help you grasp the potential range of returns for your optimized portfolio over the "
            "coming years, giving you insight into both likely and less likely financial outcomes."
        )

        # (13) Plot Portfolios
        st.subheader("All Portfolios: Return vs. Volatility vs. Sharpe Ratio", anchor="all_portfolios_scatterplot")
        portfolios_plot = change_plotly_fig_title(datasets["portfolios_plot"], "")
        st.plotly_chart(portfolios_plot)
        st.write(
            """This scatterplot visualizes the risk-return profile of various portfolio configurations generated during optimization. 
            Each point represents a portfolio, with its position indicating the trade-off between risk (volatility) and expected return.
            In addition to visualizing different optimization methods, this plot visualizes the efficiency frontier - the set of optimal
            portfolios that offer the highest expected return for a defined level of risk or the lowest risk for a given level of expected return."""
        )
        st.write(
            f"Pay attention to how the weights of different stocks in a the portfolios' returns, volatilities, and {params['optimize']['optimize_for']}s"
        )
        
        # (14) Display Portfolio Stats by Method
        st.subheader("All Portfolios: Stats by Method", anchor="all_portfolios_stats_by_method")
        methods_count = len(datasets['portfolios_stats'])
        stats_by_method_cols = st.columns(methods_count)
        for i, (method, df) in enumerate(datasets['portfolios_stats'].items()):
            with stats_by_method_cols[i]:
                st.write(f"{method.title()}")
                st.dataframe(df)  # Using st.dataframe to ensure the dataframe is displayed correctly
