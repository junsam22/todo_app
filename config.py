"""Application configuration."""
import os


class Config:
    """Base configuration."""

    # Database configuration
    basedir = os.path.abspath(os.path.dirname(__file__))

    # Vercel environment detection
    is_vercel = (
        os.environ.get('VERCEL') or
        os.environ.get('VERCEL_ENV') or
        os.environ.get('NOW_REGION') or
        'vercel.app' in os.environ.get('VERCEL_URL', '')
    )

    # Use in-memory database for serverless (Vercel), file-based for local
    if is_vercel:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    else:
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "todo.db")}'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Debug mode (only for local development)
    DEBUG = not is_vercel

    @staticmethod
    def print_config():
        """Print current configuration for debugging."""
        print("Environment detection:")
        print(f"  VERCEL: {os.environ.get('VERCEL')}")
        print(f"  VERCEL_ENV: {os.environ.get('VERCEL_ENV')}")
        print(f"  NOW_REGION: {os.environ.get('NOW_REGION')}")
        print(f"  VERCEL_URL: {os.environ.get('VERCEL_URL')}")
        print(f"  is_vercel: {Config.is_vercel}")
        print(f"  Database URI: {Config.SQLALCHEMY_DATABASE_URI}")
