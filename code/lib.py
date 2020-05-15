import pandas as pd
import numpy as np
import os
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from datetime import datetime, timedelta
from urllib.request import urlopen
import json
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import flask

from app import app


def Table(dataframe, link_column_name=None, col1=None, col2=None, drop=[]):
    """Create a table with links in columns"""
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
                        cell = html.Td(dcc.Link(href=links2[i], children=value))
                    else:
                        cell = html.Td(dcc.Link(href=links1[i], children=value))
                else:
                    cell = html.Td(children=value)
                row.append(cell)
        rows.append(html.Tr(row,
                            style={
                                'color': '#7FDBFF',
                                'fontSize': '18px',
                            }))
    return html.Table(
        # Header
        [html.Tr([html.Th(col,
                          style={
                              'background-color': '#111111',
                              'color': '#7FDBFF',
                              'fontSize': '20px',
                          }) \
                  for col in dataframe.columns if (col in [link_column_name] + drop) is False])] + \
        rows,
        style={'width':'100%'}
    )


def total_cases_graph(day, pathname, df, location_colname, dates, dates2=None):
    if not dates2:
        dates2 = dates
    try:
        location = pathname \
            .replace('/countries', '') \
            .replace('/states', '') \
            .replace(' ', '') \
            .strip('/') \
            .lower()
        if location in ['']:  # world_page
            location_df = df.groupby(['Date']).sum()[['Cases', 'Deaths']].reset_index()
            l = 'globally'
        else:
            # any county
            if len(pathname) - len(pathname.replace('/', '')) > 2:
                location = pathname.split('/')[3].lower()
                s = pathname.split('/')[2].lower()
                df[location_colname + '_'] = [x.replace(' ', '').lower() for x in df[location_colname]]
                df['State_'] = df['State'].map(lambda x: str(x).replace(' ', '').lower())
                location_df = df[(df[location_colname + '_'] == location) & (df['State_'] == s)]\
                        .reset_index(drop=True)
            # any state
            elif pathname[:7] == '/states':
                location_colname = 'State'
                location = pathname.split('/')[2].lower()
                df[location_colname + '_'] = [str(x).replace(' ', '').lower() for x in df[location_colname]]
                location_df = df[df[location_colname + '_'] == location] \
                    .reset_index(drop=True)
            # any country
            elif pathname[:7] == '/countr':
                location_colname = 'Country'
                location = pathname.split('/')[2].lower()
                df[location_colname + '_'] = [str(x).replace(' ', '').lower() for x in df[location_colname]]
                location_df = df[df[location_colname + '_'] == location] \
                    .reset_index(drop=True)
            if len(location_df) > 0:
                l_ = location_df[location_colname].values[0]
                if l_[:6].lower() == 'united':
                    l = 'in the ' + l_
                else:
                    l = 'in ' + l_
        location_df.loc[:, 'Text'] = [f'<b>{x}</b><br>{int(y):,} Cases<br>{int(z):,} Deaths' for x, y, z in \
                                     zip(location_df['Date'], location_df['Cases'], location_df['Deaths'])]
        df1 = location_df.loc[location_df['Date'] <= dates[day],:]
        df2 = location_df.loc[location_df['Date'] > dates[day],:]
        yrange = [0, max(50,df1['Cases'].max())]
        xrange = [dates[0], str(datetime.strptime(dates[-1], "%Y-%m-%d") + timedelta(days=2))]
        show_legend_2 = False
        if len(df2) > 0:
            if len(dates2) != len(dates):
               show_legend_2 = True
        return go.Figure(data=[
            go.Bar(name='Deaths', x=df1['Date'], y=df1['Deaths'],
                   marker_color='red', text=df1['Text'], hoverinfo='text'),
            go.Bar(name='Cases', x=df1['Date'], y=df1['Cases'] - df1['Deaths'],
                   marker_color='blue', text=df1['Text'], hoverinfo='text'),
            go.Bar(name='Deaths', x=df2['Date'], y=df2['Deaths'],
                   marker_color='red', text=df2['Text'],
                   hoverinfo='text', opacity=.4, showlegend=show_legend_2),
            go.Bar(name='Cases', x=df2['Date'], y=df2['Cases'] - df2['Deaths'],
                   marker_color='blue', text=df2['Text'], hoverinfo='text',
                   opacity=.4, showlegend=show_legend_2)
        ]).update_layout(barmode='stack',
                         plot_bgcolor='white',
                         xaxis=dict(title='Date', range=xrange),
                         yaxis=dict(title='Total', range=yrange),
                         title=dict(text='Total cases and deaths ' + l, x=0.5),
                         legend=dict(x=0, y=1))
    except:
        return go.Figure()


