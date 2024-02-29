from kedro.pipeline import node, Pipeline

from portfolio_optimization.units.download import download_stock_prices
# from portfolio_optimization.units.preprocess import preprocess
# from portfolio_optimization.units.optimize_old import optimize_weights, optimize_scipy, optimize_monte_carlo
from portfolio_optimization.units.optimize import optimize_weights
from portfolio_optimization.units.visualize import (
    plot_stock_prices,
    plot_stock_returns,
    plot_portfolios,
    plot_matrix_heatmap,
    plot_best_portfolio_weights,
    plot_stock_prices_box_plot_dists,
    plot_stock_returns_box_plot_dists,
)
from portfolio_optimization.units.report.stock_prices_stats import get_stock_prices_stats, get_stock_stock_prices_corr_matrix
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
                    "agg": "params:optimize.optimize_on",
                },
                outputs="stock_prices_stats",
                name="get_stock_prices_stats",
            ),
            node(
                func=get_stock_stock_prices_corr_matrix,
                inputs={
                    "stocks_data": "stock_prices",
                    "agg": "params:optimize.optimize_on",
                },
                outputs="stock_prices_corr_matrix",
                name="get_stock_prices_corr_matrix",
            ),
            node(
                func=plot_matrix_heatmap,
                inputs={
                    "matrix": "stock_prices_corr_matrix",
                    "show": "params:visualize.show",
                },
                outputs="stock_prices_cov_matrix_plot",
                name="plot_stock_prices_cov_matrix",
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
                func=plot_stock_returns,
                inputs={
                    "stocks_data": "stock_prices",
                    "agg": "params:optimize.optimize_on",
                },
                outputs="stock_returns_plot",
                name="plot_stock_returns",
            ),    
            node(
                func=plot_stock_prices_box_plot_dists,
                inputs={
                    "stocks_data": "stock_prices",
                    "agg": "params:optimize.optimize_on",
                    "show": "params:visualize.show",
                },
                outputs="stock_prices_box_plot",
                name="plot_stock_prices_box_plot",
            ),  
            node(
                func=plot_stock_returns_box_plot_dists,
                inputs={
                    "stocks_data": "stock_prices",
                    "agg": "params:optimize.optimize_on",
                    "show": "params:visualize.show",
                },
                outputs="stock_returns_box_plot",
                name="plot_stock_returns_box_plot",
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
                func=plot_best_portfolio_weights,
                inputs={
                    "best_portfolio_weights": "best_portfolio_weights",
                    "show": "params:visualize.show",
                },
                outputs="best_portfolio_weights_plot",
                name="plot_best_portfolio_weights",
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


