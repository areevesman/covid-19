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
    children=header+[
        html.H1(
            children='Tracking COVID-19',
            style={
                'textAlign': 'left',
                'color': colors['text']
            }
        ),
        dcc.Markdown(
            id='element-to-hide',
            children=[
"""Welcome to the coronavirus tracking dashboard. 
You can use this tool to view the number of 
COVID-19 cases around the world.
For the United States, data is also available at the state and 
county levels.

Use the search bar or keep scrolling to get started. You can use the slider bar to select a date."""],
            style={
                'textAlign': 'left',
                'color': colors['text'],
                'fontSize': "20px",
                'display': 'block'
            }
        ),

        search_bar,

        html.Label(id='slider-label',
                   children='Loading...',
                   style=date_style_dict),

        dcc.Slider(
            id='date--slider',
            min=0,
            max=len(world_page_dates) - 1,
            value=len(world_page_dates) - 1,
            marks={i: str() for i in range(len(world_page_dates))},
            step=1
        ),

        html.Div(id='output-totals',
                 style={'width': '30%'}),

        dcc.Graph(id='indicator-graphic'),

        dcc.Graph(id='daily-graph'),

        dcc.Graph(id='totals-graph'),

        html.Div(id='output-data-upload',
            style=table_style)
    ])

@app.callback(
    Output('indicator-graphic', 'figure'),
    [Input('date--slider', 'value')])
def update_graph(day):
    dff = world_page_df[world_page_df['Date'] == world_page_dates[day]]
    dff.loc[:, 'Text'] = [f'<b>{y}</b><br>{x:,} Cases<br>{z:,} Deaths' for x, y, z in
                          zip(dff['Cases'], dff[world_page_entities], dff['Deaths'])]

    return {
        'data': [{'type': 'choropleth',
                  'locations': dff['Code'],
                  'z': dff['Cases'],
                  'zmin': 0,
                  'zmax': world_page_df_grouped['Cases'].max() * 1.05,
                  'text': dff['Text'],
                  'hoverinfo': 'text',
                  'colorbar': {'title': 'Total Cases'},
                  'colorscale': [[0, "rgb(255, 250, 250)"],
                                 [0.0001, "rgb(255, 200, 170)"],
                                 [0.001, "rgb(255, 150, 120)"],
                                 [0.01, "rgb(255, 100, 70)"],
                                 [0.1, "rgb(255, 50, 20)"],
                                 [1.0, "rgb(100, 0, 0)"]],
                  'autocolorscale': False,
                  'reversescale': False}],
        'layout': {
            'geo': {'showframe': True,
                    'projection': {'type': 'natural earth'}
                    },
            'plot_bgcolor': 'black',
            'title': {'text': 'Total cases by country on ' + world_page_dates[day]}
        }
    }


@app.callback(Output('totals-graph', 'figure'),
              [Input('date--slider', 'value'),
               Input('url', 'pathname')])
def show_total_cases_graph(day, pathname):
    return total_cases_graph(day, pathname, world_page_df, world_page_entities, world_page_dates)


@app.callback(Output('daily-graph', 'figure'),
              [Input('date--slider', 'value'),
               Input('url', 'pathname')])
def show_daily_cases_graph(day, pathname):
    return daily_cases_graph(day, pathname, world_page_df, world_page_entities, world_page_dates)


@app.callback(Output('output-data-upload', 'children'),
              [Input('date--slider', 'value'),
               Input('url', 'pathname')])
def show_data_table(day, pathname):
    return data_table(day, pathname, world_page_df_grouped, world_page_dates, world_page_entities)

@app.callback(Output('output-totals', 'children'),
              [Input('date--slider', 'value')])
def show_updated_totals(day):
  return update_totals(day, None, world_page_df_grouped, world_page_entities, world_page_dates)


@app.callback(Output('slider-label', 'children'),
              [Input('date--slider', 'value')])
def show_date(day):
    return str(world_page_dates[day])
