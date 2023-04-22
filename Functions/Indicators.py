#!/usr/bin/env python
# coding: utf-8

import numpy as np
import yfinance as yf
import pandas as pd


def get_my_stock_variation(account, d_h1y):
    def get_my_stock_mean(x):
        return round(100*(x.mean()),2)
    def get_my_stock_stdv(x):
        return round(300*(x['returns'].std()),2)
    
    data1 =[]
    for j in range(len(account)):
        data1 = data1 + [[account[j],get_my_stock_mean(d_h1y[j]['returns']),get_my_stock_stdv(d_h1y[j])]]
    data01 = pd.DataFrame(data1,columns=['Ticker','Mean [%]','3xStd [%]'])
    return data01

def get_my_stock_data(account, period_p, addAll = True):
    d_ib = list(map(lambda ticker2: yf.Ticker(ticker2).fast_info, account))
    d_h1y = list(map(lambda ticker2: yf.Ticker(ticker2).history(period=period_p), account)) 

    for j in range(len(account)):
        if bool(d_ib[j])==True:
            d_h1y[j]['MA20'] = d_h1y[j]['Close'].rolling(20).mean()
            d_h1y[j]['MA50'] = d_h1y[j]['Close'].rolling(50).mean()
            d_h1y[j]['MA200'] = d_h1y[j]['Close'].rolling(200).mean()
            d_h1y[j]['returns'] = d_h1y[j]['Close'].pct_change(1)
            d_h1y[j]['Cumulative Return'] = (1 + d_h1y[j]['returns']).cumprod()
            
    return d_ib, d_h1y