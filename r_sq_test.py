import os
import ccxt
import time
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression

current_directory = os.path.dirname(__file__)
os.chdir(current_directory) 

def process_r_squared_matrix():
    # Initialize the Binance exchange
    exchange = ccxt.binance()

    # Define global variables
    min_days = 20
    min_length = min_days * 24 * 12  # Minimum length of data required (20 days * 24 hours * 12 5-min intervals per hour)
    since = int((datetime.now() - timedelta(days=20)).timestamp() * 1000) # Get the timestamp for 20 days ago

    # Get the list of all trading pairs on Binance
    def get_trading_pairs():
        markets = exchange.load_markets()
        spot_pairs = [symbol for symbol in markets.keys() if '/USDT' in symbol and markets[symbol]['spot'] and markets[symbol]['active']]
        perp_pairs = [symbol for symbol in markets.keys() if '/USDT' in symbol and markets[symbol]['swap'] and markets[symbol]['active']]
        all_symbols = [symbol for symbol in markets.keys() if '/USDT' in symbol and markets[symbol]['active'] and '-' not in symbol]
        perp_tickers = {symbol.split(':')[0] for symbol in perp_pairs}
        filtered_spot_pairs = [symbol for symbol in spot_pairs if symbol not in perp_tickers]
        all_symbols_unique = filtered_spot_pairs + perp_pairs
        return all_symbols_unique

    def save_ohlcv_to_db(symbol, ohlcv_data, db_folder='databases', db_name='ohlcv_data.db'):
        os.makedirs(db_folder, exist_ok=True)
        db_path = os.path.join(db_folder, db_name)
        conn = sqlite3.connect(db_path)
        df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.to_sql(symbol.replace('/', '_'), conn, if_exists='replace', index=False)
        conn.close()

    def fetch_ohlcv(symbol, since, limit=500, db_folder='databases', db_name='ohlcv_data.db'):
        try:
            all_ohlcv = []
            while True:
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe='5m', since=since, limit=limit)
                if not ohlcv:
                    break
                all_ohlcv.extend(ohlcv)
                since = ohlcv[-1][0] + 1
                if len(ohlcv) < limit:
                    break
            save_ohlcv_to_db(symbol, all_ohlcv, db_folder, db_name)
            return all_ohlcv
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return []

    def calculate_r_squared_matrix(df):
        print(">>>>>> Processing R-Square Calculations")
        symbols = df.columns
        n = len(symbols)
        r_squared_matrix = pd.DataFrame(np.zeros((n, n)), index=symbols, columns=symbols)

        for i in range(n):
            for j in range(i, n):
                if i == j:
                    r_squared_matrix.iloc[i, j] = 1.0
                else:
                    x = df.iloc[:, i].values.reshape(-1, 1)
                    y = df.iloc[:, j].values
                    if len(x) == 0 or len(y) == 0:
                        continue
                    model = LinearRegression().fit(x, y)
                    r_squared = model.score(x, y)
                    r_squared_matrix.iloc[i, j] = r_squared
                    r_squared_matrix.iloc[j, i] = r_squared

        return r_squared_matrix

    def save_r_squared_matrix_to_db(r_squared_matrix, db_folder='databases', db_name='r_squared_matrix.db'):
        os.makedirs(db_folder, exist_ok=True)
        db_path = os.path.join(db_folder, db_name)
        conn = sqlite3.connect(db_path)
        r_squared_matrix.to_sql('r_squared_matrix', conn, if_exists='replace')
        print("R-Squared matrix inserted into SQL database")
        conn.close()

    # Main process
    print("======== Processing R-Square Matrix =========")
    start_time = time.time()

    data = {}
    symbols = get_trading_pairs()
    symbols_len = len(symbols)
    count = 0
    for symbol in symbols:
        count += 1
        ohlcv = fetch_ohlcv(symbol, since)
        if len(ohlcv) >= min_length:
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            data[symbol] = df['close'].values
            print(f"{count}/{symbols_len}: Added {symbol} to database")
        else:
            print(f"{count}/{symbols_len}: {symbol} dropped because it has not recorded {min_days} of trading days")

    data_trimmed = {symbol: prices[:min_length] for symbol, prices in data.items()}
    df = pd.DataFrame(data_trimmed).dropna(axis=1)
    r_squared_matrix = calculate_r_squared_matrix(df)
    save_r_squared_matrix_to_db(r_squared_matrix)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Time taken to generate r-squared matrix: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    process_r_squared_matrix()
