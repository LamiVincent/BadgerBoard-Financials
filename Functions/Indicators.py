#!/usr/bin/env python
# coding: utf-8

import numpy as np
import yfinance as yf
import pandas as pd
import os

def get_my_stock_variation(account, d_h1y, d_ib):
    def xstr(s):
        return '' if s is None else str(s)
    def get_my_stock_mean(x):
        return round(100*(x.mean()),2)
    def get_my_stock_stdv(x):
        return round(300*(x['returns'].std()),2)
    def KGV(j,d_ib):
        if 'trailingEps' in d_ib[j]:
            if 'currentPrice' in d_ib[j]:
                return d_ib[j]['currentPrice']/d_ib[j]['trailingEps']
            else:
                return d_ib[j].get('regularMarketPrice',0)/d_ib[j]['trailingEps']
    def bookValue(j,d_ib):
        return d_ib[j].get('bookValue')
    def Sector(j,d_ib):
        return d_ib[j].get('sector')
    def Industry(j,d_ib):
        return d_ib[j].get('industry')
    def Type(j,d_ib):
        return d_ib[j].get('quoteType')
    def LastRSI(j,d_h1y):
        return d_h1y[j].get('RSI').iloc[-1]
    def Currency(j,d_h1y):
        return xstr(d_ib[j].get('currency'))+"/"+xstr(d_ib[j].get('financialCurrency'))

    data1 = []
    for j in range(len(account)):
        data1 = data1 + [[account[j], d_ib[j].get('shortName'), Type(j,d_ib), Sector(j,d_ib), Industry(j,d_ib), Currency(j,d_h1y), get_my_stock_mean(d_h1y[j]['returns']), get_my_stock_stdv(d_h1y[j]), bookValue(j,d_ib), KGV(j,d_ib),LastRSI(j,d_h1y)]]
    data01 = pd.DataFrame(data1,columns=['Ticker','Short Name','Type','Sector','Industry','Currency Equity/Company','Mean [%]','3xStd [%]','Book Value','KGV','Last RSI'])
    return data01

def get_my_stock_data(account, period_p, span12=12, span26=26, span9=9, addAll = True):
    d_ib = list(map(lambda ticker2: yf.Ticker(ticker2).info, account))
    d_h1y = list(map(lambda ticker2: yf.Ticker(ticker2).history(period=period_p), account)) 

    for j in range(len(account)):
        if bool(d_ib[j])==True:
            d_h1y[j]['MA20'] = d_h1y[j]['Close'].rolling(20).mean()
            d_h1y[j]['MA50'] = d_h1y[j]['Close'].rolling(50).mean()
            d_h1y[j]['MA200'] = d_h1y[j]['Close'].rolling(200).mean()
            d_h1y[j]['returns'] = d_h1y[j]['Close'].pct_change(1)
            d_h1y[j]['Cumulative Return'] = (1 + d_h1y[j]['returns']).cumprod()
            # Calculate the RSI and add it as a new column in the DataFrame
            d_h1y[j]['RSI'] = calculate_rsi(d_h1y[j])
            
            # Calculate MACD and Signal Line
            d_h1y[j]['EMA12'] = d_h1y[j]['Close'].ewm(span=span12, adjust=False).mean()
            d_h1y[j]['EMA26'] = d_h1y[j]['Close'].ewm(span=span26, adjust=False).mean()
            d_h1y[j]['MACD'] = d_h1y[j]['EMA12'] - d_h1y[j]['EMA26']
            d_h1y[j]['Signal'] = d_h1y[j]['MACD'].ewm(span=span9, adjust=False).mean()
            d_h1y[j]['MACD_hist'] = d_h1y[j]['MACD'] - d_h1y[j]['Signal']
            
    return d_ib, d_h1y


def get_ema(data, period=0, column='Close'):
    data['ema' + str(period)] = data[column].ewm(ignore_na=False, min_periods=period, com=period, adjust=True).mean()
    
    return data

def get_macd(data, period_long=26, period_short=12, period_signal=9, column='Close'):
    remove_cols = []
    if not 'ema' + str(period_long) in data.columns:
        data = get_ema(data, period_long, column=column)
        remove_cols.append('ema' + str(period_long))

    if not 'ema' + str(period_short) in data.columns:
        data = get_ema(data, period_short, column=column)
        remove_cols.append('ema' + str(period_short))

    data['macd_val'] = data['ema' + str(period_short)] - data['ema' + str(period_long)]
    data['macd_signal_line'] = data['macd_val'].ewm(ignore_na=False, min_periods=0, com=period_signal, adjust=True).mean()

    data = data.drop(remove_cols, axis=1)
        
    return data


def calculate_rsi(data, window=14):
    """
    Calculate the Relative Strength Index (RSI) for a given DataFrame.
    
    Parameters:
    - data: DataFrame with a 'Close' column containing the closing prices
    - window: The period over which to calculate RSI (default is 14 days)
    
    Returns:
    - RSI: A pandas Series containing the RSI values
    """
    
    # Calculate daily price changes
    delta = data['Close'].diff()
    
    # Separate the gains (positive changes) and losses (negative changes)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # Calculate the average gain and loss over the specified window
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()
    
    # Calculate the relative strength (RS)
    rs = avg_gain / avg_loss
    
    # Calculate the RSI using the RS values
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

