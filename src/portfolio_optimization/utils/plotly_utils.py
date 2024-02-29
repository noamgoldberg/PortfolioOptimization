from typing import Optional
import plotly.graph_objects as go

def change_plotly_fig_title(fig: go.Figure, new_title: Optional[str] = None) -> go.Figure:
    fig["layout"]["title"]["text"] = new_title
    return fig
    