def daily_cases_graph(day, pathname, df, location_colname, dates, dates2=None):
    if not dates2:
        dates2 = dates
    try:
        location = pathname \
            .replace('/countries', '') \
            .replace('/states', '')\
            .replace(' ','')\
            .strip('/') \
            .lower()
        if location == '':  # world_page
            location_df = df.groupby(['Date']).sum()[['Cases', 'Deaths']].reset_index()
            l = 'globally'
        else:
            # any county
            if len(pathname) - len(pathname.replace('/', '')) > 2:
                location = pathname.split('/')[3].lower()
                s = pathname.split('/')[2].lower()
                df[location_colname + '_'] = [x.replace(' ', '').lower() for x in df[location_colname]]
                df['State_'] = df['State'].map(lambda x: str(x).replace(' ', '').lower())
                location_df = df[(df[location_colname + '_'] == location) & (df['State_'] == s)] \
                    .reset_index(drop=True)
            # any state
            elif pathname[:7] == '/states':
                location_colname = 'State'
                location = pathname.split('/')[2].lower()
                df[location_colname + '_'] = [str(x).replace(' ', '').lower() for x in df[location_colname]]
                location_df = df[df[location_colname + '_'] == location] \
                    .reset_index(drop=True)
            # any country
            elif pathname[:7] == '/countr':
                location_colname = 'Country'
                location = pathname.split('/')[2].lower()
                df[location_colname + '_'] = [str(x).replace(' ', '').lower() for x in df[location_colname]]
                location_df = df[df[location_colname + '_'] == location] \
                    .reset_index(drop=True)
            if len(location_df) > 0:
                l_ = location_df[location_colname].values[0]
                if l_[:6].lower() == 'united':
                    l = 'in the ' + l_
                else:
                    l = 'in ' + l_
        # after getting l and location_df, plot
        c = location_df['Cases'].values
        d = location_df['Deaths'].values
        location_df['New Cases'] = [c[0]] + list(c[1:] - c[:-1])
        location_df['New Deaths'] = [d[0]] + list(d[1:] - d[:-1])
        location_df.loc[:, 'Text'] = [f'<b>{x}</b><br>{int(y):,} New Cases<br>{int(z):,} New Deaths' for x, y, z in \
                                      zip(location_df['Date'], location_df['New Cases'], location_df['New Deaths'])]
        df1 = location_df.loc[location_df['Date'] <= dates[day], :]
        df2 = location_df.loc[location_df['Date'] > dates[day], :]
        yrange = [0, max(5, df1['New Cases'].max())]
        xrange = [dates[0], str(datetime.strptime(dates[-1], "%Y-%m-%d") + timedelta(days=2))]
        show_legend_2 = False
        if len(df2) > 0:
            if len(dates2) != len(dates):
                show_legend_2 = True
        return go.Figure(data=[
            go.Bar(name='New Deaths', x=df1['Date'], y=df1['New Deaths'],
                   marker_color='red', text=df1['Text'], hoverinfo='text'),
            go.Bar(name='New Cases', x=df1['Date'], y=df1['New Cases'],
                   marker_color='blue', text=df1['Text'], hoverinfo='text'),
            go.Bar(name='New Deaths', x=df2['Date'], y=df2['New Deaths'],
                   marker_color='red', text=df2['Text'],
                   hoverinfo='text', opacity=.4, showlegend=show_legend_2),
            go.Bar(name='New Cases', x=df2['Date'], y=df2['New Cases'],
                   marker_color='blue', text=df2['Text'], hoverinfo='text',
                   opacity=.4, showlegend=show_legend_2)
        ]).update_layout(barmode='stack', plot_bgcolor='white',
                         xaxis=dict(title='Date', range=xrange),
                         yaxis=dict(title='Total', range=yrange),
                         title=dict(text='Daily cases and deaths ' + l, x=0.5),
                         legend=dict(x=0, y=1))
    except:
        return go.Figure()

