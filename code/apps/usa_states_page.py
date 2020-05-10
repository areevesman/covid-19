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

df_US = pd.read_csv('../data/daily_cases_USA_states.csv')
cummulative_cases_US = df_US.groupby(['Date', 'State', 'Day', 'Code'])\
    .sum()[['Cases', 'Deaths']].reset_index()
dates_US = sorted(set(df_US['Date']))
states = [x for x in set(df_US['State']) if str(x) != 'nan']

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
            max=len(dates_US) - 1,
            value=len(dates_US) - 1,
            marks={i: str() for i in range(len(dates_US))},
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
def update_graph_US(day_US):
    dff_US = df_US[df_US['Date'] == dates_US[day_US]]
    dff_US.loc[:, 'Text'] = [f'<b>{y}</b><br>{x:,} Cases<br>{z:,} Deaths' for x, y, z in
                             zip(dff_US['Cases'], dff_US['State'], dff_US['Deaths'])]

    return go.Figure(
        data=go.Choropleth(
            locations=dff_US['Code'],  # Spatial coordinates
            z=dff_US['Cases'].astype(float),  # Data to be color-coded
            zmin=0,
            zmax=cummulative_cases_US['Cases'].max() * 1.1,
            locationmode='USA-states',  # set of locations match entries in `locations`
            text=dff_US['Text'],
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
def update_table_US(day_US):
    totals_US = cummulative_cases_US[cummulative_cases_US['Date'] == dates_US[day_US]][['State', 'Cases', 'Deaths']] \
        .sort_values('Cases', ascending=False)
    totals_US['Cases'] = totals_US['Cases'].map(lambda x: f'{x:,}')
    totals_US['Deaths'] = totals_US['Deaths'].map(lambda x: f'{x:,}')
    totals_US['Links'] = ['/'+state for state in totals_US['State']]
    table_US = Table(totals_US, 'Links', 'State')
    return table_US

@app.callback(Output('output-totals_US', 'children'),
              [Input('date--slider_US', 'value')])
def update_totals_US(day_US):
    day_totals_US = cummulative_cases_US[cummulative_cases_US['Date'] == dates_US[day_US]].sum()
    # day_totals_US = df_US.sum()[['Cases', 'Deaths']].reset_index()
    d = {'Total Cases': [f"{day_totals_US['Cases']:,}"],
            'Total Deaths': [f"{day_totals_US['Deaths']:,}"]}
    totals = pd.DataFrame.from_dict(d)
    table = Table(totals)
    return table

@app.callback(Output('slider-label_US', 'children'),
              [Input('date--slider_US', 'value')])
def show_date_US(day_US):
    return str(dates_US[day_US])
