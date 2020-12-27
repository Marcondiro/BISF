# -*- coding: utf-8 -*-s
#%%
#Config
import config

#Packages
from pathlib import Path
import numpy as np
import pandas as pd
import pandas_datareader.data as web
import matplotlib.pyplot as plt

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

stocks = getStocks(config.STOCKS, config.START, config.END)
SECTORS = set(config.SECTORS)
stocks_monthly = stocks.groupby(pd.Grouper(freq='M')).mean()

#Adj close
stocks_monthly.plot(grid=True, title='Raw data: Adjusted close')

#Returns
simple_returns = stocks_monthly - stocks_monthly.shift(1)
simple_returns.plot(grid=True, title='Simple returns')
cc_returns = np.log(stocks_monthly / stocks_monthly.shift(1))
cc_returns.plot(grid=True, title='CC returns')

#returns grouped by sector
fig, axes = plt.subplots(len(SECTORS), 1)
for i, sector in enumerate(SECTORS):
    sector_stocks = [ind for ind,s in enumerate(config.SECTORS) if s == sector]
    cc_returns.iloc[:, sector_stocks].plot(ax=axes[i], sharex=True, grid=True,
        title=sector)
plt.tight_layout()

#Diagnostic plots
#cc_returns.hist(bins = 10)