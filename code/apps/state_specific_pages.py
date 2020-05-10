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


df = pd.read_csv('../data/daily_cases_USA_states.csv')
df['State_'] = [x.replace(' ','') for x in df['State']]

df_US_c = pd.read_csv('../data/daily_cases_USA_counties.csv')
cummulative_cases = df_US_c.groupby(['Date', 'County', 'State', 'Code']).sum()[['Cases', 'Deaths']].reset_index()
dates = [x.replace('date_', '').replace('.csv', '') for x in os.listdir('../data/county_data/')]
dates = sorted(set([x for x in dates]))
county_dfs = [pd.read_csv(f'../data/county_data/{f}') for f in sorted(os.listdir('../data/county_data/'))]

state_lat_lon = pd.read_csv('../data/statelatlong.csv')

layout = html.Div(
    style={'backgroundColor': colors['background']},
    children=header + [
        html.Br(),
        html.Br(),
        html.H1(id="page-title_US_c",
            children='Loading...',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),
        html.Label(id='slider-label_US_c',
                   children='Loading...',
                   style=date_style_dict),

        dcc.Slider(
            id='date--slider_US_c',
            min=0,
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

        dcc.Graph(id='totals-graph_US_c'),

        dcc.Graph(id='daily-graph_US_c'),

        html.Div(id='output-data-upload_US_c',
                 style={'padding-left': '2%',
                        'padding-right': '2%'}),
    ])


@app.callback(Output('totals-graph_US_c', 'figure'),
              [Input('date--slider_US_c', 'value'),
               Input('url', 'pathname')])
def total_cases_graph(day, pathname):
    country = pathname.strip('/')
    country_df = df[df['State_'] == country].reset_index(drop=True)[:day+1][-60:]
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
                      title=dict(text='Total Cases and Deaths in ' + country_df['State'].values[0],
                                 x=0.5),
                      legend=dict(x=0, y=1))


@app.callback(Output('daily-graph_US_c', 'figure'),
              [Input('date--slider_US_c', 'value'),
               Input('url', 'pathname')])
def daily_cases_graph(day, pathname):
    country = pathname.strip('/')
    country_df = df[df['State_'] == country].reset_index(drop=True)[:day+1][-60:]
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
                      title=dict(text='Daily Cases and Deaths in ' + country_df['State'].values[0],
                                 x=0.5),
                      legend=dict(x=0, y=1))


@app.callback(
    Output('indicator-graphic_US_c', 'figure'),
    [Input('date--slider_US_c', 'value'),
     Input('url', 'pathname')])
def update_graph(day, pathname):
    state = pathname.strip('/')
    dff_US_c = county_dfs[day]
    code = dff_US_c.loc[dff_US_c['State'].map(lambda x: str(x).replace(' ', '')) == state, 'Code'].values[0]
    state_ = dff_US_c.loc[dff_US_c['State'].map(lambda x: str(x).replace(' ', '')) == state, 'State'].values[0]
    dff_US_c['FIPS'] = dff_US_c['FIPS'].map(lambda x: '0' + str(x) if (len(str(x)) <= 4) else str(x))
    dff_US_c = dff_US_c.loc[dff_US_c['Code'] == code]
    dff_US_c.loc[:, 'Text'] = [f'<b>{w}</b><br>{int(x):,} Cases<br>{int(z):,} Deaths' for w, x, y, z in \
                               zip(dff_US_c['County'], dff_US_c['Cases'], dff_US_c['State'], dff_US_c['Deaths'])]
    state_code = dff_US_c.loc[dff_US_c['State'].map(lambda x: str(x).replace(' ','')) == state, 'Code'].values[0]
    center_dict = {"lat": float(state_lat_lon.loc[state_lat_lon['State'] == state_code, 'Latitude'].values[0]),
                   "lon": float(state_lat_lon.loc[state_lat_lon['State'] == state_code, 'Longitude'].values[0])}
    return go.Figure(data=go.Choroplethmapbox(
        locations=dff_US_c['FIPS'],  # Spatial coordinates
        geojson=counties,
        z=dff_US_c['Cases'].astype(float),  # Data to be color-coded
        zmin=0,
        zmax=cummulative_cases['Cases'].max() * 1.1,
        text=dff_US_c['Text'],
        hoverinfo='text',
        colorscale=[[0, "rgb(255, 250, 250)"],
                    [0.0001, "rgb(255, 200, 170)"],
                    [0.001, "rgb(255, 150, 120)"],
                    [0.01, "rgb(255, 100, 70)"],
                    [0.1, "rgb(255, 50, 20)"],
                    [1.0, "rgb(100, 0, 0)"]],
        colorbar_title="Total Cases",
    )).update_layout(
        mapbox_style='white-bg',
        mapbox_zoom=4,
        mapbox_center=center_dict,
        geo_scope='usa',  # limit map scope to USA,
        geo={'fitbounds': 'locations'},
        title=dict(text='Total cases by county in ' + \
                        state_ +
                        ' on ' + \
                        str(dates[day]),
                   x=0.5)
    )


@app.callback(Output('output-data-upload_US_c', 'children'),
              [Input('date--slider_US_c', 'value'),
               Input('url', 'pathname')])
def update_table(day, pathname):
    state = pathname.strip('/')
    totals = cummulative_cases \
        [((cummulative_cases['Date'] == dates[day])) & \
         (cummulative_cases['State'].map(lambda x: str(x).replace(' ','')) == state)] \
        .sort_values('Cases', ascending=False)[['County', 'Cases', 'Deaths','State']]
    totals['Cases'] = totals['Cases'].map(lambda x: f'{int(x):,}')
    totals['Deaths'] = totals['Deaths'].map(lambda x: f'{int(x):,}')
    # totals['Link'] = totals['County'].map(lambda x: 'localhost:8080' + '/' + x.replace(' ', ''))
    totals['Link'] = ['/' + state + '/' + county + ';' + '/' + state \
                          for county, state in zip(totals['County'], totals['State'])]
    table = Table(totals, link_column_name='Link', col1='County', col2='State', drop=['State'])
    return table


@app.callback(Output('output-totals_US_c', 'children'),
              [Input('date--slider_US_c', 'value'),
               Input('url', 'pathname')])
def update_totals(day, pathname):
    country = pathname.strip('/')
    day_totals = cummulative_cases[
        (cummulative_cases['Date'] == dates[day]) &
        (cummulative_cases['State'].map(lambda x: str(x).replace(' ', '')) == country)].sum()
    d = {'Total Cases': [f"{int(day_totals['Cases']):,}"],
              'Total Deaths': [f"{int(day_totals['Deaths']):,}"]}
    totals = pd.DataFrame.from_dict(d)
    table = Table(totals)
    return table


@app.callback(Output('slider-label_US_c', 'children'),
              [Input('date--slider_US_c', 'value')])
def show_date(day):
    return str(dates[day])


@app.callback(Output('page-title_US_c', 'children'),
              [Input('url', 'pathname')])
def update_header(pathname):
    country = pathname.strip('/')
    country = cummulative_cases.loc[cummulative_cases['State']\
                .map(lambda x: str(x).replace(' ', '')) == country, 'State'].values[0]
    return "Tracking COVID-19 in " + str(country)
