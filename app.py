import subprocess
import json
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    return response

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Website Speed Test</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN" crossorigin="anonymous">
    <style>
        body {font-family: sans-serif; margin: 20px;}
        .speedtest-container {max-width: 500px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; text-align: center;}
        .speedtest-button {background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;}
        .speedtest-results {margin-top: 20px;}
        .speedtest-results h2 {font-size: 18px; margin-bottom: 10px;}
        .speedtest-results .result {display: flex; justify-content: space-between; margin-bottom: 10px;}
        #loading {display: none;}
        .spinner-border{margin: 10px auto;}
    </style>
</head>
<body>
    <div class="container">
        <div class="speedtest-container">
            <h1>Website Speed Test</h1>
            <button class="speedtest-button" id="speedtest-btn">Run Speed Test</button>
            <div id="loading" class="text-center">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
        </div>
        <div class="speedtest-results" id="speedtest-results"></div>
    </div>
    <script>
        document.getElementById('speedtest-btn').addEventListener('click', async () => {
            document.getElementById("loading").style.display = "block";
            document.getElementById("speedtest-results").innerHTML = "";
            try {
                const response = await fetch('/speedtest', { method: 'POST' });
                if (!response.ok) { throw new Error('Speed test failed.'); }
                const data = await response.json();
                document.getElementById("loading").style.display = "none";
                const resultsDiv = document.getElementById('speedtest-results');
                if (data.error) { resultsDiv.innerHTML = `<p class="text-danger">${data.error}</p>`; return; }
                resultsDiv.innerHTML = `<h2>Speed Test Results</h2><div class="result"><p>Download Speed:</p><span>${data.download}</span></div><div class="result"><p>Upload Speed:</p><span>${data.upload}</span></div><div class="result"><p>Ping:</p><span>${data.ping}</span></div>`;
            } catch (error) {
                console.error('Speed test error:', error);
                document.getElementById("loading").style.display = "none";
                const resultsDiv = document.getElementById('speedtest-results');
                resultsDiv.innerHTML = '<p class="text-danger">Speed test failed. Please try again later.</p>';
            }
        });
    </script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-C6RzsynM9kWDrMNeT87bh95OGNyZPhcTNXj1NW7RuBCsyN/o0jlpcV8Qyq46cDfL" crossorigin="anonymous"></script>
</body>
</html>
""")

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

        formatted_results = {
            'download': f'{download:.2f} Mbps',
            'upload': f'{upload:.2f} Mbps',
            'ping': f'{ping:.2f} ms'
        }

        return jsonify(formatted_results)

    except FileNotFoundError:
        return jsonify({'error': 'speedtest-cli is not installed. Please install it on the server.'})

    except Exception as e:
        print(f'An unexpected error occurred: {str(e)}')
        return jsonify({'error': 'An error occurred during the speed test.'})

if __name__ == '__main__':
    app.run(debug=True)
