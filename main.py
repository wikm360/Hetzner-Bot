import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta, timezone
import pytz
from Variable import *
import requests
import schedule
import time

plt.style.use('dark_background')

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
    plt.figure(figsize=(12, 6))  # اندازه بزرگ‌تر برای وضوح بیشتر

    # رسم خطوط
    plt.plot(timestamps, inbound, label='Inbound Traffic (MB)', color='#1f77b4', linewidth=2)
    plt.plot(timestamps, outbound, label='Outbound Traffic (MB)', color='#ff7f0e', linewidth=2)

    # تنظیمات محورهای گراف
    plt.xlabel('Time', fontsize=14, color='white')
    plt.ylabel('Traffic (MB)', fontsize=14, color='white')
    plt.title(TITLE, fontsize=16, color='white')

    plt.grid(True, linestyle='--', color='gray', alpha=0.7)
    
    plt.legend(loc='upper right', fontsize=12)
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('network_traffic.png', bbox_inches='tight', dpi=300)
    plt.show()

def convert_to_tehran_time(utc_dt):
    tehran_tz = pytz.timezone('Asia/Tehran')
    return utc_dt.astimezone(tehran_tz)

def start ():
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=7)

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

    plot_and_save_traffic(timestamps, inbound_traffic, outbound_traffic)

    photo_path = './network_traffic.png'

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

    with open(photo_path, 'rb') as photo:
        response = requests.post(url, data={'chat_id': CHANNEL_ID, 'caption': CAPTION}, files={'photo': photo})

    if response.status_code == 200:
        print("Photo sent successfully")
    else:
        print("Failed to send photo:", response.text)


schedule.every().friday.at(TIME , pytz.timezone('Asia/Tehran')).do(start)

while True:
    schedule.run_pending()
    time.sleep(1)