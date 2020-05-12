import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from urllib.request import urlopen
import json
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import os
import flask



with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

date_style_dict = {
    'textAlign': 'center',
    'color': colors['text'],
    'fontSize': "18px"
}

table_style = {'padding-left': '2%',
               'padding-right': '2%'}

baseURL = 'http://coronavirusmapsonline.com'
header = [
    dcc.Link(
        html.Button('Cases by Country',
                    className='three columns',
                    style={
                        'textAlign': 'center',
                        'color': colors['text']
                    }),
        href=baseURL + '/'),
    dcc.Link(
        html.Button('Cases by US State',
                    className='three columns',
                    style={
                        'textAlign': 'center',
                        'color': colors['text']
                    }),
        href=baseURL + '/States'),
    dcc.Link(
        html.Button('Cases by US County',
                    className='three columns',
                    style={
                        'textAlign': 'center',
                        'color': colors['text']
                    }),
        href=baseURL + '/Counties'),
    dcc.Link(
        html.Button('About',
                    className='three columns',
                    style={
                        'textAlign': 'center',
                        'color': colors['text']
                    }),
        href=baseURL + '/About')]


def Table(dataframe, link_column_name=None, col1=None, col2=None, drop=[]):
    if link_column_name:
        if col2:
            links1 = dataframe[link_column_name] \
                .map(lambda x: x.replace(' ', '').split(';')[0]).values
            links2 = dataframe[link_column_name] \
                .map(lambda x: x.replace(' ', '').split(';')[1]).values
        else:
            links1 = dataframe[link_column_name] \
                .map(lambda x: x.replace(' ', '')).values
    rows = []
    for i in range(len(dataframe)):
        row = []
        for col in dataframe.columns:
            if (col in [link_column_name] + drop) is False:
                value = dataframe.iloc[i][col]
                if col in [col1, col2]:
                    if col == col2:
                        cell = html.Td(dcc.Link(href=baseURL + links2[i], children=value))
                    else:
                        cell = html.Td(dcc.Link(href=baseURL + links1[i], children=value))
                else:
                    cell = html.Td(children=value)
                row.append(cell)
        rows.append(html.Tr(row,
                            style={
                                # 'text-align': 'center',
                                #    'border': '2px',
                                #    'background-color': '#111111',
                                'color': '#7FDBFF',
                                # 'width': '100%',
                                'fontSize': '18px',
                            }))
    return html.Table(
        # Header
        [html.Tr([html.Th(col,
                          style={
                              'background-color': '#111111',
                              'color': '#7FDBFF',
                              # 'width': '50%',
                              'fontSize': '20px',
                          }) \
                  for col in dataframe.columns if (col in [link_column_name] + drop) is False])] + \
        rows,
        style={'width':'100%',
               # 'text-align':'center',
               }
    )

### Callback functions

def total_cases_graph(day, pathname, df, location_colname, dates):
    location = pathname.strip('/').lower()
    location_df = df[df[location_colname + '_'] == location].reset_index(drop=True)
    location_df.loc[:, 'Text'] = [f'<b>{x}</b><br>{int(y):,} Cases<br>{int(z):,} Deaths' for x, y, z in \
                                 zip(location_df['Date'], location_df['Cases'], location_df['Deaths'])]
    xrange = [dates[0], str(datetime.strptime(dates[-1], "%Y-%m-%d") + timedelta(days=1))]
    df1 = location_df.loc[location_df['Date'] <= dates[day],:]
    df2 = location_df.loc[location_df['Date'] > dates[day],:]
    yrange = [0, df1['Cases'].max()]
    show_legend_2 = False
    if len(df2) > 0:
        show_legend_2 = True
    return go.Figure(data=[
        go.Bar(name='Deaths',
               x=df1['Date'],
               y=df1['Deaths'],
               marker_color='red',
               text=df1['Text'],
               hoverinfo='text'),
        go.Bar(name='Cases',
               x=df1['Date'],
               y=df1['Cases'] - df1['Deaths'],
               marker_color='blue',
               text=df1['Text'],
               hoverinfo='text'),
        go.Bar(name='Deaths',
               x=df2['Date'],
               y=df2['Deaths'],
               marker_color='red',
               text=df2['Text'],
               hoverinfo='text',
               opacity=.4,
               showlegend=show_legend_2),
        go.Bar(name='Cases',
               x=df2['Date'],
               y=df2['Cases'] - df2['Deaths'],
               marker_color='blue',
               text=df2['Text'],
               hoverinfo='text',
               opacity=.4,
               showlegend=show_legend_2)
    ]).update_layout(barmode='stack',
                     plot_bgcolor='white',
                     xaxis=dict(title='Date', range=xrange),
                     yaxis=dict(title='Total', range=yrange),
                     title=dict(text='Total Cases and Deaths in ' + location_df[location_colname].values[0],
                                x=0.5),
                     legend=dict(x=0, y=1))


