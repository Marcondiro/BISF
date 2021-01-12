# -*- coding: utf-8 -*-s
#%%
#Config
from datetime import datetime
import config
#Webapp
import webapp
#Packages
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import pandas_datareader.data as web
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
from dash.dependencies import Input, Output

color_map = {s['ticker']: s['color'] for s in config.STOCKS}

def getStocks(STOCKS, START, END):
    #Carico i dati relativi alle azioni. Se presenti in cache evito di scaricarli.
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

#Stocks
stocks = getStocks([s['ticker'] for s in config.STOCKS], config.START, config.END)
stocks_monthly = stocks.groupby(pd.Grouper(freq='M')).mean()

#Returns
simple_returns = stocks_monthly - stocks_monthly.shift(1)
simple_returns = simple_returns.dropna()
cc_returns = np.log(stocks_monthly / stocks_monthly.shift(1))
cc_returns = cc_returns.dropna()


#Predictive analysis
#Scarico i dati per i periodi n (training) e m (test)
pred_raw_data = getStocks([s['ticker'] for s in config.STOCKS],
                          config.PREDICTION_PERIODS['N'],
                          config.PREDICTION_PERIODS['L'])
#Calcolo cc returns
pred_raw_data = pred_raw_data.groupby(pd.Grouper(freq='M')).mean()
pred_raw_data = np.log(pred_raw_data / pred_raw_data.shift(1))
pred_raw_data = pred_raw_data.dropna()

training_set = pred_raw_data[config.PREDICTION_PERIODS['N']:config.PREDICTION_PERIODS['M']]
test_set = pred_raw_data[config.PREDICTION_PERIODS['M']:config.PREDICTION_PERIODS['L']]

expire_time = pd.to_datetime("now") + pd.DateOffset(seconds=config.PREDICTION_LIMIT_SECONDS)
best_mse = pd.Series({s: np.inf for s in training_set.columns})
best_results = pd.Series({s: None for s in training_set.columns})
for arima_p in range(1, 10):
    for arima_q in range(1, 10):
        models = pd.Series({s: sm.tsa.statespace.SARIMAX(pred_raw_data[s],
                                        order=(arima_p, 0, arima_q),
                                        enforce_stationarity=False,
                                        enforce_invertibility=False)
                for s in training_set.columns})
        results = pd.Series({s: models[s].fit() for s in training_set.columns})
        pred = [r.get_prediction(start=test_set.index[0], dynamic= False).predicted_mean
                for r in results]
        pred = pd.concat(pred, axis=1)
        pred.columns = training_set.columns
        mse = pd.Series(((test_set - pred) ** 2).mean())
        #Salvo il modello corrente se è il migliore (mse minimo)
        best_mse = pd.concat([best_mse, mse], axis=1).min(axis=1)
        for s in training_set.columns:
            if mse[s] == best_mse[s]:
                best_results[s] = results[s]
        #Se supero il tempo limite interrompo la grid search
        if pd.to_datetime("now") > expire_time :
            print('Prediction time slice ended at p=', arima_p, 'q=', arima_q)
            break
    if pd.to_datetime("now") > expire_time:
        break

forecast = pd.Series({s: best_results[s].get_forecast(steps=config.END) for s in best_results.index})
cc_returns_forecast = [s.predicted_mean for s in forecast]
cc_returns_forecast = pd.concat(cc_returns_forecast, axis=1)
cc_returns_forecast.columns = cc_returns.columns

#Portfolio optimization buy&hold L period (no dividends)
expect_returns = (np.e ** cc_returns_forecast).prod()
cov_matrix = risk_models.sample_cov(stocks)
ef = EfficientFrontier(expect_returns, cov_matrix)
prt_weights = pd.Series(ef.max_sharpe())
prt_ret, prt_risk, prt_sharpe = ef.portfolio_performance()

buy_prices = stocks.loc[:config.PREDICTION_PERIODS['L'],:].iloc[-1,:]
buy_stocks_number = np.floor(config.BUDGET * prt_weights / buy_prices)
prt_principal = (buy_prices*buy_stocks_number).sum()
prt_real_weights = buy_prices*buy_stocks_number/prt_principal

#Beta
#Scarico i dati dell'indice
index = getStocks([config.MARKET_INDEX['ticker']], config.START, config.END)
index = index.groupby(pd.Grouper(freq='M')).mean()
index_cc_returns = np.log(index/index.shift(1))
#rimuovo NA e converto in serie
index_cc_returns = index_cc_returns.dropna()[index_cc_returns.columns[0]]

