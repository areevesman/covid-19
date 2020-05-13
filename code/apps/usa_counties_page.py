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

location_colname_t = 'Country'
df_t = pd.read_csv('../data/world_data_with_codes.csv')
df_t[location_colname_t + '_'] = [x.replace(' ','').lower() for x in df_t[location_colname_t]]
cummulative_cases_t = df_t.groupby(['Date', location_colname_t]).sum()[['Cases', 'Deaths']].reset_index()
dates = sorted(set(df_t['Date']))
dates = [x for x in dates if x if x[0]=='2']


page, pathname=None, None
location_colname = 'County'
df_US_c = pd.read_csv('../data/daily_cases_USA_counties.csv')
cummulative_cases_us_county_page = df_US_c.groupby(['Date', location_colname, 'State', 'Code']).sum()[['Cases', 'Deaths']].reset_index()
# dates = [str(x).replace('date_', '').replace('.csv', '') for x in os.listdir('../data/county_data/')]
# dates = sorted(set([x for x in dates if x if x[0]=='2']))
county_dfs = [pd.read_csv(f'../data/county_data/date_{d}.csv') for d in dates]
# county_dfs = [pd.read_csv(f'../data/county_data/{f}') for f in sorted(os.listdir('../data/county_data/'))]


# state_lat_lon = pd.read_csv('../data/statelatlong.csv')

# location_colname = 'Country'
# page = 'any_country'
# df = pd.read_csv('../data/world_data_with_codes.csv')
# df[location_colname + '_'] = [x.replace(' ','').lower() for x in df[location_colname]]
# cummulative_cases = df.groupby(['Date', location_colname]).sum()[['Cases', 'Deaths']].reset_index()
# dates = sorted(set(df['Date']))

# page, pathname=None, None
# location_colname = 'County'
# df = pd.read_csv('../data/daily_cases_USA_states.csv')
# cummulative_cases = df.groupby(['Date', 'State', 'Day', 'Code'])\
#     .sum()[['Cases', 'Deaths']].reset_index()
# dates = sorted(set(df['Date']))
# states = [x for x in set(df[location_colname]) if str(x) != 'nan']

layout = html.Div(
    style={'backgroundColor': colors['background'],
           'padding-left': '2%',
           'padding-right': '2%'},
    children=header + [
        html.H1(id="page-title_C",
            children='Loading...',
            style={
                'textAlign': 'left',
                'color': colors['text']
            }
        ),

        search_bar,

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

        html.Div(id='output-totals_C',
                 style={'width': '30%'}),

        dcc.Graph(id='indicator-graphic_C'),

        html.Div(id='output-data-upload_C',
            style=table_style)
    ])


@app.callback(Output('indicator-graphic_C', 'figure'),
              [Input('date--slider_C', 'value')])
def update_graph(day):
    dff = county_dfs[day]
    dff['FIPS'] = dff['FIPS'].map(lambda x: '0' + str(x) if (len(str(x)) <= 4) else str(x))
    dff['County_'] = dff[location_colname].map(lambda x: x if 'parish' in x.lower() else x + ' County')
    dff.loc[:, 'Text'] = [f'<b>{w}, <b>{y}</b><br>{int(x):,} Cases<br>{int(z):,} Deaths' for w, x, y, z in \
                               zip(dff['County_'], dff['Cases'], dff['Code'], dff['Deaths'])]
    return go.Figure(data=go.Choroplethmapbox(
        locations=dff['FIPS'],  # Spatial coordinates
        geojson=counties,
        z=dff['Cases'].astype(float),  # Data to be color-coded
        zmin=0,
        zmax=cummulative_cases_us_county_page['Cases'].max() * 1.1,
        text=dff['Text'],
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
        geo={'fitbounds': 'locations'},
        title=dict(text='Total cases by county on ' + dates[day], x=.5))


@app.callback(Output('output-totals_C', 'children'),
              [Input('date--slider_C', 'value'),
               Input('url', 'pathname')])
def show_updated_totals(day, pathname):
  page='unitedstates-counties'
  return update_totals(day, pathname, cummulative_cases_t, location_colname_t, dates, page)

@app.callback(Output('output-data-upload_C', 'children'),
              [Input('date--slider_C', 'value')])
def show_data_table(day):
    page = 'counties'
    return data_table(day, None, cummulative_cases_us_county_page, dates, location_colname, county_dfs, page)

@app.callback(Output('slider-label_C', 'children'),
              [Input('date--slider_C', 'value')])
def show_date(day):
    return str(dates[day])

@app.callback(Output('page-title_C', 'children'),
              [Input('url', 'pathname')])
def show_updated_header(pathname):
    return "Tracking COVID-19 in the United States"
