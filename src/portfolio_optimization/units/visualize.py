from typing import Optional, Union, Iterable, Dict, Callable, Tuple, Any
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff

from portfolio_optimization.units.report.portfolios_stats import get_best_portfolio
from portfolio_optimization.utils.data_utils import concat_partitions, filter_stocks_df_for_agg, get_stock_returns
from portfolio_optimization.utils.formatting_utils import str2list

import numpy as np
import plotly.graph_objects as go


def plot_best_portfolio_forecast(
    portfolios: pd.DataFrame,
    initial_investment: Union[int, float] = 10000,
    n_years: int = 5,
    metric: str = "Sharpe Ratio",
    show: bool = True,
) -> go.Figure:
    best_portfolio = get_best_portfolio(portfolios)
    return plot_portfolio_forecast(
        initial_investment=initial_investment,
        annual_return=best_portfolio["Return"],
        std_dev=best_portfolio["Volatility"],
        n_years=n_years,
        metrics={metric.title(): f"{best_portfolio[metric]:.1f}"},
        show=show,
    )

def plot_portfolio_forecast(
    initial_investment: Union[int, float],
    annual_return: float,
    std_dev: float,
    n_years: int = 5,
    metrics: Optional[Dict[str, Union[float, int]]] = None,
    show: bool = True,
) -> go.Figure:
    """
    Plots the portfolio forecast over n years using the expected annual return and standard deviation.

    Parameters:
    - initial_investment: The initial amount invested.
    - annual_return: The expected annual return rate (as a decimal).
    - std_dev: The standard deviation of the portfolio's return (as a decimal).
    - n_years: The number of years over which the forecast is made.
    - metrics: Values associated with the portfolio (e.g. Sharpe Ratio), dict
    - show: Whether or not to show the plot (fig.show())
    """
    # Generate years and data
    years = np.arange(0, n_years + 1)
    data = {"projected": [initial_investment * ((1 + annual_return) ** y) for y in years]}
    num_stds_range = [1, 2]

    # Initialize the figure
    fig = go.Figure()

    # Loop through each standard deviation range and create a single trace for each
    for num_stds, pct, opacity in list(zip(num_stds_range, [68, 95], [0.45, 0.15]))[::-1]:
        # Calculate the upper and lower bounds for the current standard deviation
        upper_bound = [initial_investment * ((1 + annual_return + num_stds * std_dev) ** y) for y in years]
        lower_bound = [initial_investment * ((1 + annual_return - num_stds * std_dev) ** y) for y in years]
        
        # Combine upper and lower bounds into a single trace
        combined_y = upper_bound + lower_bound[::-1]  # Upper bound followed by lower bound reversed
        combined_x = list(years) + list(years[::-1])  # Years for upper bound followed by years reversed for lower bound
        
        # Add combined trace to the figure
        fig.add_trace(go.Scatter(
            x=combined_x,
            y=combined_y,
            fill='toself',
            fillcolor="green",
            opacity=opacity,
            line=dict(width=0),  # No line around the filled area
            name=f'{pct}% Confidence Interval'
        ))
        
    # Add projected portfolio value trace
    fig.add_trace(go.Scatter(x=years, y=data["projected"], mode='lines', name='Projected Portfolio Value', line_color="yellow"))

    # Update layout with title and axis labels
    title = '<b>Portfolio Forecast with Confidence Intervals</b>'
    if metrics:
        metrics_str = ', '.join([f"{metric} = {value}" for metric, value in metrics.items()])
        title += f"<br><i>{metrics_str}</i>"
    fig.update_layout(title=title, xaxis_title='Years', yaxis_title='Portfolio Value', showlegend=True)

    # Show the figure if requested
    if show:
        fig.show()
    
    return fig


def plot_stock_prices_box_plot_dists(
    stocks_data: pd.DataFrame,
    agg: str = "Adj Close",
    show: bool = True
):
    stocks_data = filter_stocks_df_for_agg(concat_partitions(stocks_data), agg)
    return plot_grouped_boxplot(
        stocks_data,
        columns=stocks_data.columns,
        title="Stock Prices Distribution",
        xaxis_title="Stock",
        yaxis_title="Price",
        show=show
    )

