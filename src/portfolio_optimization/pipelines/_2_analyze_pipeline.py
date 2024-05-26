from kedro.pipeline import node, Pipeline

from portfolio_optimization.units.visualize import (
    plot_stock_prices,
    plot_stock_returns,
    plot_matrix_heatmap,
    plot_stock_prices_box_plot_dists,
    plot_stock_returns_box_plot_dists,
)
from portfolio_optimization.units.report.stock_prices_stats import get_stock_prices_stats, get_stock_prices_corr_matrix

def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
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
                func=get_stock_prices_corr_matrix,
                inputs={
                    "stocks_data": "stock_prices",
                    "agg": "params:optimize.optimize_on",
                },
                outputs="stock_prices_corr_matrix",
                name="get_stock_prices_corr_matrix",
            ),
            node(
                func=lambda **kwargs: plot_matrix_heatmap(
                    title="Stock Prices Correlation Matrix",
                    **kwargs
                ),
                inputs={
                    "matrix": "stock_prices_corr_matrix",
                    "show": "params:visualize.show",
                },
                outputs="stock_prices_corr_matrix_plot",
                name="plot_stock_prices_corr_matrix",
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
        ]
    )
    