def data_table(day=None, pathname=None, cummulative_cases=None,
               dates=None, location_colname=None):
    try:
        if pathname != '/':
            if pathname.lower()[:7] == '/states':
                if len(pathname) - len(pathname.replace('/', '')) <= 2:
                    location_colname = 'County'
                    location = pathname\
                        .lower()\
                        .replace(' ', '')\
                        .replace('/countries', '') \
                        .replace('/states', '') \
                        .strip('/')
                    cummulative_cases['State_'] = cummulative_cases['State'].map(lambda x: str(x).replace(' ', '').lower())
                    cummulative_cases['County_'] = cummulative_cases['County'].map(lambda x: str(x).replace(' ', '').lower())
                    totals = cummulative_cases[
                        (cummulative_cases['Date'] == dates[day]) &\
                        (cummulative_cases['State_'] == location)][['State_', 'County_', 'County', 'Cases', 'Deaths']] \
                        .sort_values('Cases', ascending=False)
                    totals['Cases'] = totals['Cases'].map(lambda x: f'{x:,}')
                    totals['Deaths'] = totals['Deaths'].map(lambda x: f'{x:,}')
                    totals['Links'] = ['/states/' + state + '/' + county \
                                       for state, county in zip(totals['State_'], totals['County_'])]
                    totals = totals.drop(['State_', 'County_'], axis=1)

            elif pathname.lower() == '/countries/unitedstates-counties':
                location_colname = 'County'
                location = 'unitedstates'
                cummulative_cases['State_'] = cummulative_cases['State'].map(lambda x: str(x).replace(' ', '').lower())
                cummulative_cases['County_'] = cummulative_cases['County'].map(
                    lambda x: str(x).replace(' ', '').lower())
                totals = cummulative_cases[cummulative_cases['Date'] == dates[day]][['State_','County_', 'State', 'County', 'Cases', 'Deaths']] \
                    .sort_values('Cases', ascending=False)
                totals['Cases'] = totals['Cases'].map(lambda x: f'{x:,}')
                totals['Deaths'] = totals['Deaths'].map(lambda x: f'{x:,}')
                totals['Links'] = ['/states/' + state + \
                                   ';/states/' + state + '/' + county
                                   for state, county in zip(totals['State_'], totals['County_'])]
                totals = totals.drop(['State_', 'County_'], axis=1)
                table = Table(totals, 'Links', 'State', 'County')
                return table
            elif pathname.lower() == '/countries/unitedstates':
                location_colname = 'State'
                cummulative_cases['State_'] = cummulative_cases['State'].map(lambda x: str(x).replace(' ', '').lower())
                totals = cummulative_cases[cummulative_cases['Date'] == dates[day]][['State_', 'State', 'Cases', 'Deaths']]\
                    .sort_values('Cases', ascending=False)
                totals['Cases'] = totals['Cases'].map(lambda x: f'{x:,}')
                totals['Deaths'] = totals['Deaths'].map(lambda x: f'{x:,}')
                totals['Links'] = ['/states/' + state \
                                   for state in totals['State_']]
                totals = totals.drop(['State_'], axis=1)
            table_US = Table(totals, 'Links', location_colname)
            return table_US
        else:
            totals = cummulative_cases[cummulative_cases['Date'] == dates[day]][['Country', 'Cases', 'Deaths']] \
                .sort_values('Cases', ascending=False)
            totals['Cases'] = totals['Cases'].map(lambda x: f'{x:,}')
            totals['Deaths'] = totals['Deaths'].map(lambda x: f'{x:,}')
            totals['Link'] = totals['Country'].map(lambda x: '/countries/' + x.replace(' ', ''))
            table = Table(totals, link_column_name='Link', col1='Country')
            return table
    except:
        return



def update_header(pathname, cummulative_cases, location_colname):
    try:
        if len(pathname) - len(pathname.replace('/','')) > 2:
            location_colname = 'County'
            location = pathname.split('/')[3].lower()
            location = cummulative_cases\
                .loc[cummulative_cases[location_colname]\
                .map(lambda x: str(x).replace(' ', '').lower()) == location, location_colname].values[0]
            if 'parish' in location.lower():
                return "Tracking COVID-19 in " + str(location)
            else:
                return "Tracking COVID-19 in " + str(location) + ' County'
        elif pathname == '/countries/unitedstates-counties':
            location = 'unitedstates'
            location_colname = 'County'
            location = cummulative_cases \
                .loc[cummulative_cases[location_colname] \
                         .map(lambda x: str(x).replace(' ', '').lower()) == location, location_colname].values[0]
            if location.lower()[:6] == 'united':
                return "Tracking COVID-19 in the " + str(location)
            return "Tracking COVID-19 in " + str(location)
        else:
            if pathname[:7] in ['/states', '/countr']:
                if pathname[:7] == '/states':
                    location_colname = 'State'
                else:
                    location_colname = 'Country'
                location = pathname \
                    .replace('/countries', '') \
                    .replace('/states', '') \
                    .strip('/')\
                    .lower()
                location = cummulative_cases\
                    .loc[cummulative_cases[location_colname]\
                    .map(lambda x: str(x).replace(' ', '').lower()) == location, location_colname].values[0]
                if location.lower()[:6] == 'united':
                    return "Tracking COVID-19 in the " + str(location)
                return "Tracking COVID-19 in " + str(location),
    except:
        return "Tracking COVID-19"


