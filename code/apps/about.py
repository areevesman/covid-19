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


from lib import *

from app import app


layout = html.Div(
    style={'backgroundColor': colors['background']},
    children=header+[
        html.Br(),
        html.Br(),
        html.H2(
            children='About the Dashboard',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),
        html.H4(
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
        html.H4(
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
        html.H4(
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
    ])
