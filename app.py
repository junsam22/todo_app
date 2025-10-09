from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# データベース設定
basedir = os.path.abspath(os.path.dirname(__file__))
# Vercel用の設定: メモリ内データベースを使用（サーバーレス環境対応）
# Vercel環境の検出（複数の方法で確認）
is_vercel = (
    os.environ.get('VERCEL') or 
    os.environ.get('VERCEL_ENV') or 
    os.environ.get('NOW_REGION') or
    'vercel.app' in os.environ.get('VERCEL_URL', '')
)

if is_vercel:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "todo.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Todoモデル
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    priority = db.Column(db.String(10), default='medium')  # high, medium, low
    order = db.Column(db.Integer, default=0)  # ドラッグ&ドロップ用の順序
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
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

# ルート定義
@app.route('/')
def index():
    todos = Todo.query.order_by(Todo.order.asc(), Todo.created_at.desc()).all()
    return render_template('index.html', todos=todos)

@app.route('/api/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.order_by(Todo.order.asc(), Todo.created_at.desc()).all()
    return jsonify([todo.to_dict() for todo in todos])

@app.route('/api/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    
    # 新しいタスクの順序を設定（最後に追加）
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

@app.route('/api/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    return jsonify(todo.to_dict())

@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    data = request.get_json()
    
    todo.title = data.get('title', todo.title)
    todo.description = data.get('description', todo.description)
    todo.completed = data.get('completed', todo.completed)
    todo.priority = data.get('priority', todo.priority)
    todo.order = data.get('order', todo.order)
    todo.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify(todo.to_dict())

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    
    return '', 204

@app.route('/api/todos/<int:todo_id>/toggle', methods=['PATCH'])
def toggle_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    todo.completed = not todo.completed
    todo.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify(todo.to_dict())

@app.route('/api/todos/reorder', methods=['POST'])
def reorder_todos():
    data = request.get_json()
    todo_orders = data.get('todo_orders', [])
    
    try:
        for item in todo_orders:
            todo = Todo.query.get(item['id'])
            if todo:
                todo.order = item['order']
                todo.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Vercel用のWSGIアプリケーション
app = app

# アプリケーション起動時の初期化
def init_db():
    with app.app_context():
        # デバッグ用ログ
        print(f"Environment detection:")
        print(f"  VERCEL: {os.environ.get('VERCEL')}")
        print(f"  VERCEL_ENV: {os.environ.get('VERCEL_ENV')}")
        print(f"  NOW_REGION: {os.environ.get('NOW_REGION')}")
        print(f"  VERCEL_URL: {os.environ.get('VERCEL_URL')}")
        print(f"  is_vercel: {is_vercel}")
        print(f"  Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        db.create_all()
        # Vercel環境（メモリ内DB）の場合、サンプルデータを追加
        if is_vercel:
            # 既存のデータがあるかチェック
            if Todo.query.count() == 0:
                sample_todos = [
                    Todo(title="サンプルタスク1", description="これはサンプルタスクです", priority="high", order=1),
                    Todo(title="サンプルタスク2", description="ドラッグ&ドロップで順序を変更できます", priority="medium", order=2),
                    Todo(title="サンプルタスク3", description="編集・削除も可能です", priority="low", order=3)
                ]
                for todo in sample_todos:
                    db.session.add(todo)
                db.session.commit()

# アプリケーション起動時に初期化
init_db()

if __name__ == '__main__':
    app.run(debug=True)