"""Supabase client configuration."""
import os
from supabase import create_client, Client

# Load environment variables from .env file (only in local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed in production, which is fine

# Supabase configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://virsdnelwxmoklxcogsd.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZpcnNkbmVsd3htb2tseGNvZ3NkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk5OTc2OTYsImV4cCI6MjA3NTU3MzY5Nn0.ypa1txNxO--ghdTeAdrztxi4uMcT8YolOMjTQKVjFvE')

print(f"[DEBUG] Initializing Supabase client with URL: {SUPABASE_URL[:40]}...")
print(f"[DEBUG] Using API key: {SUPABASE_KEY[:20]}...")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase_client() -> Client:
    """Get Supabase client instance."""
    return supabase
