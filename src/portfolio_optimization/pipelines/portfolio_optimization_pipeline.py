from kedro.pipeline import Pipeline

from portfolio_optimization.pipelines import _1_download_pipeline as p1
from portfolio_optimization.pipelines import _2_analyze_pipeline as p2
from portfolio_optimization.pipelines import _3_optimize_pipeline as p3
from portfolio_optimization.pipelines import _4_simulate_and_evaluate_pipeline as p4


def create_pipeline(**kwargs) -> Pipeline:
    _1_ = p1.create_pipeline()
    _2_ = p2.create_pipeline()
    _3_ = p3.create_pipeline()
    _4_ = p4.create_pipeline()
    portfolio_optimization_pipeline = _1_ + _2_ + _3_ + _4_
    return portfolio_optimization_pipeline
    