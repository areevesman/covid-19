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


df = pd.read_csv('../data/world_data_with_codes.csv')
df_US = pd.read_csv('../data/daily_cases_USA_states.csv')
df_US_c = pd.read_csv('../data/daily_cases_USA_counties.csv')

app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    pathname = pathname.lower()
    if pathname == '/':
        return world_page.layout
    # elif pathname == '/states':
    #     return usa_states_page.layout
    elif pathname == '/countries/unitedstates-counties':
        return usa_counties_page.layout
    elif pathname == '/about':
        return about.layout
    elif pathname in['/countries/'+x.replace(' ','').lower() for x in set(df['Country'].values) if str(x) != 'nan']:
        if pathname.lower()=='/countries/unitedstates':
            return usa_states_page.layout
        else:
            return country_specific_pages.layout
    elif pathname in['/states/'+x.replace(' ','').lower() for x in set(df_US['State'].values) if str(x) != 'nan']:
        return state_specific_pages.layout
    elif pathname in['/states/' + y.replace(' ','').lower() + '/' + x.replace(' ','').lower()\
                     for x,y in set(zip(df_US_c['County'].values, df_US_c['State'].values))\
                     if (str(x) !='nan' and str(y) != 'nan')]:
        return county_specific_pages.layout
    else:
        return '404. This page does not exist.'


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8080)