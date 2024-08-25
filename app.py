import pandas as pd
import os
import numpy as np
import plotly.graph_objects as go

from dash import Dash, dcc, html, Input, Output,callback,  dash_table
from dash import jupyter_dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash import no_update


# 1 
dirpath = os.getcwd()
datapath = os.path.join(dirpath, "data")

trial_dict = [{'label': c, 'value': c} for c in os.listdir(datapath)]
factor_dict = [{'label': '15', 'value': '15'}, {'label': '25', 'value': '25'},{'label': '50', 'value': '50'},]


def blank_fig():
    fig = go.Figure(go.Scatter3d(x=[], y = [], z=[]))
    fig.update_layout(paper_bgcolor="black")
    fig.update_layout(legend_font_color="white")
    fig.update_scenes(xaxis_visible=False, yaxis_visible=False,zaxis_visible=False)
    return fig
    
def plot_teat(trial_name, cow, factor, ti):
    if cow == None:
        fig = blank_fig()
    else:
        filename = f"teat_points_{cow}_{factor}.csv"
        filepath = os.path.join(datapath, trial_name, filename)
        teat_df = pd.read_csv(filepath, header=None).to_numpy()
        
        filename = f"vectors_points_{cow}_{factor}.csv"
        filepath = os.path.join(datapath, trial_name, filename)
        vacotrs_df = pd.read_csv(filepath, header=None).to_numpy()
    
        # udder = teat_df[np.where((teat_df[:, 4]==1) & (teat_df[:, 3]=="u"))[0], :]
        fteat = teat_df[np.where((teat_df[:, 4]==ti) & (teat_df[:, 3]=="t2"))[0], :]
        cteat = teat_df[np.where((teat_df[:, 4]==ti) & (teat_df[:, 3]=="t1"))[0], :]
        circ = teat_df[np.where((teat_df[:, 4]==ti) & (teat_df[:, 3]=="c"))[0], :]
        # udder[:, 2] =  udder[:, 2]- cteat[:, 2]
        
        data1 = vacotrs_df[np.where((vacotrs_df[:, 4]==ti) & (vacotrs_df[:, 3]=="d1"))[0], :]
        data2 = vacotrs_df[np.where((vacotrs_df[:, 4]==ti) & (vacotrs_df[:, 3]=="d2"))[0], :]
        data3 = vacotrs_df[np.where((vacotrs_df[:, 4]==ti) & (vacotrs_df[:, 3]=="d3"))[0], :]
        points = cteat
        fig =  go.Figure(data=[go.Scatter3d(x = points[:, 0], y = points[:, 1], z=points[:, 2],mode='markers',
             marker=dict(size=1, color="gray", opacity=0.5), name = "unfiltered")])
        
        points = fteat
        fig.add_trace(go.Scatter3d(x= points[:, 0], y = points[:, 1], z=points[:, 2], mode='markers', marker=dict(color="white", size = 2, opacity = 1), name = "filtered"))
        points = circ
        fig.add_trace(go.Scatter3d(x= points[:, 0], y = points[:, 1], z=points[:, 2], mode='markers', marker=dict(color="skyblue", size = 1, opacity = 0.2), name = "ellipse", visible = "legendonly"))
        
        for vec in zip([data1, data2, data3], ["red", "blue", "green"]):
            points = vec[0]
            color = vec[1]
            fig.add_trace(go.Scatter3d(x= points[:, 0], y = points[:, 1], z=points[:, 2], mode='lines', marker=dict(color=color, size = 2), name = color))
            fig.update_layout(paper_bgcolor="black", font_color = "white", plot_bgcolor = "black")
            fig.update_scenes(xaxis_visible=False, yaxis_visible=False,zaxis_visible=False)
    return fig

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

MENU_STYLE = {
    'backgroundColor': 'black',
    'color': 'white',
}

sidebar = html.Div(
    [
        html.H2("SVD", className="display-4"),
        html.Hr(),
        html.P(
            "choose a preprocessing option, factor fot the threshold, and a cow", className="lead"
        ),
        html.Label("Trial mane:"),
        dcc.Dropdown(id='tn-dpdn',options= trial_dict, value = 'vol', style = MENU_STYLE),
        html.Label("Filter threshold:"),
        dcc.RadioItems(id = 'factor', options=factor_dict, value='25',  inline=True),
        
        html.Label("Cow ID:"),
        dcc.Dropdown(id='cows-dpdn',options= [], style = MENU_STYLE),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(
[html.Div(
             [dbc.Row(
                [dbc.Col([dcc.Graph(id='graph2', figure = blank_fig())], md = 6),
                 dbc.Col([dcc.Graph(id='graph1', figure = blank_fig())], md = 6),]),
              dbc.Row(
                [dbc.Col([dcc.Graph(id='graph4', figure = blank_fig())], md = 6),
                 dbc.Col([dcc.Graph(id='graph3', figure = blank_fig())], md = 6),]), 
             ])
], id="page-content", style=CONTENT_STYLE)


app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

@app.callback(
    Output('cows-dpdn', 'options'),
    Input('tn-dpdn', 'value'))
def get_frames(trial_name):
    global datapath
    file_list = os.listdir(os.path.join(datapath, trial_name))
    cow_list = np.unique([file.split("_")[2] for file in file_list])
    return [{'label': c, 'value': c} for c in cow_list]

@app.callback(
    Output("graph1", "figure"), 
    Input('tn-dpdn', 'value'),
    Input('cows-dpdn', 'value'),
    Input('factor', 'value'))
def update_bar_chart(trial_name, cow, factor):
    fig = plot_teat(trial_name, cow, factor, 1)
    return fig

@app.callback(
    Output("graph2", "figure"), 
    Input('tn-dpdn', 'value'),
    Input('cows-dpdn', 'value'),
    Input('factor', 'value'))
def update_bar_chart(trial_name, cow, factor):
    fig = plot_teat(trial_name, cow, factor, 2)
    return fig

@app.callback(
    Output("graph3", "figure"), 
    Input('tn-dpdn', 'value'),
    Input('cows-dpdn', 'value'),
    Input('factor', 'value'))
def update_bar_chart(trial_name, cow, factor):
    fig = plot_teat(trial_name, cow, factor, 3)
    return fig

@app.callback(
    Output("graph4", "figure"), 
    Input('tn-dpdn', 'value'),
    Input('cows-dpdn', 'value'),
    Input('factor', 'value'))
def update_bar_chart(trial_name, cow, factor):
    fig = plot_teat(trial_name, cow, factor, 4)
    return fig

if __name__ == '__main__':
    app.run(jupyter_mode="tab")