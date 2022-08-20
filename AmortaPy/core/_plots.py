"""Graph Plotting Functions 
"""
from __future__ import annotations
import sys
try:
    import plotly.express as px
    import plotly.graph_objs as go
except ImportError:
    pass

import pandas as pd

def plot_stacked_bar_chart(df:pd.DataFrame, x:str, y:list[str], chart_layout:dict)-> go.Figure:
    """Plot Dataframe data in a stacked bar chart

    Args:
        df (pd.DataFrame): Pandas Dataframe containing data to be stacked
        x (str): X_Axis Column Name
        y (list[str]): Y_Axis Column Names
        chart_layout (dict): Dictionary of chart properties to be updated: [Plotty API Docs](https://plotly.com/python-api-reference/)
    
    Raises:
        ImportError: If `plotly.express` has not been installed.
    
    Returns:
        go.Figure: Plotted Data Figure
    """
    if 'plotly.express' not in sys.modules:
        raise ImportError('plotly.express is required for charts. Please pip intall plotly-express')

    fig = px.bar(df, x=x, y=y, barmode='stack')
    fig.update_layout(chart_layout)
    return fig
