import os
import requests
from datetime import datetime

SUPABASE_URL = "https://ijzazdwdgtxsosiibjoj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlqemF6ZHdkZ3R4c29zaWliam9qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwNjMyMTIsImV4cCI6MjA4NzYzOTIxMn0.NVQpQFJlfHC1eKWSenc9XfMfRyeJ6W0OCkKzZqXN1lQ"

def insert_alert(org_id=None):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    payload = {
        "tenant_id": "fa60ff74-574a-48a4-8ec9-074dde3746aa",
        "organization_id": org_id,
        "sector": "AGRO",
        "item_key": "GLIFOSATO",
        "price": 14000.0,
        "timestamp": datetime.now().isoformat(),
        "metadata_json": {
            "trend": "critical",
            "intelligence_note": f"AUMENTO CRITICO: Sector AGRO - Glifosato se dispara por cepo cambiario",
            "source": "antigravity_bot"
        }
    }

    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/historical_data",
        json=payload,
        headers=headers
    )
    print(f"Insert for {org_id}: Status {response.status_code}")
    if response.status_code >= 400:
        print(f"Error detail: {response.text}")

if __name__ == "__main__":
    for org in ["kixnlqjuiqtodzdubydb"]:
        insert_alert(org)
