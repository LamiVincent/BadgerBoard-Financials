import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import pandas as pd
from IPython.display import display, HTML
from collections import defaultdict

def plot_my_stock_comparision(account,d_h1y, d_ib, addAll = True):
    for j in range(len(account)):
        #d_h1y[j]['Cumulative Return'].plot(label=account[j],figsize=(16,8))
        d_h1y[j]['Cumulative Return'].plot(label=d_ib[j]['longName'],figsize=(16,8))
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
            #label=account[column],
            label=dfi[column]['longName'],
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
 
def plot_equity_table(df_equities, df_etfs, df_others, width="1200px", height = "800px"):
    from IPython.display import display, HTML
    # Adjust display settings to make the output window bigger
    display(HTML("""
        <style>
            .output_html {
                max-width: width;  /* Adjust the max width as needed */
                max-height: height;  /* Adjust the max height as needed */
                overflow-y: scroll;  /* Add scrollbars if content exceeds height */
            }
        </style>
    """))

        # Show Equity Table with a title and spacing
    if 'df_equities' in locals() and not df_equities.empty:
        display(HTML("<br>"))  # Spacing
        display(HTML("<h3>Equity Table</h3>"))  # Title
        display(df_equities)  # Display the table

    # Show ETF Table with a title and spacing
    if 'df_etfs' in locals() and not df_etfs.empty:
        display(HTML("<br>"))  # Spacing
        display(HTML("<h3>ETF Table</h3>"))  # Title
        display(HTML(df_etfs.to_html(escape=False)))  # Display the table

    # Show Other Table with a title and spacing
    if 'df_others' in locals() and not df_others.empty:
        display(HTML("<br>"))  # Spacing
        display(HTML("<h3>Other Table</h3>"))  # Title
        display(df_others)  # Display the table

def map_country_to_region(country):
    europe = {"Germany","Deutschland", "Frankreich", "Schweiz", "Irland", "Niederlande", "Großbritannien", "Schweden", "Italien", "Spanien", "Dänemark", "Jersey"}
    if country in europe:
        return "Europe"
    if country in {"Canada","Kanada"}:
        return "Canada"
    if country in {"USA","United States"}:
        return "USA"
    return country

def map_sector_to_sector(sector):
    # normalize: lowercase and replace underscores with spaces
    normalized = sector.lower().replace("_", " ")
    
    mapping = {
        "basic materials": "Basic Materials",
        #"financial services": "Financial Services",
        #"technology": "Technology",
        #"consumer cyclical": "Consumer Cyclical",
        #"industrials": "Industrials",
    }
    
    return mapping.get(normalized, normalized.title())  # default: capitalize each word        
        
