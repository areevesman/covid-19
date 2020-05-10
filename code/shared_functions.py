import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from urllib.request import urlopen
import json


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

header = [
    html.A(
        html.Button('Cases by Country',
                    className='three columns',
                    style={
                        'textAlign': 'center',
                        'color': colors['text']
                    }),
        href='/'),
    html.A(
        html.Button('Cases by US State',
                    className='three columns',
                    style={
                        'textAlign': 'center',
                        'color': colors['text']
                    }),
        href='States'),
    html.A(
        html.Button('Cases by US County',
                    className='three columns',
                    style={
                        'textAlign': 'center',
                        'color': colors['text']
                    }),
        href='Counties'),
    html.A(
        html.Button('About',
                    className='three columns',
                    style={
                        'textAlign': 'center',
                        'color': colors['text']
                    }),
        href='About')]


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
                        cell = html.Td(html.A(href=links2[i], children=value))
                    else:
                        cell = html.Td(html.A(href=links1[i], children=value))
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
