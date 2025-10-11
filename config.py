"""Application configuration."""
import os
from pathlib import Path


class Config:
    """Base configuration."""

    # Paths
    basedir = Path(__file__).resolve().parent
    db_filename = "todo.db"

    # Vercel environment detection
    is_vercel = (
        os.environ.get('VERCEL') or
        os.environ.get('VERCEL_ENV') or
        os.environ.get('NOW_REGION') or
        'vercel.app' in os.environ.get('VERCEL_URL', '')
    )

    # Use in-memory database for serverless (Vercel), file-based for local
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' if is_vercel else ''

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Debug mode (only for local development)
    DEBUG = not is_vercel

    @staticmethod
    def print_config(database_uri: str | None = None):
        """Print current configuration for debugging."""
        db_uri = database_uri or Config.SQLALCHEMY_DATABASE_URI
        print("Environment detection:")
        print(f"  VERCEL: {os.environ.get('VERCEL')}")
        print(f"  VERCEL_ENV: {os.environ.get('VERCEL_ENV')}")
        print(f"  NOW_REGION: {os.environ.get('NOW_REGION')}")
        print(f"  VERCEL_URL: {os.environ.get('VERCEL_URL')}")
        print(f"  is_vercel: {Config.is_vercel}")
        print(f"  Database URI: {db_uri}")

    @classmethod
    def ensure_local_storage(cls, instance_path: str) -> str:
        """Ensure local SQLite storage directory exists and return URI."""
        storage_path = Path(instance_path)
        try:
            storage_path.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            print(f"Warning: unable to ensure storage directory {storage_path}: {exc}")
            storage_path = cls.basedir

        db_path = storage_path / cls.db_filename
        return f"sqlite:///{db_path}"
