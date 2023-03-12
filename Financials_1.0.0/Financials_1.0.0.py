#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Finance data by Python
#1. First of all, install the package yfinance. 
#2. Afterwards add ssl certificate by pip install certifi.

#Let's start with importing all we need:

import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')
import datetime

#Next, let us define my portfolio:
t_test = ['VGWL.F','AAPL','TSLA']

#d = yf.Ticker('VGWL.F').fast_info

# Get the data: 
#################
account = t_test # <-- Put in here the account of interest 
#################
period_p="2y"

d_ib = list(map(lambda ticker2: yf.Ticker(ticker2).fast_info, account))
d_h1y = list(map(lambda ticker2: yf.Ticker(ticker2).history(period=period_p), account)) 

# Documentation for yfinance: https://pypi.org/project/yfinance/

#Calculate the moving averages: 
for j in range(len(account)):
    if bool(d_ib[j])==True:
        d_h1y[j]['MA20'] = d_h1y[j]['Close'].rolling(20).mean()
        d_h1y[j]['MA50'] = d_h1y[j]['Close'].rolling(50).mean()
        d_h1y[j]['MA200'] = d_h1y[j]['Close'].rolling(200).mean()
        
# Cool Matplotlip cheatsheets: https://matplotlib.org/cheatsheets/

for j in range(len(account)): 
    if bool(d_ib[j])==True:
        d_h1y[j]['returns'] = d_h1y[j]['Close'].pct_change(1)
        d_h1y[j]['Cumulative Return'] = (1 + d_h1y[j]['returns']).cumprod()
        d_h1y[j]['Cumulative Return'].plot(label=account[j],figsize=(16,8))
        plt.legend()
        
# One could also start to apply statistical models and time series analysis to our data by statsmodels: https://www.statsmodels.org/stable/index.html
#import statsmodels.api as sm


# In[2]:


#Next, we want to check, how the returns ditributed in the last year, 
#and look at the distribution. This should give us an indication for 
#the volatility of this particular stock:

box_df = d_h1y[0]['returns']
box_dfc = [account[0]]
props = dict(facecolor='white', alpha=0.8, linewidth=0)

def get_recommendations(j):
    if all(k in d_ib[j] for k in ["recommendationKey","targetMeanPrice","currentPrice"]):
        if d_ib[j]["recommendationKey"]!="none" and d_ib[j]["targetMeanPrice"]!="None":
            price = d_ib[j]["last_price"]
            print(account[j],':\t',d_ib[j]["recommendationKey"],'with a pot. gain of:',round(100*d_ib[j]["targetMeanPrice"]/price-100,2),'%')
    else:
        print(account[j],':\tno reccomendations')

get_recommendations(0)
for j in range(len(account)-1):
    if bool(account[j+1])==True:
        box_df = pd.concat([box_df,d_h1y[j+1]['returns']],axis=1)
        box_dfc.append(account[j+1])
        get_recommendations(j+1)
box_df.columns = box_dfc
bp = box_df.plot(kind='box', figsize=(16,8))
for xtick in bp.get_xticks():
    if bool(account[xtick-1])==True:
        text_to = 'Mean: '+str(round(100*(d_h1y[xtick-1]['returns'].mean()),2))+' % \n3xStd: '+str(round(300*(d_h1y[xtick-1]['returns'].std()),2))+' %'
        bp.text(xtick-0.15,d_h1y[xtick-1]['returns'].mean()+min(box_df.max().max(),-box_df.min().min())*0.95*2*(xtick%2-0.5),text_to,bbox=props)


# In[3]:


import plotly.graph_objects as go

fig = go.Figure()
# Use x instead of y argument for horizontal plot
for j in range(len(account)):
    fig.add_trace(go.Box(y=d_h1y[j]['returns'], name=account[j]))

fig.update_layout(
    title='Box plot of returns',
    paper_bgcolor='rgb(243, 243, 243)',
    plot_bgcolor='rgb(243, 243, 243)',
    showlegend=False
)    

fig.show()


# In[4]:


import plotly.graph_objects as go
#from plotly.subplots import make_subplots

