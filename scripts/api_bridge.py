import os
from dotenv import load_dotenv
from supabase import create_client
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_KEY')
supabase = create_client(url, key)

app = FastAPI()

# Enable CORS for the dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/data')
async def get_data():
    try:
        response = supabase.table('dashboard_agro').select('*').execute()
        return response.data
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
