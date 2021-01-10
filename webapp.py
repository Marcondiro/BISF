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
    html.H2('Forecasting-based trading strategy'),
    html.Div([
            html.P(['Budget ', html.Strong('10.000$')]),
            html.Table([
                html.Thead([
                    html.Th('Stock'),
                    html.Th('Price'),
                    html.Th('Quantity'),
                    html.Th('Total price'),
                    html.Th('Sell Price'),
                    html.Th('Payoff'),
                    html.Th('Fee'),
                    html.Th('Profit'),
                    html.Th('Return'),
                ]),
                html.Tbody([
                    html.Tr([
                        html.Th('Taiwan Semiconductor'),
                        html.Td('55.03'),
                        html.Td('30'),
                        html.Td('1650.90'),
                        html.Td('82.27'),
                        html.Td('2468.10'),
                        html.Td('12.34'),
                        html.Td('804.86'),
                        html.Td('48.75%', className='w3-pale-green'),
                    ]),
                    html.Tr([
                        html.Th('Nvidia'),
                        html.Td('224.28'),
                        html.Td('2'),
                        html.Td('448.56'),
                        html.Td('544.42'),
                        html.Td('1088.84'),
                        html.Td('5.45'),
                        html.Td('634,83'),
                        html.Td('141.53%', className='w3-pale-green'),
                    ]),
                    html.Tr([
                        html.Th('Boeing'),
                        html.Td('337.13'),
                        html.Td('10'),
                        html.Td('3371.30'),
                        html.Td('167.86'),
                        html.Td('1678.60'),
                        html.Td('8.39'),
                        html.Td('-1701.09'),
                        html.Td('-50.46%', className='w3-pale-red'),
                    ]),
                    html.Tr([
                        html.Th('Southwest Airlines'),
                        html.Td('54.56'),
                        html.Td('20'),
                        html.Td('1091.20'),
                        html.Td('37.93'),
                        html.Td('758.60'),
                        html.Td('3.79'),
                        html.Td('-336.39'),
                        html.Td('-30.83%', className='w3-pale-red'),
                    ]),
                    html.Tr([
                        html.Th('Pfizer'),
                        html.Td('35.30'),
                        html.Td('30'),
                        html.Td('1059.00'),
                        html.Td('34.16'),
                        html.Td('1024.80'),
                        html.Td('5.12'),
                        html.Td('-39.32'),
                        html.Td('-3.71%', className='w3-pale-red'),
                    ]),
                    html.Tr([
                        html.Th('Bristol-Myers Squibb'),
                        html.Td('59.88'),
                        html.Td('39'),
                        html.Td('2335.32'),
                        html.Td('59.35'),
                        html.Td('2314.65'),
                        html.Td('11.57'),
                        html.Td('-32.24'),
                        html.Td('-1.38%', className='w3-pale-red'),
                    ]),
                    html.Tr([
                        html.Th('Total'),
                        html.Td(''),
                        html.Td(''),
                        html.Td('9956.28'),
                        html.Td(''),
                        html.Td('9333.59'),
                        html.Td('46.67'),
                        html.Td('-669.35'),
                        html.Td('-6.72%'),
                        ],
                        className='w3-gray'
                    ),
                ]),
            ],
            className='w3-table w3-bordered'),
            html.P('Supposing no dividens, transaction costs: 0.5% for sells'),
        ],
        className='w3-light-grey w3-container w3-card w3-row'
    ),
])

portfolio_management = html.Div([
    html.H2(children='portfolio_management')
    #TODO Piechart per il risultato del markovitz
])

redirect = dcc.Location(pathname='/DescriptiveAnalysis', id='_')