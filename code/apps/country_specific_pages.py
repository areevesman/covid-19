import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
from urllib.request import urlopen
import json
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import os
import flask

# from shared_functions import *
from lib import *


from app import app


layout = html.Div(
    style={'backgroundColor': colors['background'],
           'padding-left': '2%',
           'padding-right': '2%'},
    children=header + [
        html.H1(id="page-title_CS",
            children='Loading...',
            style={
                'textAlign': 'left',
                'color': colors['text']
            }
        ),

        search_bar,

        html.Label(id='slider-label_CS',
                   children='Loading...',
                   style=date_style_dict),

        dcc.Slider(
            id='date--slider_CS',
            min=0,
            max=len(C_page_dates) - 1,
            value=len(C_page_dates) - 1,
            marks={i: str() for i in range(len(C_page_dates))},
            step=1
        ),

        html.Div(id='output-totals_CS',
                 style={'width': '30%'}),

        dcc.Graph(id='daily-graph_CS'),

        dcc.Graph(id='totals-graph_CS')
    ])

@app.callback(Output('totals-graph_CS', 'figure'),
              [Input('date--slider_CS', 'value'),
               Input('url', 'pathname')])
def show_total_cases_graph(day, pathname):
    return total_cases_graph(day, pathname, C_page_df, C_page_entities, C_page_dates)


@app.callback(Output('daily-graph_CS', 'figure'),
              [Input('date--slider_CS', 'value'),
               Input('url', 'pathname')])
def show_daily_cases_graph(day, pathname):
    return daily_cases_graph(day, pathname, C_page_df, C_page_entities, C_page_dates)

@app.callback(Output('output-totals_CS', 'children'),
              [Input('date--slider_CS', 'value'),
               Input('url', 'pathname')])
def show_updated_totals(day, pathname):
    print(world_page_df_grouped)
    return update_totals(day, pathname, world_page_df_grouped, world_page_entities, world_page_dates)


@app.callback(Output('slider-label_CS', 'children'),
              [Input('date--slider_CS', 'value')])
def show_date(day):
    return str(C_page_dates[day])


@app.callback(Output('page-title_CS', 'children'),
              [Input('url', 'pathname')])
def show_updated_header(pathname):
    return update_header(pathname, C_page_df_grouped, C_page_entities)
