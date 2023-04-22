#!/usr/bin/env python
# coding: utf-8

import numpy as np
import yfinance as yf
import pandas as pd
import os

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

def update_local_version(path_current_version, filename_func1, filename_func2):

    #Get the current version of the function files on this iPad
    ###############################################################################
    import requests

    #path_current_version = 'Current_version.py'

    if os.path.exists("Functions/" + path_current_version)==True:
        current_version = open(path_current_version,'r').readline()
    else:
        current_version = 0

    repo_name = "LamiVincent/BadgerBoard-Financials" 

    url_version = f"https://api.github.com/repos/{repo_name}/releases/latest"
    response = requests.get(url_version)

    if response.status_code == 200:
        release_info = response.json()
        version = release_info["tag_name"]
        #print(f"The latest release version of {repo_name} is {version}.")
    else:
        version = current_version
        #print(f"Failed to retrieve latest release version. Status code: {response.status_code}")

    #filename_func1 = "indicators_LamiVincent.py"
    #filename_func2 = "plots_LamiVincent.py"

    if (current_version!=version) and (current_version!=0):
        url_git = "https://raw.githubusercontent.com/"
        url_LamiVincent = url_git + repo_name
        LamiVincent_indicators = "/main/Functions/Indicators.py"
        LamiVincent_plots = "/main/Functions/Plots.py"

        r2 = requests.get(url_LamiVincent + LamiVincent_indicators,allow_redirects=True)
        r3 = requests.get(url_LamiVincent + LamiVincent_plots,allow_redirects=True)

        open('Functions/' + filename_func1,'wb').write(r2.content)
        open('Functions/' + filename_func2,'wb').write(r3.content)
        open('Functions/Current_version.py','wb').write(bytes(version,"utf-8"))

    ###############################################################################