def update_totals(day, pathname, cummulative_cases, location_colname, dates):
    try:
        if pathname:
            if pathname.lower()[:6] in ['/state','/count']:
                if len(pathname) - len(pathname.replace('/','')) > 2:
                    location = pathname.split('/')[3].lower()
                    location_colname = 'County'
                elif pathname.lower() == '/countries/unitedstates-counties':
                    location = 'unitedstates'
                    location_colname = 'Country'
                elif pathname.lower()[:7] == '/countr':
                    location = pathname \
                        .replace('/countries', '') \
                        .replace('/states', '') \
                        .strip('/') \
                        .lower()
                    location_colname = 'Country'
                else:
                    location = pathname\
                        .replace('/countries','')\
                        .replace('/states','')\
                        .strip('/')\
                        .lower()
                    location_colname = 'State'
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
    except:
        return

def state_county_choropleth(day, pathname, county_dfs, location_colname, location_lat_lon, dates, cummulative_cases):
    try:
        if len(pathname) - len(pathname.replace('/','')) > 2:
            return go.Figure()
        location = pathname \
            .replace('/countries', '') \
            .replace('/states', '') \
            .strip('/')\
            .lower()
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
                            str(dates[day]), x=0.5))
    except:
        return go.Figure()


def create_dropdown_options(world_data, county_data):
    """Create options for dropdown menu from input data"""
    world_dropdown_choices = sorted(set(world_data['Country']))
    state_dropdown_choices = sorted(set(county_data['State'][county_data['State'].isna() == False]))
    combinations = sorted(set(zip(county_data['State'][county_data['State'].isna() == False],
                                  county_data['County'][county_data['State'].isna() == False])))
    county_dropdown_labels = [s + ' - ' + c for s, c in combinations if str(s) not in ['nan', '']]
    county_dropdown_values = ['/states/' + c.replace(' ', '').lower() + '/' + s.replace(' ', '').lower() \
                              for c, s in combinations]
    top_options = [{'label': 'Global Cases', 'value': '/' },
                 {'label': 'United States - by State', 'value': '/countries/unitedstates'},
                 {'label': 'United States - by County', 'value': '/countries/unitedstates-counties'}]
    country_options = [{'label': location, 'value': '/countries/' + location.replace(' ', '').lower()} \
                 for location in world_dropdown_choices]
    state_options = [{'label': location, 'value': '/states/' + location.replace(' ', '').lower()} \
                 for location in state_dropdown_choices]
    county_options = [{'label': l, 'value': v} \
                 for l, v in zip(county_dropdown_labels, county_dropdown_values)]
    dropdown_options = top_options + country_options + state_options + county_options
    return dropdown_options

def create_search_bar(dropdown_options, dropdown_style, dropdown_id):
    """Create a dash dropdown menu with choices given"""
    return dcc.Dropdown(
            id=dropdown_id,
            options=dropdown_options,
            placeholder="Jump to a country/state/county (search or select)",
            searchable=True,
            clearable=True,
            style=dropdown_style)


## Styles
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}
date_style_dict = {
    'textAlign': 'center',
    'color': colors['text'],
    'fontSize': "18px"
}
table_style = {}
baseURL = 'http://coronavirusmapsonline.com'
header = []


## Data
world_data = pd.read_csv('../data/world_data_with_codes.csv')
state_data = pd.read_csv('../data/daily_cases_USA_states.csv')
county_data = pd.read_csv('../data/daily_cases_USA_counties.csv')

dates = [str(x).replace('date_', '').replace('.csv', '') \
         for x in os.listdir('../data/county_data/')]
dates = sorted(set([x for x in dates if x if x[0]=='2']))
county_data_by_date = [pd.read_csv(f'../data/county_data/date_{d}.csv') for d in dates]
location_lat_lon = pd.read_csv('../data/statelatlong.csv')

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)


## Search bar / Dropdown
dropdown_style = {
    'padding-left': '0%',
    'padding-right': '0%',
    'width': '60%'
}
dropdown_id = 'location-dropdown'
dropdown_options = create_dropdown_options(world_data, county_data)
search_bar = create_search_bar(dropdown_options=dropdown_options,
                               dropdown_style=dropdown_style,
                               dropdown_id=dropdown_id)

