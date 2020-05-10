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
df['Country_'] = [x.replace(' ','') for x in df['Country']]
cummulative_cases = df.groupby(['Date', 'Country']).sum()[['Cases', 'Deaths']].reset_index()
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

        dcc.Graph(id='totals-graph_CS'),

        dcc.Graph(id='daily-graph_CS')
    ])

@app.callback(Output('totals-graph_CS', 'figure'),
              [Input('date--slider_CS', 'value'),
               Input('url', 'pathname')])
def total_cases_graph(day, pathname):
    country = pathname.strip('/')
    country_df = df[df['Country_'] == country].reset_index(drop=True)[:day+1][-60:]
    country_df.loc[:, 'Text'] = [f'<b>{x}</b><br>{int(y):,} Cases<br>{int(z):,} Deaths' for x, y, z in \
                                 zip(country_df['Date'], country_df['Cases'], country_df['Deaths'])]
    return go.Figure(data=[
        go.Bar(name='Deaths',
               x=country_df['Date'],
               y=country_df['Deaths'],
               marker_color='red',
               text=country_df['Text'],
               hoverinfo='text'),
        go.Bar(name='Cases',
               x=country_df['Date'],
               y=country_df['Cases'] - country_df['Deaths'],
               marker_color='blue',
               text=country_df['Text'],
               hoverinfo='text')
    ]).update_layout(barmode='stack',
                      plot_bgcolor='white',
                      xaxis=dict(title='Date'),
                      yaxis=dict(title='Total'),
                      title=dict(text='Total Cases and Deaths in ' + country_df['Country'].values[0],
                                 x=0.5),
                      legend=dict(x=0, y=1))


@app.callback(Output('daily-graph_CS', 'figure'),
              [Input('date--slider_CS', 'value'),
               Input('url', 'pathname')])
def daily_cases_graph(day, pathname):
    country = pathname.strip('/')
    country_df = df[df['Country_'] == country].reset_index(drop=True)[:day+1][-60:]
    c = country_df['Cases'].values
    d = country_df['Deaths'].values
    country_df['New Cases'] = [c[0]] + list(c[1:] - c[:-1])
    country_df['New Deaths'] = [d[0]] + list(d[1:] - d[:-1])
    country_df.loc[:, 'Text'] = [f'<b>{x}</b><br>{int(y):,} New Cases<br>{int(z):,} New Deaths' for x, y, z in \
                                 zip(country_df['Date'], country_df['New Cases'], country_df['New Deaths'])]
    return go.Figure(data=[
        go.Bar(name='New Deaths',
               x=country_df['Date'],
               y=country_df['New Deaths'],
               marker_color='red',
               text=country_df['Text'],
               hoverinfo='text'),
        go.Bar(name='New Cases',
               x=country_df['Date'],
               y=country_df['New Cases'],
               marker_color='blue',
               text=country_df['Text'],
               hoverinfo='text')
    ]).update_layout(barmode='stack',
                      plot_bgcolor='white',
                      xaxis=dict(title='Date'),
                      yaxis=dict(title='Total'),
                      title=dict(text='Daily Cases and Deaths in ' + country_df['Country'].values[0],
                                 x=0.5),
                      legend=dict(x=0, y=1))


@app.callback(Output('output-totals_CS', 'children'),
              [Input('date--slider_CS', 'value'),
               Input('url', 'pathname')])
def update_totals_CS(day, pathname):
    country = pathname.strip('/')
    day_totals = cummulative_cases[
        (cummulative_cases['Date'] == dates[day]) &
        (cummulative_cases['Country'].map(lambda x: str(x).replace(' ', '')) == country)].sum()
    d = {'Total Cases': [f"{int(day_totals['Cases']):,}"],
              'Total Deaths': [f"{int(day_totals['Deaths']):,}"]}
    totals = pd.DataFrame.from_dict(d)
    table = Table(totals, None, None)
    return table


@app.callback(Output('slider-label_CS', 'children'),
              [Input('date--slider_CS', 'value')])
def show_date_CS(day):
    return str(dates[day])


@app.callback(Output('page-title_CS', 'children'),
              [Input('url', 'pathname')])
def update_header_CS(pathname):
    country = pathname.strip('/')
    country = cummulative_cases.loc[cummulative_cases['Country']\
                .map(lambda x: str(x).replace(' ', '')) == country, 'Country'].values[0]
    return "Tracking COVID-19 in " + str(country)
