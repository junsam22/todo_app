"""API routes for the Todo application."""
from flask import render_template, request, jsonify
from datetime import datetime
from models import db, Todo
from ai_service import generate_description


def register_routes(app):
    """Register all routes with the Flask app."""

    @app.route('/')
    def index():
        """Render the main page."""
        # Define priority order mapping: high=3, medium=2, low=1
        priority_order = db.case(
            (Todo.priority == 'high', 3),
            (Todo.priority == 'medium', 2),
            (Todo.priority == 'low', 1),
            else_=0
        )
        todos = (
            Todo.query
            .order_by(
                priority_order.desc(),
                Todo.order.asc(),
                Todo.created_at.desc(),
            )
            .all()
        )
        return render_template('index.html', todos=todos)

    @app.route('/api/todos', methods=['GET'])
    def get_todos():
        """Get all todos."""
        # Define priority order mapping: high=3, medium=2, low=1
        priority_order = db.case(
            (Todo.priority == 'high', 3),
            (Todo.priority == 'medium', 2),
            (Todo.priority == 'low', 1),
            else_=0
        )
        todos = (
            Todo.query
            .order_by(
                priority_order.desc(),
                Todo.order.asc(),
                Todo.created_at.desc(),
            )
            .all()
        )
        return jsonify([todo.to_dict() for todo in todos])

    @app.route('/api/todos', methods=['POST'])
    def create_todo():
        """Create a new todo."""
        try:
            data = request.get_json()

            if not data or 'title' not in data:
                return jsonify({'error': 'Title is required'}), 400

            # Set order for new task (append to end)
            max_order = db.session.query(db.func.max(Todo.order)).scalar() or 0

            todo = Todo(
                title=data['title'],
                description=data.get('description', ''),
                priority=data.get('priority', 'medium'),
                order=max_order + 1
            )

            db.session.add(todo)
            db.session.commit()

            return jsonify(todo.to_dict()), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @app.route('/api/todos/<int:todo_id>', methods=['GET'])
    def get_todo(todo_id):
        """Get a specific todo by ID."""
        todo = Todo.query.get_or_404(todo_id)
        return jsonify(todo.to_dict())

    @app.route('/api/todos/<int:todo_id>', methods=['PUT'])
    def update_todo(todo_id):
        """Update an existing todo."""
        try:
            todo = Todo.query.get_or_404(todo_id)
            data = request.get_json()

            if not data:
                return jsonify({'error': 'No data provided'}), 400

            # Update fields if provided
            todo.title = data.get('title', todo.title)
            todo.description = data.get('description', todo.description)
            todo.completed = data.get('completed', todo.completed)
            todo.priority = data.get('priority', todo.priority)
            todo.order = data.get('order', todo.order)
            todo.updated_at = datetime.utcnow()

            db.session.commit()

            return jsonify(todo.to_dict())

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
    def delete_todo(todo_id):
        """Delete a todo."""
        try:
            todo = Todo.query.get_or_404(todo_id)
            db.session.delete(todo)
            db.session.commit()

            return '', 204

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @app.route('/api/todos/<int:todo_id>/toggle', methods=['PATCH'])
    def toggle_todo(todo_id):
        """Toggle todo completion status."""
        try:
            todo = Todo.query.get_or_404(todo_id)
            todo.completed = not todo.completed
            todo.updated_at = datetime.utcnow()

            db.session.commit()

            return jsonify(todo.to_dict())

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @app.route('/api/todos/reorder', methods=['POST'])
    def reorder_todos():
        """Reorder todos based on drag & drop."""
        try:
            data = request.get_json()

            if not data or 'todo_orders' not in data:
                return jsonify({'error': 'todo_orders is required'}), 400

            todo_orders = data.get('todo_orders', [])

            for item in todo_orders:
                if 'id' not in item or 'order' not in item:
                    continue

                todo = Todo.query.get(item['id'])
                if todo:
                    todo.order = item['order']
                    todo.updated_at = datetime.utcnow()

            db.session.commit()
            return jsonify({'success': True}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @app.route('/api/generate-description', methods=['POST'])
    def generate_task_description():
        """Generate a description for a task based on its title using AI."""
        try:
            data = request.get_json()

            if not data or 'title' not in data:
                return jsonify({'error': 'Title is required'}), 400

            title = data['title'].strip()

            if not title:
                return jsonify({'error': 'Title cannot be empty'}), 400

            # Generate description using AI service
            description = generate_description(title)

            return jsonify({
                'description': description,
                'success': True
            }), 200

        except Exception as e:
            return jsonify({
                'error': str(e),
                'success': False
            }), 500

    return app