def beta(stocks, index, delta_months):
    beta = pd.DataFrame(columns=stocks.columns)
    for i in range(delta_months, len(index)):
        b = {s: stocks[s][i-delta_months:i-1].cov(index[i-delta_months:i-1]) / index[i-delta_months:i-1].var()
            for s in stocks} 
        b = pd.Series(b)
        beta = beta.append(b, ignore_index=True)
    beta.index = stocks.iloc[delta_months:, 0:0].index
    return beta
betas = beta(cc_returns, index_cc_returns, 12)

#Webapp
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
    elif pathname.lower() == '/beta':
        return webapp.beta
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
    plot.update(layout_showlegend=False)
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

@app.callback(Output('descriptive-statistics-table', 'children'),
              [Input('url', 'pathname')])
def update_descriptive_statistics_table(pathname):
    if pathname.lower() != '/descriptiveanalysis': return None
    df = pd.DataFrame(data ={
        'stock': [s['ticker'] for s in config.STOCKS],
        'mean': cc_returns.mean(axis=0).round(4),
        'variance': cc_returns.var(axis=0).round(4),
        'standard_deviation': cc_returns.std(axis=0).round(4),
        'skewness': cc_returns.skew(axis=0).round(4),
        'kurtosis': cc_returns.kurtosis(axis=0).round(4),
    })
    table = webapp.generate_descriptive_statistics_table(df)
    return table

@app.callback(Output('correlation-matrix-table', 'children'),
              [Input('url', 'pathname')])
def update_correlation_matrix_table(pathname):
    if pathname.lower() != '/descriptiveanalysis': return None
    table = webapp.generate_correlation_matrix_table(cc_returns.corr().round(4))
    return table

@app.callback(Output('scatterplot-graph', 'figure'),
              [Input('scatterplot-stocks-checklist', 'value')])
def update_density_graph(stocks):
    if len(stocks) < 2: return {}
    plot = px.scatter_matrix(cc_returns[stocks], title='')
    return plot

#predictive_analysis
@app.callback(Output('forecast-graph', 'figure'),
              [Input('forecast-stock-dropdown', 'value'),
              Input('forecast-checklist', 'value'),
              Input('forecast-confidence-slider', 'value')])
def update_forecast_graph(stock, values, confidence):
    if stock == None: return {}
    df = cc_returns[[stock]].loc[:cc_returns_forecast.index[0],:]
    if 'observed' in values:
        df = cc_returns[[stock]]
    df.columns = ['Observed']
    plot = px.line(df, title='', color_discrete_sequence=[color_map[stock], 'Red'])
    if 'forecast' in values:
        df = df.join(cc_returns_forecast[[stock]], how='outer')
        df.columns = ['Observed', 'Forecast']
        plot = px.line(df, title='', color_discrete_sequence=[color_map[stock], 'Red'])
        confidece_interval = forecast[stock].conf_int(alpha=(1.0-confidence/100.0))
        upper = confidece_interval.iloc[:,1]
        lower = confidece_interval.iloc[:,0][::-1]
        plot.add_trace(go.Scatter(
            x=list(cc_returns_forecast.index)+list(cc_returns_forecast.index[::-1]),
            y=list(upper)+list(lower),
            fill='toself',
            fillcolor='rgba(255,0,0,0.2)',
            line_color='rgba(255,255,255,0)',
            showlegend=False,
        ))
    return plot
#portfolio management
@app.callback(Output('portfolio-weights-graph', 'figure'), 
              [Input('portfolio-realweights-checklist', 'value')])
def update_prt_weights_graph(real_weights):
    if real_weights == ['True']:
        df = prt_real_weights
    else:
        df = prt_weights
    df = pd.DataFrame(df, columns=['weight'])
    df['stock'] = df.index
    plot = px.pie(df, title='Weights', names='stock', values = 'weight',
                color_discrete_map=color_map, hole=0.4)
    return plot

@app.callback(Output('portfolio-details', 'children'), 
              [Input('url', 'pathname')])
def update_prt_details(pathname):
    if pathname.lower() != '/portfoliomanagement': return None
    return webapp.generate_portfolio_details(
        config.BUDGET, config.PREDICTION_PERIODS['L'], config.END,
        prt_principal, (prt_ret-1)*100, prt_risk, prt_sharpe)

#beta
@app.callback(Output('beta-graph', 'figure'), 
              [Input('url', 'pathname')])
def update_beta_graph(pathname):
    if pathname.lower() != '/beta': return {}
    plot = px.line(betas, color_discrete_map=color_map)
    plot.update_layout(
        title='',
        yaxis_title=None,
    )
    return plot




if __name__ == '__main__':
    app.run_server(debug=config.DEBUG)