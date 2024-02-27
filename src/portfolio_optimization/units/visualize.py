import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Iterable


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
            name=method
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
            name=f"Best {portfolio['Method']}"
        ))

    fig.update_layout(
        title='<b>Portfolio Optimization Results</b><br><h2><i>The best of each method highlighted</i></h2>',
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




def plot_monte_carlo_iterations(
    *,
    return_arr: np.ndarray,
    volatility_arr: np.ndarray,
    sharpe_ratio_arr: np.ndarray,
    all_weights_arr: np.ndarray,
    tickers: Iterable,
    sample: int = 10000,
    show: bool = False
):
    fig = go.Figure()

    # Adjusted function to include Sharpe Ratio in hover text
    def create_hover_text(weights, tickers, sharpe_ratio=None):
        top_indices = np.argsort(weights)[::-1][:10]  # Get indices of top 10 Weights
        top_tickers = np.array(tickers)[top_indices]
        top_weights = weights[top_indices]
        hover_texts = [f"{ticker}: {weight:.5%}" for ticker, weight in zip(top_tickers, top_weights)]
        if sharpe_ratio is not None:
            hover_texts.insert(0, f"Sharpe Ratio: {sharpe_ratio:.5f}")  # Include Sharpe ratio at the start
        return "<br>".join(hover_texts)
    
    # (1) Update for Max Sharpe Ratio Marker
    max_sr_index = np.argmax(sharpe_ratio_arr)
    max_sr_weights = all_weights_arr[max_sr_index]
    max_sr_hover_text = create_hover_text(max_sr_weights, tickers, sharpe_ratio_arr[max_sr_index])
    max_sr_ret = return_arr[max_sr_index]
    max_sr_vol = volatility_arr[max_sr_index]
    
    max_sr_marker = go.Scatter(
        x=[max_sr_vol],
        y=[max_sr_ret],
        mode='markers',
        marker=dict(
            symbol='x',
            size=12,
            color='Black',
        ),
        name='Max Sharpe Ratio',
        text=[max_sr_hover_text],  # Set hover text
        hoverinfo='text+x+y'
    )
    
    # (2) Sample Non-Optimal Portfolios
    total_points = min(return_arr.shape[0], sample)
    indices = np.random.choice(return_arr.shape[0], total_points, replace=False)
    
    sampled_weights = all_weights_arr[indices]
    sampled_returns = return_arr[indices]
    sampled_volatilities = volatility_arr[indices]
    sampled_sharpe_ratios = sharpe_ratio_arr[indices]
    
    sampled_hover_texts = [create_hover_text(weights, tickers, sharpe_ratio) for weights, sharpe_ratio in zip(sampled_weights, sampled_sharpe_ratios)]
    
    # (3) Scatter Plot Object for Sampled Points
    scatter = go.Scatter(
        x=sampled_volatilities,
        y=sampled_returns,
        mode='markers',
        marker=dict(
            size=8,
            color=sampled_sharpe_ratios,
            colorscale='Plasma',
            colorbar=dict(title='Sharpe Ratio'),
            line=dict(width=1, color='DarkSlateGrey')
        ),
        name='Data Points',
        text=sampled_hover_texts,  # Set hover text for each point
        hoverinfo='text+x+y'
    )
    
    # (4) Add Traces
    fig.add_trace(scatter)
    fig.add_trace(max_sr_marker)
    
    # (5) Update Layout
    fig.update_layout(
        autosize=False,
        width=700,
        height=700,
        title='Monte Carlo Simulation Results',
        xaxis_title='Volatility',
        yaxis_title='Return',
        showlegend=True,
        legend_orientation="h",
    )
    if show:
        fig.show()
    
    return fig
