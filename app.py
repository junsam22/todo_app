"""Main Flask application for Todo App."""
from flask import Flask
from config import Config
from models import db, init_sample_data
from routes import register_routes


def create_app():
    """Application factory pattern."""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(Config)

    # Initialize database
    db.init_app(app)

    # Register routes
    register_routes(app)

    # Initialize database tables and sample data
    with app.app_context():
        Config.print_config()
        db.create_all()
        init_sample_data(app)

    return app


# Create application instance
app = create_app()


if __name__ == '__main__':
    app.run(debug=True)
