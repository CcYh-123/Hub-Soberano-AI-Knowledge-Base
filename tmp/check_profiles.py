import os
import requests

SUPABASE_URL = "https://ijzazdwdgtxsosiibjoj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlqemF6ZHdkZ3R4c29zaWliam9qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwNjMyMTIsImV4cCI6MjA4NzYzOTIxMn0.NVQpQFJlfHC1eKWSenc9XfMfRyeJ6W0OCkKzZqXN1lQ"

def check_profiles():
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
    
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/profiles?select=*",
        headers=headers
    )
    print(f"Profiles Status: {response.status_code}")
    print(f"Profiles: {response.json()}")

if __name__ == "__main__":
    check_profiles()
