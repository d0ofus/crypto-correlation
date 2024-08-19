#TODO: Find tokens whose RS line is just starting to increase and recent RS is above that of BTC 

import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Define the exchanges you want to scan
exchanges = {
    'binance': ccxt.binance(),
    'bybit': ccxt.bybit()
}

# Define the symbols for Bitcoin and the perpetual contracts you want to scan
base_currency = 'BTC'
timeframe = '1w'  # Weekly timeframe

def get_perpetual_symbols(exchange):
    """
    Fetch all active perpetual contracts from the exchange.
    """
    markets = exchange.load_markets()
    perpetual_symbols = [symbol for symbol in markets if 'swap' in markets[symbol]['type']]
    return perpetual_symbols

def fetch_ohlcv(exchange, symbol, since):
    """
    Fetch historical OHLCV data from the exchange.
    """
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def calculate_performance(df, base_df):
    """
    Calculate the performance of a contract relative to Bitcoin.
    """
    # Calculate weekly returns
    df['return'] = df['close'].pct_change()
    base_df['return'] = base_df['close'].pct_change()
    
    # Calculate relative performance
    df['relative_performance'] = df['return'] - base_df['return']
    
    # Calculate total performance over the period
    total_performance = df['relative_performance'].sum()
    return total_performance

# Define the time period for the scan (last 30 days for example)
since = int((datetime.utcnow() - timedelta(days=30)).timestamp() * 1000)

# Retrieve Bitcoin data
bitcoin_df = {}
for exchange_name, exchange in exchanges.items():
    symbols = get_perpetual_symbols(exchange)
    btc_symbol = next((symbol for symbol in symbols if symbol.endswith('/BTC')), None)
    if btc_symbol:
        bitcoin_df[exchange_name] = fetch_ohlcv(exchange, btc_symbol, since)

# Scan all perpetual contracts for outperformance
results = []
for exchange_name, exchange in exchanges.items():
    symbols = get_perpetual_symbols(exchange)
    for symbol in symbols:
        if symbol.endswith('/BTC'):
            continue  # Skip BTC pairs for comparison
            
        df = fetch_ohlcv(exchange, symbol, since)
        if df is not None and exchange_name in bitcoin_df:
            base_df = bitcoin_df[exchange_name]
            performance = calculate_performance(df, base_df)
            results.append((exchange_name, symbol, performance))

# Sort and display results
results_sorted = sorted(results, key=lambda x: x[2], reverse=True)
for exchange_name, symbol, performance in results_sorted:
    print(f"Exchange: {exchange_name}, Symbol: {symbol}, Performance: {performance:.2%}")

