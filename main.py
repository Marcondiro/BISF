# -*- coding: utf-8 -*-s
#Config
import config

#Webapp
import webapp

#Packages
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import pandas_datareader.data as web
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import dash
from dash.dependencies import Input, Output

color_map = {s['ticker']: s['color'] for s in config.STOCKS}

def getStocks(STOCKS, START, END):
    #Carico i dati relativi alle azioni.
    #Se presenti in cache evito di scaricarli.
    CACHE_DIR = './stocks_cache/'
    Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)
    dataFrame = None
    for stock in STOCKS:
        try:
            s = pd.read_csv(CACHE_DIR+stock+'_'+START+'_'+END+'.csv',
                index_col=0, parse_dates=True)
            print(stock + ' loaded from cache.')
        except:
            s = web.get_data_yahoo(stock, START, END)
            s.to_csv(CACHE_DIR + stock + '_' + START +'_'+END+'.csv')
            print(stock + ' downloaded from Yahoo.')
        s = s[['Adj Close']]
        s.columns = [stock]
        if dataFrame is None:
            dataFrame = s
        else:
            dataFrame = dataFrame.join(s)
    return dataFrame

stocks = getStocks([s['ticker'] for s in config.STOCKS], config.START, config.END)
stocks_monthly = stocks.groupby(pd.Grouper(freq='M')).mean()

#Adj close
#stocks_monthly.plot(grid=True, title='Raw data: Adjusted close')

#Returns
simple_returns = stocks_monthly - stocks_monthly.shift(1)
simple_returns = simple_returns.dropna()
#simple_returns.plot(grid=True, title='Simple returns')
cc_returns = np.log(stocks_monthly / stocks_monthly.shift(1))
cc_returns = cc_returns.dropna()
#cc_returns.plot(grid=True, title='CC returns')

#returns grouped by sector
# SECTORS = set(s['sector'] for s in config.STOCKS)
# fig, axes = plt.subplots(len(SECTORS), 1)
# for i, sector in enumerate(SECTORS):
#     sector_stocks = [ind for ind,s in enumerate(config.SECTORS) if s == sector]
#     cc_returns.iloc[:, sector_stocks].plot(ax=axes[i], sharex=True, grid=True,
#         title=sector)
# plt.tight_layout()

#Diagnostic plots
#cc_returns.hist(bins = 10)

app = dash.Dash(title='BISF Project', external_stylesheets=webapp.css)
app.config.suppress_callback_exceptions = True
app.layout = webapp.layout

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname.lower() == '/':
        return webapp.home
    if pathname.lower() == '/descriptiveanalysis':
        return webapp.descriptive_analysis
    elif pathname.lower() == '/predictiveanalysis':
        return webapp.predictive_analysis
    elif pathname.lower() == '/portfoliomanagement':
        return webapp.portfolio_management
    else:
        return webapp.redirect

#home
@app.callback(Output('home-graph', 'figure'), 
              [Input('home-dropdown', 'value')])
def update_summary_graph(selected_dropdown_values):
    if selected_dropdown_values == []:
        return {}
    plot = px.line(stocks_monthly[selected_dropdown_values], color_discrete_map=color_map)
    plot.update_layout(
        title='Raw data: Adjusted close',
        yaxis_title=None,
    )
    return plot

#descriptive_analysis
@app.callback(Output('returns-graph', 'figure'), 
              [Input('returns-radio', 'value'),
              Input('returns-groupbysector', 'value'),
              Input('returns-sector-dropdown', 'value')
              ])
def update_returns_graph(radio, groupby ,sector):
    if groupby == ['True'] and sector!=None:
        plot_stocks = [s['ticker']for s in config.STOCKS if s['sector']==sector]
    else:
        plot_stocks = stocks.columns
    if radio == 'simple':
        title = 'Simple returns'
        df = simple_returns
    else:
        title='Continuos compounded returns'
        df = cc_returns
    plot = px.line(df[plot_stocks], title=title, color_discrete_map=color_map)
    return plot

@app.callback(Output('returns-sector-dropdown', 'className'), 
              [Input('returns-groupbysector', 'value')])
def show_dropdown(groupby):
    if groupby == ['True']:
        return 'w3-show'
    return 'w3-hide'

@app.callback(Output('hist-graph', 'figure'), 
              [Input('diagnostic-stock-dropdown', 'value'),
              Input('hist-bins-slider', 'value')])
def update_hist_graph(stock, bins):
    if stock == None: return {}
    plot = px.histogram(cc_returns[stock], nbins=bins, title=stock+' cc returns distribution',
        color_discrete_map=color_map)
    plot.update(layout_showlegend=False)
    return plot

@app.callback(Output('density-graph', 'figure'), 
              [Input('diagnostic-stock-dropdown', 'value')])
def update_density_graph(stock):
    if stock == None: return {}
    plot = ff.create_distplot([cc_returns[stock]], [stock], show_hist=False, show_rug=False,
        colors=[color_map[stock]])
    plot.update(layout_showlegend=False)
    return plot

@app.callback(Output('boxplot-graph', 'figure'), 
              [Input('diagnostic-stock-dropdown', 'value'),
              Input('boxplot-showall', 'value'),])
def update_boxplot_graph(stock, show_all):
    if stock == None: return {}
    if show_all == ['True']: df = cc_returns
    else: df = cc_returns[[stock]]
    df = df.melt(var_name='stock')
    plot = px.box(df, y='value', x='stock', color='stock', color_discrete_map=color_map)
    return plot

@app.callback(Output('qqplot-graph', 'figure'), 
              [Input('diagnostic-stock-dropdown', 'value')])
def update_qqplot_graph(stock):
    if stock == None: return {}
    qq = stats.probplot(cc_returns[stock])
    plot = px.scatter(x=qq[0][0], y=qq[0][1], color_discrete_sequence=[color_map[stock]])
    x = np.array([qq[0][0][0], qq[0][0][-1]])
    plot.add_scatter(
        x=x,
        y=qq[1][1]+qq[1][0]*x,
        mode="lines",
        showlegend=False
    )
    return plot

if __name__ == '__main__':
    app.run_server(debug=config.DEBUG)