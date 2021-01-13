# -*- coding: utf-8 -*-s
#%%
#Config
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
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
from dash.dependencies import Input, Output

def getStocks(STOCKS, START, END):
    #Carico i dati relativi alle azioni. Se presenti in cache evito di scaricarli.
    #Creazione directory cache se non presente
    Path(config.CACHE_DIR).mkdir(parents=True, exist_ok=True)
    dataFrame = None
    for stock in STOCKS:
        try:
            #Lettura cache
            s = pd.read_csv(config.CACHE_DIR+stock+'_'+START+'_'+END+'.csv',
                index_col=0, parse_dates=True)
            print(stock + ' loaded from cache.')
        except:
            #se fallisce la lettura scarico da Yahoo! e salvo in cache
            s = web.get_data_yahoo(stock, START, END)
            s.to_csv(config.CACHE_DIR + stock + '_' + START +'_'+END+'.csv')
            print(stock + ' downloaded from Yahoo.')
        s = s[['Adj Close']]
        s.columns = [stock]
        if dataFrame is None:
            dataFrame = s
        else:
            dataFrame = dataFrame.join(s)
    return dataFrame

#Stocks
tickers = [s['ticker'] for s in config.STOCKS]
stocks = getStocks(tickers, config.START, config.END)
stocks_monthly = stocks.groupby(pd.Grouper(freq='M')).mean()

#Returns
simple_returns = stocks_monthly/stocks_monthly.shift(1) - 1
simple_returns = simple_returns.dropna()
cc_returns = np.log(stocks_monthly / stocks_monthly.shift(1))
cc_returns = cc_returns.dropna()

#Predictive analysis
#Scarico i dati per i periodi n (training) e m (test)
pred_raw_data = getStocks(tickers,
                          config.PREDICTION_PERIODS['N'],
                          config.PREDICTION_PERIODS['L'])
#Calcolo cc returns mensili
pred_raw_data = pred_raw_data.groupby(pd.Grouper(freq='M')).mean()
pred_raw_data = np.log(pred_raw_data/pred_raw_data.shift(1))
pred_raw_data = pred_raw_data.dropna()
#Divido training e test set
training_set = pred_raw_data[config.PREDICTION_PERIODS['N']:
                            config.PREDICTION_PERIODS['M']]
test_set = pred_raw_data[config.PREDICTION_PERIODS['M']:
                        config.PREDICTION_PERIODS['L']]
del pred_raw_data

#Scadenza tempo per la computazione
expire_time = pd.DateOffset(seconds=config.PREDICTION_LIMIT_SECONDS)
expire_time = pd.to_datetime("now") + expire_time

best_mse = pd.Series({s: np.inf for s in tickers})
best_results = pd.Series({s: None for s in tickers})
for arima_p in range(1, 11):
    for arima_q in range(1, 11):
        models = pd.Series(
            {s: sm.tsa.statespace.SARIMAX(training_set[s].append(test_set[s]),
                                        order=(arima_p, 0, arima_q),
                                        enforce_stationarity=False,
                                        enforce_invertibility=False)
            for s in tickers})
        results = pd.Series({s: models[s].fit() for s in tickers})
        pred = [r.get_prediction(start=test_set.index[0],
                                dynamic= False).predicted_mean
                for r in results]
        pred = pd.concat(pred, axis=1)
        pred.columns = tickers
        mse = pd.Series(((test_set - pred) ** 2).mean())
        #Salvo il modello corrente se è il migliore (mse minimo)
        best_mse = pd.concat([best_mse, mse], axis=1).min(axis=1)
        for s in tickers:
            if mse[s] == best_mse[s]:
                best_results[s] = results[s]
        #Se supero il tempo limite interrompo la grid search
        if pd.to_datetime("now") > expire_time :
            expire_time = -1
            print('Prediction time slice ended at p=', arima_p, 'q=', arima_q)
            break
    if expire_time == -1:
        break

forecast = pd.Series({s: best_results[s].get_forecast(steps=config.END)
                    for s in tickers})
cc_returns_forecast = [f.predicted_mean for f in forecast]
cc_returns_forecast = pd.concat(cc_returns_forecast, axis=1)
cc_returns_forecast.columns = tickers

