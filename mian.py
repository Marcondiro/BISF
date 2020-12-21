# -*- coding: utf-8 -*-s

#Config
import config

#Packages
import numpy as np
import pandas as pd
import pandas_datareader.data as web
import matplotlib as pltgi

def getStocks(STOCKS):
    #Carico i dati relativi alle azioni.
    #Se presenti in cache evito di scaricarli.
    for stock in STOCKS:
        print(stock)

getStocks(config.STOCKS)