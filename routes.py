"""API routes for the Todo application."""
from flask import render_template, request, jsonify
from models import TodoRepository
from ai_service import generate_description


def register_routes(app):
    """Register all routes with the Flask app."""

    @app.route('/')
    def index():
        """Render the main page."""
        todos = TodoRepository.get_all_todos_ordered()
        return render_template('index.html', todos=todos)

    @app.route('/api/todos', methods=['GET'])
    def get_todos():
        """Get all todos."""
        todos = TodoRepository.get_all_todos_ordered()
        return jsonify([todo.to_dict() for todo in todos])

    @app.route('/api/todos', methods=['POST'])
    def create_todo():
        """Create a new todo."""
        try:
            data = request.get_json()

            if not data or 'title' not in data:
                return jsonify({'error': 'Title is required'}), 400

            todo = TodoRepository.create_todo(
                title=data['title'],
                description=data.get('description', ''),
                priority=data.get('priority', 'medium')
            )

            if todo:
                return jsonify(todo.to_dict()), 201
            else:
                return jsonify({'error': 'Failed to create todo', 'details': 'TodoRepository.create_todo returned None'}), 500

        except Exception as e:
            import traceback
            return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

    @app.route('/api/todos/<int:todo_id>', methods=['GET'])
    def get_todo(todo_id):
        """Get a specific todo by ID."""
        todo = TodoRepository.get_todo_by_id(todo_id)
        if todo:
            return jsonify(todo.to_dict())
        return jsonify({'error': 'Todo not found'}), 404

    @app.route('/api/todos/<int:todo_id>', methods=['PUT'])
    def update_todo(todo_id):
        """Update an existing todo."""
        try:
            data = request.get_json()

            if not data:
                return jsonify({'error': 'No data provided'}), 400

            # Update fields if provided
            todo = TodoRepository.update_todo(
                todo_id,
                title=data.get('title'),
                description=data.get('description'),
                completed=data.get('completed'),
                priority=data.get('priority'),
                order=data.get('order')
            )

            if todo:
                return jsonify(todo.to_dict())
            else:
                return jsonify({'error': 'Todo not found or update failed'}), 404

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
    def delete_todo(todo_id):
        """Delete a todo."""
        try:
            success = TodoRepository.delete_todo(todo_id)
            if success:
                return '', 204
            else:
                return jsonify({'error': 'Failed to delete todo'}), 500

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/todos/<int:todo_id>/toggle', methods=['PATCH'])
    def toggle_todo(todo_id):
        """Toggle todo completion status."""
        try:
            todo = TodoRepository.toggle_todo_completion(todo_id)
            if todo:
                return jsonify(todo.to_dict())
            else:
                return jsonify({'error': 'Todo not found'}), 404

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/todos/reorder', methods=['POST'])
    def reorder_todos():
        """Reorder todos based on drag & drop."""
        try:
            data = request.get_json()

            if not data or 'todo_orders' not in data:
                return jsonify({'error': 'todo_orders is required'}), 400

            todo_orders = data.get('todo_orders', [])
            success = TodoRepository.reorder_todos(todo_orders)

            if success:
                return jsonify({'success': True}), 200
            else:
                return jsonify({'error': 'Failed to reorder todos'}), 500

        except Exception as e:
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