def plot_stock_returns_box_plot_dists(
    stocks_data: pd.DataFrame,
    agg: str = "Adj Close",
    show: bool = True
):
    stock_returns = get_stock_returns(stocks_data, agg)
    return plot_grouped_boxplot(
        stock_returns,
        columns=stock_returns.columns,
        title="Stock Returns Distribution",
        xaxis_title="Stock",
        yaxis_title="Return (%)",
        show=show
    )

def plot_grouped_boxplot(
    df: pd.DataFrame,
    columns: Optional[Union[str, Iterable[str]]] = None,
    title: str = "Grouped Box Plot",
    xaxis_title: str = "Columns",
    yaxis_title: str = "Values",
    show: bool = True
):
    fig = go.Figure()
    columns = df.columns if columns is None else str2list(columns)
    for column in columns:
        fig.add_trace(go.Box(y=df[column], name=column))
    fig.update_layout(title=title, xaxis_title=xaxis_title, yaxis_title=yaxis_title, legend_title=xaxis_title)
    if show:
        fig.show()
    return fig

def get_best_portfolio_and_plot_weights(
    portfolios: pd.DataFrame,
    show: bool = True
) -> Tuple[Dict[str, Any], go.Figure]:
    best_portfolio = get_best_portfolio(portfolios)
    best_portfolio_weights_plot = plot_best_portfolio_weights(
        best_portfolio["Weights"],
        show=show
    )
    return best_portfolio, best_portfolio_weights_plot

