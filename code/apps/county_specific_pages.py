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


location_colname = 'County'
page = 'any_county'
df = pd.read_csv('../data/daily_cases_USA_counties.csv')
df[location_colname + '_'] = [str(y).replace(' ','').lower() + '/' + str(x).replace(' ','').lower() for x,y in zip(df[location_colname], df['State'])]
cummulative_cases = df.groupby(['Date', location_colname, 'State', 'Code']).sum()[['Cases', 'Deaths']].reset_index()
dates = [str(x).replace('date_', '').replace('.csv', '') for x in os.listdir('../data/county_data/')]
dates = sorted(set([x for x in dates if x if x[0]=='2']))
location_dfs = [pd.read_csv(f'../data/county_data/{f}') for f in sorted(os.listdir('../data/county_data/'))]

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
            max=len(dates) - 1,
            value=len(dates) - 1,
            marks={i: str() for i in range(len(dates))},
            step=1
        ),

        html.Div(id='output-totals_US_CS',
                 style={'padding-left': '2%',
                        'padding-right': '2%',
                        'width': '30%'}),

        dcc.Graph(id='daily-graph_US_CS'),

        dcc.Graph(id='totals-graph_US_CS')
    ])


@app.callback(Output('totals-graph_US_CS', 'figure'),
              [Input('date--slider_US_CS', 'value'),
               Input('url', 'pathname')])
def show_total_cases_graph(day, pathname):
    return total_cases_graph(day, pathname, df, location_colname, dates)


@app.callback(Output('daily-graph_US_CS', 'figure'),
              [Input('date--slider_US_CS', 'value'),
               Input('url', 'pathname')])
def show_daily_cases_graph(day, pathname):
    return daily_cases_graph(day, pathname, df, location_colname, dates)


@app.callback(Output('output-totals_US_CS', 'children'),
              [Input('date--slider_US_CS', 'value'),
               Input('url', 'pathname')])
def show_updated_totals(day, pathname):
  return update_totals(day, pathname, cummulative_cases, location_colname, dates, page)


@app.callback(Output('slider-label_US_CS', 'children'),
              [Input('date--slider_US_CS', 'value')])
def show_date(day):
    return str(dates[day])


@app.callback(Output('page-title_US_CS', 'children'),
              [Input('url', 'pathname')])
def show_updated_header(pathname):
    return update_header(pathname, cummulative_cases, location_colname, page)

