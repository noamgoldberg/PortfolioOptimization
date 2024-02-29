from typing import Optional, Union, Iterable, Dict, Callable
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from portfolio_optimization.utils.data_utils import concat_partitions, filter_stocks_df_for_agg, get_stock_returns
from portfolio_optimization.utils.formatting_utils import str2list


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

def plot_best_portfolio_weights(best_portfolio_weights: pd.DataFrame, show: bool = True) -> go.Figure:
    return plot_bar_chart(
        best_portfolio_weights,
        x="Stock",
        y="Weight",
        title="Stock Weights for Optimal Portfolio",
        orientation="h",
        show=show
    )

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
        colorscale='haline',
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
):
    fig = go.Figure()

    # Define a color palette
    color_palette = ['blue', 'green', 'red', 'purple', 'orange', 'yellow', 'pink', 'cyan', 'magenta', 'grey']
    
    # Group portfolios by method and find the best one in each group
    portfolios_by_method = {}
    for index, row in portfolios.iterrows():
        method = row['Method']
        if method not in portfolios_by_method:
            portfolios_by_method[method] = []
        portfolios_by_method[method].append(row)

    best_portfolios = []
    method_colors = {method: color_palette[i % len(color_palette)] for i, method in enumerate(portfolios_by_method.keys())}

    for method, portfolios in portfolios_by_method.items():
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

        # Plot all (or sampled) portfolios for this method with assigned color
        fig.add_trace(go.Scatter3d(
            x=sampled_portfolios['Volatility'],
            y=sampled_portfolios['Return'],
            z=sampled_portfolios['Sharpe Ratio'],
            mode='markers',
            marker=dict(
                size=6,
                opacity=0.5,
                color=method_colors[method],  # Use method-specific color
            ),
            name=method,
            hovertext=[
                f"Volatility: {vol:.3f}<br>Return: {ret:.3f}<br>Sharpe Ratio: {sr:.3f}<br>" + 
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
                color=method_colors[portfolio['Method']],  # Use method-specific color
                line=dict(
                    color='Black',
                    width=2
                ),
            ),
            name=f"Best {portfolio['Method']}",
            hovertext=[
                f"Volatility: {portfolio['Volatility']:.3f}<br>Return: {portfolio['Return']:.3f}<br>Sharpe Ratio: {portfolio['Sharpe Ratio']:.3f}<br><br>" +
                "<br>".join([f"{k}: {v:.2%}" for k, v in portfolio["Weights"].items()])
            ],
            hoverinfo='text'
        ))

    fig.update_layout(
        title='<b>Portfolio Optimization Results</b><br><i>The best of each method highlighted</i>',
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
