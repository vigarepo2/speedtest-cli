import subprocess
import json
from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    return response

@app.route('/')
def index():
    return render_template('''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Website Speed Test</title><style>body {font-family: sans-serif;margin: 20px;}.speedtest-container {border: 1px solid #ddd;padding: 20px;border-radius: 5px;text-align: center;}.speedtest-button {background-color: #007bff;color: white;padding: 10px 20px;border: none;border-radius: 5px;cursor: pointer;}.speedtest-results {margin-top: 20px;}.speedtest-results h2 {font-size: 18px;margin-bottom: 10px;}.speedtest-results span {font-weight: bold;}</style></head><body><h1>Website Speed Test</h1><div class="speedtest-container"><button class="speedtest-button" id="speedtest-btn">Run Speed Test</button></div><div class="speedtest-results" id="speedtest-results"></div><script>document.getElementById('speedtest-btn').addEventListener('click', async () => {try {const response = await fetch('/speedtest', { method: 'POST' });if (!response.ok) {throw new Error('Speed test failed.');}const data = await response.json();const resultsDiv = document.getElementById('speedtest-results');if (data.error) {resultsDiv.innerHTML = `<p>${data.error}</p>`;return;}resultsDiv.innerHTML = `<h2>Speed Test Results</h2><p>Download Speed: <span>${data.download.toFixed(2)} Mbps</span></p><p>Upload Speed: <span>${data.upload.toFixed(2)} Mbps</span></p><p>Ping: <span>${data.ping.toFixed(2)} ms</span></p>`;} catch (error) {console.error('Speed test error:', error);const resultsDiv = document.getElementById('speedtest-results');resultsDiv.innerHTML = '<p>Speed test failed. Please try again later.</p>';}});</script></body></html>''')

@app.route('/speedtest', methods=['POST'])
def speedtest():
    try:
        process = subprocess.Popen(['speedtest-cli', '--json'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if stderr:
          return jsonify({'error': stderr.decode()})
        output = json.loads(stdout.decode())
        download = output.get('download') / 1000000 if output.get('download') else None
        upload = output.get('upload') / 1000000 if output.get('upload') else None
        ping = output.get('ping')

        if download is None or upload is None or ping is None:
          return jsonify({'error': 'Could not retrieve all speed test data.'})

        return jsonify({'download': download, 'upload': upload, 'ping': ping})
    except FileNotFoundError:
        return jsonify({'error': 'speedtest-cli is not installed. Please install it on the server.'})
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)
