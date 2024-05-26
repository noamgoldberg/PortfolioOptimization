from kedro.pipeline import node, Pipeline

from portfolio_optimization.units.download import download_stock_prices


def create_pipeline() -> Pipeline:
    return Pipeline(
        [
            node(
                func=download_stock_prices,
                inputs=["parameters"],
                outputs="stock_prices",
                name="download",
            ),
        ]
    )
    