@app.callback(Output(component_id='url', component_property='pathname'),
              [Input(component_id=dropdown_id, component_property='value')])
def link_to_choice(dropdown_value):
    """"Update the URL with the value from dropdown selection"""
    return dropdown_value


# world_page
world_page_entities = 'Country'
world_page_df = world_data.copy()
world_page_df_grouped = world_page_df\
        .groupby(['Date', world_page_entities])\
        .sum()[['Cases', 'Deaths']]\
        .reset_index()
world_page_dates = sorted(set(world_page_df['Date']))


# # usa counties page
# world_page_entities = 'Country'
# world_page_df = world_data.copy()
# world_page_df_grouped = world_page_df\
#         .groupby(['Date', world_page_entities])\
#         .sum()[['Cases', 'Deaths']]\
#         .reset_index()
# world_page_dates = sorted(set(world_page_df['Date']))

usa_county_page_entities = 'County'
usa_county_page_df = pd.read_csv('../data/daily_cases_USA_counties.csv')
usa_county_page_dates = [str(x).replace('date_', '').replace('.csv', '') for x in os.listdir('../data/county_data/')]
usa_county_page_dates = sorted(set([x for x in usa_county_page_dates if x if x[0]=='2']))
usa_county_page_county_dfs = [x.copy() for x in county_data_by_date]
usa_county_page_df_grouped = usa_county_page_df.groupby(['Date', usa_county_page_entities, 'State', 'Code']).sum()[['Cases', 'Deaths']].reset_index()
county_dfs = [pd.read_csv(f'../data/county_data/date_{d}.csv') for d in usa_county_page_dates]


# usa states page
# world_page_entities = 'Country'
# world_page_df = world_data.copy()
# world_page_df_grouped = world_page_df\
#         .groupby(['Date', world_page_entities])\
#         .sum()[['Cases', 'Deaths']]\
#         .reset_index()
# world_page_dates = sorted(set(world_page_df['Date']))

state_page_df = state_data.copy()
state_page_df_grouped = state_page_df.groupby(['Date', 'State', 'Day', 'Code'])\
    .sum()[['Cases', 'Deaths']].reset_index()
state_page_dates = sorted(set(state_page_df['Date']))
states = [x for x in set(state_page_df['State']) if str(x) != 'nan']
usa_state_page_dates = [str(x).replace('date_', '').replace('.csv', '') for x in os.listdir('../data/county_data/')]
usa_state_page_dates = sorted(set([x for x in usa_state_page_dates if x if x[0]=='2']))


# country specific pages
C_page_entities = 'Country'
C_page_df = world_data.copy()
C_page_df[C_page_entities + '_'] = [x.replace(' ','').lower() for x in C_page_df[C_page_entities]]
C_page_df_grouped = C_page_df.groupby(['Date', C_page_entities]).sum()[['Cases', 'Deaths']].reset_index()
C_page_dates = sorted(set(C_page_df['Date']))


# state specific pages
# location
SS_page_entities = 'State'
SS_page_df = state_data.copy()
SS_page_df[SS_page_entities + '_'] = [str(x).replace(' ','').lower() for x in SS_page_df[SS_page_entities]]

# county
SS_page_df_counties = county_data.copy()
SS_page_df_grouped = SS_page_df_counties.groupby(['Date', 'County', SS_page_entities, 'Code']).sum()[['Cases', 'Deaths']].reset_index()
SS_page_dates = [str(x).replace('date_', '').replace('.csv', '') for x in os.listdir('../data/county_data/')]
SS_page_dates = sorted(set([x for x in SS_page_dates if x if x[0]=='2']))
SS_page_county_dfs = [x.copy() for x in county_data_by_date]

SS_page_location_lat_lon = location_lat_lon.copy()


# county specific pages
CS_page_entities = 'County'
CS_page_df = county_data.copy()
CS_page_df[CS_page_entities + '_'] = [str(y).replace(' ','').lower() + '/' + str(x).replace(' ','').lower() for x,y in zip(CS_page_df[CS_page_entities], CS_page_df['State'])]
CS_page_df_grouped = CS_page_df.groupby(['Date', CS_page_entities, 'State', 'Code']).sum()[['Cases', 'Deaths']].reset_index()
CS_page_dates = [str(x).replace('date_', '').replace('.csv', '') for x in os.listdir('../data/county_data/')]
CS_page_dates = sorted(set([x for x in CS_page_dates if x if x[0]=='2']))
CS_page_county_dfs = [x.copy() for x in county_data_by_date]
