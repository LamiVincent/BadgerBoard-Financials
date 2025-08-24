#!/usr/bin/env python
# coding: utf-8

import numpy as np
import yfinance as yf
import pandas as pd
import os
from datetime import timedelta

def style_table(df):
    return df.style \
        .set_properties(**{'text-align': 'center'}) \
        .set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}]) \
        .format({
            'Mean [%]': '{:.2f}%',
            '3xStd [%]': '{:.2f}%',
            'Book Value': '{:.2f}',
            'KGV': '{:.2f}',
            'Last RSI': '{:.2f}'
        }) \
        .bar(subset=['Mean [%]', '3xStd [%]'], color='#FFA07A')  # Adds a bar visualization for these columns

def get_my_portfolio(account):
    df_my_portfolio = list(map(lambda x: yf.Ticker(x).info, account))
    return df_my_portfolio

def get_my_stock_variation2(account, d_h1y, d_ib, d_cal_EQI, d_qis_EQI, d_top_ETF):
    def xstr(s):
        return '' if s is None else str(s)

    def get_my_stock_mean(x):
        return round(100 * (x.mean()), 2)

    def get_my_stock_stdv(x):
        return round(300 * (x['returns'].std()), 2)

    def KGV(j, d_ib):
        if 'trailingEps' in d_ib[j]:
            price = d_ib[j].get('currentPrice', d_ib[j].get('regularMarketPrice', 0))
            return round(price / d_ib[j]['trailingEps'], 2)
        return None
    
    def fKGV(j, d_ib):
        if 'forwardEps' in d_ib[j]:
            price = d_ib[j].get('currentPrice', d_ib[j].get('regularMarketPrice', 0))
            return round(price / d_ib[j]['forwardEps'], 2)
        return None

    def bookValue(j, d_ib):
        return d_ib[j].get('bookValue')

    def Sector(j, d_ib):
        return d_ib[j].get('sector')

    def Industry(j, d_ib):
        return d_ib[j].get('industry')

    def Type(j, d_ib):
        return d_ib[j].get('quoteType')

    def LastRSI(j, d_h1y):
        return round(d_h1y[j].get('RSI').iloc[-1], 2)

    def Currency(j, d_ib):
        return xstr(d_ib[j].get('currency')) + "/" + xstr(d_ib[j].get('financialCurrency'))
    
    def last_earnings_date(j, d_qis_EQI):
        # Extract the name of the first column in d_qis_EQI (representing the earnings date)
        if len(d_qis_EQI[j]) > 0:
            return d_qis_EQI[j].columns[0].strftime('%d.%m.%Y')  # The first column in the quarterly income statement is the earnings date
        return None
    
    # Initialize tables
    data_equities = []
    data_etfs = []
    data_other = []

    for j in range(len(account)):
        asset_type = Type(j, d_ib)
        row = [account[j], d_ib[j].get('shortName'), asset_type, Currency(j, d_ib), 
               get_my_stock_mean(d_h1y[j]['returns']), get_my_stock_stdv(d_h1y[j]), LastRSI(j, d_h1y)]
        
        if asset_type == "EQUITY":
            # Get earnings date in German format
            next_earnings_date = ""
            if isinstance(d_cal_EQI[j], dict) and 'Earnings Date' in d_cal_EQI[j] and len(d_cal_EQI[j]['Earnings Date']) > 0:
                next_earnings_date = pd.to_datetime(d_cal_EQI[j]['Earnings Date'][0]).strftime('%d.%m.%Y')


            # Extract financial data from quarterly income statement
            if not d_qis_EQI[j].empty:
                first_col = d_qis_EQI[j].iloc[:, 0]
                second_col = d_qis_EQI[j].iloc[:, 1] if d_qis_EQI[j].shape[1] > 1 else None

                def get_value_change(key):
                    if key in first_col:
                        if pd.isna(first_col[key]):
                            value = "N/A"  # Return a default value or placeholder
                        else:
                            #value = round(first_col[key], 0)
                            value = int(first_col[key])  # Convert to integer to avoid decimals
                            value = f"{value} Mio"
                        change = ""
                        if second_col is not None and key in second_col:
                            if second_col[key]==0:
                                change = 100
                                change = f"{change}%"  # Add percentage sign to the change
                            else:
                                change = round(100 * (first_col[key] - second_col[key]) / second_col[key], 2)
                                change = f"{change}%"  # Add percentage sign to the change
                        return value, change
                    return None, None

                total_revenue, rev_change = get_value_change("Total Revenue")
                gross_profit, profit_change = get_value_change("Gross Profit")
                ebit, ebit_change = get_value_change("EBIT")
            else:
                total_revenue = gross_profit = ebit = rev_change = profit_change = ebit_change = None

            data_equities.append(row + [Sector(j, d_ib), Industry(j, d_ib), bookValue(j, d_ib), KGV(j, d_ib), fKGV(j, d_ib),
                                        last_earnings_date(j, d_qis_EQI), next_earnings_date, total_revenue, rev_change, gross_profit,                                               profit_change, ebit, ebit_change])
            
        elif asset_type == "ETF":
            # Format top holdings as a readable string
            top_holdings = ""
            #if not d_top_ETF[j].empty:
            if len(d_top_ETF[j]) > 0:
                top_holdings = "<br>".join([f"{row['Name']} (<b>{round(row['Holding Percent']*100, 2)}%</b>)" 
                                  for _, row in d_top_ETF[j].iterrows()][:10])  # Only show top 10
                
            data_etfs.append(row + [top_holdings])

        else:
            data_other.append(row)

    # Convert to DataFrame
    df_equities = pd.DataFrame(data_equities, columns=['Ticker', 'Short Name', 'Type', 'Currency', 'Mean [%]', 
                                                       '3xStd [%]', 'Last RSI', 'Sector', 'Industry', 'Book Value', 
                                                       'KGV','f_KGV', 'Last Earnings Date','Next Earnings Date', 'Total Revenue', 'Rev % Change', 
                                                       'Gross Profit', 'Profit % Change', 'EBIT', 'EBIT % Change'])
    
    df_etfs = pd.DataFrame(data_etfs, columns=['Ticker', 'Short Name', 'Type', 'Currency', 'Mean [%]', 
                                               '3xStd [%]', 'Last RSI', 'Top Holdings'])
    
    df_other = pd.DataFrame(data_other, columns=['Ticker', 'Short Name', 'Type', 'Currency', 'Mean [%]', 
                                                 '3xStd [%]', 'Last RSI'])

    return df_equities, df_etfs, df_other

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
                return round(d_ib[j]['currentPrice']/d_ib[j]['trailingEps'],2)
            else:
                return round(d_ib[j].get('regularMarketPrice',0)/d_ib[j]['trailingEps'],2)
    def bookValue(j,d_ib):
        return d_ib[j].get('bookValue')
    def Sector(j,d_ib):
        return d_ib[j].get('sector')
    def Industry(j,d_ib):
        return d_ib[j].get('industry')
    def Type(j,d_ib):
        return d_ib[j].get('quoteType')
    def LastRSI(j,d_h1y):
        return round(d_h1y[j].get('RSI').iloc[-1],2)
    def Currency(j,d_h1y):
        return xstr(d_ib[j].get('currency'))+"/"+xstr(d_ib[j].get('financialCurrency'))

    data1 = []
    for j in range(len(account)):
        data1 = data1 + [[account[j], d_ib[j].get('shortName'), Type(j,d_ib), Sector(j,d_ib), Industry(j,d_ib), Currency(j,d_h1y), get_my_stock_mean(d_h1y[j]['returns']), get_my_stock_stdv(d_h1y[j]), bookValue(j,d_ib), KGV(j,d_ib),LastRSI(j,d_h1y)]]
    data01 = pd.DataFrame(data1,columns=['Ticker','Short Name','Type','Sector','Industry','Currency Equity/Company','Mean [%]','3xStd [%]','Book Value','KGV','Last RSI'])
    return data01

