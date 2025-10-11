"""Database models for the Todo application."""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Todo(db.Model):
    """Todo model representing a task."""

    __tablename__ = 'todo'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    priority = db.Column(db.String(10), default='medium')  # high, medium, low
    order = db.Column(db.Integer, default=0)  # For drag & drop ordering
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert Todo object to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'priority': self.priority,
            'order': self.order,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        """String representation of Todo."""
        return f'<Todo {self.id}: {self.title}>'


def init_sample_data(app):
    """Initialize sample data for Vercel environment (in-memory database)."""
    from config import Config

    if Config.is_vercel:
        with app.app_context():
            # Check if data already exists
            if Todo.query.count() == 0:
                sample_todos = [
                    Todo(
                        title="サンプルタスク1",
                        description="これはサンプルタスクです",
                        priority="high",
                        order=1
                    ),
                    Todo(
                        title="サンプルタスク2",
                        description="ドラッグ&ドロップで順序を変更できます",
                        priority="medium",
                        order=2
                    ),
                    Todo(
                        title="サンプルタスク3",
                        description="編集・削除も可能です",
                        priority="low",
                        order=3
                    )
                ]
                for todo in sample_todos:
                    db.session.add(todo)
                db.session.commit()
