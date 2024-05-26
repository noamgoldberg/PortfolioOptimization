from kedro.pipeline import node, Pipeline

from portfolio_optimization.units.optimize import optimize_weights, extract_best_portfolio_weights
from portfolio_optimization.units.visualize import plot_portfolios, plot_best_portfolio_weights


def create_pipeline() -> Pipeline:
    return Pipeline(
        [
            node(
                func=optimize_weights,
                inputs={
                    "stocks_data": "stock_prices",
                    "params": "parameters",
                },
                outputs="portfolios",
                name="optimize",
            ),
            node(
                func=plot_portfolios,
                inputs={
                    "portfolios": "portfolios",
                    "sample": "params:visualize.plotly_sample",
                    "show": "params:visualize.show",
                },
                outputs="portfolios_plot",
                name="plot_portfolios",
            ),
            node(
                func=extract_best_portfolio_weights,
                inputs={
                    "portfolios": "portfolios",
                    "min_weight": "params:optimize.min_weight",
                },
                outputs="best_portfolio_weights",
                name="extract_best_portfolio_weights",
            ),
            node(
                func=plot_best_portfolio_weights,
                inputs={
                    "weights_dict": "best_portfolio_weights",
                    "show": "params:visualize.show",
                },
                outputs="best_portfolio_weights_plot",
                name="plot_best_portfolio_weights",
            ),

        ]
    )
    

