import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import pandas as pd

def plot_my_stock_comparision(account,d_h1y, addAll = True):
    for j in range(len(account)):
        d_h1y[j]['Cumulative Return'].plot(label=account[j],figsize=(16,8))
        plt.legend()

def multi_plot3(dfi, dfh, title, account, addAll=True):
    data = []
    for j in range(len(account)):   
        # Calculate necessary stuff for volume profile
        hist, bin_edges = np.histogram(dfh[j]['Close'], bins=100, range=(dfh[j]['Close'].min(), dfh[j]['Close'].max()))
        bin_mids = 0.5*(bin_edges[1:] + bin_edges[:-1])
        volume_profile = np.zeros_like(bin_mids)
        for i in range(len(bin_mids)):
            volume_profile[i] = dfh[j]['Volume'][(dfh[j]['Close'] > bin_edges[i]) & (dfh[j]['Close'] < bin_edges[i+1])].sum()


        # Add traces for the main plot (Candlestick, volume, moving averages)
        trace1 = go.Candlestick(
            x=dfh[j].index,
            open=dfh[j]['Open'], high=dfh[j]['High'],
            low=dfh[j]['Low'], close=dfh[j]['Close'],
            visible=False
        )
        trace2 = go.Bar(
            x=dfh[j].index,
            y=dfh[j]["Volume"], 
            name="Volume",
            visible=False,
            xaxis="x", yaxis="y2"
        )
        trace30 = go.Scatter(
            x=dfh[j].index,
            y=dfh[j]['MA20'],
            name='MA20', 
            line_color='darkorange',
            mode='lines', 
            line={'dash': 'solid'},
            visible=False,
            xaxis="x", yaxis="y"
        )
        trace31 = go.Scatter(
            x=dfh[j].index,
            y=dfh[j]['MA50'],
            name='MA50', 
            line_color='cornflowerblue',
            mode='lines', 
            line={'dash': 'solid'}, 
            visible=False, 
            xaxis="x", yaxis="y"
        )
        trace32 = go.Scatter(
            x=dfh[j].index,
            y=dfh[j]['MA200'],
            name='MA200', 
            line_color='darkblue',
            mode='lines', 
            line={'dash': 'solid'},
            visible=False, 
            xaxis="x", yaxis="y"
        )
        trace4 = go.Bar(
            x=volume_profile, 
            y=bin_mids, 
            name='Volume profile', 
            orientation='h',
            opacity=0.25,
            visible=False,
            xaxis="x2", yaxis="y"
        )

        # Add RSI trace
        trace_rsi = go.Scatter(
            x=dfh[j].index,
            y=dfh[j]['RSI'],
            name='RSI',
            line_color='purple',
            mode='lines',
            visible=False,
            xaxis="x", yaxis="y3"
        )

        # Add MACD Histogram and Signal Line
        trace_macd_hist = go.Bar(
            x=dfh[j].index,
            y=dfh[j]['MACD_hist'],
            name='MACD Histogram',
            marker=dict(color=dfh[j]['MACD_hist'].apply(lambda x: 'green' if x >= 0 else 'red')),
            visible=False,
            xaxis="x", yaxis="y4"
        )
        trace_macd_line = go.Scatter(
            x=dfh[j].index,
            y=dfh[j]['MACD'],
            name='MACD Line',
            line_color='blue',
            mode='lines',
            visible=False,
            xaxis="x", yaxis="y4"
        )
        trace_signal_line = go.Scatter(
            x=dfh[j].index,
            y=dfh[j]['Signal'],
            name='Signal Line',
            line_color='orange',
            mode='lines',
            visible=False,
            xaxis="x", yaxis="y4"
        )

        # Append all traces
        data += [trace1, trace2, trace30, trace31, trace32, trace4, trace_rsi, trace_macd_hist, trace_macd_line, trace_signal_line]

    
    # Layout adjustments to add a subplot for RSI below the main chart
    layout = go.Layout(
        width=1000,   # Adjust width as needed (default is usually 800)
        height=800,   # Adjust height as needed (default is usually 600)
        xaxis=dict(
            domain=[0, 1]
        ),
        yaxis=dict(
            domain=[0.45, 1]
        ),
        yaxis2=dict(
            domain=[0.32, 0.42],  # Volume axis is now positioned higher up
            title="Volume"#,
            #type="log"
        ),
        xaxis2=dict(
            domain=[0, 1],
            overlaying='x',
            side='top',
            autorange=True
        ),
        yaxis3=dict(
            domain=[0.2, 0.3],  # Set domain for RSI plot (lower part of the figure)
            title="RSI"
        ),
        yaxis4=dict(
            domain=[0.0, 0.18],  # Set domain for MACD plot
            title="MACD",
            showgrid=True
        )
    )

    nr_of_traces = 10  # Update the number of traces due to RSI

    # Create a boolean matrix for visibility control
    butt1 = np.zeros((len(account), len(account)*nr_of_traces), int)
    for j in range(len(account)):
        butt1[j][(nr_of_traces*j):(nr_of_traces*(j+1))] = 1
    
    # Create button options
    button_all = dict(
        label='None',
        method='update',
        args=[{'visible': list(butt1[0] == 1),
               'title': 'None',
               'showlegend': True}]
    )

    def create_layout_button(column):
        return dict(
            label=account[column],
            method='update',
            args=[{'visible': list(butt1[column] == 1),
                   'title': account[column],
                   'showlegend': False}]
        )

    fig = go.Figure(data=data, layout=layout)
    fig.update_layout(
        updatemenus=[go.layout.Updatemenu(
            active=0,
            buttons=[button_all] * addAll + [create_layout_button(column) for column in range(len(account))],
            direction="down",
            pad={"r": 10, "t": 10},
            showactive=True,
            x=1.05, xanchor="right",
            y=1.2, yanchor="top")
        ]
    )
    fig.update_layout(
        title_text=title,
        yaxis=dict(autorange=True),
        hovermode="x unified",
    )
    fig.update_xaxes(
        rangeslider_visible=False,
        rangeselector=dict(
            buttons=list([dict(count=1, label="1m", step="month", stepmode="backward"),
                          dict(count=3, label="3m", step="month", stepmode="backward"),
                          dict(count=6, label="6m", step="month", stepmode="backward"),
                          dict(count=1, label="YTD", step="year", stepmode="todate"),
                          dict(count=1, label="1y", step="year", stepmode="backward"),
                          dict(step="all")])
        ),
        rangebreaks=[dict(bounds=["sat", "mon"]),  # hide weekends
                     dict(values=["2015-12-25", "2016-01-01"])]  # hide holidays
    )
    
    fig.show()
