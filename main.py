# -*- coding: utf-8 -*-s
#%%

#Config
import config

#Packages
import numpy as np
import pandas as pd
import pandas_datareader.data as web
import matplotlib as pltgi

def getStocks(STOCKS, START, END):
    #Carico i dati relativi alle azioni.
    #Se presenti in cache evito di scaricarli.
    CACHE_DIR = "./stocks_cache/"
    dataFrame = None
    for stock in STOCKS:
        try:
            s = pd.read_csv(CACHE_DIR+stock+"_"+START+"_"+END+'.csv')
            print(stock + " loaded from cache.")
        except:
            s = web.get_data_yahoo(stock, START, END)
            s.to_csv(CACHE_DIR + stock + "_" + START +"_"+END+'.csv')
            print(stock + " downloaded from Yahoo.")
        s.index =  s.Date
        s = s[["Adj Close"]]
        s.columns = s.columns + "_" + stock
        if dataFrame is None:
            dataFrame = s
        else:
            dataFrame = dataFrame.join(s)
    return dataFrame

dataFrame = getStocks(config.STOCKS, config.START, config.END)
dataFrame.plot()