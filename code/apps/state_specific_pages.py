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


# location
location_colname = 'State'
page = 'any_state'
df = pd.read_csv('../data/daily_cases_USA_states.csv')
df[location_colname + '_'] = [str(x).replace(' ','').lower() for x in df[location_colname]]

# county
df_counties = pd.read_csv('../data/daily_cases_USA_counties.csv')
cummulative_cases = df_counties.groupby(['Date', 'County', location_colname, 'Code']).sum()[['Cases', 'Deaths']].reset_index()
dates = [str(x).replace('date_', '').replace('.csv', '') for x in os.listdir('../data/county_data/')]
dates = sorted(set([x for x in dates if x if x[0]=='2']))
county_dfs = [pd.read_csv(f'../data/county_data/date_{d}.csv') for d in dates]

location_lat_lon = pd.read_csv('../data/statelatlong.csv')

layout = html.Div(
    style={'backgroundColor': colors['background'],
           'padding-left': '2%',
           'padding-right': '2%'},
    children=header + [
        html.H1(id="page-title_US_c",
            children='Loading...',
            style={
                'textAlign': 'left',
                'color': colors['text']
            }
        ),

        search_bar,

        html.Label(id='slider-label_US_c',
                   children='Loading...',
                   style=date_style_dict),

        dcc.Slider(
            id='date--slider_US_c',
            min=1,
            max=len(dates) - 1,
            value=len(dates) - 1,
            marks={i: str() for i in range(len(dates))},
            step=1
        ),

        html.Div(id='output-totals_US_c',
                 style={'padding-left': '2%',
                        'padding-right': '2%',
                        'width': '30%'}),

        dcc.Graph(id='indicator-graphic_US_c'),

        dcc.Graph(id='daily-graph_US_c'),

        dcc.Graph(id='totals-graph_US_c'),

        html.Div(id='output-data-upload_US_c',
                 style={'padding-left': '2%',
                        'padding-right': '2%'}),
    ])


@app.callback(Output('totals-graph_US_c', 'figure'),
              [Input('date--slider_US_c', 'value'),
               Input('url', 'pathname')])
def show_total_cases_graph(day, pathname):
    return total_cases_graph(day, pathname, df, location_colname, dates)


@app.callback(Output('daily-graph_US_c', 'figure'),
              [Input('date--slider_US_c', 'value'),
               Input('url', 'pathname')])
def show_daily_cases_graph(day, pathname):
    return daily_cases_graph(day, pathname, df, location_colname, dates)


@app.callback(
    Output('indicator-graphic_US_c', 'figure'),
    [Input('date--slider_US_c', 'value'),
     Input('url', 'pathname')])
def show_state_county_choropleth(day, pathname):
    return state_county_choropleth(day, pathname,
                                   county_dfs, location_colname,
                                   location_lat_lon, dates,
                                   cummulative_cases)


@app.callback(Output('output-data-upload_US_c', 'children'),
              [Input('date--slider_US_c', 'value'),
               Input('url', 'pathname')])
def show_data_table(day, pathname):
    page='any_state'
    return data_table(day, pathname, cummulative_cases, dates, location_colname, county_dfs, page)


@app.callback(Output('output-totals_US_c', 'children'),
              [Input('date--slider_US_c', 'value'),
               Input('url', 'pathname')])
def show_updated_totals(day, pathname):
  return update_totals(day, pathname, cummulative_cases, location_colname, dates, page)


@app.callback(Output('slider-label_US_c', 'children'),
              [Input('date--slider_US_c', 'value')])
def show_date(day):
    return str(dates[day])


@app.callback(Output('page-title_US_c', 'children'),
              [Input('url', 'pathname')])
def show_updated_header(pathname):
    page='any_state'
    return update_header(pathname, cummulative_cases, location_colname, page)


# @app.callback(Output('date--slider_US_c', 'children'),
#               [Input('url', 'pathname')])
# def update_date_range(pathname, dates):
#     location = pathname.strip('/')
#     day_totals = cummulative_cases[
#         (cummulative_cases[location_colname].map(lambda x: str(x).replace(' ', '')) == location)].sum()
#     dates = [x for x in dates if x if x[0] == '2']))
#     d = {'Total Cases': [f"{int(day_totals['Cases']):,}"],
#          'Total Deaths': [f"{int(day_totals['Deaths']):,}"]}
#     totals = pd.DataFrame.from_dict(d)
#     table = Table(totals)
#     return table
