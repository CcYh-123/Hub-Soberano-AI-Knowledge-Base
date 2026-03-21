import os
import requests

url = "https://ijzazdwdgtxsosiibjoj.supabase.co/rest/v1/dashboard_agro"
headers = {
    "apikey": "sb_publishable_8PjB5UfXcJAf5MbtvDizlQ_xcH4mEQO",
    "Authorization": "Bearer sb_publishable_8PjB5UfXcJAf5MbtvDizlQ_xcH4mEQO"
}
try:
    response = requests.get(url, headers=headers)
    print("Supabase Data:", response.json())
except Exception as e:
    print("Error:", e)
