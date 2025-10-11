"""Main Flask application for Todo App with Supabase."""
from flask import Flask
from routes import register_routes


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
