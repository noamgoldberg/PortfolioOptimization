import streamlit as st

def display_q_and_a():
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
            "external factors that could indicate different kinds of risk\n- Sensitive to the risk "
            "free rate; ratio can fluctuate can fluctuate due to factors unrelated to the investment's "
            "performance, potentially misleading in different interest rate environments."
        )
    with st.expander("What is a Monte Carlo simulation?"):
        st.write(
            "A Monte Carlo Simulation is a statistical technique that utilizes random sampling and repeated "
            "simulations to model and analyze the behavior and performance of complex systems or processes "
            "over time."
        )