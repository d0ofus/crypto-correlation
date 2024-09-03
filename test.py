import subprocess
import os
import sqlite3
import pandas as pd

current_directory = os.path.dirname(__file__)
os.chdir(current_directory)

venv_path = os.path.join(current_directory, '.venv', 'Scripts', 'python.exe')
result = subprocess.run([venv_path, 'r_sq_test.py'], capture_output=True, text=True)

print('Return Code:', result.returncode)
print('STDOUT:', result.stdout)
print('STDERR:', result.stderr)

# Test extraction from db
def load_r_squared_matrix_from_db(db_folder='databases', db_name='test.db'):
    db_path = os.path.join(db_folder, db_name)
    conn = sqlite3.connect(db_path)
    r_squared_matrix = pd.read_sql('SELECT * FROM r_squared_matrix', conn, index_col='index')
    conn.close()
    return r_squared_matrix

r_squared_matrix = load_r_squared_matrix_from_db()
print(r_squared_matrix.iloc[0])
