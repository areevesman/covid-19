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

page, pathname=None, None
location_colname = 'State'
df = pd.read_csv('../data/daily_cases_USA_states.csv')
cummulative_cases = df.groupby(['Date', location_colname, 'Day', 'Code'])\
    .sum()[['Cases', 'Deaths']].reset_index()
dates = sorted(set(df['Date']))
states = [x for x in set(df[location_colname]) if str(x) != 'nan']

layout = html.Div(
    style={'backgroundColor': colors['background']},
    children=header+[
        html.Br(),
        html.Br(),
        html.H1(
            children='Tracking COVID-19',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),
        html.Label(id='slider-label_US',
                   children='Loading...',
                   style=date_style_dict),

        dcc.Slider(
            id='date--slider_US',
            min=0,
            max=len(dates) - 1,
            value=len(dates) - 1,
            marks={i: str() for i in range(len(dates))},
            step=1
        ),

        dcc.Graph(id='indicator-graphic_US'),

        html.Div(id='output-totals_US',
                 style={'padding-left': '2%',
                        'padding-right': '2%',
                        'width': '30%'}),

        html.Div(id='output-data-upload_US',
            style=table_style)
    ])

@app.callback(
    Output('indicator-graphic_US', 'figure'),
    [Input('date--slider_US', 'value')])
def update_graph(day):
    dff = df[df['Date'] == dates[day]]
    dff.loc[:, 'Text'] = [f'<b>{y}</b><br>{x:,} Cases<br>{z:,} Deaths' for x, y, z in
                             zip(dff['Cases'], dff[location_colname], dff['Deaths'])]

    return go.Figure(
        data=go.Choropleth(
            locations=dff['Code'],  # Spatial coordinates
            z=dff['Cases'].astype(float),  # Data to be color-coded
            zmin=0,
            zmax=cummulative_cases['Cases'].max() * 1.1,
            locationmode='USA-states',  # set of locations match entries in `locations`
            text=dff['Text'],
            hoverinfo='text',
            colorscale=[[0, "rgb(255, 250, 250)"],
                        [0.0016, "rgb(255, 200, 170)"],
                        [0.008, "rgb(255, 150, 120)"],
                        [0.04, "rgb(255, 100, 70)"],
                        [0.2, "rgb(255, 50, 20)"],
                        [1.0, "rgb(100, 0, 0)"]],
            colorbar_title="Total Cases")) \
        .update_layout(geo_scope='usa')

@app.callback(Output('output-data-upload_US', 'children'),
              [Input('date--slider_US', 'value')])
def show_data_table(day):
    page = 'states'
    return data_table(day, None, cummulative_cases, dates, location_colname, None, page)


@app.callback(Output('output-totals_US', 'children'),
              [Input('date--slider_US', 'value')])
def show_updated_totals(day):
  return update_totals(day, pathname, cummulative_cases, location_colname, dates, page)

@app.callback(Output('slider-label_US', 'children'),
              [Input('date--slider_US', 'value')])
def show_date(day):
    return str(dates[day])
