# Todo App

シンプルで使いやすいタスク管理Webアプリケーションです。

## 機能

- ✅ タスクの作成・編集・削除
- ✅ タスクの完了切り替え
- ✅ 優先度設定（高・中・低）
- ✅ 期限設定
- ✅ タスクのフィルタリング（すべて・未完了・完了）
- ✅ レスポンシブデザイン（モバイル対応）
- ✅ リアルタイム更新

## 技術スタック

- **バックエンド**: Python + Flask
- **データベース**: SQLite
- **フロントエンド**: HTML + Tailwind CSS + Vanilla JavaScript
- **ORM**: SQLAlchemy

## セットアップ

### 1. 依存関係のインストール

```bash
cd todo_app
pip install -r requirements.txt
```

### 2. アプリケーションの起動

```bash
python app.py
```

### 3. ブラウザでアクセス

```
http://localhost:5000
```

## プロジェクト構成

```
todo_app/
├── app.py                 # Flask アプリケーション
├── requirements.txt       # Python依存関係
├── todo.db               # SQLiteデータベース（自動生成）
├── templates/
│   ├── base.html         # ベーステンプレート
│   └── index.html        # メインページ
└── static/
    ├── css/
    │   └── style.css     # カスタムCSS
    └── js/
        └── app.js        # JavaScript
```

## API エンドポイント

- `GET /api/todos` - タスク一覧取得
- `POST /api/todos` - タスク作成
- `PUT /api/todos/<id>` - タスク更新
- `DELETE /api/todos/<id>` - タスク削除
- `PATCH /api/todos/<id>/toggle` - タスク完了切り替え

## 使い方

1. **タスクの作成**: 上部のフォームから新しいタスクを作成
2. **タスクの編集**: タスクの編集ボタン（鉛筆アイコン）をクリック
3. **タスクの完了**: チェックボックスをクリック
4. **タスクの削除**: 削除ボタン（ゴミ箱アイコン）をクリック
5. **フィルタリング**: 上部のボタンでタスクを絞り込み

## 特徴

- **シンプル**: 必要最小限の機能で使いやすい
- **レスポンシブ**: スマートフォン・タブレット対応
- **高速**: 軽量な構成で高速動作
- **美しいUI**: Tailwind CSSによるモダンなデザイン

## ライセンス

MIT License
