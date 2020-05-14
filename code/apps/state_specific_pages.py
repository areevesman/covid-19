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


# location
# SS_page_entities = 'State'
# SS_page_df = pd.read_csv('../data/daily_cases_USA_states.csv')
# SS_page_df[SS_page_entities + '_'] = [str(x).replace(' ', '').lower() for x in SS_page_df[SS_page_entities]]
#
# # county
# SS_page_df_counties = pd.read_csv('../data/daily_cases_USA_counties.csv')
# SS_page_df_grouped = SS_page_df_counties.groupby(['Date', 'County', SS_page_entities, 'Code']).sum()[['Cases', 'Deaths']].reset_index()
# SS_page_dates = [str(x).replace('date_', '').replace('.csv', '') for x in os.listdir('../data/county_data/')]
# SS_page_dates = sorted(set([x for x in SS_page_dates if x if x[0] == '2']))
# SS_page_county_dfs = [pd.read_csv(f'../data/county_data/date_{d}.csv') for d in SS_page_dates]
#
# SS_page_location_lat_lon = pd.read_csv('../data/statelatlong.csv')

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
            max=len(SS_page_dates) - 1,
            value=len(SS_page_dates) - 1,
            marks={i: str() for i in range(len(SS_page_dates))},
            step=1
        ),

        html.Div(id='output-totals_US_c',
                 style={'width': '30%'}),

        dcc.Graph(id='indicator-graphic_US_c'),

        dcc.Graph(id='daily-graph_US_c'),

        dcc.Graph(id='totals-graph_US_c'),

        html.Div(id='output-data-upload_US_c',
                 style={}),
    ])


@app.callback(Output('totals-graph_US_c', 'figure'),
              [Input('date--slider_US_c', 'value'),
               Input('url', 'pathname')])
def show_total_cases_graph(day, pathname):
    return total_cases_graph(day, pathname, SS_page_df, SS_page_entities, SS_page_dates, SS_page_dates)


@app.callback(Output('daily-graph_US_c', 'figure'),
              [Input('date--slider_US_c', 'value'),
               Input('url', 'pathname')])
def show_daily_cases_graph(day, pathname):
    return daily_cases_graph(day, pathname, SS_page_df, SS_page_entities, SS_page_dates, SS_page_dates)


@app.callback(
    Output('indicator-graphic_US_c', 'figure'),
    [Input('date--slider_US_c', 'value'),
     Input('url', 'pathname')])
def show_state_county_choropleth(day, pathname):
    return state_county_choropleth(day, pathname,
                                   SS_page_county_dfs, SS_page_entities,
                                   SS_page_location_lat_lon, SS_page_dates,
                                   SS_page_df_grouped)


@app.callback(Output('output-data-upload_US_c', 'children'),
              [Input('date--slider_US_c', 'value'),
               Input('url', 'pathname')])
def show_data_table(day, pathname):
    return data_table(day, pathname, SS_page_df_grouped, SS_page_dates, SS_page_entities)


@app.callback(Output('output-totals_US_c', 'children'),
              [Input('date--slider_US_c', 'value'),
               Input('url', 'pathname')])
def show_updated_totals(day, pathname):
  return update_totals(day, pathname, SS_page_df_grouped, SS_page_entities, SS_page_dates)


@app.callback(Output('slider-label_US_c', 'children'),
              [Input('date--slider_US_c', 'value')])
def show_date(day):
    return str(SS_page_dates[day])


@app.callback(Output('page-title_US_c', 'children'),
              [Input('url', 'pathname')])
def show_updated_header(pathname):
    return update_header(pathname, SS_page_df_grouped, SS_page_entities)
