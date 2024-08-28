import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, timezone
import pytz
from Variable import *

API_URL = f'https://api.hetzner.cloud/v1/servers/{SERVER_ID}/metrics'
headers = {
    'Authorization': f'Bearer {API_TOKEN}'
}

def get_network_traffic(start_time, end_time, step):
    params = {
        'start': start_time.isoformat(),
        'end': end_time.isoformat(),
        'type': 'network',
        'step': step
    }
    
    response = requests.get(API_URL, headers=headers, params=params)
    
    if response.status_code != 200:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
    
    data = response.json()
    
    if 'metrics' not in data or 'time_series' not in data['metrics']:
        raise KeyError("No 'metrics' or 'time_series' data found in the API response.")
    
    return data['metrics']

def plot_and_save_traffic(timestamps, inbound, outbound):
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, inbound, label='Inbound Traffic (MBps)')
    plt.plot(timestamps, outbound, label='Outbound Traffic (MBps)')
    plt.xlabel('Time')
    plt.ylabel('Traffic (MBps)')
    plt.title('Network Traffic over the Last 24 Hours')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('network_traffic.png')
    plt.show()

def convert_to_tehran_time(utc_dt):
    tehran_tz = pytz.timezone('Asia/Tehran')
    return utc_dt.astimezone(tehran_tz)

end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(days=1)

step = 3600
traffic_data = get_network_traffic(start_time, end_time, step)

timestamps = []
inbound_traffic = []
outbound_traffic = []

time_series = traffic_data['time_series']
for i in range(0, len(time_series['network.0.bandwidth.in']['values'])):
    utc_timestamp = datetime.fromtimestamp(time_series['network.0.bandwidth.in']['values'][i][0], timezone.utc)
    tehran_timestamp = convert_to_tehran_time(utc_timestamp)
    
    inbound = float(time_series['network.0.bandwidth.in']['values'][i][1]) / (1024 * 1024)
    outbound = float(time_series['network.0.bandwidth.out']['values'][i][1]) / (1024 * 1024)
    
    timestamps.append(tehran_timestamp)
    inbound_traffic.append(inbound)
    outbound_traffic.append(outbound)

# create graph
plot_and_save_traffic(timestamps, inbound_traffic, outbound_traffic)
