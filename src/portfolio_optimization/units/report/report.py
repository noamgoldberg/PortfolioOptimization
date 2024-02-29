from typing import Optional, Union
from pathlib import PosixPath, Path
import pandas as pd
import os

from .section import Section
from .analysis_report import AnalysisReport

from portfolio_optimization.utils.kedro_utils import read_catalog


def get_report_relpath(filepath: Union[PosixPath, str]):
    return os.path.relpath(filepath, start="data/08_reporting")

# report = AnalysisReport("My Analysis Report")
def generate_report(
    *,
    params: dict,
    portfolio_weights_scipy: Optional[pd.DataFrame] = None,
    portfolio_weights_monte_carlo: Optional[pd.DataFrame] = None,
    portfolios_scatterplot: Optional[pd.DataFrame] = None,
    **kwargs
):
        
    # Read Catalog
    catalog = read_catalog()
    
    # Initialize Report
    report = AnalysisReport(title="Analysis Report")
    
    # Section 1: SciPy Weights
    if portfolio_weights_scipy is not None:
        section_1_title = f"Weights: Scipy (via {params['optimize']['scipy_solver']} solver)"
        section1 = Section(section_1_title, dropdown=True)
        section1.add_table(portfolio_weights_scipy.reset_index())
        report.add_section(section1)
    
    # Section 2: Monte Carlo Weights
    if portfolio_weights_monte_carlo is not None:
        section_2_title = f"Weights: Monte Carlo"
        section2 = Section(section_2_title, dropdown=True)
        section2.add_table(portfolio_weights_monte_carlo.reset_index())
        report.add_section(section2)

    # Section 3: Portfolios Plot
    if portfolios_scatterplot is not None:
        section3 = Section("Portfolios Scatterplot", dropdown=True)
        image_path = get_report_relpath(catalog["monte_carlo_iterations_plot"]["filepath"])
        image_path = f"{image_path.split('.')[0]}.png"
        section3.add_image(image_path, alt_text="Portfolios Scatterplot")
        report.add_section(section3)

    return report.generate_report()