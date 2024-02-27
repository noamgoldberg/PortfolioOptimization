"""Project pipelines."""
from typing import Dict

# from kedro.framework.project import find_pipelines
from kedro.pipeline import Pipeline
from portfolio_optimization.pipelines import portfolio_optimization_pipeline as pop

def register_pipelines() -> Dict[str, Pipeline]:
    # pipelines = find_pipelines()
    # pipelines["__default__"] = sum(pipelines.values())
    portfolio_optimization_pipeline = pop.create_pipeline()
    pipelines = {
        "portfolio_optimization": portfolio_optimization_pipeline,
        "__default__": portfolio_optimization_pipeline,
    }
    return pipelines

from kedro.extras.datasets.plotly.plotly_dataset import PlotlyDataSet