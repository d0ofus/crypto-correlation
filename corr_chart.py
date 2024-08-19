import os
import sqlite3
import pandas as pd
import mplfinance as mpf

current_directory = os.path.dirname(__file__)
os.chdir(current_directory) 

def plot_overlay_charts(symbols, db_folder='databases', db_name='r_squared_matrix.db'):
    db_path = os.path.join(db_folder, db_name)
    conn = sqlite3.connect(db_path)
    ohlcv_data = {}
    
    for symbol in symbols:
        # Escape special characters in table names
        table_name = symbol.replace('/', '_').replace(':', '_')
        try:
            df = pd.read_sql(f"SELECT * FROM [{table_name}]", conn)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            ohlcv_data[symbol] = df
        except pd.io.sql.DatabaseError as e:
            print(f"Error loading data for {symbol}: {e}")
    
    conn.close()

    if not ohlcv_data:
        return

    # Use the first symbol as the base chart
    base_symbol = symbols[0]
    base_df = ohlcv_data[base_symbol]

    # Add the other symbols as overlays
    add_plot = []
    for symbol in symbols[1:]:
        overlay_df = ohlcv_data[symbol]
        add_plot.append(mpf.make_addplot(overlay_df['close'], secondary_y=True, ylabel=symbol))
        
    # Plotting the charts
    mpf.plot(base_df, type='candle', style='charles', title=f"Overlay Charts for {', '.join(symbols)}", ylabel='Price', addplot=add_plot, volume=False, show_nontrading=True)

# Example usage
symbols = ['BTC/USDT:USDT', 'ETH/USDT:USDT']
plot_overlay_charts(symbols)
