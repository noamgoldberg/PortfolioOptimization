from typing import Dict, Any
import streamlit as st
import pandas as pd

from portfolio_optimization.utils.plotly_utils import change_plotly_fig_title
from portfolio_optimization.utils.formatting_utils import format_currency_str


def display_results(
    *,
    tab: st.tabs,
    params: Dict[str, Any],
    datasets: Dict[str, Any]
) -> None:
    
    with tab:
        _display_titles_and_questions(params=params)
        _display_weights(datasets=datasets, params=params)
        _display_simulation_and_evaluation(datasets=datasets, params=params)
        
def _display_titles_and_questions(
    *,
    params: Dict[str, Any],
) -> None:
    st.header("Monte Carlo Simulation & Evaluation", anchor="portfolio_mc_simulations")
    st.write(
        f"This section visualizes the projected portfolio performances from {params['simulate']['num_sims']} "
        "simulation iterations, highlighting the Value at Risk (VaR) and Conditional Value at Risk (CVaR) for "
        "a user-selected alpha value via a slider."
    )
    with st.expander("What are VaR and CVaR?"):
        st.write(
            "Value at Risk (VaR) measures the maximum potential loss in the value of a portfolio over a "
            "specified time period with a given confidence level, while Conditional Value at Risk (CVaR) "
            "represents the expected loss exceeding the VaR, providing a more comprehensive risk assessment "
            "of extreme losses."
        )
        st.write(
            "For example, let's say a portfolio has a VaR of \$10,000. That means that, given a certain "
            "confidence level, the portfolio will lose more than \$10,000 over the specified period. The CVaR "
            "might be \$15,000, indicating that if the portfolio does lose more than \$10,000, the average loss "
            "would be \$15,000."
        )
    with st.expander("What is alpha? How does it affect VaR and CVaR?"):
        st.write(
            "Alpha indicates the confidence level used in measuring risk and calculating VaR and CVaR. It "
            "represents the probability that the portfolio loss will exceed VaR (confidence level represents "
            "the inverse - the probability that the portfolio loss will NOT exceed VaR). A lower alpha results "
            "in a higher VaR, indicating a more conservative risk estimate, and consequently, a greater expected "
            "loss beyond the VaR threshold, or CVaR."
        )
        st.write(
            "For example, with an alpha of 10% (0.1), one might have a VaR of \$10,000 and CVaR of \$15,000. With "
            "an 5% (0.05), however, the VaR might increase to \$12,000, reflecting a more conservative estimate "
            "of potential loss. Accordingly, the CVaR might increase to \$17,000, capturing a higher average loss "
            "beyond the (now-higher) VaR threshold of \$12,000."
        )


def _display_weights(
    *,
    params: Dict[str, Any],
    datasets: Dict[str, Any]
) -> None:
    st.subheader("Optimized Portfolio Weights", anchor="optimized_portfolio_weights")
    st.write(
        "Sequential Least Squares Programming (via scipy library) was used to optimize for the set of weights "
        "(given the selected set of stocks) that yielded the highest Sharpe Ratio. Below are the optimal weights."
    )
    chosen_stocks = pd.Index(datasets["best_portfolio_weights_plot"]["data"][0]["y"])
    chosen_stocks_colors = pd.Index(datasets["best_portfolio_weights_plot"]["data"][0]["marker"]["color"])
    chosen_stocks_str = ", ".join(["<font style='color: {}'>{}".format(color, stock) for stock, color in zip(chosen_stocks, chosen_stocks_colors)]) + "</font>"
    unchosen_stocks = pd.Index(params["data"]["stocks"]["symbols"]).difference(chosen_stocks)
    st.markdown(
        f"- The following stocks were assigned non-zero portfolio weights: **{chosen_stocks_str}**",
        unsafe_allow_html=True
    )
    st.markdown(
        "- The following stocks were assigned a weight of 0 (or near-zero) due to their negative effect on the "
        f"Sharpe Ratio of the portfolio: :gray[**{', '.join(unchosen_stocks)}**]"
    )
    best_portfolio_weights_plot = datasets["best_portfolio_weights_plot"]
    fig1 = change_plotly_fig_title(best_portfolio_weights_plot, "")
    st.plotly_chart(fig1)
    
