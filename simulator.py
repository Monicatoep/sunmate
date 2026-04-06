import requests
import random
import time
from datetime import datetime

API_URL = "http://127.0.0.1:8000"
INTERVAL = 10

def send_energy_consumption():
    data = {
        "timestamp": datetime.now().isoformat(),
        "consumption_kwh": round(random.uniform(0.5, 5.0), 2)
    }
    response = requests.post(f"{API_URL}/energy/consumption", json=data)
    print(f"Energy: {data['consumption_kwh']} kWh -> {response.status_code}")

def send_battery_data():
    data = [{
        "timestamp": datetime.now().isoformat(),
        "soc": random.randint(10, 100)
    }]
    response = requests.post(f"{API_URL}/battery/daily", json=data)
    print(f"Battery: {data[0]['soc']}% -> {response.status_code}")

if __name__ == "__main__":
    print(f"Simulator started. Sending data every {INTERVAL} seconds...")
    while True:
        send_energy_consumption()
        send_battery_data()
        time.sleep(INTERVAL)
