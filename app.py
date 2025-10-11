"""Main Flask application for Todo App."""
from flask import Flask
from config import Config
from models import db, init_sample_data
from routes import register_routes


def create_app():
    """Application factory pattern."""
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration
    app.config.from_object(Config)

    if not Config.is_vercel:
        sqlite_uri = Config.ensure_local_storage(app.instance_path)
        app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_uri
    else:
        sqlite_uri = app.config['SQLALCHEMY_DATABASE_URI']

    # Initialize database
    db.init_app(app)

    # Register routes
    register_routes(app)

    # Initialize database tables and sample data
    with app.app_context():
        if app.config['DEBUG']:
            Config.print_config(sqlite_uri)
        db.create_all()
        init_sample_data(app)

    return app


# Create application instance
app = create_app()


if __name__ == '__main__':
    app.run(debug=True)