def get_my_stock_data(account, period_p, span12=12, span26=26, span9=9, addAll = True):
    d_ib = list(map(lambda ticker2: yf.Ticker(ticker2).info, account))
    
    # Get calendar and quearterly income statements for EQUITYs
    d_cal_EQI = list(map(lambda j_ticker: yf.Ticker(j_ticker[1]).calendar if d_ib[j_ticker[0]].get('quoteType') == "EQUITY" else [], enumerate(account)))
    d_qis_EQI = list(map(lambda j_ticker: yf.Ticker(j_ticker[1]).quarterly_income_stmt/1000000 if d_ib[j_ticker[0]].get('quoteType') == "EQUITY" else [], enumerate(account)))
    # Get top holdings for ETFs
    #d_top_ETF = list(map(lambda j_ticker: yf.Ticker(j_ticker[1]).funds_data.top_holdings if d_ib[j_ticker[0]].get('quoteType') == "ETF" else [], enumerate(account)))
    
    def get_top_holdings(ticker):
        try:
            ticker_data = yf.Ticker(ticker)
            if ticker_data.info.get('quoteType') == "ETF":
                # Try to access top_holdings and handle if it fails
                try:
                    top_holdings = ticker_data.funds_data.top_holdings
                    if top_holdings is not None and len(top_holdings) > 0:
                        return top_holdings
                    else:
                        return []  # Return empty if top_holdings is None or empty
                except AttributeError as e:
                    print(f"AttributeError for {ticker}: {e}")
                    return []  # Return empty list if there's an error accessing top_holdings
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return []  # Return empty list if any other error occurs

    # Map the function to the tickers
    d_top_ETF = list(map(lambda j_ticker: get_top_holdings(j_ticker[1]), enumerate(account)))
    
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
            
    return d_ib, d_h1y, d_cal_EQI, d_qis_EQI, d_top_ETF

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