def _display_simulation_and_evaluation(
    *,
    params: Dict[str, Any],
    datasets: Dict[str, Any]
) -> None:
    
    # (1) Simulation
    st.subheader("Monte Carlo Simulation")
    st.warning("Note: Simulation results use adjusted close prices and therefore exclude dividends from the total return calculation.")
    alphas = params["evaluate"]["alphas"]
    simulation_and_evaluation_plots_dict = datasets["simulation_and_evaluation_plots"]
    default_alpha = 0.05
    if 'alpha' not in st.session_state:
        st.session_state['alpha'] = min(alphas, key=lambda x: abs(x - default_alpha))  
    st.session_state['alpha'] = st.select_slider(
        'Select an alpha value to set the confidence level for risk assessment (e.g., 5% (0.05) for 95% confidence):',
        options=alphas,
        value=st.session_state['alpha']
    )
    
    # (2) Evaluation

    # ...a. Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    initial_investment = params["simulate"]["initial_investment"]
    expected_return = datasets["simulated_portfolio_returns_stats"]["mean"]
    fig2 = simulation_and_evaluation_plots_dict.get(st.session_state['alpha'])
    VaR = -(initial_investment - fig2.data[-2:][1]["y"][0])
    CVaR = -(initial_investment - fig2.data[-2:][0]["y"][0])
    
    col1.metric("# Simulations", params["simulate"]["num_sims"])
    col2.metric("Investment", f"${initial_investment // 1000}K")
    col3.metric(":green[Expected Return] ", format_currency_str(expected_return, "$", 0), f"{expected_return / initial_investment:.2%}")
    col4.metric(f":{params['visualize']['VaR_color']}[VaR]", format_currency_str(VaR, "$", 0), f"{VaR / initial_investment:.2%}")
    col5.metric(f":{params['visualize']['CVaR_color']}[CVaR]", format_currency_str(CVaR, "$", 0), f"{CVaR / initial_investment:.2%}")
    
    # ...b.  Explanation of Results
    explanation = "- The result of {num_sims} simulations indicate an expected return of {expected_return}\n- With the " + \
        "selected :{alpha_color}[**alpha of {alpha:.1%}**], the simulation shows a :{VaR_color}[**VaR of {VaR}**] and " + \
        "a :{CVaR_color}[**CVaR of \${CVaR}**]. \n- In other words, assuming an initial investment of {investment}, one " + \
        "can be {confidence:.1%} confident that one will not lose more than {VaR}. In the event that this portfolio " + \
        "loss threshold is exceeded (the unlikely {alpha:.1%} of cases), the average expected loss is {CVaR}."
    format_dict = dict(
        num_sims=params["simulate"]["num_sims"],
        expected_return=format_currency_str(expected_return, "$", 0),
        alpha=st.session_state['alpha'],
        confidence=1 - st.session_state['alpha'],
        investment=format_currency_str(VaR, "$", 0, True),
        alpha_color="red",
        VaR=format_currency_str(VaR, "$", 0, True),
        CVaR=format_currency_str(CVaR, "$", 0, True),
        VaR_color=params["visualize"]["VaR_color"],
        CVaR_color=params["visualize"]["CVaR_color"],
    )
    st.markdown(explanation.format(**format_dict))

    # ...c. Plot Simulations
    st.plotly_chart(fig2)
    
    # ...d. Distribution of Simulated Returns
    fig3 = datasets["simulated_portfolio_returns_dist_plots"].get(st.session_state['alpha'])
    st.plotly_chart(fig3)
    
