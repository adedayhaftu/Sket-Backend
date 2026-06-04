import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Missing Supabase environment variables. Check your .env file.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def test_connection():
    try:
        response = supabase.table("users").select("*").limit(1).execute()
        return {"status": "connected", "message": "Supabase connection successful!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}