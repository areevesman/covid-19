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
# cummulative_cases = df.groupby(['Date', 'Country']).sum()[['Cases', 'Deaths']].reset_index()
# dates = sorted(set(df['Date']))

df_US = pd.read_csv('../data/daily_cases_USA_states.csv')
# cummulative_cases_US = df_US.groupby(['Date', 'State', 'Day', 'Code'])\
#     .sum()[['Cases', 'Deaths']].reset_index()
# dates_US = sorted(set(df_US['Date']))
# states = [x for x in set(df_US['State']) if str(x) != 'nan']

df_US_c = pd.read_csv('../data/daily_cases_USA_counties.csv')
# cummulative_cases_US_c = df_US_c.groupby(['Date', 'County', 'State', 'Code']).sum()[['Cases', 'Deaths']].reset_index()
# dates_US_c = [x.replace('date_', '').replace('.csv', '') for x in os.listdir('../data/county_data/')]
# dates_US_c = sorted(set([x for x in dates_US_c]))
# county_dfs = [pd.read_csv(f'../data/county_data/{f}') for f in sorted(os.listdir('../data/county_data/'))]


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
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