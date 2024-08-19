import os
import sqlite3
import pandas as pd
import tkinter as tk
from tkinter import ttk
from corr_chart import plot_overlay_charts

# TODO: Create corr charts function

current_directory = os.path.dirname(__file__)
os.chdir(current_directory) 

print("Initializing R-Squared Query GUI")

# Load the R-squared matrix from SQLite database
def load_r_squared_matrix_from_db(db_folder='databases', db_name='r_squared_matrix.db'):
    db_path = os.path.join(db_folder, db_name)
    conn = sqlite3.connect(db_path)
    r_squared_matrix = pd.read_sql('SELECT * FROM r_squared_matrix', conn, index_col='index')
    conn.close()
    return r_squared_matrix

# Function to get top correlated tokens
def get_top_correlated_tokens(token, r_squared_matrix, top_n=10):
    if token not in r_squared_matrix.columns:
        return False
    correlations = r_squared_matrix[token].sort_values(ascending=False)
    top_correlated_tokens = correlations.index[1:top_n+1].tolist()
    top_r_squared_values = correlations.iloc[1:top_n+1].tolist()
    return list(zip(top_correlated_tokens, top_r_squared_values))

# Load the R-squared matrix
r_squared_matrix = load_r_squared_matrix_from_db()

# Create the GUI
root = tk.Tk()
root.title("Top Correlated Tokens")

# Function to update the dropdown values based on input when 'Enter' is pressed
def update_dropdown(event):
    input_text = selected_token.get()
    filtered_values = [symbol for symbol in all_symbols if input_text.lower() in symbol.lower()]
    dropdown['values'] = filtered_values
    dropdown.event_generate("<Down>")  # Open the dropdown list

# Dropdown menu for selecting a token
selected_token = tk.StringVar()
all_symbols = r_squared_matrix.columns.tolist()
dropdown = ttk.Combobox(root, textvariable=selected_token)
dropdown['values'] = all_symbols
dropdown.grid(column=0, row=0)
dropdown.bind('<Return>', update_dropdown)  # Bind the update function to 'Enter' key press event

# Text widget to display the results
result_text = tk.Text(root, height=10, width=50)
result_text.grid(column=0, row=1)

# Function to update the results
def update_results(event):
    token = selected_token.get()
    top_correlated_tokens = get_top_correlated_tokens(token, r_squared_matrix)
    if top_correlated_tokens:
        result_text.delete('1.0', tk.END)
        result_text.insert(tk.END, f"Top {len(top_correlated_tokens)} tokens most correlated with {token}:\n")
        for correlated_token, r_squared in top_correlated_tokens:
            result_text.insert(tk.END, f"{correlated_token}: R-squared = {r_squared:.4f}\n")
    else:
        result_text.delete('1.0', tk.END)
        result_text.insert(tk.END, f"{token} not found in R-squared matrix")

# Bind the dropdown selection event to the update function
dropdown.bind("<<ComboboxSelected>>", update_results)

# Button to plot overlay charts
def plot_charts():
    token = selected_token.get()
    top_correlated_tokens = get_top_correlated_tokens(token, r_squared_matrix)
    if top_correlated_tokens:
        symbols = [token] + [t[0] for t in top_correlated_tokens]
        plot_overlay_charts(symbols)

plot_button = tk.Button(root, text="Plot Chart", command=plot_charts)
plot_button.grid(column=0, row=2)

root.mainloop()
