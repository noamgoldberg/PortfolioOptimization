from typing import Dict, Any
import streamlit as st
import pandas as pd

from portfolio_optimization.utils.plotly_utils import change_plotly_fig_title
 

def display_optimize(
    *,
    tab: st.tabs,
    params: Dict[str, Any],
    datasets: Dict[str, Any]
):
    
    with tab:
        
        # (1) Optimized Portfolios: Return vs. Volatility vs. Sharpe Ratio
        
        # ...a. Display Plots
        st.header("Optimization", anchor="optimization")
        st.subheader("Optimized Portfolios: Return vs. Volatility vs. Sharpe Ratio", anchor="all_portfolios_scatterplot")
        portfolios_plot = change_plotly_fig_title(datasets["portfolios_plot"], "")
        st.plotly_chart(portfolios_plot)
        
        # ...b. Display Description
        st.write(
            """This scatterplot visualizes the risk-return profile of various portfolio configurations generated during optimization. 
            Each point represents a portfolio, with its position indicating the trade-off between risk (volatility) and expected return."""
        )
        st.write(
            f"Pay attention to how the weights of different stocks in a portfolio affect its return, volatility, and {params['optimize']['optimize_for']}"
        )
    
def display_simulation_and_evaluation(
    *,
    tab: st.tabs,
    params: Dict[str, Any],
    datasets: Dict[str, Any]
) -> None:
    
    with tab:
        
        # (0) Titles & Subtitles, and Q&A Descriptions
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

        # (1) Portfolio Weights
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

        # (2) Monte Carlo Simulation
        
        # ...a. Subsection Subheader
        st.subheader("Monte Carlo Simulation")
        
        # ...b. Extract each alpha value and its corresponding plot
        alphas = params["evaluate"]["alphas"]
        simulation_and_evaluation_plots_dict = datasets["simulation_and_evaluation_plots"]
        
        # ...c. Initialize session state for the alpha value (value closest to 'default' value)
        default_alpha = 0.05
        if 'alpha' not in st.session_state:
            st.session_state['alpha'] = min(alphas, key=lambda x: abs(x - default_alpha))  
            
        # ...d. Display slider to adjust the alpha value & corresponding figure
        st.session_state['alpha'] = st.select_slider(
            'Select an alpha value to set the confidence level for risk assessment (e.g., 5% (0.05) for 95% confidence):',
            options=alphas,
            value=st.session_state['alpha']
        )
        
        # (3) Explain Results & Diplay Plot
        explanation = "- With the selected :blue[**alpha of {alpha:.1%}**], the simulation shows a :orange[**VaR of \${VaR:,.0f}**] and a :red[**CVaR of " + \
            "\${CVaR:,.0f}**]. \n- In other words, assuming an :violet[**initial investment of \${investment:,.0f}**], one can be " + \
            ":blue[**{confidence:.1%}**] confident that one will not lose more than :orange[**\${VaR:,.0f}**]. In the event that this portfolio " + \
            "loss threshold is exceeded (the unlikely :blue[**{alpha:.1%}**] of cases), the average expected loss is :red[**\${CVaR:,.0f}**]."
        initial_portfolio_value = params["simulate"]["initial_portfolio_value"]
        fig2 = change_plotly_fig_title(simulation_and_evaluation_plots_dict.get(st.session_state['alpha']), "")
        format_dict = dict(
            alpha=st.session_state['alpha'],
            confidence=1 - st.session_state['alpha'],
            investment=initial_portfolio_value,
            VaR=initial_portfolio_value - fig2.data[-2:][1]["y"][0],
            CVaR=initial_portfolio_value - fig2.data[-2:][0]["y"][0],
        )
        st.markdown(explanation.format(**format_dict))
        st.plotly_chart(fig2)