def plot_portfolio(df_my_portfolio, b2, etf_data):
    region_profits_losses = {}
    
    for i, entry in enumerate(df_my_portfolio):
        if 'symbol' not in entry or 'regularMarketPrice' not in entry:
            print(f"Skipping {entry.get('symbol', 'Unknown')} due to missing data.")
            continue
        
        symbol = entry['symbol']
        quote_type = entry.get('quoteType', '')
        current_price = entry['regularMarketPrice']
        
        # Find matching asset data
        symbol_data = next((item for item in b2 if item['symbol'] == symbol), None)
        if not symbol_data:
            continue
        
        purchase_price = symbol_data['purchase_price']
        num_equities = symbol_data['num_equities']
        profit_loss = (current_price - purchase_price) * num_equities
        
        if quote_type == 'CRYPTOCURRENCY':
            region = "Crypto"
            region_profits_losses[region] = region_profits_losses.get(region, 0) + profit_loss
        elif quote_type == 'MUTUALFUND':
            region = "Mutualfund"
            region_profits_losses[region] = region_profits_losses.get(region, 0) + profit_loss
        elif quote_type == 'ETF' and symbol in etf_data:
            # Handle ETFs: distribute profit/loss across regions
            for country_info in etf_data[symbol]:
                for country, percentage in country_info.items():
                    if country:
                        try:
                            weight = float(percentage.strip().replace(',', '.').replace('\xa0', '').strip().strip('%')) / 100
                            mapped_region = "Other" if country == "Sonstige" else map_country_to_region(country)
                            region_profits_losses[mapped_region] = region_profits_losses.get(mapped_region, 0) + (profit_loss * weight)
                        except ValueError:
                            print(f"Skipping invalid percentage value: {percentage} for {country}")
        else:
            # Regular stock: use its country
            region = map_country_to_region(entry.get('country', 'Unknown'))
            region_profits_losses[region] = region_profits_losses.get(region, 0) + profit_loss
    
    # Group all regions with less than 1% contribution into 'Others'
    def aggregate_small_contributions(profits_losses):
        total_profit_loss = sum(profits_losses.values())
        others_profit_loss = 0
        regions_to_remove = []
        
        for region, value in profits_losses.items():
            percentage = (value / total_profit_loss) * 100 if total_profit_loss != 0 else 0
            if abs(percentage) < 1:
                others_profit_loss += value
                regions_to_remove.append(region)
        
        # Remove small regions and add the "Others" category
        for region in regions_to_remove:
            del profits_losses[region]
        
        if others_profit_loss != 0:
            profits_losses["Other"] = profits_losses.get("Other", 0) + others_profit_loss

    # Aggregate small contributions for both profit/loss distributions
    aggregate_small_contributions(region_profits_losses)
    
    # Plot results
    region_labels = list(region_profits_losses.keys())
    region_values = list(region_profits_losses.values())
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(region_labels, region_values, color=['green' if x >= 0 else 'red' for x in region_values])
    
    ax.set_xlabel('Region')
    ax.set_ylabel('Profit / Loss (EUR)')
    ax.set_title('Portfolio Performance by Region')
    plt.xticks(rotation=45)
    plt.show()
    
