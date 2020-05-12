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

from shared_functions import *

from app import app

location_colname = 'Country'
page = 'any_country'
df = pd.read_csv('../data/world_data_with_codes.csv')
df[location_colname + '_'] = [x.replace(' ','').lower() for x in df[location_colname]]
cummulative_cases = df.groupby(['Date', location_colname]).sum()[['Cases', 'Deaths']].reset_index()
dates = sorted(set(df['Date']))

layout = html.Div(
    style={'backgroundColor': colors['background']},
    children=header + [
        html.Br(),
        html.Br(),
        html.H1(id="page-title_CS",
            children='Loading...',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),
        html.Label(id='slider-label_CS',
                   children='Loading...',
                   style=date_style_dict),

        dcc.Slider(
            id='date--slider_CS',
            min=0,
            max=len(dates) - 1,
            value=len(dates) - 1,
            marks={i: str() for i in range(len(dates))},
            step=1
        ),

        html.Div(id='output-totals_CS',
                 style={'padding-left': '2%',
                        'padding-right': '2%',
                        'width': '30%'}),

        dcc.Graph(id='daily-graph_CS'),

        dcc.Graph(id='totals-graph_CS')
    ])

@app.callback(Output('totals-graph_CS', 'figure'),
              [Input('date--slider_CS', 'value'),
               Input('url', 'pathname')])
def show_total_cases_graph(day, pathname):
    return total_cases_graph(day, pathname, df, location_colname, dates)


@app.callback(Output('daily-graph_CS', 'figure'),
              [Input('date--slider_CS', 'value'),
               Input('url', 'pathname')])
def show_daily_cases_graph(day, pathname):
    return daily_cases_graph(day, pathname, df, location_colname, dates)

@app.callback(Output('output-totals_CS', 'children'),
              [Input('date--slider_CS', 'value'),
               Input('url', 'pathname')])
def show_updated_totals(day, pathname):
  return update_totals(day, pathname, cummulative_cases, location_colname, dates, page)


@app.callback(Output('slider-label_CS', 'children'),
              [Input('date--slider_CS', 'value')])
def show_date(day):
    return str(dates[day])


@app.callback(Output('page-title_CS', 'children'),
              [Input('url', 'pathname')])
def show_updated_header(pathname):
    return update_header(pathname, cummulative_cases, location_colname, page)
