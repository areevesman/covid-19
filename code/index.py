import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from app import server
from apps import world_page, country_specific_pages,\
    usa_states_page, usa_counties_page,\
    state_specific_pages, county_specific_pages,\
    about

import pandas as pd


app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return world_page.layout
    elif pathname == '/States':
        return usa_states_page.layout
    elif pathname == '/Counties':
        return usa_counties_page.layout
    elif pathname == '/About':
        return about.layout
    elif pathname in['/'+x.replace(' ','') for x in set(df['Country'].values)]:
        return country_specific_pages.layout
    elif pathname in['/'+x.replace(' ','') for x in set(df_US['State'].values)]:
        return state_specific_pages.layout
    elif pathname in['/' + y.replace(' ','') + '/' + x.replace(' ','')\
                     for x,y in set(zip(df_US_c['County'].values, df_US_c['State'].values))]:
        return county_specific_pages.layout
    else:
        return '404. This page does not exist.'


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8080)