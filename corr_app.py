from flask import Flask, jsonify
import subprocess
import os
import sqlite3
import pandas as pd

current_directory = os.path.dirname(__file__)
os.chdir(current_directory)

# venv_path = os.path.join(current_directory, '.venv', 'Scripts', 'python.exe')

app = Flask(__name__)

@app.route('/run-r-squared')
def run_r_squared():
    try:
        # Call the script to process the R-squared matrix
        result = subprocess.run(['python', 'r_sq_test.py'], capture_output=True, text=True)
        if result.returncode == 0:
            return jsonify({'status': 'success', 'output': result.stdout}), 200
        else:
            return jsonify({'status': 'error', 'output': result.stderr}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/test')
def test(db_folder='databases', db_name='test.db'):
    db_path = os.path.join(db_folder, db_name)
    conn = sqlite3.connect(db_path)
    r_squared_matrix = pd.read_sql('SELECT * FROM r_squared_matrix', conn, index_col='index')
    conn.close()

    print(r_squared_matrix.iloc[0])

    return jsonify({"status": "Test Initiated."})

@app.route('/')
def index():
    return "Service up and running!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
