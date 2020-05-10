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
import numpy as np

# import plotly.figure_factory as ff
# import plotly.express as px


df = pd.read_csv('../data/world_data_with_codes.csv')
cummulative_cases = df.groupby(['Date', 'Country']).sum()[['Cases', 'Deaths']].reset_index()
dates = sorted(set(df['Date']))

df_US = pd.read_csv('../data/daily_cases_USA_states.csv')
cummulative_cases_US = df_US.groupby(['Date', 'State', 'Day', 'Code']).sum()[['Cases', 'Deaths']].reset_index()
dates_US = sorted(set(df_US['Date']))
states = [x for x in set(df_US['State']) if str(x) != 'nan']

dropdown_choices = [{'label': x[0], 'value': x[1]} for x in \
                    sorted(list(set(zip(df_US.State, df_US.Code)))) if x[0] != 'District of Columbia']

df_US_c = pd.read_csv('../data/daily_cases_USA_counties.csv')
cummulative_cases_US_c = df_US_c.groupby(['Date', 'County', 'State', 'Code']).sum()[['Cases', 'Deaths']].reset_index()
dates_US_c = [x.replace('date_', '').replace('.csv', '') for x in os.listdir('../data/county_data/')]
dates_US_c = sorted(set([x for x in dates_US_c]))
county_dfs = [pd.read_csv(f'../data/county_data/{f}') for f in sorted(os.listdir('../data/county_data/'))]

state_lat_lon = pd.read_csv('../data/statelatlong.csv')

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = flask.Flask(__name__)
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, server=server)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

date_style_dict = {
    'textAlign': 'center',
    'color': colors['text'],
    'fontSize': "18px"
}

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        {%scripts%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])
#
# index_page = html.Div([
#     dcc.Link('Go to Page 1', href='/NY'),
#     html.Br(),
#     dcc.Link('Go to Page 2', href='/CA'),
# ])