#Portfolio optimization buy&hold L period (no dividends)
expect_returns = (np.e ** cc_returns_forecast).prod()
#Per avere una covarianza migliore utilizzo i dati giornalieri
cov_matrix = risk_models.sample_cov(stocks)
ef = EfficientFrontier(expect_returns, cov_matrix)
prt_weights = pd.Series(ef.max_sharpe())
prt_ret, prt_risk, prt_sharpe = ef.portfolio_performance()

buy_prices = stocks.loc[:config.PREDICTION_PERIODS['L'],:].iloc[-1,:]
buy_prices.name = 'BuyPrice'
buy_stocks_number = np.floor(config.BUDGET * prt_weights / buy_prices)
buy_stocks_number.name = 'Quantity'
prt_principal = (buy_prices*buy_stocks_number).sum()
prt_real_weights = buy_prices*buy_stocks_number/prt_principal
sell_prices = stocks.iloc[-1,:]
sell_prices.name = 'SellPrice'

#Beta
#Scarico i dati dell'indice di mercato
index = getStocks([config.MARKET_INDEX['ticker']], config.START, config.END)
index = index.groupby(pd.Grouper(freq='M')).mean()
index_cc_returns = np.log(index/index.shift(1))
#rimuovo NA e converto in serie
index_cc_returns = index_cc_returns.dropna()[index_cc_returns.columns[0]]

def beta(stocks_r, index_r, delta_months):
    beta = pd.DataFrame(columns=tickers)
    for i in range(delta_months, len(index_r)):
        b = {s: stocks_r[s][i-delta_months:i-1].cov(
                    index_r[i-delta_months:i-1])/
                index_r[i-delta_months:i-1].var()
            for s in stocks_r}
        b = pd.Series(b)
        beta = beta.append(b, ignore_index=True)
    beta.index = stocks_r.iloc[delta_months:,:].index
    return beta
betas = beta(cc_returns, index_cc_returns, 10)
#CAPM expected returns
market_returns = index_cc_returns[config.PREDICTION_PERIODS['L']:]
capm_ret = [betas.tail(len(market_returns))[s] * (market_returns -0.02) + 0.02
            for s in tickers]
capm_ret = pd.concat(capm_ret, axis=1)
capm_ret.columns = tickers
capm_ret = (np.e ** capm_ret).prod()

#Webapp
app = dash.Dash(title='BISF Project', external_stylesheets=webapp.css)
app.config.suppress_callback_exceptions = True
app.layout = webapp.layout

#Webapp callbacks
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
    plot = px.line(stocks_monthly[selected_dropdown_values],
                color_discrete_map=webapp.color_map)
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
        plot_stocks=[s['ticker'] for s in config.STOCKS if s['sector']==sector]
    else:
        plot_stocks = tickers
    if radio == 'simple':
        title = 'Simple returns'
        df = simple_returns
    else:
        title='Continuos compounded returns'
        df = cc_returns
    plot = px.line(df[plot_stocks], title=title,
                color_discrete_map=webapp.color_map)
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
    if stock == None:
        return {}
    plot = px.histogram(cc_returns[stock], nbins=bins,
                        title=stock+' cc returns distribution',
                        color_discrete_map=webapp.color_map)
    plot.update(layout_showlegend=False)
    return plot

@app.callback(Output('density-graph', 'figure'), 
              [Input('diagnostic-stock-dropdown', 'value')])
def update_density_graph(stock):
    if stock == None: return {}
    plot = ff.create_distplot([cc_returns[stock]], [stock], show_hist=False,
                            show_rug=False, colors=[webapp.color_map[stock]])
    plot.update(layout_showlegend=False)
    return plot

@app.callback(Output('boxplot-graph', 'figure'), 
              [Input('diagnostic-stock-dropdown', 'value'),
              Input('boxplot-showall', 'value'),])
def update_boxplot_graph(stock, show_all):
    if stock == None:
        return {}
    if show_all == ['True']:
        df = cc_returns
    else:
        df = cc_returns[[stock]]
    df = df.melt(var_name='stock')
    plot = px.box(df, y='value', x='stock', color='stock',
                color_discrete_map=webapp.color_map)
    plot.update(layout_showlegend=False)
    return plot

@app.callback(Output('qqplot-graph', 'figure'), 
              [Input('diagnostic-stock-dropdown', 'value')])
