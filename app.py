import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output
import pandas as pd

df = pd.read_csv('./world_data_with_codes.csv')
cummulative_cases = df.groupby(['Date','Country']).sum()['Cases'].reset_index()
dates = sorted(set(df['Date']))

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Tracking COVID-19',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Label(id='slider-label',
               children='Days since January 22',
               style={
                   'textAlign': 'center',
                   'color': colors['text']
               }),

    dcc.Slider(
        id='date--slider',
        min=0,
        max=len(dates)-1,
        value=len(dates)-1,
        marks={i: str() for i in range(len(dates))},
        step=1
    ),

    dcc.Graph(id='indicator-graphic'),

    html.Div(id='output-data-upload')
])

@app.callback(
    Output('indicator-graphic', 'figure'),
    [Input('date--slider', 'value')])
def update_graph(day):
    dff = df[df['Date'] == dates[day]]
    dff.loc[:,'Text'] = [f'{y}: {x:,}' for x,y in zip(dff['Cases'], dff['Country'])]

    return {
        'data': [{'type': 'choropleth',
                  'locations': dff['Code'],
                  'z': dff['Cases'],
                  'zmin': 0,
                  'zmax': 300000,
                  'text': dff['Text'],
                  'hoverinfo': 'text',
                  'colorbar': {'title' : 'Total Cases'},
                  'colorscale': [[0, "rgb(255, 250, 250)"],
                                 [0.0001, "rgb(255, 200, 170)"],
                                 [0.001, "rgb(255, 150, 120)"],
                                 [0.01, "rgb(255, 100, 70)"],
                                 [0.1, "rgb(255, 50, 20)"],
                                 [1.0, "rgb(100, 0, 0)"]],
                  'autocolorscale': False,
                  'reversescale': False}],
        'layout': {
            # 'title': 'Number of cases on ' + str(dates[day]),
            # 'titlefont': {"size": 28},
            'geo': {'showframe': True,
                    'projection': {'type' : 'natural earth'}}
        }
    }

@app.callback(Output('output-data-upload', 'children'),
            [
                Input('date--slider', 'value')
            ])
def update_table(day):
    totals = cummulative_cases[cummulative_cases['Date'] == dates[day]][['Country', 'Cases']]\
        .sort_values('Cases', ascending=False)
    totals['Cases'] = totals['Cases'].map(lambda x: f'{x:,}')
    table = html.Div([
        html.H5('Total Cases',
                style={
                    'textAlign': 'left',
                    'color': colors['text']
                }),
        dash_table.DataTable(
            data=totals.to_dict('rows'),
            columns=[{'name': i, 'id': i} for i in totals.columns],
            fixed_rows={'headers': True, 'data': 0},
            style_cell_conditional=[
                {'if': {'column_id': 'Country'},
                 'width': '50%'},
                {'if': {'column_id': 'Cases'},
                 'width': '50%px'}
            ]
        ),
        html.Hr()
    ])
    return table

@app.callback(Output('slider-label', 'children'),
            [Input('date--slider', 'value')])
def show_date(day):
    return str(dates[day])


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8080)