def daily_cases_graph(day, pathname, df, location_colname, dates):
    location = pathname.strip('/').lower()
    location_df = df[df[location_colname + '_'] == location].reset_index(drop=True)
    c = location_df['Cases'].values
    d = location_df['Deaths'].values
    location_df['New Cases'] = [c[0]] + list(c[1:] - c[:-1])
    location_df['New Deaths'] = [d[0]] + list(d[1:] - d[:-1])
    location_df.loc[:, 'Text'] = [f'<b>{x}</b><br>{int(y):,} New Cases<br>{int(z):,} New Deaths' for x, y, z in \
                                 zip(location_df['Date'], location_df['New Cases'], location_df['New Deaths'])]
    df1 = location_df.loc[location_df['Date'] <= dates[day],:]
    df2 = location_df.loc[location_df['Date'] > dates[day],:]
    yrange = [0, df1['New Cases'].max()]
    show_legend_2 = False
    if len(df2) > 0:
        show_legend_2 = True
    xrange = [dates[0], str(datetime.strptime(dates[-1], "%Y-%m-%d") + timedelta(days=1))]
    return go.Figure(data=[
        go.Bar(name='New Deaths',
               x=df1['Date'],
               y=df1['New Deaths'],
               marker_color='red',
               text=df1['Text'],
               hoverinfo='text'),
        go.Bar(name='New Cases',
               x=df1['Date'],
               y=df1['New Cases'],
               marker_color='blue',
               text=df1['Text'],
               hoverinfo='text'),
        go.Bar(name='New Deaths',
               x=df2['Date'],
               y=df2['New Deaths'],
               marker_color='red',
               text=df2['Text'],
               hoverinfo='text',
               opacity=.4,
               showlegend=show_legend_2),
        go.Bar(name='New Cases',
               x=df2['Date'],
               y=df2['New Cases'],
               marker_color='blue',
               text=df2['Text'],
               hoverinfo='text',
               opacity=.4,
               showlegend=show_legend_2)
    ]).update_layout(barmode='stack',
                      plot_bgcolor='white',
                      xaxis=dict(title='Date', range=xrange),
                      yaxis=dict(title='Total', range=yrange),
                      title=dict(text='Daily Cases and Deaths in ' + location_df[location_colname].values[0],
                                 x=0.5),
                      legend=dict(x=0, y=1))


def state_county_choropleth(day, pathname, county_dfs, location_colname, location_lat_lon, dates, cummulative_cases):
    location = pathname.strip('/').lower()
    dff = county_dfs[day]
    code = dff.loc[dff[location_colname].map(lambda x: str(x).replace(' ', '').lower()) == location, 'Code'].values[0]
    location_ = dff.loc[dff[location_colname].map(lambda x: str(x).replace(' ', '').lower()) == location, location_colname].values[0]
    dff['FIPS'] = dff['FIPS'].map(lambda x: '0' + str(x) if (len(str(x)) <= 4) else str(x))
    dff = dff.loc[dff['Code'] == code]
    dff.loc[:, 'Text'] = [f'<b>{w}</b><br>{int(x):,} Cases<br>{int(z):,} Deaths' for w, x, y, z in \
                               zip(dff['County'], dff['Cases'], dff[location_colname], dff['Deaths'])]
    location_code = dff.loc[dff[location_colname].map(lambda x: str(x).replace(' ','').lower()) == location, 'Code'].values[0]
    center_dict = {"lat": float(location_lat_lon.loc[location_lat_lon[location_colname] == location_code, 'Latitude'].values[0]),
                   "lon": float(location_lat_lon.loc[location_lat_lon[location_colname] == location_code, 'Longitude'].values[0])}
    return go.Figure(data=go.Choroplethmapbox(
        locations=dff['FIPS'],  # Spatial coordinates
        geojson=counties,
        z=dff['Cases'].astype(float),  # Data to be color-coded
        zmin=0,
        zmax=cummulative_cases['Cases'].max() * 1.1,
        text=dff['Text'],
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
                        location_ +
                        ' on ' + \
                        str(dates[day]),
                   x=0.5))


