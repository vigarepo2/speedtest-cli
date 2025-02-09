import socket
import psutil
import platform
import time
import requests
from flask import Flask, render_template_string

app = Flask(__name__)

def get_external_ip():
    """Fetches the server's external IP address using an external service."""
    try:
        url = "https://api.ipify.org"  # Using ipify for external IP
        response = requests.get(url, timeout=5) #Added timeout to prevent indefinite hanging
        if response.status_code == 200:
            return response.text.strip()
        else:
            return f"Error fetching external IP: Status Code {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Error fetching external IP: {e}"

def get_uptime():
    """Calculates and formats system uptime."""
    uptime_seconds = time.time() - psutil.boot_time()
    days = int(uptime_seconds // (24 * 3600))
    hours = int((uptime_seconds % (24 * 3600)) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)
    return f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"

@app.route('/')
def index():
    # Server details
    hostname = socket.gethostname()
    try:
        internal_ip = socket.gethostbyname(hostname)
    except socket.gaierror:
        internal_ip = "Could not resolve hostname."
    external_ip = get_external_ip()
    operating_system = platform.system() + ' ' + platform.release()
    cpu_percent = psutil.cpu_percent()
    cpu_count = psutil.cpu_count(logical=False)
    cpu_threads = psutil.cpu_count()
    total_memory = psutil.virtual_memory().total / (1024 ** 3)  # GB
    available_memory = psutil.virtual_memory().available / (1024 ** 3)
    memory_percent = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    disk_total = psutil.disk_usage('/').total / (1024**3)
    disk_used = psutil.disk_usage('/').used / (1024**3)
    uptime = get_uptime()

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Server Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            body {{ background-color: #f8f9fa; }}
            .dashboard-container {{ margin-top: 50px; }}
            .card {{ border: none; box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15); }}
            .card-header {{ background-color: #ffffff; border-bottom: 1px solid #eee; font-weight: 600; }}
            .icon {{ font-size: 2em; margin-right: 10px; color: #007bff; }}
            .progress {{ height: 25px; }}
            .progress-bar {{
                background-color: #007bff;
                color: white;
                font-weight: bold;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container dashboard-container">
            <h1 class="mb-4 text-center">Server Dashboard</h1>
            <div class="row">
                <div class="col-md-6">
                    <div class="card mb-4">
                        <div class="card-header"><i class="fas fa-server icon"></i>Server Information</div>
                        <div class="card-body">
                            <p><strong>Hostname:</strong> {hostname}</p>
                            <p><strong>Internal IP:</strong> {internal_ip}</p>
                            <p><strong>External IP:</strong> {external_ip}</p>
                            <p><strong>Operating System:</strong> {operating_system}</p>
                            <p><strong>Uptime:</strong> {uptime}</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card mb-4">
                        <div class="card-header"><i class="fas fa-microchip icon"></i>CPU Usage</div>
                        <div class="card-body">
                            <p><strong>CPU Usage:</strong> {cpu_percent:.1f}%</p>
                            <p><strong>CPU Cores:</strong> {cpu_count}</p>
                            <p><strong>CPU Threads:</strong> {cpu_threads}</p>
                            <div class="progress">
                                <div class="progress-bar" role="progressbar" style="width: {cpu_percent:.1f}%;" aria-valuenow="{cpu_percent:.1f}" aria-valuemin="0" aria-valuemax="100">{cpu_percent:.1f}%</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="col-md-6">
                    <div class="card mb-4">
                        <div class="card-header"><i class="fas fa-memory icon"></i>Memory Usage</div>
                        <div class="card-body">
                            <p><strong>Total Memory:</strong> {total_memory:.2f} GB</p>
                            <p><strong>Available Memory:</strong> {available_memory:.2f} GB</p>
                            <p><strong>Memory Usage:</strong> {memory_percent:.1f}%</p>
                            <div class="progress">
                                <div class="progress-bar" role="progressbar" style="width: {memory_percent:.1f}%;" aria-valuenow="{memory_percent:.1f}" aria-valuemin="0" aria-valuemax="100">{memory_percent:.1f}%</div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card mb-4">
                        <div class="card-header"><i class="fas fa-hdd icon"></i>Disk Usage (Root Partition)</div>
                        <div class="card-body">
                            <p><strong>Total Disk Space:</strong> {disk_total:.2f} GB</p>
                            <p><strong>Used Disk Space:</strong> {disk_used:.2f} GB</p>
                            <p><strong>Disk Usage:</strong> {disk_usage:.1f}%</p>
                            <div class="progress">
                                <div class="progress-bar" role="progressbar" style="width: {disk_usage:.1f}%;" aria-valuenow="{disk_usage:.1f}" aria-valuemin="0" aria-valuemax="100">{disk_usage:.1f}%</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    return render_template_string(html_content, hostname=hostname, internal_ip=internal_ip, external_ip=external_ip, operating_system=operating_system, cpu_percent=cpu_percent, cpu_count=cpu_count, cpu_threads=cpu_threads, total_memory=total_memory, available_memory=available_memory, memory_percent=memory_percent, disk_usage=disk_usage, disk_total=disk_total, disk_used=disk_used, uptime=uptime)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0") # Make it accessible externally.