page_1_layout = html.Div(
    # children=[
        # dcc.Location(id='url', refresh=False),
        # html.Div(
        #     children=
            dcc.Tabs(
                id="tabs",
                value='tab-1',
                colors={
                    "border": "#7FDBFF",
                    "primary": "#7FDBFF",
                    "background": "white"
                },
                children=[
                    dcc.Tab(
                        value='tab-1',
                        label='World Map',
                        children=[
                            html.Div(
                                style={'backgroundColor': colors['background']},
                                children=[
                                    html.H1(
                                        children='Tracking COVID-19',
                                        style={
                                            'textAlign': 'center',
                                            'color': colors['text']
                                        }
                                    ),

                                    html.Label(id='slider-label',
                                               children='Days since January 22',
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

                                    html.Div(id='output-totals'),

                                    html.Div(id='output-data-upload')
                                ]),
                        ]),
                     dcc.Tab(
                         value='tab-2',
                             label='United States',
                         children=[
                             html.Div(
                                 style={'backgroundColor': colors['background']},
                                 children=[
                                 html.H1(
                                     children='Tracking COVID-19',
                                     style={
                                         'textAlign': 'center',
                                         'color': colors['text']
                                     }
                                 ),

                                 html.Label(
                                     id='slider-label2',
                                            children='Days since January 22',
                                            style=date_style_dict),

                                 dcc.Slider(
                                     id='date--slider2',
                                     min=0,
                                     max=len(dates_US) - 1,
                                     value=len(dates_US) - 1,
                                     marks={i: str() for i in range(len(dates_US))},
                                     step=1
                                 ),

                                     dcc.Graph(id='indicator-graphic2'),

                                     html.Div(id='output-totals_US'),

                                     html.Div(id='output-data-upload2')
                                 ]),
                         ]),
                    dcc.Tab(
                        value='tab-3',
                        label='State Maps',
                        children=[
                            html.Div(style={'backgroundColor': colors['background']},
                                     children=[
                                         html.H1(
                                             children='Tracking COVID-19',
                                             style={
                                                 'textAlign': 'center',
                                                 'color': colors['text']
                                             }
                                         ),

                                         html.Label(
                                             id='slider-label3',
                                             children='Days since January 22',
                                             style=date_style_dict),

                                         dcc.Slider(
                                             id='date--slider3',
                                             min=0,
                                             max=len(dates_US_c) - 1,
                                             value=len(dates_US_c) - 1,
                                             marks={i: str() for i in range(len(dates_US_c))},
                                             step=1
                                         ),

                                         dcc.Dropdown(
                                             id='dropdown-state',
                                             options=dropdown_choices,
                                             value='AL',
                                             placeholder="Select a State",
                                             clearable=False,
                                             searchable=False
                                         ),

                                         dcc.Graph(id='indicator-graphic3'),

                                         html.Div(id='output-totals_US_c'),

                                         html.Div(id='output-data-upload3')
                                     ]),
                        ]),
                    dcc.Tab(value='tab-4',
                            label='About',
                            children=[
                                html.Div(
                                    style={'backgroundColor': colors['background']},
                                    children=[
                                        html.H3(
                                            children='Data',
                                            style={
                                                'textAlign': 'left',
                                                'color': colors['text'],
                                                'marginLeft': 10,
                                                'marginRight': 10,
                                                'marginTop': 10,
                                                'marginBottom': 0
                                            }
                                        ),
                                        dcc.Markdown(
                                            children="""
The New York Times and the Johns Hopkins University Center for Systems Science and Engineering are providing daily COVID-19 case count files on GitHub. The links are provided below:

- [New York Times](https://github.com/nytimes/covid-19-data)
- [Johns Hopkins University](https://github.com/CSSEGISandData/COVID-19)

[This repository](https://github.com/willhaslett/covid-19-growth) by Will Haslett aggregates these files (more details can be found in the README).

Please see the README in each repository above for information on the data collection process and missing values.""",
                                            style={
                                                'textAlign': 'left',
                                                'color': colors['text'],
                                                'fontSize': '18px',
                                                'marginLeft': 10,
                                                'marginRight': 10,
                                                'marginTop': 10,
                                                'marginBottom': 10
                                            }
                                        ),
                                        html.H3(
                                            children='Contact',
                                            style={
                                                'textAlign': 'left',
                                                'color': colors['text'],
                                                'marginLeft': 10,
                                                'marginRight': 10,
                                                'marginTop': 10,
                                                'marginBottom': 10
                                            }
                                        ),
                                        dcc.Markdown(
                                            children="""
 This application was created entirely in Python using plotly and dash. If you would like to offer feedback, ask a question, or have an idea and would like to contribute, I can always be reached on [Linkedin](https://www.linkedin.com/in/adamreevesman) or over email at areevesman@gmail.com.
 """,
                                            style={
                                                'textAlign': 'left',
                                                'color': colors['text'],
                                                'fontSize': '18px',
                                                'marginLeft': 10,
                                                'marginRight': 10,
                                                'marginTop': 10,
                                                'marginBottom': 10
                                            }
                                        ),
                                        html.H3(
                                            children='Broken Links',
                                            style={
                                                'textAlign': 'left',
                                                'color': colors['text'],
                                                'marginLeft': 10,
                                                'marginRight': 10,
                                                'marginTop': 10,
                                                'marginBottom': 10
                                            }
                                        ),
                                        dcc.Markdown(
                                            children="""
 Some users have had issues with the links above. If you have trouble, here are the full links.
- New York Times: [https://github.com/nytimes/covid-19-data](https://github.com/nytimes/covid-19-data)
- Johns Hopkins: University: [https://github.com/CSSEGISandData/COVID-19](https://github.com/CSSEGISandData/COVID-19)
- Will Haslett's repository: [https://github.com/willhaslett/covid-19-growth](https://github.com/willhaslett/covid-19-growth)
- My Linkedin: [https://www.linkedin.com/in/adamreevesman](https://www.linkedin.com/in/adamreevesman)
 """,
                                            style={
                                                'textAlign': 'left',
                                                'color': colors['text'],
                                                'fontSize': '18px',
                                                'marginLeft': 10,
                                                'marginRight': 10,
                                                'marginTop': 10,
                                                'marginBottom': 10
                                            }
                                        )
                                    ]),
                            ])
                ])
        )
    # ])

page_2_layout = html.Div(style={'backgroundColor': colors['background']}, children=[
                html.H1(
                    children='Tracking COVID-19',
                    style={
                        'textAlign': 'center',
                        'color': colors['text']
                    }
                ),

                html.Label(id='slider-label3-1',
                           children='Days since January 22',
                           style=date_style_dict),

                dcc.Slider(
                    id='date--slider3-1',
                    min=0,
                    max=len(dates_US_c)-1,
                    value=len(dates_US_c)-1,
                    marks={i: str() for i in range(len(dates_US_c))},
                    step=1
                ),

                dcc.Graph(id='indicator-graphic3-1'),

                html.Div(id='output-totals_US_c-1'),

                html.Div(id='output-data-upload3-1')
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


@app.callback(
    Output('indicator-graphic2', 'figure'),
    [Input('date--slider2', 'value')])
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


@app.callback(
    Output('indicator-graphic3', 'figure'),
    [Input('date--slider3', 'value'),
     Input('dropdown-state', 'value')])
def update_graph_US_c(day_US_c, code):
    dff_US_c = county_dfs[day_US_c]
    dff_US_c['FIPS'] = dff_US_c['FIPS'].map(lambda x: '0' + str(x) if (len(str(x)) <= 4) else str(x))
    dff_US_c = dff_US_c.loc[(dff_US_c['Code'] == code)]
    dff_US_c.loc[:, 'Text'] = [f'<b>{w}</b><br>{int(x):,} Cases<br>{int(z):,} Deaths' for w, x, y, z in \
                               zip(dff_US_c['County'], dff_US_c['Cases'], dff_US_c['State'], dff_US_c['Deaths'])]
    center_dict = {"lat": float(state_lat_lon.loc[state_lat_lon['State'] == code, 'Latitude'].values[0]),
                   "lon": float(state_lat_lon.loc[state_lat_lon['State'] == code, 'Longitude'].values[0])}
    return go.Figure(data=go.Choroplethmapbox(
        locations=dff_US_c['FIPS'],  # Spatial coordinates
        geojson=counties,
        z=dff_US_c['Cases'].astype(float),  # Data to be color-coded
        zmin=0,
        zmax=cummulative_cases_US_c['Cases'].max() * 1.1,
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
        geo={'fitbounds': 'locations'}
    )

def Table(dataframe, link_column_name, col_to_link):
    if link_column_name:
        links = dataframe[link_column_name].map(lambda x: x.replace(' ','')).values
    rows = []
    for i in range(len(dataframe)):
        row = []
        for col in dataframe.columns:
            if col != link_column_name:
                value = dataframe.iloc[i][col]
                # update this depending on which
                # columns you want to show links for
                # and what you want those links to be
                if col == col_to_link:
                    cell = html.Td(html.A(href=links[i], children=value))
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
                                   # 'padding': '10px'
                                   }))
    return html.Table(
        # Header
        [html.Tr([html.Th(col,
                          style={
                              'background-color': '#111111',
                              'color': '#7FDBFF',
                              'width': '50%',
                              'fontSize': '20px',
                              # 'padding-left': '10px'
                          })\
                  for col in dataframe.columns if col != link_column_name])] +\
        rows,
        style={'width':'100%',
               # 'text-align':'center',
               # 'padding-left': '10px'
               }
    )

@app.callback(Output('output-data-upload', 'children'),
              [Input('date--slider', 'value')])
def update_table(day):
    totals = cummulative_cases[cummulative_cases['Date'] == dates[day]][['Country', 'Cases', 'Deaths']] \
        .sort_values('Cases', ascending=False)
    totals['Cases'] = totals['Cases'].map(lambda x: f'{x:,}')
    totals['Deaths'] = totals['Deaths'].map(lambda x: f'{x:,}')
    # table = html.Div([
    #     dash_table.DataTable(
    #         data=totals.to_dict('rows'),
    #         columns=[{'name': i, 'id': i} for i in totals.columns],
    #         fixed_rows={'headers': True, 'data': 0},
    #         style_header={'fontSize': '20px',
    #                       'border': '2px solid white'},
    #         style_cell={
    #             'backgroundColor': '#111111',
    #             'color': '#7FDBFF',
    #             'width': '30%',
    #             'fontSize': '16px'
    #         },
    #     ),
    #     # html.Hr()
    # ])
    table = Table(totals, link_column_name=None, col_to_link=None)
    return table


@app.callback(Output('output-data-upload2', 'children'),
              [Input('date--slider2', 'value')])
def update_table_US(day_US):
    totals_US = cummulative_cases_US[cummulative_cases_US['Date'] == dates_US[day_US]][['State', 'Cases', 'Deaths']] \
        .sort_values('Cases', ascending=False)
    totals_US['Cases'] = totals_US['Cases'].map(lambda x: f'{x:,}')
    totals_US['Deaths'] = totals_US['Deaths'].map(lambda x: f'{x:,}')
    totals_US['Links'] = ['localhost:8080'+'/'+state for state in totals_US['State']]
    # table_US = html.Div([
    #     dash_table.DataTable(
    #         data=totals_US.to_dict('rows'),
    #         columns=[{'name': i, 'id': i} for i in totals_US.columns],
    #         fixed_rows={'headers': True, 'data': 0},
    #         style_header={'fontSize': '20px',
    #                       'border': '2px solid white'},
    #         style_cell={
    #             'backgroundColor': '#111111',
    #             'color': '#7FDBFF',
    #             'width': '30%',
    #             'fontSize': '16px'
    #         },
    #     ),
    #     # html.Hr()
    # ])
    table_US = Table(totals_US,'Links', 'State')
    return table_US


@app.callback(Output('output-data-upload3', 'children'),
              [Input('date--slider3', 'value'),
               Input('dropdown-state', 'value')])
def update_table_US_c(day_US_c, code):
    totals_US_c = cummulative_cases_US_c \
        [((cummulative_cases_US_c['Date'] == dates_US_c[day_US_c])) & \
         (cummulative_cases_US_c['Code'] == code)] \
        .sort_values('Cases', ascending=False)[['County', 'Cases', 'Deaths']]
    totals_US_c['Cases'] = totals_US_c['Cases'].map(lambda x: f'{int(x):,}')
    totals_US_c['Deaths'] = totals_US_c['Deaths'].map(lambda x: f'{int(x):,}')
    # table_US_c = html.Div([
    #     dash_table.DataTable(
    #         data=totals_US_c.to_dict('rows'),
    #         columns=[{'name': i, 'id': i} for i in totals_US_c.columns],
    #         fixed_rows={'headers': True, 'data': 0},
    #         style_header={'fontSize': '20px',
    #                       'border': '2px solid white'},
    #         style_cell={
    #             'backgroundColor': '#111111',
    #             'color': '#7FDBFF',
    #             'width': '30%',
    #             'fontSize': '16px'
    #         },
    #     ),
    #     # html.Hr()
    # ])
    table_US_c = Table(totals_US_c, link_column_name=None, col_to_link=None)
    return table_US_c


@app.callback(Output('output-totals', 'children'),
              [
                  Input('date--slider', 'value')
              ])
def update_totals(day):
    day_totals = cummulative_cases[cummulative_cases['Date'] == dates[day]].sum()
    d = {'Cases': [f"{day_totals['Cases']:,}"],
         'Deaths': [f"{day_totals['Deaths']:,}"]}
    return html.H5(
        children=[f'Total Cases: {d["Cases"][0]}', html.Br(), f'Total Deaths: {d["Deaths"][0]}'],
        style={
            'textAlign': 'left',
            'color': colors['text'],
            'marginLeft': 10,
            'marginRight': 10,
            'marginTop': 10,
            'marginBottom': 0
        }
    )


@app.callback(Output('output-totals_US', 'children'),
              [
                  Input('date--slider2', 'value')
              ])
def update_totals_US(day_US):
    day_totals_US = cummulative_cases_US[cummulative_cases_US['Date'] == dates_US[day_US]].sum()
    d_US = {'Cases': [f"{day_totals_US['Cases']:,}"],
            'Deaths': [f"{day_totals_US['Deaths']:,}"]}
    return html.H5(
        children=[f'Total Cases: {d_US["Cases"][0]}', html.Br(), f'Total Deaths: {d_US["Deaths"][0]}'],
        style={
            'textAlign': 'left',
            'color': colors['text'],
            'marginLeft': 10,
            'marginRight': 10,
            'marginTop': 10,
            'marginBottom': 0
        }
    )


@app.callback(Output('output-totals_US_c', 'children'),
              [Input('date--slider3', 'value'),
               Input('dropdown-state', 'value')])
def update_totals_US_c(day_US_c, code):
    day_totals_US_c = cummulative_cases_US_c[
        (cummulative_cases_US_c['Date'] == dates_US_c[day_US_c]) & (cummulative_cases_US_c['Code'] == code)].sum()
    d_US_c = {'Cases': [f"{int(day_totals_US_c['Cases']):,}"],
              'Deaths': [f"{int(day_totals_US_c['Deaths']):,}"]}
    return html.H5(
        children=[f'Total Cases: {d_US_c["Cases"][0]}', html.Br(), f'Total Deaths: {d_US_c["Deaths"][0]}'],
        style={
            'textAlign': 'left',
            'color': colors['text'],
            'marginLeft': 10,
            'marginRight': 10,
            'marginTop': 10,
            'marginBottom': 0
        }
    )


@app.callback(Output('slider-label', 'children'),
              [Input('date--slider', 'value')])
def show_date(day):
    return str(dates[day])


@app.callback(Output('slider-label2', 'children'),
              [Input('date--slider2', 'value')])
def show_date_US(day_US):
    return str(dates_US[day_US])


@app.callback(Output('slider-label3', 'children'),
              [Input('date--slider3', 'value')])
def show_date_US_c(day_US_c):
    return str(dates_US_c[day_US_c])


@app.callback(
    Output('indicator-graphic3-1', 'figure'),
    [Input('date--slider3-1', 'value'),
     Input('url', 'pathname')])
def update_graph_US_c_1(day_US_c, pathname):
    state = pathname.strip('/')
    dff_US_c = county_dfs[day_US_c]
    code = dff_US_c.loc[dff_US_c['State'].map(lambda x: str(x).replace(' ', '')) == state, 'Code'].values[0]
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
        zmax=cummulative_cases_US_c['Cases'].max() * 1.1,
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
        geo={'fitbounds': 'locations'}
    )

