from dash_html_components.Thead import Thead
import config

import dash_html_components as html
import dash_core_components as dcc

SECTORS = list(sorted(set(s['sector'] for s in config.STOCKS)))

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
        className='w3-container',
        style={'marginBottom': '50px'},),
    html.Footer(
        children=[
            html.Small('Stocks: ' + ' '.join([s['ticker'] for s in config.STOCKS])),
            html.Br(),
            html.Small('From ' + config.START + ' To ' + config.END)
        ],
        className='w3-container w3-blue-grey',
        style={'bottom': 0, 'position': 'fixed', 'width': '100%'}
    ),
])

home = html.Div([
    html.H1('Summary'),
    dcc.Dropdown(id='home-dropdown',
        options=[{'label': s['label'], 'value': s['ticker']} for s in config.STOCKS],
        value=[s['ticker'] for s in config.STOCKS],
        multi=True),
    dcc.Graph(id='home-graph'),
    html.Div([
        html.H2('Choosen stocks'),
        html.Table(
            [html.Tr([
                html.Th('Ticker'),
                html.Th('Name'),
                html.Th('Industrial sector'),
            ])] +
            [html.Tr([
                html.Td(s['ticker']),
                html.Td(s['label']),
                html.Td(s['sector']),
            ])for s in config.STOCKS],
            className='w3-table w3-bordered'
        )],
        className='w3-container'
    )
])

descriptive_analysis = html.Div([
    html.H1('Descriptive Analysis'),
    html.Div([
        html.Div([
            html.H3('Settings'),
            dcc.RadioItems(
                id='returns-radio',
                options=[
                    {'label': ' Simple', 'value': 'simple'},
                    {'label': ' Compounded', 'value': 'compounded'},
                ],
                value='compounded',
                className='w3-container',
                inputClassName='w3-radio',
                labelStyle={'display': 'block'},
            ),
            html.Br(),
            dcc.Checklist(
                id='returns-groupbysector',
                options=[{'label': ' Group by sector', 'value': 'True'},],
                value=[],
                className='w3-container',
                inputClassName='w3-check',
            ),
            html.Br(),
            dcc.Dropdown(
                id='returns-sector-dropdown',
                options=[{'label': s, 'value': s} for s in SECTORS]
            ),
            ],
            className='w3-light-grey w3-container w3-cell w3-card',
            style={'minWidth': '220px'},
            ),
        html.Div(
            [dcc.Graph(id='returns-graph')],
            className='w3-cell w3-container',
            ),
        ],
        className='w3-cell-row',
    ),
    html.Br(),
    html.H2('Diagnostic plots'),
    html.Div([
        html.Div([
            html.H3('Settings'),
            html.H5('Stock'),
            dcc.Dropdown(
                id='diagnostic-stock-dropdown',
                options=[{'label': s['label'], 'value': s['ticker']} for s in config.STOCKS],
                value=config.STOCKS[1]['ticker']
            ),
            html.H5('Histogram bins'),
            dcc.Slider(
                id='hist-bins-slider',
                marks={i: str(i) for i in [5,10,15]},
                min=5,
                max=15,
                value=9,
            ),
            html.H5('Boxplot'),
            dcc.Checklist(
                id='boxplot-showall',
                options=[{'label': ' Show all stocks', 'value': 'True'},],
                value=[],
                inputClassName='w3-check',
            ),
            ],
            className='w3-light-grey w3-container w3-cell w3-card',
            style={'minWidth': '220px'},
        ),
        html.Div([
            html.Div([
                html.Div(
                    [dcc.Graph(id='hist-graph')],
                    className='w3-col s12 m6 l6',
                ),
                html.Div(
                    [dcc.Graph(id='density-graph')],
                    className='w3-col s12 m6 l6',
                    ),
                ],
                className='w3-row',
            ),
            html.Div([
                html.Div(
                    [dcc.Graph(id='boxplot-graph')],
                    className='w3-col s12 m6 l6',
                ),
                html.Div(
                    [dcc.Graph(id='qqplot-graph')],
                    className='w3-col s12 m6 l6',
                    ),
                ],
                className='w3-row',
            ),
            ],
            className='w3-cell',
        ),
        ],
        className='w3-cell-row',
    ),
    html.Br(),
    html.H2('Descriptive statistics'),
    html.Div(
        id='descriptive-statistics-table',
        className='w3-container',
    ),
    html.Br(),
    html.H4('Correlation matrix'),
    html.Div(
        id='correlation-matrix-table',
        className='w3-container',
    ),
    html.Br(),
    html.H2('Scatterplot matrix'),
    html.Div([
        html.Div([
            html.H3('Settings'),
            dcc.Checklist(
                id='scatterplot-stocks-checklist',
                options=[{'label': ' '+s['label'], 'value': s['ticker']} for s in config.STOCKS],
                value=[s['ticker'] for s in config.STOCKS][0:2],
                inputClassName='w3-check',
                labelStyle={'display': 'block'},
                className='w3-container',
            )],
            className='w3-light-grey w3-container w3-cell w3-card',
            style={'minWidth': '220px'},
        ),
        html.Div(
            [dcc.Graph(id='scatterplot-graph')],
            className='w3-container w3-cell',
        ),],
        className='w3-cell-row',
    )
])