def multi_plot(dfi, dfh, title, addAll = True):
    data = []
    for j in range(len(account)):   
        #Calculate necessary stuff for volume profile:
        hist, bin_edges = np.histogram(dfh[j]['Close'], bins=100, range=(dfh[j]['Close'].min(), dfh[j]['Close'].max()))
        bin_mids = 0.5*(bin_edges[1:] + bin_edges[:-1])
        volume_profile = np.zeros_like(bin_mids)
        for i in range(len(bin_mids)):
            volume_profile[i] = dfh[j]['Volume'][(dfh[j]['Close'] > bin_edges[i]) & (dfh[j]['Close'] < bin_edges[i+1])].sum()
        # Add traces which will be present on the plot:
        trace1 = go.Candlestick(
            x=dfh[j].index,
            open=dfh[j]['Open'], high=dfh[j]['High'],
            low=dfh[j]['Low'], close=dfh[j]['Close'],
            visible = False
        )
        trace2 = go.Bar(
            x=dfh[j].index,
            y=dfh[j]["Volume"], 
            name="Volume",
            visible = False,
            xaxis="x", yaxis="y2"
        )
        trace30 = go.Scatter(
            x=dfh[j].index,
            y=dfh[j]['MA20'],
            name='MA20', 
            line_color='darkorange',
            mode = 'lines', 
            line={'dash': 'solid'},
            visible = False,
            xaxis="x", yaxis="y"
        )
        trace31 = go.Scatter(
            x=dfh[j].index,
            y=dfh[j]['MA50'],
            name='MA50', 
            line_color='cornflowerblue',
            mode = 'lines', 
            line={'dash': 'solid'}, 
            visible = False, 
            xaxis="x", yaxis="y"
        )
        trace32 = go.Scatter(
            x=dfh[j].index,
            y=dfh[j]['MA200'],
            name='MA200', 
            line_color = 'darkblue',
            mode = 'lines', 
            line={'dash': 'solid'},
            visible = False, 
            xaxis="x", yaxis="y"
        )
        trace4 = go.Bar(
            x=volume_profile, 
            y=bin_mids, 
            name='Volume profile', 
            orientation='h',
            opacity=0.25,
            visible = False,
            xaxis="x2", yaxis="y"
        )
        data = data + [trace1,trace2,trace30,trace31,trace32,trace4]
    
    layout = go.Layout(
        xaxis=dict(
            domain=[0, 1]
        ),
        yaxis=dict(
            domain=[0.3, 1]
        ),
        yaxis2=dict(
            domain=[0, 0.25]
        ),
        xaxis2=dict(
            domain=[0, 1],
            #anchor='free', 
            overlaying='x',
            side='top',
            autorange=True
        ),
        yaxis3=dict(
            domain=[0.4, 1]
        )
    )
    nr_of_traces = 6
    #Create a boolean matrix
    butt1 = np.zeros((len(account),len(account)*nr_of_traces),int)
    for j in range(len(account)):
        butt1[j][(nr_of_traces*j):(nr_of_traces*(j+1))]=1
    
    #Create button options
    button_all = dict(label = 'None',
                      method = 'update',
                      args = [{'visible': list(butt1[0]==1),
                               'title': 'None',
                               'showlegend':True}])

    def create_layout_button(column):
        return dict(label = account[column],
                    method = 'update',
                    args = [{'visible': list(butt1[column]==1),
                             'title': account[column],
                             'showlegend': False}])
    
    fig = go.Figure(data=data, layout=layout)
    fig.update_layout(
        updatemenus=[go.layout.Updatemenu(
            active = 0,
            buttons = ([button_all] * addAll) + list(map(lambda column: create_layout_button(column), list(range(len(account))))),
            direction="down",
            pad={"r": 10, "t": 10},
            showactive=True,
            x=1.05, xanchor="right",
            y=1.2, yanchor="top")
        ]
    )
    fig.update_layout(
        title_text=title,
        yaxis = dict(autorange=True),
        hovermode="x unified",
        )
    fig.update_xaxes(
        rangeslider_visible=False,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=3, label="3m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])),
        rangebreaks=[
            dict(bounds=["sat", "mon"]), #hide weekends
            dict(values=["2015-12-25", "2016-01-01"])  # hide Christmas and New Year's
        ])
    fig.show()  
    
multi_plot(dfi = d_ib,dfh = d_h1y, title="Charts")


# In[ ]:




