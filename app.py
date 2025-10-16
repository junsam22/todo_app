"""Main Flask application for Todo App with Supabase."""
import os
from flask import Flask
from routes import register_routes
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()


def create_app():
    """Application factory pattern."""
    app = Flask(__name__, instance_relative_config=True)

    # Register routes
    register_routes(app)

    return app


# Create application instance
app = create_app()


if __name__ == '__main__':
    app.run(debug=True)
