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
# strip() to remove any trailing newlines or whitespace from environment variables
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://virsdnelwxmoklxcogsd.supabase.co').strip()
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZpcnNkbmVsd3htb2tseGNvZ3NkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk5OTc2OTYsImV4cCI6MjA3NTU3MzY5Nn0.ypa1txNxO--ghdTeAdrztxi4uMcT8YolOMjTQKVjFvE').strip()

# Cache for client instance
_client_cache = None

def get_supabase_client() -> Client:
    """Get or create Supabase client instance."""
    global _client_cache

    if _client_cache is None:
        print(f"[DEBUG] Creating new Supabase client with URL: {SUPABASE_URL[:40] if SUPABASE_URL else 'None'}...")
        print(f"[DEBUG] Using API key: {SUPABASE_KEY[:20] if SUPABASE_KEY else 'None'}...")

        if not SUPABASE_URL or not SUPABASE_KEY:
            print(f"[ERROR] Missing Supabase credentials! URL: {bool(SUPABASE_URL)}, KEY: {bool(SUPABASE_KEY)}")
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

        try:
            _client_cache = create_client(SUPABASE_URL, SUPABASE_KEY)
            print(f"[DEBUG] Supabase client created successfully")
        except Exception as e:
            print(f"[ERROR] Failed to create Supabase client: {type(e).__name__}: {e}")
            raise

    return _client_cache
