-- todosテーブルを作成
CREATE TABLE IF NOT EXISTS todos (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT false,
    priority TEXT DEFAULT 'medium',
    "order" INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- updated_atを自動更新するトリガー関数を作成
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- トリガーを作成
DROP TRIGGER IF EXISTS update_todos_updated_at ON todos;
CREATE TRIGGER update_todos_updated_at BEFORE UPDATE ON todos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS)を有効化
ALTER TABLE todos ENABLE ROW LEVEL SECURITY;

-- 全ユーザーに読み書き権限を付与（開発用）
DROP POLICY IF EXISTS "Enable all access for todos" ON todos;
CREATE POLICY "Enable all access for todos" ON todos
    FOR ALL USING (true) WITH CHECK (true);
