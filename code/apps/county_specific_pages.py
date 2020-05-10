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


df = pd.read_csv('../data/daily_cases_USA_counties.csv')
df['County_'] = [y.replace(' ','') + '/' + x.replace(' ','') for x,y in zip(df['County'], df['State'])]

cummulative_cases = df.groupby(['Date', 'County', 'State', 'Code']).sum()[['Cases', 'Deaths']].reset_index()
dates = [x.replace('date_', '').replace('.csv', '') for x in os.listdir('../data/county_data/')]
dates = sorted(set([x for x in dates]))
county_dfs = [pd.read_csv(f'../data/county_data/{f}') for f in sorted(os.listdir('../data/county_data/'))]

layout = html.Div(
    style={'backgroundColor': colors['background']},
    children=header + [
        html.Br(),
        html.Br(),
        html.H1(id="page-title_US_CS",
            children='Loading...',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),
        html.Label(id='slider-label_US_CS',
                   children='Loading...',
                   style=date_style_dict),

        dcc.Slider(
            id='date--slider_US_CS',
            min=0,
            max=len(dates) - 1,
            value=len(dates) - 1,
            marks={i: str() for i in range(len(dates))},
            step=1
        ),

        html.Div(id='output-totals_US_CS',
                 style={'padding-left': '2%',
                        'padding-right': '2%',
                        'width': '30%'}),

        dcc.Graph(id='totals-graph_US_CS'),

        dcc.Graph(id='daily-graph_US_CS'),
    ])


@app.callback(Output('totals-graph_US_CS', 'figure'),
              [Input('date--slider_US_CS', 'value'),
               Input('url', 'pathname')])
def total_cases_graph(day, pathname):
    country = pathname.strip('/')
    country_df = df[df['County_'] == country].reset_index(drop=True)[:day+1][-60:]
    country_df.loc[:, 'Text'] = [f'<b>{x}</b><br>{int(y):,} Cases<br>{int(z):,} Deaths' for x, y, z in \
                                 zip(country_df['Date'], country_df['Cases'], country_df['Deaths'])]
    if 'parish' in country_df['County'].values[0].lower():
        title = "Tracking COVID-19 in " + country_df['County'].values[0]
    else:
        title = "Tracking COVID-19 in " + country_df['County'].values[0] + ' County'

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
                      title=dict(text=title, x=0.5),
                      legend=dict(x=0, y=1))


@app.callback(Output('daily-graph_US_CS', 'figure'),
              [Input('date--slider_US_CS', 'value'),
               Input('url', 'pathname')])
def daily_cases_graph(day, pathname):
    country = pathname.strip('/')
    country_df = df[df['County_'] == country].reset_index(drop=True)[:day+1][-60:]
    c = country_df['Cases'].values
    d = country_df['Deaths'].values
    country_df['New Cases'] = [c[0]] + list(c[1:] - c[:-1])
    country_df['New Deaths'] = [d[0]] + list(d[1:] - d[:-1])
    country_df.loc[:, 'Text'] = [f'<b>{x}</b><br>{int(y):,} New Cases<br>{int(z):,} New Deaths' for x, y, z in \
                                 zip(country_df['Date'], country_df['New Cases'], country_df['New Deaths'])]
    if 'parish' in country_df['County'].values[0].lower():
        title = "Tracking COVID-19 in " + country_df['County'].values[0]
    else:
        title = "Tracking COVID-19 in " + country_df['County'].values[0] + ' County'

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
                      title=dict(text=title, x=0.5),
                      legend=dict(x=0, y=1))


@app.callback(Output('output-totals_US_CS', 'children'),
              [Input('date--slider_US_CS', 'value'),
               Input('url', 'pathname')])
def update_totals(day_US_c, pathname):
    county = pathname.split('/')[2]
    day_totals_US_c = cummulative_cases[(cummulative_cases['Date'] == dates[day_US_c]) &\
                                        (cummulative_cases['County']\
            .map(lambda x: str(x).replace(' ','')) == county)].sum()
    d = {'Cases': [f"{int(day_totals_US_c['Cases']):,}"],
              'Deaths': [f"{int(day_totals_US_c['Deaths']):,}"]}
    totals = pd.DataFrame.from_dict(d)
    table = Table(totals)
    return table


@app.callback(Output('slider-label_US_CS', 'children'),
              [Input('date--slider_US_CS', 'value')])
def show_date_CS(day):
    return str(dates[day])


@app.callback(Output('page-title_US_CS', 'children'),
              [Input('url', 'pathname')])
def update_header_CS(pathname):
    county = pathname.split('/')[2]
    county = cummulative_cases.loc[cummulative_cases['County']\
                .map(lambda x: str(x).replace(' ', '')) == county, 'County'].values[0]
    if 'parish' in county.lower():# | 'county' in county.lower():
        return "Tracking COVID-19 in " + str(county)
    else:
        return "Tracking COVID-19 in " + str(county) + ' County'