def update_qqplot_graph(stock):
    if stock == None:
        return {}
    qq = stats.probplot(cc_returns[stock])
    plot = px.scatter(x=qq[0][0], y=qq[0][1],
                    color_discrete_sequence=[webapp.color_map[stock]])
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
        'stock': tickers,
        'mean': cc_returns.mean(axis=0).round(4),
        'variance': cc_returns.var(axis=0).round(4),
        'standard_deviation': cc_returns.std(axis=0).round(4),
        'skewness': cc_returns.skew(axis=0).round(4),
        'kurtosis': cc_returns.kurtosis(axis=0).round(4),
    })
    return webapp.generate_descriptive_statistics_table(df)

@app.callback(Output('correlation-matrix-table', 'children'),
              [Input('url', 'pathname')])
def update_correlation_matrix_table(pathname):
    if pathname.lower() != '/descriptiveanalysis': return None
    return webapp.generate_correlation_matrix_table(cc_returns.corr().round(4))

@app.callback(Output('scatterplot-graph', 'figure'),
              [Input('scatterplot-stocks-checklist', 'value')])
def update_density_graph(stocks):
    if len(stocks) < 2:
        return {}
    plot = px.scatter_matrix(cc_returns[stocks], title='')
    return plot

#predictive_analysis
@app.callback(Output('forecast-graph', 'figure'),
              [Input('forecast-stock-dropdown', 'value'),
              Input('forecast-checklist', 'value'),
              Input('forecast-confidence-slider', 'value')])
def update_forecast_graph(stock, values, confidence):
    if stock == None:
        return {}
    df = cc_returns[[stock]].loc[:cc_returns_forecast.index[0],:]
    if 'observed' in values:
        df = cc_returns[[stock]]
    df.columns = ['Observed']
    plot = px.line(df, title=stock+' CC returns forecasting',
                color_discrete_sequence=[webapp.color_map[stock], 'Red'])
    if 'forecast' in values:
        df = df.join(cc_returns_forecast[[stock]], how='outer')
        df.columns = ['Observed', 'Forecast']
        plot = px.line(df, title=stock+' CC returns forecasting',
                color_discrete_sequence=[webapp.color_map[stock], 'Red'])
        conf_interval = forecast[stock].conf_int(alpha=(1.0-confidence/100.0))
        upper = conf_interval.iloc[:,1]
        lower = conf_interval.iloc[:,0][::-1]
        plot.add_trace(go.Scatter(
            x=list(cc_returns_forecast.index)+
                list(cc_returns_forecast.index[::-1]),
            y=list(upper)+list(lower),
            fill='toself',
            fillcolor='rgba(255,0,0,0.2)',
            line_color='rgba(255,255,255,0)',
            showlegend=False,
        ))
    return plot

#portfolio_management
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
                color_discrete_map=webapp.color_map, hole=0.4)
    return plot

@app.callback(Output('portfolio-details', 'children'), 
              [Input('url', 'pathname')])
def update_prt_details(pathname):
    if pathname.lower() != '/portfoliomanagement':
        return None
    return webapp.generate_portfolio_details(
        config.BUDGET, config.PREDICTION_PERIODS['L'], config.END,
        prt_principal, (prt_ret-1)*100, prt_risk, prt_sharpe)

@app.callback(Output('results-table', 'children'), 
              [Input('url', 'pathname')])
def update_results_table(pathname):
    if pathname.lower() != '/portfoliomanagement':
        return None
    df = pd.DataFrame([buy_prices, buy_stocks_number, sell_prices])
    return webapp.generate_results_table(df)

#beta
@app.callback(Output('beta-graph', 'figure'), 
              [Input('url', 'pathname')])
def update_beta_graph(pathname):
    if pathname.lower() != '/beta':
        return {}
    plot = px.line(betas, color_discrete_map=webapp.color_map)
    plot.update_layout(
        title='',
        yaxis_title=None,
    )
    return plot

@app.callback(Output('capm-table', 'children'), 
              [Input('url', 'pathname')])
def update_beta_graph(pathname):
    if pathname.lower() != '/beta': return {}
    df = pd.DataFrame([capm_ret, sell_prices/buy_prices])
    return webapp.generate_capm_table(df)

#if __name__ == '__main__':
#    app.run_server(debug=config.DEBUG)