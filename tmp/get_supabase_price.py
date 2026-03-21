import requests
import os
from dotenv import load_dotenv

load_dotenv()
url = "https://ijzazdwdgtxsosiibjoj.supabase.co"
key = os.getenv("SUPABASE_KEY")

def get_price():
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    endpoint = f"{url}/rest/v1/dashboard_agro?item_key=like.*Glifosato*"
    try:
        r = requests.get(endpoint, headers=headers)
        print(f"Status: {r.status_code}")
        print(f"Data: {r.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_price()
