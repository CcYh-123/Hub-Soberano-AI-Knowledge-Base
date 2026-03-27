import os
import requests
from datetime import datetime

SUPABASE_URL = "https://ijzazdwdgtxsosiibjoj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlqemF6ZHdkZ3R4c29zaWliam9qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwNjMyMTIsImV4cCI6MjA4NzYzOTIxMn0.NVQpQFJlfHC1eKWSenc9XfMfRyeJ6W0OCkKzZqXN1lQ"

def setup_test_data():
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    # 1. Update profiles with organization_id
    org_id = "antigravity-test-org"
    profiles = ['d0636a5b-d53a-4316-ba8a-5737c61c66a0', 'dd626c9a-43e0-44a6-9bda-a66ebdf01d24']
    
    for profile_id in profiles:
        print(f"Updating profile {profile_id}...")
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/profiles?id=eq.{profile_id}",
            json={"organization_id": org_id, "sector": "AGRO"},
            headers=headers
        )

    # 2. Insert alert for that org_id
    payload = {
        "tenant_id": "fa60ff74-574a-48a4-8ec9-074dde3746aa",
        "organization_id": org_id,
        "sector": "AGRO",
        "item_key": "GLIFOSATO",
        "price": 14000.0,
        "timestamp": datetime.now().isoformat(),
        "metadata_json": {
            "trend": "critical",
            "intelligence_note": f"TEST ALERT: Glifosato con alza crítica detectada (Sincronización OK)",
            "source": "antigravity_bot"
        }
    }

    print(f"Inserting alert for {org_id}...")
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/historical_data",
        json=payload,
        headers=headers
    )
    print(f"Insert Status: {response.status_code}")

if __name__ == "__main__":
    setup_test_data()
