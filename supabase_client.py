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

# Cache for client instance
_client_cache = None

def get_supabase_client() -> Client:
    """Get or create Supabase client instance."""
    global _client_cache

    if _client_cache is None:
        print(f"[DEBUG] Creating new Supabase client with URL: {SUPABASE_URL[:40]}...")
        print(f"[DEBUG] Using API key: {SUPABASE_KEY[:20]}...")
        _client_cache = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(f"[DEBUG] Supabase client created successfully")

    return _client_cache
