from kedro.pipeline import node, Pipeline

from portfolio_optimization.units.download import download_stock_prices
# from portfolio_optimization.units.preprocess import preprocess
# from portfolio_optimization.units.optimize_old import optimize_weights, optimize_scipy, optimize_monte_carlo
from portfolio_optimization.units.optimize import optimize_weights
from portfolio_optimization.units.visualize import plot_portfolios
from portfolio_optimization.units.report.report import generate_report


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=download_stock_prices,
                inputs=["parameters"],
                outputs="stock_prices",
                name="download",
            ),
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
        ]
    )


