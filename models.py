"""Database models and operations for the Todo application using Supabase."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from supabase_client import get_supabase_client


class Todo:
    """Todo model representing a task."""

    def __init__(self, id: int = None, title: str = '', description: str = '',
                 completed: bool = False, priority: str = 'medium',
                 order: int = 0, created_at: str = None, updated_at: str = None):
        self.id = id
        self.title = title
        self.description = description
        self.completed = completed
        self.priority = priority
        self.order = order
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert Todo object to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'priority': self.priority,
            'order': self.order,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Todo':
        """Create Todo object from dictionary."""
        return Todo(
            id=data.get('id'),
            title=data.get('title', ''),
            description=data.get('description', ''),
            completed=data.get('completed', False),
            priority=data.get('priority', 'medium'),
            order=data.get('order', 0),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def __repr__(self):
        """String representation of Todo."""
        return f'<Todo {self.id}: {self.title}>'


class TodoRepository:
    """Repository for Todo database operations using Supabase."""

    @staticmethod
    def get_all_todos_ordered() -> List[Todo]:
        """Get all todos ordered by priority, order, and creation date."""
        try:
            supabase = get_supabase_client()

            # Fetch all todos and sort in Python since Supabase doesn't support custom SQL expressions easily
            response = supabase.table('todos').select('*').order('created_at', desc=True).execute()

            todos = [Todo.from_dict(item) for item in response.data]

            # Custom sorting: priority (high=3, medium=2, low=1), then order, then created_at
            priority_map = {'high': 3, 'medium': 2, 'low': 1}
            todos.sort(
                key=lambda t: (
                    -priority_map.get(t.priority, 0),  # Priority descending
                    t.order,  # Order ascending
                    t.created_at  # Created at descending (but already reversed with -)
                ),
                reverse=False
            )

            return todos
        except Exception as e:
            print(f"Error fetching todos: {e}")
            return []

    @staticmethod
    def get_todo_by_id(todo_id: int) -> Optional[Todo]:
        """Get a specific todo by ID."""
        try:
            supabase = get_supabase_client()
            response = supabase.table('todos').select('*').eq('id', todo_id).single().execute()

            if response.data:
                return Todo.from_dict(response.data)
            return None
        except Exception as e:
            print(f"Error fetching todo {todo_id}: {e}")
            return None

    @staticmethod
    def create_todo(title: str, description: str = '', priority: str = 'medium') -> Optional[Todo]:
        """Create a new todo."""
        try:
            print(f"[DEBUG] create_todo called with: title={title}, description={description}, priority={priority}")
            supabase = get_supabase_client()
            print(f"[DEBUG] Got supabase client: {supabase}")

            # Get max order
            max_order_response = supabase.table('todos').select('order').order('order', desc=True).limit(1).execute()
            max_order = max_order_response.data[0]['order'] if max_order_response.data else 0
            print(f"[DEBUG] Max order: {max_order}")

            # Create new todo
            todo_data = {
                'title': title,
                'description': description,
                'priority': priority,
                'order': max_order + 1,
                'completed': False
            }
            print(f"[DEBUG] Todo data: {todo_data}")

            response = supabase.table('todos').insert(todo_data).execute()
            print(f"[DEBUG] Insert response: {response.data}")

            if response.data:
                return Todo.from_dict(response.data[0])
            print("[DEBUG] No data in response")
            return None
        except Exception as e:
            print(f"Error creating todo: {e}")
            import traceback
            traceback.print_exc()
            return None

    @staticmethod
    def update_todo(todo_id: int, **kwargs) -> Optional[Todo]:
        """Update an existing todo."""
        try:
            supabase = get_supabase_client()

            # Prepare update data
            update_data = {}
            allowed_fields = ['title', 'description', 'completed', 'priority', 'order']

            for field in allowed_fields:
                if field in kwargs:
                    update_data[field] = kwargs[field]

            if not update_data:
                return TodoRepository.get_todo_by_id(todo_id)

            # Update timestamp
            update_data['updated_at'] = datetime.utcnow().isoformat()

            response = supabase.table('todos').update(update_data).eq('id', todo_id).execute()

            if response.data:
                return Todo.from_dict(response.data[0])
            return None
        except Exception as e:
            print(f"Error updating todo {todo_id}: {e}")
            return None

    @staticmethod
    def delete_todo(todo_id: int) -> bool:
        """Delete a todo."""
        try:
            supabase = get_supabase_client()
            supabase.table('todos').delete().eq('id', todo_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting todo {todo_id}: {e}")
            return False

    @staticmethod
    def toggle_todo_completion(todo_id: int) -> Optional[Todo]:
        """Toggle todo completion status."""
        try:
            todo = TodoRepository.get_todo_by_id(todo_id)
            if todo:
                return TodoRepository.update_todo(todo_id, completed=not todo.completed)
            return None
        except Exception as e:
            print(f"Error toggling todo {todo_id}: {e}")
            return None

    @staticmethod
    def reorder_todos(todo_orders: List[Dict[str, int]]) -> bool:
        """Reorder todos based on provided order list."""
        try:
            supabase = get_supabase_client()

            for item in todo_orders:
                if 'id' not in item or 'order' not in item:
                    continue

                supabase.table('todos').update({
                    'order': item['order'],
                    'updated_at': datetime.utcnow().isoformat()
                }).eq('id', item['id']).execute()

            return True
        except Exception as e:
            print(f"Error reordering todos: {e}")
            return False


# For backward compatibility (if needed for initialization)
db = None

def init_sample_data(app):
    """Initialize sample data (not needed for Supabase as data persists)."""
    pass
