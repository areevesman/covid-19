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


df = pd.read_csv('../data/world_data_with_codes.csv')
cummulative_cases = df.groupby(['Date', 'Country']).sum()[['Cases', 'Deaths']].reset_index()
dates = sorted(set(df['Date']))

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
        dcc.Markdown(
            id='element-to-hide',
            children=[
"""Welcome to the coronavirus tracking dashboard. 
You can use this tool to view the number of 
COVID-19 **cases** and **deaths** in countries around the world.
For the United States, data is also available at the state and 
county levels.

Instructions for accessing the data are provided below (click to make them visible):"""],
            style={
                'textAlign': 'left',
                'color': colors['text'],
                'fontSize': "20px",
                'padding-left': '2%',
                'padding-right': '2%',
                'display': 'block'
            }
        ),
        dcc.Dropdown(
            id = 'dropdown-to-show_or_hide-element',
            options=[
                {'label': 'Instructions Visible', 'value': 'on'},
                {'label': 'Instructions Hidden', 'value': 'off'}
            ],
            value='off',
            searchable=False,
            clearable=False,
            style={
                'padding-left': '2%',
                'padding-right': '0%',
                'width': '50%'
            }
        ),
        # Create Div to place a conditionally visible element inside
        html.Div([
            dcc.Markdown(
                id='element-to-hide',
                children=[
"""* For country-level data, either:
  * Click on a country in the table below, or
  * Add "/<country>" to the URL in your browser window (remove any spaces)
    * Example: [http://coronavirusmapsonline.com/UnitedKingdom](http://coronavirusmapsonline.com/UnitedKingdom)
* For US state-level data, either:
  * Navigate to the **CASES BY US STATE** tab above, then click on a state in the table, or
  * Navigate to the **CASES BY US COUNTY** tab above, then click on a state in the table, or
  * Add "/<state>" to the URL in your browser window (remove any spaces)
    * Example: [http://coronavirusmapsonline.com/NewYork](http://coronavirusmapsonline.com/NewYork)
* For US county-level data, either:
  * Navigate to the **CASES BY US COUNTY** tab above, then click on a county in the table, or
  * From a "/<state>" page, click on the county, or 
  * Add "/<state>/<county>" to the URL in your browser window (remove any spaces)
    * Example: [http://coronavirusmapsonline.com/California/SantaClara](http://coronavirusmapsonline.com/California/SantaClara)
* **Note:** Some links may need to be opened in a new tab"""],
                style={
                    'textAlign': 'left',
                    'color': colors['text'],
                    'fontSize': "20px",
                    'padding-left': '2%',
                    'padding-right': '2%',
                    'display': 'block'
                }
            )
        ]),
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

        dcc.Graph(id='indicator-graphic'),

        html.Div(id='output-totals',
                 style={'padding-left': '2%',
                        'padding-right': '2%',
                        'width': '30%'}),

        html.Div(id='output-data-upload',
            style=table_style)
    ])

@app.callback(
    Output('indicator-graphic', 'figure'),
    [Input('date--slider', 'value')])
def update_graph(day):
    dff = df[df['Date'] == dates[day]]
    dff.loc[:, 'Text'] = [f'<b>{y}</b><br>{x:,} Cases<br>{z:,} Deaths' for x, y, z in
                          zip(dff['Cases'], dff['Country'], dff['Deaths'])]

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
            'plot_bgcolor': 'black'
        }
    }

@app.callback(Output('output-data-upload', 'children'),
              [Input('date--slider', 'value')])
def update_table(day):
    totals = cummulative_cases[cummulative_cases['Date'] == dates[day]][['Country', 'Cases', 'Deaths']] \
        .sort_values('Cases', ascending=False)
    totals['Cases'] = totals['Cases'].map(lambda x: f'{x:,}')
    totals['Deaths'] = totals['Deaths'].map(lambda x: f'{x:,}')
    totals['Link'] = totals['Country'].map(lambda x: '/' + x.replace(' ',''))
    table = Table(totals, link_column_name='Link', col1='Country')
    return table

@app.callback(Output('output-totals', 'children'),
              [Input('date--slider', 'value')])
def update_totals(day):
    day_totals = cummulative_cases[cummulative_cases['Date'] == dates[day]].sum()
    d = {'Total Cases': [f"{day_totals['Cases']:,}"],
         'Total Deaths': [f"{day_totals['Deaths']:,}"]}
    totals = pd.DataFrame.from_dict(d)
    table = Table(totals)
    return table


@app.callback(Output('slider-label', 'children'),
              [Input('date--slider', 'value')])
def show_date(day):
    return str(dates[day])


@app.callback(
   Output(component_id='element-to-hide', component_property='style'),
   [Input(component_id='dropdown-to-show_or_hide-element', component_property='value')])
def show_hide_element(visibility_state):
    if visibility_state == 'on':
        return {
            'textAlign': 'left',
            'color': colors['text'],
            'fontSize': "20px",
            'padding-left': '2%',
            'padding-right': '2%',
            'display': 'block'
        }
    if visibility_state == 'off':
        return {
            'textAlign': 'left',
            'color': colors['text'],
            'fontSize': "20px",
            'padding-left': '2%',
            'padding-right': '2%',
            'display': 'none'
        }
