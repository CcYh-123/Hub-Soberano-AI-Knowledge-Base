import httpx
import os
from dotenv import load_dotenv

load_dotenv()

class SupabaseClient:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        if not self.url or not self.key:
            print("⚠️ ERROR: No encontré SUPABASE_URL o KEY en el .env")
        
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json"
        }

    def traer_productos(self):
        """Prueba de fuego: trae los primeros 5 productos"""
        endpoint = f"{self.url}/rest/v1/products?select=*&limit=5"
        with httpx.Client() as client:
            response = client.get(endpoint, headers=self.headers)
            return response.json()

# Instancia global
db = SupabaseClient()

if __name__ == "__main__":
    # Si ejecutás este archivo solo, hace un test
    print("🚀 Probando conexión directa...")
    print(db.traer_productos())