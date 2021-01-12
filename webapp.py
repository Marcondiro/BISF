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
                className='w3-bar-item w3-button'),
            html.A(children='Beta',
                href='/beta',
                className='w3-bar-item w3-button'),
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
                value=config.STOCKS[0]['ticker']
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
    html.H2('Portfolio management'),
    html.H3('Mean-Variance model market portfolio. Expected returns based on forecasting.'),
    html.Div([
        html.Div([
            html.H3('Settings'),
            dcc.Checklist(
                id='portfolio-realweights-checklist',
                options=[{'label': ' Real weights', 'value': 'True'},],
                value=[],
                inputClassName='w3-check',
                labelStyle={'display': 'block'},
                className='w3-container',
            ),
            html.H3('Portfolio Details'),
            html.Div(id='portfolio-details'),
            ],
            className='w3-light-grey w3-container w3-cell w3-card',
            style={'minWidth': '220px'},
            ),
        html.Div(
            [dcc.Graph(id='portfolio-weights-graph')],
            className='w3-cell w3-container',
            ),
        ],
        className='w3-cell-row',
    ),
    html.H2('Investment results'),
        html.Div([
            html.Div(id = 'results-table'),
            html.P('Supposing no dividens, transaction costs: '+ str(config.FEE*100) + '% for sells'),
        ],
        className='w3-light-grey w3-container w3-card w3-row'
    ),
])

def generate_portfolio_details(budget, start, end, principal, ret, risk, sharpe):
    return html.Div([
        html.P('Budget: '+str(budget)),
        html.P('Start: '+start),
        html.P('End: '+end),
        html.P('Principal: '+str(round(principal, 2))),
        html.P('Expected return: '+str(round(ret, 2))+'%'),
        html.P('Risk: '+str(round(risk, 2))),
        html.P('Sharpe ratio: '+str(round(sharpe, 2))),
    ])

def generate_results_table(data):
    return html.Table([
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
        html.Tbody(
            [html.Tr([
                html.Th(s),
                html.Td(round(data[s][0], 2)),
                html.Td(round(data[s][1], 0)),
                html.Td(round(data[s][0]*data[s][1], 2)),
                html.Td(round(data[s][2], 2)),
                html.Td(round(data[s][2]*data[s][1], 2)),
                html.Td(round(data[s][2]*data[s][1]*config.FEE, 2)),
                html.Td(round(data[s][2]*data[s][1]*(1-config.FEE)-data[s][0]*data[s][1], 2)),
                html.Td([round((data[s][2]*(1-config.FEE)/data[s][0]-1)*100, 2), '%'])
            ])for s in data]+
            [html.Tr([
                html.Th('Total'),
                html.Td(''),
                html.Td(''),
                html.Td(round((data.iloc[0,:]*data.iloc[1,:]).sum(), 2)),
                html.Td(''),
                html.Td(round((data.iloc[2,:]*data.iloc[1,:]).sum(), 2)),
                html.Td(round((data.iloc[2,:]*data.iloc[1,:]).sum()*config.FEE, 2)),
                html.Td(round((data.iloc[2,:]*data.iloc[1,:]).sum()*(1-config.FEE)-
                        (data.iloc[0,:]*data.iloc[1,:]).sum(), 2)),
                html.Td([round(((data.iloc[2,:]*data.iloc[1,:]).sum()*(1-config.FEE)/
                        (data.iloc[0,:]*data.iloc[1,:]).sum()-1)*100, 2), '%']),
                ],
                className='w3-gray'
            )]
        ),
    ],
    className='w3-table w3-bordered')

beta = html.Div([
    html.H2('Beta 10-months based on '+config.MARKET_INDEX['label']),
    html.Div(
        [dcc.Graph(id='beta-graph')],
        className='w3-container',
    ),
    html.H2('CAPM expected returns'),
    html.Div([
        html.Div(id = 'capm-table'),
    ],
    className='w3-light-grey w3-container w3-card w3-row'
    ),
])

def generate_capm_table(data):
    return html.Table([
        html.Thead([
            html.Th('Stock'),
            html.Th('CAPM expected return'),
            html.Th('Observed return'),
        ]),
        html.Tbody(
            [html.Tr([
                html.Th(s),
                html.Td([round(data[s][0]*100-100, 2), '%']),
                html.Td([round(data[s][1]*100-100, 2), '%']),
            ])for s in data]
        ),
    ],
    className='w3-table w3-bordered')

redirect = dcc.Location(pathname='/', id='_')