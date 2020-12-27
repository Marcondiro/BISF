import dash_html_components as html
import dash_core_components as dcc
from dash_html_components import Header

css = ['https://www.w3schools.com/w3css/4/w3.css']

layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(
        className='w3-bar w3-blue',
        children=[
            html.A(children='Descriptive Analisys',
                href='/DescriptiveAnalisys',
                className='w3-bar-item w3-button'),
            html.A(children='Predictive Analisys',
                href='PredictiveAnalisys',
                className='w3-bar-item w3-button'),
            html.A(children='Portfolio Management',
                href='PortfolioManagement',
                className='w3-bar-item w3-button')
            ]
        ),
    html.H1(children='BISF Project'),
    html.Div(id='page-content')
])

descriptive_analysis = html.Div([
    html.H2(children='descriptive_analysis')
])

predictive_analysis = html.Div([
    html.H2(children='predictive_analysis')
])

portfolio_management = html.Div([
    html.H2(children='portfolio_management')
])

redirect = dcc.Location(pathname='/DescriptiveAnalysis', id='_')