"""Test Supabase insert directly."""
from supabase_client import get_supabase_client

try:
    supabase = get_supabase_client()

    # Test insert
    print("Testing Supabase insert...")
    todo_data = {
        'title': 'Direct Insert Test',
        'description': 'Testing direct Supabase insert',
        'priority': 'high',
        'order': 1,
        'completed': False
    }

    response = supabase.table('todos').insert(todo_data).execute()
    print(f"✓ Insert successful!")
    print(f"Response: {response.data}")

    # Test select
    print("\nTesting Supabase select...")
    response = supabase.table('todos').select('*').execute()
    print(f"✓ Select successful!")
    print(f"Found {len(response.data)} todos")
    for todo in response.data:
        print(f"  - {todo['title']}")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
