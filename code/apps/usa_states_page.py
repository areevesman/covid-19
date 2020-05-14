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
        html.H1(id="page-title_US",
            children='Loading...',
            style={
                'textAlign': 'left',
                'color': colors['text']
            }
        ),

        search_bar,

        html.Label(id='slider-label_US',
                   children='Loading...',
                   style=date_style_dict),

        dcc.Slider(
            id='date--slider_US',
            min=0,
            max=len(state_page_dates) - 1,
            value=len(state_page_dates) - 1,
            marks={i: str() for i in range(len(state_page_dates))},
            step=1
        ),

        html.Div(id='output-totals_US',
                 style={'width': '30%'}),

        dcc.Graph(id='indicator-graphic_US'),

        dcc.Graph(id='daily-graph_US'),

        dcc.Graph(id='totals-graph_US'),

        html.Div(id='output-data-upload_US',
            style=table_style)
    ])


@app.callback(
    Output('indicator-graphic_US', 'figure'),
    [Input('date--slider_US', 'value')])
def update_graph(day):
    dff = state_page_df[state_page_df['Date'] == state_page_dates[day]]
    dff.loc[:, 'Text'] = [f'<b>{y}</b><br>{x:,} Cases<br>{z:,} Deaths' for x, y, z in
                             zip(dff['Cases'], dff['State'], dff['Deaths'])]

    return go.Figure(
        data=go.Choropleth(
            locations=dff['Code'],  # Spatial coordinates
            z=dff['Cases'].astype(float),  # Data to be color-coded
            zmin=0,
            zmax=state_page_df_grouped['Cases'].max() * 1.1,
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
        .update_layout(geo_scope='usa',
                       title=dict(text='Total cases by state on ' + state_page_dates[day], x=.5))


@app.callback(Output('totals-graph_US', 'figure'),
              [Input('date--slider_US', 'value'),
               Input('url', 'pathname')])
def show_total_cases_graph(day, pathname):
    return total_cases_graph(day, pathname, world_page_df, world_page_entities, state_page_dates, world_page_dates)

@app.callback(Output('daily-graph_US', 'figure'),
              [Input('date--slider_US', 'value'),
               Input('url', 'pathname')])
def show_daily_cases_graph(day, pathname):
    return daily_cases_graph(day, pathname, world_page_df, world_page_entities, state_page_dates, world_page_dates)

@app.callback(Output('output-totals_US', 'children'),
              [Input('date--slider_US', 'value'),
               Input('url', 'pathname')])
def show_updated_totals(day, pathname):
  return update_totals(day, pathname, state_page_df_grouped, 'State', state_page_dates)

@app.callback(Output('output-data-upload_US', 'children'),
              [Input('date--slider_US', 'value'),
               Input('url', 'pathname')])
def show_data_table(day, pathname):
    return data_table(day, pathname, state_page_df_grouped, state_page_dates, 'State')

@app.callback(Output('slider-label_US', 'children'),
              [Input('date--slider_US', 'value')])
def show_date(day):
    return str(state_page_dates[day])

@app.callback(Output('page-title_US', 'children'),
              [Input('url', 'pathname')])
def show_updated_header(pathname):
    return "Tracking COVID-19 in the United States"
