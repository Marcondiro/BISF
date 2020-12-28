from dash_html_components.Br import Br
from dash_html_components.Div import Div
from pandas_datareader.data import Options
import config

from dash_core_components.Dropdown import Dropdown
import dash_html_components as html
import dash_core_components as dcc

css = ['https://www.w3schools.com/w3css/4/w3.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css']

layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Header(
        className='w3-bar w3-blue',
        children=[
            html.A(children=html.I(className='fa fa-home'),
                href='/',
                className='w3-bar-item w3-button'),
            html.A(children='Descriptive Analysis',
                href='/DescriptiveAnalysis',
                className='w3-bar-item w3-button'),
            html.A(children='Predictive Analysis',
                href='/PredictiveAnalysis',
                className='w3-bar-item w3-button'),
            html.A(children='Portfolio Management',
                href='/PortfolioManagement',
                className='w3-bar-item w3-button')
            ]
        ),
    html.Div(id='page-content',
        className='w3-container'),
    html.Footer(
        children=[
            html.Small('Stocks: ' + ' '.join([s['ticker'] for s in config.STOCKS])),
            html.Br(),
            html.Small('From ' + config.START + ' To ' + config.END)
        ],
        className='w3-container w3-blue-grey',
        style={'bottom': 0, 'position': 'fixed', 'width': '100%'}
    )
])

home = html.Div([
    html.H1(children='Summary'),
    dcc.Dropdown(id='home-dropdown',
        options=[{'label': s['label'], 'value': s['ticker']} for s in config.STOCKS],
        value=[s['ticker'] for s in config.STOCKS],
        multi=True),
    dcc.Graph(id='home-graph'),
])

descriptive_analysis = html.Div([
    html.H1(children='Descriptive Analysis'),
    html.Div(
        children=[
            html.Div(
                dcc.Graph(id='returns-graph'),
                className='w3-container w3-cell',
            ),
            html.Div([
                html.H3('Options'),
                dcc.RadioItems(
                    id='returns_radio',
                    options=[
                        {'label': ' Simple', 'value': 'simple'},
                        {'label': ' Compounded', 'value': 'compounded'},
                    ],
                    value='simple',
                    className='w3-container',
                    inputClassName='w3-radio',
                    labelStyle={'display': 'block'},
                )],
                className='w3-container w3-cell-middle',
                )
            ],
        className='w3-cell-row',
    ),
])

predictive_analysis = html.Div([
    html.H2(children='predictive_analysis')
])

portfolio_management = html.Div([
    html.H2(children='portfolio_management')
])

redirect = dcc.Location(pathname='/DescriptiveAnalysis', id='_')