def plot_bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str = "Bar Chart",
    orientation: str = 'v',
    show: bool = True
) -> go.Figure:
    # Extend the color palette by concatenating multiple qualitative color palettes
    base_colors = px.colors.qualitative.Plotly  # Default Plotly qualitative colors
    extended_colors = base_colors + px.colors.qualitative.Alphabet + px.colors.qualitative.Light24
    # Ensure the color list is long enough for 50+ categories, repeat the color list if necessary
    colors = (extended_colors * ((len(df) // len(extended_colors)) + 1))[:len(df)]
    
    if orientation == 'v':  # Vertical bars
        fig = go.Figure(data=[go.Bar(
            x=df[x],
            y=df[y],
            marker_color=colors,  # Apply extended color sequence
            orientation=orientation
        )])
    elif orientation == 'h':  # Horizontal bars
        fig = go.Figure(data=[go.Bar(
            x=df[y],
            y=df[x],
            marker_color=colors,  # Apply extended color sequence
            orientation=orientation
        )])
    else:
        raise ValueError("Orientation must be 'v' for vertical or 'h' for horizontal.")
    
    # Update layout with titles
    fig.update_layout(title=title, xaxis_title=x if orientation == 'v' else y, yaxis_title=y if orientation == 'v' else x)
    
    if show:
        fig.show()
    return fig

def plot_matrix_heatmap(matrix: pd.DataFrame, title: Optional[str] = None, show: bool = True):
    fig = go.Figure(data=go.Heatmap(
        z=matrix.values,
        x=matrix.columns,
        y=matrix.index,
        colorscale='RdBu',
        colorbar=dict(title="Scale")
    ))
    fig.update_layout(title=f"{title} Heatmap" if title else "", xaxis_title="Variables", yaxis_title="Variables")
    if show:
       fig.show()
    return fig

def plot_stock_returns(
    stocks_data: Dict[str, Union[Callable, pd.DataFrame]],
    agg: str = "Adj Close",
) -> go.Figure:
    fig = go.Figure()
    returns = get_stock_returns(stocks_data, agg)
    for ticker in returns.columns:
        fig.add_trace(go.Scatter(
            x=returns.index,
            y=returns[ticker], 
            mode='lines', name=ticker
        ))
    fig.update_layout(
        title="Stock Returns Over Time",
        xaxis_title="Date",
        yaxis_title="Stock Return",
        xaxis=dict(rangeslider=dict(visible=True)),
    )
    return fig

def plot_stock_prices(
    stocks_data: Dict[str, Union[Callable, pd.DataFrame]],
    agg: str = "Adj Close",
) -> go.Figure:
    fig = go.Figure()
    stocks_data = filter_stocks_df_for_agg(concat_partitions(stocks_data), agg)
    for ticker in stocks_data.columns:
        fig.add_trace(go.Scatter(
            x=stocks_data.index,
            y=stocks_data[ticker], 
            mode='lines', name=ticker
        ))
    fig.update_layout(
        title="Stock Prices Over Time",
        xaxis_title="Date",
        yaxis_title="Stock Price",
        xaxis=dict(rangeslider=dict(visible=True)),
    )
    return fig

def plot_portfolios(
    portfolios: pd.DataFrame,
    sample: int = 50000,
    show: bool = False
) -> go.Figure:
    fig = go.Figure()

    # Define a color palette
    color_palette = ['blue', 'green', 'red', 'purple', 'orange', 'yellow', 'pink', 'cyan', 'magenta', 'grey']
    
    # Group portfolios by solver and find the best one in each group
    portfolios_by_solver = {}
    for index, row in portfolios.iterrows():
        solver = row['Solver']
        if solver not in portfolios_by_solver:
            portfolios_by_solver[solver] = []
        portfolios_by_solver[solver].append(row)

    best_portfolios = []
    solver_colors = {solver: color_palette[i % len(color_palette)] for i, solver in enumerate(portfolios_by_solver.keys())}

    for solver, portfolios in portfolios_by_solver.items():
        # Convert list of portfolios to DataFrame for easier manipulation
        portfolios_df = pd.DataFrame(portfolios)
        best_portfolio = portfolios_df.loc[portfolios_df['Sharpe Ratio'].idxmax()]
        best_portfolios.append(best_portfolio)

        # Sample if necessary
        if len(portfolios) > sample:
            sampled_portfolios = portfolios_df.sample(n=sample-1, random_state=42)  # Reserve one spot for the best portfolio
            sampled_portfolios = pd.concat([sampled_portfolios, best_portfolio.to_frame().T], ignore_index=True)
        else:
            sampled_portfolios = portfolios_df

        # Plot all (or sampled) portfolios for this solver with assigned color
        fig.add_trace(go.Scatter3d(
            x=sampled_portfolios['Volatility'],
            y=sampled_portfolios['Return'],
            z=sampled_portfolios['Sharpe Ratio'],
            mode='markers',
            marker=dict(
                size=6,
                opacity=0.5,
                color=solver_colors[solver],  # Use solver-specific color
            ),
            name=solver,
            hovertext=[
                f"Volatility: {vol:.3f}<br>Return: {ret:.3f}<br>Sharpe Ratio: {sr:.3f}<br><br>" + 
                "<br>".join([f"{k}: {v:.2%}" for k, v in row["Weights"].items()])
                for vol, ret, sr, row in zip(sampled_portfolios['Volatility'], sampled_portfolios['Return'], sampled_portfolios['Sharpe Ratio'], sampled_portfolios.to_dict('records'))
            ],
            hoverinfo='text'
        ))

    # Plot best portfolios with special markers and assigned colors
    for portfolio in best_portfolios:
        fig.add_trace(go.Scatter3d(
            x=[portfolio['Volatility']],
            y=[portfolio['Return']],
            z=[portfolio['Sharpe Ratio']],
            mode='markers',
            marker=dict(
                size=10,
                symbol='diamond',
                color=solver_colors[portfolio['Solver']],  # Use solver-specific color
                line=dict(
                    color='Black',
                    width=2
                ),
            ),
            name=f"Best {portfolio['Solver']}",
            hovertext=[
                f"Volatility: {portfolio['Volatility']:.3f}<br>Return: {portfolio['Return']:.3f}<br>Sharpe Ratio: {portfolio['Sharpe Ratio']:.3f}<br><br>" +
                "<br>".join([f"{k}: {v:.2%}" for k, v in portfolio["Weights"].items()])
            ],
            hoverinfo='text'
        ))

    fig.update_layout(
        title='<b>Portfolio Optimization Results</b><br><i>The best of each solver highlighted</i>',
        scene=dict(
            xaxis_title='Volatility',
            yaxis_title='Return',
            zaxis_title='Sharpe Ratio'
        ),
        width=900,
        height=700,
    )

    if show:
        fig.show()

    return fig

def plot_best_portfolio_weights(
    weights_dict: Dict[str, float],
    orientation: str = "h",
    show: bool = False
) -> go.Figure:
    x_col, y_col = "Stock", "Weight"
    df = pd.Series(weights_dict).reset_index().rename(columns={"index": x_col, 0: y_col})
    return plot_bar_chart(
        df=df,
        x=x_col,
        y=y_col,
        title="Best Portfolio Weights",
        orientation=orientation,
        show=show,
    )
    
def plot_portfolio_simulation_returns_over_time(portfolio_sims_df: pd.DataFrame, show: bool = False) -> go.Figure:
    """
    Plots the return over time of multiple portfolios.

    Parameters:
    - portfolio_sims_df: DataFrame containing the simulation results. Each column represents a portfolio simulation.
    - show: Whether to display the plot immediately (default: False).

    Returns:
    - fig: Plotly Figure object.
    """
    fig = go.Figure()

    for col in portfolio_sims_df.columns:
        fig.add_trace(go.Scatter(
            x=portfolio_sims_df.index,
            y=portfolio_sims_df[col],
            mode='lines',
            name=f'Portfolio {col}'
        ))

    fig.update_layout(
        title='Portfolio Returns Over Time',
        xaxis_title='Time (days)',
        yaxis_title='Portfolio Value ($)',
        showlegend=True
    )

    if show:
        fig.show()

    return fig

def plot_simulation_and_evaluation(
    portfolio_sims_df: pd.DataFrame,
    initial_portfolio_value: Optional[Union[int, float]] = None,
    VaR: Optional[float] = None,
    CVaR: Optional[float] = None,
    days: int = 90,
    dashed: bool = False,
    show: bool = False
) -> go.Figure:
    """
    Plots the return over time of multiple portfolios.

    Parameters:
    - portfolio_sims_df: DataFrame containing the simulation results. Each column represents a portfolio simulation.
    - show: Whether to display the plot immediately (default: False).

    Returns:
    - fig: Plotly Figure object.
    """
    fig = go.Figure()
    
    COLD_COLORS = [
        '#0000FF', '#1E90FF', '#00CED1', '#00FA9A', '#7FFFD4', '#5F9EA0', '#4682B4', '#6495ED', '#40E0D0', '#8A2BE2',
        '#4B0082', '#483D8B', '#6A5ACD', '#000080', '#008080', '#2E8B57', '#3CB371', '#7B68EE'
    ]

    for i, col in enumerate(portfolio_sims_df.columns[::-1]):
        fig.add_trace(go.Scatter(
            x=portfolio_sims_df.index,
            y=portfolio_sims_df[col],
            mode='lines',
            name=f'Portfolio {col}',
            line=dict(color=COLD_COLORS[i % len(COLD_COLORS)]),
        ))

    # Add VaR and CVaR lines
    traces = {}
    num_pts = 30
    if initial_portfolio_value is not None:
        for (name, value, color, dash) in [
            ('CVaR = ${value:,.0f}', CVaR, 'red', 'dot'),
            ('VaR = ${value:,.0f}', VaR, 'orange', 'dash'),
        ]:
            if value is not None:
                incr = (portfolio_sims_df.index.max() - portfolio_sims_df.index.min()) / num_pts
                trace_name = name.format(color=color, value=-value)
                trace = go.Scatter(
                    x=[portfolio_sims_df.index.min() + (i * incr) for i in range(num_pts)],
                    y=[initial_portfolio_value + value for _ in range(num_pts)],
                    mode='lines',
                    name=trace_name,
                    line=dict(
                        color=color,
                        dash=dash if dashed else None
                    ),
                    hovertemplate='{name}<extra></extra>'.format(name=trace_name)
                )
                traces[trace_name] = trace
                fig.add_trace(trace)

    fig.update_layout(
        title=f'Simulated Portfolio Returns Over {days} Days',
        xaxis_title='Time (days)',
        yaxis_title='Portfolio Value ($)',
        showlegend=True
    )
    
    fig.update_layout(
        legend=dict(
            traceorder="reversed"  # reverse the order of the traces in the legend
        )
    )
    
    if show:
        fig.show()

    return fig

def plot_simulation_and_evaluation_all_alphas(
    portfolio_sims_df: pd.DataFrame,
    initial_portfolio_value: Optional[Union[int, float]] = None,
    VaR_series: Optional[Union[Dict[float, Union[int, float]], pd.Series]] = None,
    CVaR_series: Optional[Union[Dict[float, Union[int, float]], pd.Series]] = None,
    days: int = 90,
    show: bool = False
) -> Dict[float, go.Figure]: # figure for each alpha
    
    if VaR_series is not None:
        VaR_series = dict(VaR_series)
    if CVaR_series is not None:
        CVaR_series = dict(CVaR_series)

    if VaR_series is not None and CVaR_series is not None:
        if set(VaR_series.keys()) != set(CVaR_series.keys()):
            raise ValueError("VaR and CVaR must have identical keys.")

    figs_dict = {}
    for alpha in (VaR_series or CVaR_series).keys():
        VaR = VaR_series.get(alpha) if VaR_series else None
        CVaR = CVaR_series.get(alpha) if CVaR_series else None
        fig = plot_simulation_and_evaluation(
            portfolio_sims_df,
            initial_portfolio_value=initial_portfolio_value,
            VaR=VaR,
            CVaR=CVaR,
            days=days,
            show=show
        )
        figs_dict[alpha] = fig

    return figs_dict

def plot_simulated_portfolio_returns_dist(
    returns: pd.Series,
    mean: Optional[Union[int, float]] = None,
    VaR: Optional[Union[int, float]] = None,
    CVaR: Optional[Union[int, float]] = None,
    bins: int = 25,
    days: int = 90,
    show: bool = True,
) -> go.Figure:
    group_labels = ['Simulated Returns']
    fig = ff.create_distplot(
        [returns.values],
        group_labels,
        bin_size=(returns.max() - returns.min()) / bins
    )
    num_pts = 20
    max_density = np.histogram(returns, bins=bins, density=True)[0].max()
    for (value, name, color, dash) in [
        (mean, "Mean = {sign}${value:,.0f}", "lightblue", "dash"),
        (VaR, "VaR = {sign}${value:,.0f}", "orange", None),
        (CVaR, "CVaR = {sign}${value:,.0f}", "red", None),
    ]:
        if value is not None:
            incr = (max_density - 0) / num_pts
            trace_name = name.format(sign=["", "-"][int(value<0)], value=np.abs(value))
            fig.add_trace(
                go.Scatter(
                    x=[value for _ in range(num_pts)],
                    y=[0 + (i * incr) for i in range(num_pts)],
                    mode="lines",
                    line=dict(
                        color=color,
                        # width=2,
                        dash=dash
                    ),
                    name=trace_name,
                    hovertemplate='{name}<extra></extra>'.format(name=trace_name)
                )
            )
    fig.update_layout(
        title=f'Distribution of Simulated Portfolio Returns Over {days} Days',
        xaxis_title='Return ($)',
        yaxis_title='Density',
        showlegend=True
    )
    if show:
        fig.show()
    return fig

def plot_simulated_portfolio_returns_dist_all_alphas(
    returns: pd.Series,
    VaR_series: Optional[Union[Dict[float, Union[int, float]], pd.Series]] = None,
    CVaR_series: Optional[Union[Dict[float, Union[int, float]], pd.Series]] = None,
    bins: int = 25,
    days: int = 90,
    show: bool = True,
) -> Dict[float, go.Figure]: # figure for each alpha
    
    if VaR_series is not None:
        VaR_series = dict(VaR_series)
    if CVaR_series is not None:
        CVaR_series = dict(CVaR_series)

    if VaR_series is not None and CVaR_series is not None:
        if set(VaR_series.keys()) != set(CVaR_series.keys()):
            raise ValueError("VaR and CVaR must have identical keys.")
    figs_dict = {}
    for alpha in (VaR_series or CVaR_series).keys():
        VaR = VaR_series.get(alpha) if VaR_series else None
        CVaR = CVaR_series.get(alpha) if CVaR_series else None
        fig = plot_simulated_portfolio_returns_dist(
            returns=returns,
            mean=returns.mean(),
            VaR=VaR,
            CVaR=CVaR,
            bins=bins,
            days=days,
            show=show,
        )
        figs_dict[alpha] = fig

    return figs_dict