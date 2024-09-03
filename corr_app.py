from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

@app.route('/run-r-squared', methods=['POST'])
def run_r_squared():
    try:
        # Call the script to process the R-squared matrix
        result = subprocess.run(['python', 'r_sq.py'], capture_output=True, text=True)
        if result.returncode == 0:
            return jsonify({'status': 'success', 'output': result.stdout}), 200
        else:
            return jsonify({'status': 'error', 'output': result.stderr}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
