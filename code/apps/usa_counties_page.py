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

df_US_c = pd.read_csv('../data/daily_cases_USA_counties.csv')
cummulative_cases = df_US_c.groupby(['Date', 'County', 'State', 'Code']).sum()[['Cases', 'Deaths']].reset_index()
dates = [x.replace('date_', '').replace('.csv', '') for x in os.listdir('../data/county_data/')]
dates = sorted(set([x for x in dates]))
county_dfs = [pd.read_csv(f'../data/county_data/{f}') for f in sorted(os.listdir('../data/county_data/'))]

state_lat_lon = pd.read_csv('../data/statelatlong.csv')

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
        html.Label(id='slider-label_C',
                   children='Loading...',
                   style=date_style_dict),

        dcc.Slider(
            id='date--slider_C',
            min=0,
            max=len(dates) - 1,
            value=len(dates) - 1,
            marks={i: str() for i in range(len(dates))},
            step=1
        ),

        dcc.Graph(id='indicator-graphic_C'),

        html.Div(id='output-totals_C',
                 style={'padding-left': '2%',
                        'padding-right': '2%',
                        'width': '30%'}),

        html.Div(id='output-data-upload_C',
            style=table_style)
    ])


@app.callback(
    Output('indicator-graphic_C', 'figure'),
    [Input('date--slider_C', 'value'),
     Input('url', 'pathname')])
def update_graph(day, pathname):
    state = pathname.strip('/')
    dff_US_c = county_dfs[day]
    # code = dff_US_c.loc[dff_US_c['State'].map(lambda x: str(x).replace(' ', '')) == state, 'Code'].values[0]
    dff_US_c['FIPS'] = dff_US_c['FIPS'].map(lambda x: '0' + str(x) if (len(str(x)) <= 4) else str(x))
    # dff_US_c = dff_US_c.loc[dff_US_c['Code'] == code]
    dff_US_c['County_'] = dff_US_c['County'].map(lambda x: x if 'parish' in x.lower() else x + ' County')
    dff_US_c.loc[:, 'Text'] = [f'<b>{w}, <b>{y}</b><br>{int(x):,} Cases<br>{int(z):,} Deaths' for w, x, y, z in \
                               zip(dff_US_c['County_'], dff_US_c['Cases'], dff_US_c['Code'], dff_US_c['Deaths'])]
    # state_code = dff_US_c.loc[dff_US_c['State'].map(lambda x: str(x).replace(' ','')) == state, 'Code'].values[0]
    # center_dict = {"lat": float(state_lat_lon.loc[state_lat_lon['State'] == state_code, 'Latitude'].values[0]),
    #                "lon": float(state_lat_lon.loc[state_lat_lon['State'] == state_code, 'Longitude'].values[0])}
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
        marker_line_width=0
    )).update_layout(
        mapbox_style='white-bg',
        mapbox_zoom=2.5,
        mapbox_center={"lat": 37.0902, "lon": -95.7129},
        geo_scope='usa',  # limit map scope to USA,
        geo={'fitbounds': 'locations'}
    )


@app.callback(Output('output-data-upload_C', 'children'),
              [Input('date--slider_C', 'value')])
def update_table_US(day):
    totals_US = county_dfs[day][['County', 'State', 'Cases', 'Deaths']] \
        .sort_values('Cases', ascending=False).reset_index(drop=True)
    totals_US['Cases'] = totals_US['Cases'].map(lambda x: f'{x:,}')
    totals_US['Deaths'] = totals_US['Deaths'].map(lambda x: f'{x:,}')
    totals_US = totals_US.loc[totals_US['State'].isna()==False,:]
    totals_US['Links'] = ['coronavirusmapsonline.com'+'/'+state+'/'+county+';'+'coronavirusmapsonline.com'+'/'+state\
                          for county,state in zip(totals_US['County'], totals_US['State'])]
    table_US = Table(totals_US, 'Links', 'County', 'State')
    return table_US

@app.callback(Output('output-totals_C', 'children'),
              [Input('date--slider_C', 'value')])
def update_totals_US(day_US):
    day_totals_US = cummulative_cases[cummulative_cases['Date'] == dates[day_US]].sum()
    d = {'Total Cases': [f"{day_totals_US['Cases']:,}"],
            'Total Deaths': [f"{day_totals_US['Deaths']:,}"]}
    totals = pd.DataFrame.from_dict(d)
    table = Table(totals)
    return table

@app.callback(Output('slider-label_C', 'children'),
              [Input('date--slider_C', 'value')])
def show_date_US(day):
    return str(dates[day])
