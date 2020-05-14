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
        html.H1(id="page-title_US_CS",
            children='Loading...',
            style={
                'textAlign': 'left',
                'color': colors['text']
            }
        ),

        search_bar,

        html.Label(id='slider-label_US_CS',
                   children='Loading...',
                   style=date_style_dict),

        dcc.Slider(
            id='date--slider_US_CS',
            min=1,
            max=len(CS_page_dates) - 1,
            value=len(CS_page_dates) - 1,
            marks={i: str() for i in range(len(CS_page_dates))},
            step=1
        ),

        html.Div(id='output-totals_US_CS',
                 style={'width': '30%'}),

        dcc.Graph(id='daily-graph_US_CS'),

        dcc.Graph(id='totals-graph_US_CS')
    ])


@app.callback(Output('totals-graph_US_CS', 'figure'),
              [Input('date--slider_US_CS', 'value'),
               Input('url', 'pathname')])
def show_total_cases_graph(day, pathname):
    return total_cases_graph(day, pathname, CS_page_df, CS_page_entities, CS_page_dates)


@app.callback(Output('daily-graph_US_CS', 'figure'),
              [Input('date--slider_US_CS', 'value'),
               Input('url', 'pathname')])
def show_daily_cases_graph(day, pathname):
    return daily_cases_graph(day, pathname, CS_page_df, CS_page_entities, CS_page_dates)


@app.callback(Output('output-totals_US_CS', 'children'),
              [Input('date--slider_US_CS', 'value'),
               Input('url', 'pathname')])
def show_updated_totals(day, pathname):
  return update_totals(day, pathname, CS_page_df_grouped, CS_page_entities, CS_page_dates)


@app.callback(Output('slider-label_US_CS', 'children'),
              [Input('date--slider_US_CS', 'value')])
def show_date(day):
    return str(CS_page_dates[day])


@app.callback(Output('page-title_US_CS', 'children'),
              [Input('url', 'pathname')])
def show_updated_header(pathname):
    return update_header(pathname, CS_page_df_grouped, CS_page_entities)