def generate_descriptive_statistics_table(data):
    table_head = [
        html.Thead(html.Tr([
            html.Th('Stock'),
            html.Th('Mean'),
            html.Th('Variance'),
            html.Th('Standard deviation'),
            html.Th('Skewness'),
            html.Th('Kurtosis'),
        ]))]
    table_body = [
        html.Tr([
                html.Td(d['stock']),
                html.Td(d['mean']),
                html.Td(d['variance']),
                html.Td(d['standard_deviation']),
                html.Td(d['skewness']),
                html.Td(d['kurtosis']),
            ],
            className='w3-hover-light-gray')
        for index, d in data.iterrows()
    ]
    table_body = [html.Tbody(table_body)]
    table = html.Table(table_head+table_body, className='w3-table w3-bordered')
    return table

def generate_correlation_matrix_table(data):
    table_head = [
        html.Thead(
            html.Tr([html.Th('')]+
                [html.Th(c) for c in data.columns]))]
    table_body = [
        html.Tr(
            [html.Th(index)] +
            [html.Td(
                cell,
                className='w3-pale-green'if cell>0.5 else '')
            for cell in row])
        for index, row in data.iterrows()]
    table_body = [html.Tbody(table_body)]
    table = html.Table(table_head+table_body, className='w3-table w3-bordered')
    return table

predictive_analysis = html.Div([
    html.H1('Predictive Analysis'),
    html.Div([
        html.Div([
            html.H3('Settings'),
            dcc.Dropdown(
                id='forecast-stock-dropdown',
                options=[{'label': s['label'], 'value': s['ticker']} for s in config.STOCKS],
                value=config.STOCKS[0]['ticker'],
            ),
            html.Br(),
            dcc.Checklist(
                id='forecast-checklist',
                options=[{'label': ' Forecast', 'value': 'forecast'},
                        {'label': ' Observed', 'value': 'observed'},],
                value=['forecast'],
                inputClassName='w3-check',
                labelStyle={'display': 'block'},
                className='w3-container',
            ),
            html.Br(),
            html.H5('Forecast confidence %'),
            dcc.Slider(
                id='forecast-confidence-slider',
                marks={i: str(i) for i in [80,90,95,99]},
                min=80,
                max=99,
                value=95,
            ),
            ],
            className='w3-light-grey w3-container w3-cell w3-card',
            style={'minWidth': '220px'},
            ),
        html.Div(
            [dcc.Graph(id='forecast-graph')],
            className='w3-cell w3-container',
            ),
        ],
        className='w3-cell-row',
    ),
])

portfolio_management = html.Div([
    html.H2(children='portfolio_management')
    #TODO Piechart per il risultato del markovitz
])

redirect = dcc.Location(pathname='/DescriptiveAnalysis', id='_')