"""API routes for the Todo application."""
import os
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

    @app.route('/api/debug/env', methods=['GET'])
    def debug_env():
        """Debug endpoint to check environment variables (disabled in production)."""
        # Disable in production for security
        if os.environ.get('VERCEL_ENV') == 'production':
            return jsonify({'error': 'Not available in production'}), 403

        return jsonify({
            'SUPABASE_URL_SET': bool(os.environ.get('SUPABASE_URL')),
            'SUPABASE_KEY_SET': bool(os.environ.get('SUPABASE_KEY')),
            'SUPABASE_URL_PREFIX': os.environ.get('SUPABASE_URL', '')[:30] if os.environ.get('SUPABASE_URL') else 'NOT_SET',
            'VERCEL': os.environ.get('VERCEL'),
            'VERCEL_ENV': os.environ.get('VERCEL_ENV'),
        })

    @app.route('/api/todos', methods=['GET'])
    def get_todos():
        """Get all todos."""
        todos = TodoRepository.get_all_todos_ordered()
        return jsonify([todo.to_dict() for todo in todos])

    @app.route('/api/todos', methods=['POST'])
    def create_todo():
        """Create a new todo."""
        import sys
        import io

        # Check if we're in debug mode (non-production environment)
        is_debug_mode = os.environ.get('VERCEL_ENV') != 'production'

        # Capture stdout only in debug mode to avoid performance overhead
        if is_debug_mode:
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()

        try:
            data = request.get_json()

            if not data or 'title' not in data:
                if is_debug_mode:
                    sys.stdout = old_stdout
                return jsonify({'error': 'Title is required'}), 400

            todo = TodoRepository.create_todo(
                title=data['title'],
                description=data.get('description', ''),
                priority=data.get('priority', 'medium')
            )

            # Get captured output if in debug mode
            if is_debug_mode:
                sys.stdout = old_stdout
                debug_output = captured_output.getvalue()

            if todo:
                return jsonify(todo.to_dict()), 201
            else:
                error_response = {
                    'error': 'Failed to create todo',
                    'details': 'TodoRepository.create_todo returned None'
                }
                # Only include debug output in non-production environments
                if is_debug_mode:
                    error_response['debug_output'] = debug_output
                return jsonify(error_response), 500

        except Exception as e:
            if is_debug_mode:
                sys.stdout = old_stdout
                debug_output = captured_output.getvalue()

            import traceback
            error_response = {
                'error': str(e)
            }
            # Only include traceback and debug output in non-production environments
            if is_debug_mode:
                error_response['traceback'] = traceback.format_exc()
                error_response['debug_output'] = debug_output

            return jsonify(error_response), 500

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

    @app.route('/api/chatkit/create-session', methods=['POST'])
    def create_chatkit_session():
        """Create a ChatKit session for AI assistant."""
        try:
            import os
            import requests

            # ChatKit設定（環境変数から読み込む）
            workflow_id = os.environ.get('CHATKIT_WORKFLOW_ID') or os.environ.get('NEXT_PUBLIC_CHATKIT_WORKFLOW_ID')
            api_key = os.environ.get('OPENAI_API_KEY')

            if not api_key:
                return jsonify({'error': 'OpenAI API key not configured'}), 500

            if not workflow_id:
                return jsonify({'error': 'ChatKit workflow ID not configured'}), 500
            
            # OpenAI ChatKit APIを呼び出し
            url = "https://api.openai.com/v1/chatkit/sessions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "OpenAI-Beta": "chatkit_beta=v1"
            }
            
            data = request.get_json() or {}
            # ユニークなデバイスIDを生成（セッション管理用）
            import time
            device_id = data.get('device_id', f'todo_user_{int(time.time())}')

            # ドキュメント通りのペイロード構造
            payload = {
                "workflow": {"id": workflow_id},
                "user": device_id
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return jsonify(response.json()), 200
            else:
                return jsonify({
                    'error': f'Failed to create session: {response.status_code}',
                    'details': response.text
                }), response.status_code
                
        except Exception as e:
            return jsonify({
                'error': f'Unexpected error: {str(e)}'
            }), 500

    return app