def data_table(day=None, pathname=None, cummulative_cases=None,
               dates=None, location_colname=None, county_dfs=None, page=None):
    if pathname:
        location = pathname.strip('/').lower()
        totals = cummulative_cases \
            [((cummulative_cases['Date'] == dates[day])) & \
             (cummulative_cases[location_colname].map(lambda x: str(x).replace(' ', '').lower()) == location)] \
            .sort_values('Cases', ascending=False)[['County', 'Cases', 'Deaths', location_colname]]
        totals['Cases'] = totals['Cases'].map(lambda x: f'{int(x):,}')
        totals['Deaths'] = totals['Deaths'].map(lambda x: f'{int(x):,}')
        if page == 'any_state':
            totals['Link'] = [('/' + location + '/' + county + ';' + '/' + location).lower() \
                              for county, location in zip(totals['County'], totals[location_colname])]
            table = Table(totals, link_column_name='Link', col1='County', col2=location_colname, drop=[location_colname])
            return table
    elif page == 'states':
        totals = cummulative_cases[cummulative_cases['Date'] == dates[day]][['State', 'Cases', 'Deaths']] \
            .sort_values('Cases', ascending=False)
        totals['Cases'] = totals['Cases'].map(lambda x: f'{x:,}')
        totals['Deaths'] = totals['Deaths'].map(lambda x: f'{x:,}')
        totals['Links'] = ['/' + state for state in totals['State']]
        table_US = Table(totals, 'Links', 'State')
        return table_US
    elif page == 'counties':
        totals_US = county_dfs[day][['County', 'State', 'Cases', 'Deaths']] \
            .sort_values('Cases', ascending=False).reset_index(drop=True)
        totals_US['Cases'] = totals_US['Cases'].map(lambda x: f'{x:,}')
        totals_US['Deaths'] = totals_US['Deaths'].map(lambda x: f'{x:,}')
        totals_US = totals_US.loc[totals_US['State'].isna() == False, :]
        totals_US['Links'] = ['/' + state + '/' + county + ';' + '/' + state \
                              for county, state in zip(totals_US['County'], totals_US['State'])]
        table_US = Table(totals_US, 'Links', 'County', 'State')
        return table_US
    elif page == 'world':
        totals = cummulative_cases[cummulative_cases['Date'] == dates[day]][['Country', 'Cases', 'Deaths']] \
            .sort_values('Cases', ascending=False)
        totals['Cases'] = totals['Cases'].map(lambda x: f'{x:,}')
        totals['Deaths'] = totals['Deaths'].map(lambda x: f'{x:,}')
        totals['Link'] = totals['Country'].map(lambda x: '/' + x.replace(' ', ''))
        table = Table(totals, link_column_name='Link', col1='Country')
        return table


def update_header(pathname, cummulative_cases, location_colname, page):
    if page == 'any_county':
        location = pathname.split('/')[2].lower()
        location = cummulative_cases\
            .loc[cummulative_cases[location_colname]\
            .map(lambda x: str(x).replace(' ', '').lower()) == location, location_colname].values[0]
        if 'parish' in location.lower():
            return "Tracking COVID-19 in " + str(location)
        else:
            return "Tracking COVID-19 in " + str(location) + ' County'
    else:
        if page in ['any_state', 'any_country']:
            location = pathname.strip('/').lower()
            location = cummulative_cases\
                .loc[cummulative_cases[location_colname]\
                .map(lambda x: str(x).replace(' ', '').lower()) == location, location_colname].values[0]
            return "Tracking COVID-19 in " + str(location)


def update_totals(day, pathname, cummulative_cases, location_colname, dates, page):
    if page in ['any_county', 'any_state', 'any_country']:
        if page == 'any_county':
            location = pathname.split('/')[2].lower()
        else:
            location = pathname.strip('/').lower()
        day_totals = cummulative_cases[
            (cummulative_cases['Date'] == dates[day]) &
            (cummulative_cases[location_colname].map(lambda x: str(x).replace(' ', '').lower()) == location)].sum()
        d = {'Total Cases': [f"{int(day_totals['Cases']):,}"],
              'Total Deaths': [f"{int(day_totals['Deaths']):,}"]}
    else:
        day_totals = cummulative_cases[cummulative_cases['Date'] == dates[day]].sum()
        d = {'Total Cases': [f"{day_totals['Cases']:,}"],
             'Total Deaths': [f"{day_totals['Deaths']:,}"]}
    totals = pd.DataFrame.from_dict(d)
    table = Table(totals)
    return table
