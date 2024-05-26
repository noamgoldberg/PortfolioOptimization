"""Project pipelines."""
from typing import Dict

from kedro.pipeline import Pipeline
from portfolio_optimization.pipelines import _1_download_pipeline as p1
from portfolio_optimization.pipelines import _2_analyze_pipeline as p2
from portfolio_optimization.pipelines import _3_optimize_pipeline as p3
from portfolio_optimization.pipelines import _4_simulate_and_evaluate_pipeline as p4
from portfolio_optimization.pipelines import portfolio_optimization_pipeline as pop

def register_pipelines() -> Dict[str, Pipeline]:
    portfolio_optimization_pipeline = pop.create_pipeline()
    _1_ = p1.create_pipeline()
    _2_ = p2.create_pipeline()
    _3_ = p3.create_pipeline()
    _4_ = p4.create_pipeline()
    pipelines = {
        "_1_": _1_,
        "_2_": _2_,
        "_3_": _3_,
        "_4_": _4_,
        "portfolio_optimization": portfolio_optimization_pipeline,
        "__default__": portfolio_optimization_pipeline,
    }
    return pipelines