@app.callback(Output('output-data-upload3-1', 'children'),
              [Input('date--slider3-1', 'value'),
               Input('url', 'pathname')])
def update_table_US_c_1(day_US_c, pathname):
    state = pathname.strip('/')
    totals_US_c = cummulative_cases_US_c \
        [((cummulative_cases_US_c['Date'] == dates_US_c[day_US_c])) & \
         (cummulative_cases_US_c['State'].map(lambda x: str(x).replace(' ','')) == state)] \
        .sort_values('Cases', ascending=False)[['County', 'Cases', 'Deaths']]
    totals_US_c['Cases'] = totals_US_c['Cases'].map(lambda x: f'{int(x):,}')
    totals_US_c['Deaths'] = totals_US_c['Deaths'].map(lambda x: f'{int(x):,}')
    # table_US_c = html.Div([
    #     dash_table.DataTable(
    #         data=totals_US_c.to_dict('rows'),
    #         columns=[{'name': i, 'id': i} for i in totals_US_c.columns],
    #         fixed_rows={'headers': True, 'data': 0},
    #         style_header={'fontSize': '20px',
    #                       'border': '2px solid white'},
    #         style_cell={
    #             'backgroundColor': '#111111',
    #             'color': '#7FDBFF',
    #             'width': '30%',
    #             'fontSize': '16px'
    #         },
    #     ),
    #     # html.Hr()
    # ])
    table_US_c = Table(totals_US_c, None, None)
    return table_US_c

