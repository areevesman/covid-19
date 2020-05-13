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

page, pathname = None, None
location_colname = 'Country'
df = pd.read_csv('../data/world_data_with_codes.csv')
cummulative_cases = df.groupby(['Date', location_colname]).sum()[['Cases', 'Deaths']].reset_index()
dates = sorted(set(df['Date']))

# county_level_df = pd.read_csv('../data/daily_cases_USA_counties.csv')
# world_dropdown_choices = sorted(set(df[location_colname]))
# state_dropdown_choices = sorted(set(county_level_df['State'][county_level_df['State'].isna()==False]))
# combinations = sorted(set(zip(county_level_df['State'][county_level_df['State'].isna()==False],
#                               county_level_df['County'][county_level_df['State'].isna()==False])))
# county_dropdown_labels = [s + ' - ' + c for s,c in combinations if str(s) not in ['nan','']]
# county_dropdown_values = ['/' + c + '/' + s for c,s in combinations]

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

Use the search bar or keep scrolling to get started"""],
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
            max=len(dates) - 1,
            value=len(dates) - 1,
            marks={i: str() for i in range(len(dates))},
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
    dff = df[df['Date'] == dates[day]]
    dff.loc[:, 'Text'] = [f'<b>{y}</b><br>{x:,} Cases<br>{z:,} Deaths' for x, y, z in
                          zip(dff['Cases'], dff[location_colname], dff['Deaths'])]

    return {
        'data': [{'type': 'choropleth',
                  'locations': dff['Code'],
                  'z': dff['Cases'],
                  'zmin': 0,
                  'zmax': cummulative_cases['Cases'].max() * 1.05,
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
            'title': {'text': 'Total cases by country on ' + dates[day]}
        }
    }


@app.callback(Output('totals-graph', 'figure'),
              [Input('date--slider', 'value'),
               Input('url', 'pathname')])
def show_total_cases_graph(day, pathname):
    page = 'world'
    return total_cases_graph(day, pathname, df, location_colname, dates, page)


@app.callback(Output('daily-graph', 'figure'),
              [Input('date--slider', 'value'),
               Input('url', 'pathname')])
def show_daily_cases_graph(day, pathname):
    page='world'
    return daily_cases_graph(day, pathname, df, location_colname, dates, page)


@app.callback(Output('output-data-upload', 'children'),
              [Input('date--slider', 'value')])
def show_data_table(day):
    page='world'
    return data_table(day, None, cummulative_cases, dates, location_colname, None, page)

@app.callback(Output('output-totals', 'children'),
              [Input('date--slider', 'value')])
def show_updated_totals(day):
  return update_totals(day, pathname, cummulative_cases, location_colname, dates, page)


@app.callback(Output('slider-label', 'children'),
              [Input('date--slider', 'value')])
def show_date(day):
    return str(dates[day])
