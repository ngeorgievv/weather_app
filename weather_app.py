from flask import Flask, render_template, request
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Gauge
import requests
import psutil

app = Flask(__name__)

metrics = PrometheusMetrics(app)

metrics.info('app_info', 'Application info', version='1.0.0')

# OpenWeatherMap API key (replace with your own API key)
API_KEY = '887c036370a292228f42e4a5bc944873'
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'

cpu_usage_metric = Gauge('app_cpu_usage_percent', 'CPU usage in percentage')
memory_usage_metric = Gauge('app_memory_usage_percent', 'Memory usage in percentage')
network_sent_metric = Gauge('app_network_sent_bytes', 'Total network bytes sent')
network_recv_metric = Gauge('app_network_received_bytes', 'Total network bytes received')

def collect_system_metrics():
    """Collect system-level metrics."""
    cpu_usage_metric.set(psutil.cpu_percent(interval=1))  # CPU usage in percentage
    memory_usage_metric.set(psutil.virtual_memory().percent)  # Memory usage in percentage
    net_io = psutil.net_io_counters()
    network_sent_metric.set(net_io.bytes_sent)  # Network bytes sent
    network_recv_metric.set(net_io.bytes_recv)  # Network bytes received

@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None
    error_message = None

    if request.method == 'POST':
        city = request.form.get('city')
        if city:
            # Fetch weather data
            params = {
                'q': city,
                'appid': API_KEY,
                'units': 'metric'
            }
            response = requests.get(BASE_URL, params=params)
            if response.status_code == 200:
                weather_data = response.json()
            else:
                error_message = f"Could not find weather for '{city}'. Please try again."

    return render_template('index.html', weather_data=weather_data, error_message=error_message)

def update_metrics():
    """Update metrics before every request."""
    collect_system_metrics()


if __name__ == '__main__':
    app.run(debug=False, port=8003)
