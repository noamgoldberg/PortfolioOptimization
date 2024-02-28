from kedro.pipeline import node, Pipeline

from portfolio_optimization.units.download import download_stock_prices
# from portfolio_optimization.units.preprocess import preprocess
# from portfolio_optimization.units.optimize_old import optimize_weights, optimize_scipy, optimize_monte_carlo
from portfolio_optimization.units.optimize import optimize_weights
from portfolio_optimization.units.visualize import plot_stock_prices, plot_portfolios
from portfolio_optimization.units.report.stock_prices_stats import get_stock_prices_stats
from portfolio_optimization.units.report.portfolios_stats import get_portfolios_stats, get_best_portfolio_weights
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
                func=get_stock_prices_stats,
                inputs={
                    "stocks_data": "stock_prices",
                    "params": "parameters",
                },
                outputs="stock_prices_stats",
                name="get_stock_prices_stats",
            ),
            node(
                func=plot_stock_prices,
                inputs={
                    "stocks_data": "stock_prices",
                    "agg": "params:optimize.optimize_on",
                },
                outputs="stock_prices_plot",
                name="plot_stock_prices",
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
                func=get_portfolios_stats,
                inputs={
                    "portfolios": "portfolios",
                },
                outputs="portfolios_stats",
                name="get_portfolios_stats",
            ),
            node(
                func=get_best_portfolio_weights,
                inputs={
                    "portfolios": "portfolios",
                },
                outputs="best_portfolio_weights",
                name="get_best_portfolio_weights",
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


