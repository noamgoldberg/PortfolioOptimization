from kedro.pipeline import node, Pipeline

from portfolio_optimization.units.visualize import (
    plot_simulation_and_evaluation_all_alphas,
    plot_simulated_portfolio_returns_dist_all_alphas
)
from portfolio_optimization.units.simulate import (
    simulate_portfolio_returns,
    calculate_simulated_portfolio_returns,
    calculate_simulated_portfolio_returns_stats
)
from portfolio_optimization.units.evaluate import calculate_mcVaR_for_each_alpha, calculate_mcCVaR_for_each_alpha


def create_pipeline() -> Pipeline:
    return Pipeline(
        [
            node(
                func=simulate_portfolio_returns,
                inputs={
                    "stocks_data": "stock_prices",
                    "weights_dict": "best_portfolio_weights",
                    "params": "parameters",
                },
                outputs="portfolio_simulations",
                name="simulate_portfolio_returns",
            ),
            node(
                func=calculate_simulated_portfolio_returns,
                inputs={
                    "portfolio_simulations": "portfolio_simulations",
                    "initial_portfolio_value": "params:simulate.initial_portfolio_value",
                },
                outputs="simulated_portfolio_returns",
                name="calculate_simulated_portfolio_returns",
            ),
            node(
                func=calculate_simulated_portfolio_returns_stats,
                inputs={
                    "simulated_portfolio_returns": "simulated_portfolio_returns",
                },
                outputs="simulated_portfolio_returns_stats",
                name="calculate_simulated_portfolio_returns_stats",
            ),
            node(
                func=calculate_mcVaR_for_each_alpha,
                inputs={
                    "portfolio_returns": "simulated_portfolio_returns",
                    "alphas": "params:evaluate.alphas",
                },
                outputs="portfolio_simulations_VaR",
                name="calculate_portfolio_simulations_VaR",
            ),
            node(
                func=calculate_mcCVaR_for_each_alpha,
                inputs={
                    "portfolio_returns": "simulated_portfolio_returns",
                    "alphas": "params:evaluate.alphas",
                    "VaR_series": "portfolio_simulations_VaR",
                },
                outputs="portfolio_simulations_CVaR",
                name="calculate_portfolio_simulations_CVaR",
            ),
            node(
                func=plot_simulation_and_evaluation_all_alphas,
                inputs={
                    "portfolio_sims_df": "portfolio_simulations",
                    "initial_portfolio_value": "params:simulate.initial_portfolio_value",
                    "VaR_series": "portfolio_simulations_VaR",
                    "CVaR_series": "portfolio_simulations_CVaR",
                    "days": "params:simulate.timeframe",
                    "show": "params:visualize.show",
                },
                outputs="simulation_and_evaluation_plots",
                name="plot_simulation_and_evaluation_all_alphas",
            ),
            node(
                func=plot_simulated_portfolio_returns_dist_all_alphas,
                inputs={
                    "returns": "simulated_portfolio_returns",
                    "VaR_series": "portfolio_simulations_VaR",
                    "CVaR_series": "portfolio_simulations_CVaR",
                    "days": "params:simulate.timeframe",
                    "show": "params:visualize.show",
                },
                outputs="simulated_portfolio_returns_dist_plots",
                name="plot_simulated_portfolio_returns_dist_all_alphas",
            ),
        ]
    )
    