@app.callback(Output('output-totals_US_c-1', 'children'),
              [Input('date--slider3-1', 'value'),
               Input('url', 'pathname')])
def update_totals_US_c_1(day_US_c, pathname):
    state = pathname.strip('/')
    day_totals_US_c = cummulative_cases_US_c[
        (cummulative_cases_US_c['Date'] == dates_US_c[day_US_c]) &
        (cummulative_cases_US_c['State'].map(lambda x: str(x).replace(' ','')) == state)].sum()
    d_US_c = {'Cases': [f"{int(day_totals_US_c['Cases']):,}"],
              'Deaths': [f"{int(day_totals_US_c['Deaths']):,}"]}
    return html.H5(
        children=[f'Total Cases: {d_US_c["Cases"][0]}', html.Br(), f'Total Deaths: {d_US_c["Deaths"][0]}'],
        style={
            'textAlign': 'left',
            'color': colors['text'],
            'marginLeft': 10,
            'marginRight': 10,
            'marginTop': 10,
            'marginBottom': 0
        }
    )

@app.callback(Output('slider-label3-1', 'children'),
              [Input('date--slider3-1', 'value')])
def show_date_US_c_1(day_US_c):
    return str(dates_US_c[day_US_c])

@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname in ['/' + state.replace(' ','') for state in states]:
        return page_2_layout
    elif pathname=='/':
        return page_1_layout
    else:
        return '404. The page you are looking for does not exist.'

# @app.callback([Output('tabs', 'value'),
#                Output('dropdown-state', 'value')],
#               [Input('url', 'pathname')])
# def display_page(state_code):
#     if state_code in ['/' + code for code in state_codes]:
#         return 'tab-3', state_code.strip('/')
#     else:
#         return 'tab-1', 'AL'

# @app.callback([Output('url', 'pathname')],
#                [Input('dropdown-state', 'value')])
# def redirect_to_state_page(state_code):
#     return ['/' + state_code]




if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8080)