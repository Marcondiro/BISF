# -*- coding: utf-8 -*-s

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
    data = {}
    for stock in STOCKS:
        try:
            data[stock] = pd.read_csv("./stocks_cache/" + stock +"_"+ START +
                "_" + END + '.csv')
        except:
            data[stock] = web.get_data_yahoo(stock, START, END)
            data[stock].to_csv()
        print(data[stock])

getStocks(config.STOCKS, config.START, config.END)