def income_statement_overview(which, d_ib, dfv, quarterly_income_statement):
    from IPython.display import display, HTML
    if 'quarterly_income_statement' in locals() and not quarterly_income_statement.empty:
        quarterly_income_statement.loc['EBITDA percentage'] = quarterly_income_statement.apply(lambda x: 100*x['EBITDA']/x['Total Revenue']).round(2)
    ttm = quarterly_income_statement.iloc[:, 0:4].sum(axis=1)
    dfv.insert(0, "", ttm.round(3))
    if 'Total Revenue' in dfv.index and 'EBITDA' in dfv.index:
        dfv.loc['EBITDA percentage'] = dfv.apply(lambda x: 100*x['EBITDA']/x['Total Revenue']).round(2)
    display(HTML(d_ib[which]['shortName']))  # Title
    if 'quarterly_income_statement' in locals() and not quarterly_income_statement.empty:
        display(HTML("Quarterly income statement"))
        display(quarterly_income_statement.loc[['Total Revenue','Gross Profit','EBITDA','EBITDA percentage']]) #2,6,9,11)  # Display the table
    else:
        display(HTML("No quarterly income statement"))
    if 'dfv' in locals() and not dfv.empty:
        display(HTML("Yearly income statement"))
        listv=[];
        if 'Total Revenue' in dfv.index:
            listv=listv+['Total Revenue']
        if 'Gross Profit' in dfv.index:
            listv=listv+['Gross Profit']
        if 'EBIT' in dfv.index:
            listv=listv+['EBIT']
        if 'EBITDA' in dfv.index:
            listv=listv+['EBITDA']
        if 'EBITDA percentage' in dfv.index:
            listv=listv+['EBITDA percentage']
        display(dfv.loc[listv]) #2,6,9,11)  # Display the table
    else:
        display(HTML("No yearly income statement"))

def calculate_dividend_yield(dividends: pd.Series, market_price: float) -> float:
    """
    Calculate the dividend yield based on the past 12 months' dividends.
    
    :param dividends: A Pandas Series where the index is datetime (timezone-aware) and values are dividends.
    :param market_price: The current market price of the ETF.
    :return: The dividend yield as a percentage.
    """
    # Ensure today's timestamp has the same timezone as the index
    today = pd.Timestamp.now(tz=dividends.index.tz)

    # Calculate one year ago
    one_year_ago = today - timedelta(days=365)

    # Filter dividends from the last 12 months
    recent_dividends = dividends[dividends.index > one_year_ago]

    # Sum the dividends paid in the last year
    total_dividends = recent_dividends.sum()

    # Calculate dividend yield
    dividend_yield = (total_dividends / market_price) * 100  # Convert to percentage

    return dividend_yield

def calculate_dividends(df_my_portfolio, b2, etf_data):

    yield_percentages = []
    yield_EUR = []

    for entry in df_my_portfolio:
        if 'symbol' not in entry or 'regularMarketPrice' not in entry:
            yield_percentages.append(None)  # or 0, depending on preference
            yield_EUR.append(None) 
            continue

        symbol = entry['symbol']
        quote_type = entry.get('quoteType', '')
        current_price = entry['regularMarketPrice']

        symbol_data = next((item for item in b2 if item['symbol'] == symbol), None)
        if not symbol_data:
            yield_percentages.append(None)
            yield_EUR.append(None) 
            continue

        if quote_type in ['CRYPTOCURRENCY', 'MUTUALFUND']:
            yield_percentages.append(0)
            yield_EUR.append(0) 

        elif quote_type == 'ETF' and symbol in etf_data:
            dividends = yf.Ticker(symbol).dividends
            dividends.index = pd.to_datetime(dividends.index)  # ensure datetime
            dividends = dividends.tz_convert("Europe/Berlin")  # convert timezone
            y = calculate_dividend_yield(dividends, current_price)
            yield_percentages.append(y)
            yield_EUR.append(y*current_price/100)

        else:
            info = yf.Ticker(symbol).info
            y=info.get('dividendYield', 0)
            yield_percentages.append(y)
            yield_EUR.append(y*current_price/100)
    
    return yield_percentages, yield_EUR