def plot_country_distribution(df_my_portfolio, b2, etf_data):
    initial_distribution = defaultdict(float)
    current_distribution = defaultdict(float)
    
    for entry in df_my_portfolio:
        if 'symbol' not in entry or 'regularMarketPrice' not in entry:
            continue
        
        symbol = entry['symbol']
        quote_type = entry.get('quoteType', '')
        current_price = entry['regularMarketPrice']
        
        symbol_data = next((item for item in b2 if item['symbol'] == symbol), None)
        if not symbol_data:
            continue
        
        purchase_price = symbol_data['purchase_price']
        num_equities = symbol_data['num_equities']
        initial_value = purchase_price * num_equities
        current_value = current_price * num_equities
        
        if quote_type == 'CRYPTOCURRENCY':
            region = "Crypto"
            initial_distribution[region] += initial_value
            current_distribution[region] += current_value
        elif quote_type == 'MUTUALFUND':
            region = "Mutualfund"
            initial_distribution[region] += initial_value
            current_distribution[region] += current_value
        elif quote_type == 'ETF' and symbol in etf_data:
            for country_info in etf_data[symbol]:
                for country, percentage in country_info.items():
                    if country:
                        try:
                            weight = float(percentage.strip().replace(',', '.').replace('\xa0', '').strip().strip('%')) / 100
                            mapped_region = "Other" if country == "Sonstige" else map_country_to_region(country)
                            initial_distribution[mapped_region] += initial_value * weight
                            current_distribution[mapped_region] += current_value * weight
                        except ValueError:
                            print(f"Skipping invalid percentage value: {percentage} for {country}")
        else:
            region = map_country_to_region(entry.get('country', 'Unknown'))
            initial_distribution[region] += initial_value
            current_distribution[region] += current_value
            
    # Group all regions with less than 1% contribution into 'Others'
    def aggregate_small_contributions(distribution):
        total = sum(distribution.values())
        others_contribution = 0
        regions_to_remove = []
        
        for region, value in distribution.items():
            percentage = (value / total) * 100
            if percentage < 1:
                others_contribution += value
                regions_to_remove.append(region)
        
        # Remove small regions and add the "Others" category
        for region in regions_to_remove:
            del distribution[region]
        
        if others_contribution > 0:
            distribution["Other"] += others_contribution

    aggregate_small_contributions(initial_distribution)
    aggregate_small_contributions(current_distribution)

    fig, axs = plt.subplots(1, 2, figsize=(14, 6))
    axs[0].pie(initial_distribution.values(), labels=initial_distribution.keys(), 
               autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    axs[0].axis('equal')  
    axs[0].set_title('Initial Portfolio Distribution (Based on Purchase Price)')

    axs[1].pie(current_distribution.values(), labels=current_distribution.keys(), 
               autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    axs[1].axis('equal')  
    axs[1].set_title('Current Portfolio Distribution (Based on Market Price)')

    plt.tight_layout()
    plt.show()

def get_sector_distribution(df_my_portfolio, b2):
    initial_distribution = defaultdict(float)
    current_distribution = defaultdict(float)
    
    for entry in df_my_portfolio:
        if 'symbol' not in entry or 'regularMarketPrice' not in entry:
            continue
        
        symbol = entry['symbol']
        quote_type = entry.get('quoteType', '')
        current_price = entry['regularMarketPrice']
        
        symbol_data = next((item for item in b2 if item['symbol'] == symbol), None)
        if not symbol_data:
            continue
        
        purchase_price = symbol_data['purchase_price']
        num_equities = symbol_data['num_equities']
        initial_value = purchase_price * num_equities
        current_value = current_price * num_equities
        
        if quote_type == 'CRYPTOCURRENCY':
            sector = "Cryptocurrency"
            initial_distribution[sector] += initial_value
            current_distribution[sector] += current_value
        elif quote_type == 'MUTUALFUND':
            sector = "Mutualfund"
            initial_distribution[sector] += initial_value
            current_distribution[sector] += current_value
        elif quote_type == 'ETF':
            etf_data = yf.Ticker(symbol).funds_data.sector_weightings
            for sector, weight in etf_data.items():  # iterate directly over items
                try:
                    #weight = float(percentage.strip().replace(',', '.').replace('\xa0', '').strip().strip('%')) / 100
                    mapped_sector = map_sector_to_sector(sector)
                    initial_distribution[mapped_sector] += initial_value * weight
                    current_distribution[mapped_sector] += current_value * weight
                except TypeError:
                    print(f"Skipping invalid weight value: {weight} for {sector}")
            #for sector_info in etf_data:
            #    for sector, percentage in sector_info.items():
            #        try:
            #            weight = float(percentage.strip().replace(',', '.').strip('%')) / 100
            #            initial_distribution[sector] += initial_value * weight
            #            current_distribution[sector] += current_value * weight
            #        except ValueError:
            #            print(f"Skipping invalid percentage value: {percentage} for {sector}")
        else:
            sector = entry.get('sector', 'Unknown')
            initial_distribution[sector] += initial_value
            current_distribution[sector] += current_value
    
    def aggregate_small_contributions(distribution):
        total = sum(distribution.values())
        others_contribution = 0
        regions_to_remove = []
        
        for sector, value in distribution.items():
            percentage = (value / total) * 100
            if percentage < 1:
                others_contribution += value
                regions_to_remove.append(sector)
        
        for sector in regions_to_remove:
            del distribution[sector]
        
        if others_contribution > 0:
            distribution["Other"] += others_contribution
    
    aggregate_small_contributions(initial_distribution)
    aggregate_small_contributions(current_distribution)
    
    fig, axs = plt.subplots(1, 2, figsize=(14, 6))
    axs[0].pie(initial_distribution.values(), labels=initial_distribution.keys(), 
               autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    axs[0].axis('equal')  
    axs[0].set_title('Initial Portfolio Sector Distribution')
    
    axs[1].pie(current_distribution.values(), labels=current_distribution.keys(), 
               autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    axs[1].axis('equal')  
    axs[1].set_title('Current Portfolio Sector Distribution')
    
    plt.tight_layout()
    plt.show()


