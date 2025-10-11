// Todo App JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // DOM要素の取得
    const todoForm = document.getElementById('todo-form');
    const editForm = document.getElementById('edit-form');
    const editModal = document.getElementById('edit-modal');
    const cancelEditBtn = document.getElementById('cancel-edit');
    const todoList = document.getElementById('todo-list');
    const filterButtons = document.querySelectorAll('[id^="filter-"]');
    const emptyMessage = document.getElementById('empty-message');
    
    let currentFilter = 'all';
    
    // イベントリスナーの設定
    todoForm.addEventListener('submit', handleCreateTodo);
    editForm.addEventListener('submit', handleUpdateTodo);
    cancelEditBtn.addEventListener('click', closeEditModal);

    // AI生成ボタンのイベントリスナー
    const aiGenerateBtn = document.getElementById('ai-generate-btn');
    const aiGenerateEditBtn = document.getElementById('ai-generate-edit-btn');

    if (aiGenerateBtn) {
        aiGenerateBtn.addEventListener('click', () => handleAIGenerate(false));
    }

    if (aiGenerateEditBtn) {
        aiGenerateEditBtn.addEventListener('click', () => handleAIGenerate(true));
    }
    
    // フィルターボタンのイベントリスナー
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const filter = this.id.replace('filter-', '');
            setFilter(filter);
        });
    });
    
    // タスク一覧のイベントリスナー（イベント委譲）
    todoList.addEventListener('click', function(e) {
        if (e.target.closest('.todo-toggle')) {
            const todoId = e.target.closest('.todo-toggle').dataset.id;
            toggleTodo(todoId);
        } else if (e.target.closest('.edit-todo')) {
            const todoId = e.target.closest('.edit-todo').dataset.id;
            openEditModal(todoId);
        } else if (e.target.closest('.delete-todo')) {
            const todoId = e.target.closest('.delete-todo').dataset.id;
            deleteTodo(todoId);
        }
    });
    
    // AI生成機能
    async function handleAIGenerate(isEditMode) {
        const titleInput = isEditMode ? document.getElementById('edit-title') : document.getElementById('title');
        const descriptionInput = isEditMode ? document.getElementById('edit-description') : document.getElementById('description');
        const generateBtn = isEditMode ? document.getElementById('ai-generate-edit-btn') : document.getElementById('ai-generate-btn');

        const title = titleInput.value.trim();

        if (!title) {
            showMessage('タイトルを入力してください', 'error');
            return;
        }

        // ボタンを無効化してローディング状態にする
        const originalText = generateBtn.innerHTML;
        generateBtn.disabled = true;
        generateBtn.innerHTML = `
            <svg class="animate-spin h-3 w-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>生成中...</span>
        `;

        try {
            const response = await fetch('/api/generate-description', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ title })
            });

            if (response.ok) {
                const data = await response.json();
                descriptionInput.value = data.description;
                showMessage('説明文を生成しました', 'success');
            } else {
                throw new Error('説明文の生成に失敗しました');
            }
        } catch (error) {
            console.error('Error:', error);
            showMessage('説明文の生成に失敗しました', 'error');
        } finally {
            // ボタンを元に戻す
            generateBtn.disabled = false;
            generateBtn.innerHTML = originalText;
        }
    }

    // 新しいタスクの作成
    async function handleCreateTodo(e) {
        e.preventDefault();
        
        const formData = new FormData(todoForm);
        const todoData = {
            title: formData.get('title'),
            description: formData.get('description'),
            priority: formData.get('priority')
        };
        
        try {
            const response = await fetch('/api/todos', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(todoData)
            });
            
            if (response.ok) {
                const newTodo = await response.json();
                addTodoToList(newTodo);
                todoForm.reset();
                showMessage('タスクが作成されました', 'success');
            } else {
                throw new Error('タスクの作成に失敗しました');
            }
        } catch (error) {
            console.error('Error:', error);
            showMessage('タスクの作成に失敗しました', 'error');
        }
    }
    
    // タスクの更新
    async function handleUpdateTodo(e) {
        e.preventDefault();
        
        const todoId = document.getElementById('edit-id').value;
        const formData = new FormData(editForm);
        const todoData = {
            title: formData.get('edit-title'),
            description: formData.get('edit-description'),
            priority: formData.get('edit-priority')
        };
        
        try {
            const response = await fetch(`/api/todos/${todoId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(todoData)
            });
            
            if (response.ok) {
                const updatedTodo = await response.json();
                updateTodoInList(updatedTodo);
                closeEditModal();
                showMessage('タスクが更新されました', 'success');
            } else {
                throw new Error('タスクの更新に失敗しました');
            }
        } catch (error) {
            console.error('Error:', error);
            showMessage('タスクの更新に失敗しました', 'error');
        }
    }
    
    // タスクの完了切り替え
    async function toggleTodo(todoId) {
        try {
            const response = await fetch(`/api/todos/${todoId}/toggle`, {
                method: 'PATCH'
            });
            
            if (response.ok) {
                const updatedTodo = await response.json();
                updateTodoInList(updatedTodo);
            } else {
                throw new Error('タスクの更新に失敗しました');
            }
        } catch (error) {
            console.error('Error:', error);
            showMessage('タスクの更新に失敗しました', 'error');
        }
    }
    
    // タスクの削除
    async function deleteTodo(todoId) {
        if (!confirm('このタスクを削除しますか？')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/todos/${todoId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                removeTodoFromList(todoId);
                showMessage('タスクが削除されました', 'success');
            } else {
                throw new Error('タスクの削除に失敗しました');
            }
        } catch (error) {
            console.error('Error:', error);
            showMessage('タスクの削除に失敗しました', 'error');
        }
    }
    
    // 編集モーダルを開く
    async function openEditModal(todoId) {
        try {
            const response = await fetch(`/api/todos/${todoId}`);
            if (response.ok) {
                const todo = await response.json();
                
                document.getElementById('edit-id').value = todo.id;
                document.getElementById('edit-title').value = todo.title;
                document.getElementById('edit-description').value = todo.description || '';
                document.getElementById('edit-priority').value = todo.priority;
                
                editModal.classList.remove('hidden');
                editModal.classList.add('show');
            }
        } catch (error) {
            console.error('Error:', error);
            showMessage('タスクの取得に失敗しました', 'error');
        }
    }
    
    // 編集モーダルを閉じる
    function closeEditModal() {
        editModal.classList.add('hidden');
        editModal.classList.remove('show');
        editForm.reset();
    }
    
    // フィルターの設定
    function setFilter(filter) {
        currentFilter = filter;
        
        // フィルターボタンの状態更新
        filterButtons.forEach(button => {
            button.classList.remove('filter-active');
            if (button.id === `filter-${filter}`) {
                button.classList.add('filter-active');
            }
        });
        
        // タスクの表示/非表示
        const todoItems = document.querySelectorAll('.todo-item');
        todoItems.forEach(item => {
            const isCompleted = item.dataset.completed === 'true';
            
            switch (filter) {
                case 'all':
                    item.style.display = 'block';
                    break;
                case 'active':
                    item.style.display = isCompleted ? 'none' : 'block';
                    break;
                case 'completed':
                    item.style.display = isCompleted ? 'block' : 'none';
                    break;
            }
        });
        
        updateEmptyState();
    }
    
    // タスクをリストに追加（優先度順）
    function addTodoToList(todo) {
        const todoElement = createTodoElement(todo);

        // 優先度のマッピング（高 > 中 > 低）
        const priorityValue = {
            'high': 3,
            'medium': 2,
            'low': 1
        };

        const newPriority = priorityValue[todo.priority] || 0;
        const newCreatedAt = new Date(todo.created_at);

        // 既存のタスクを取得して適切な位置を探す
        const existingTodos = Array.from(todoList.querySelectorAll('.todo-item'));
        let insertPosition = null;

        for (const existingTodo of existingTodos) {
            const existingPriority = priorityValue[existingTodo.dataset.priority] || 0;

            // 優先度が低い、または優先度が同じで作成日時が古いタスクを見つけたらその前に挿入
            if (newPriority > existingPriority) {
                insertPosition = existingTodo;
                break;
            }
        }

        if (insertPosition) {
            todoList.insertBefore(todoElement, insertPosition);
        } else {
            todoList.appendChild(todoElement);
        }

        updateEmptyState();
    }
    
    // タスクをリストから更新（優先度変更時は再配置）
    function updateTodoInList(todo) {
        const existingElement = document.querySelector(`[data-id="${todo.id}"]`);
        if (existingElement) {
            existingElement.remove();
        }
        // 削除してから追加することで、優先度順に再配置される
        addTodoToList(todo);
    }
    
    // タスクをリストから削除
    function removeTodoFromList(todoId) {
        const element = document.querySelector(`[data-id="${todoId}"]`);
        if (element) {
            element.remove();
        }
        updateEmptyState();
    }
    
    // タスクが存在しない場合のメッセージを制御
    function updateEmptyState() {
        if (!emptyMessage) {
            return;
        }
        
        const todoItems = Array.from(document.querySelectorAll('.todo-item'));
        const hasVisibleTodo = todoItems.some(item => item.style.display !== 'none');
        
        if (todoItems.length === 0 || !hasVisibleTodo) {
            emptyMessage.classList.remove('hidden');
        } else {
            emptyMessage.classList.add('hidden');
        }
    }
    
    // Helper: Get priority label in Japanese
    function getPriorityLabel(priority) {
        const labels = {
            'high': '高優先度',
            'medium': '中優先度',
            'low': '低優先度'
        };
        return labels[priority] || '中優先度';
    }

    // Helper: Get priority badge class
    function getPriorityBadgeClass(priority) {
        const classes = {
            'high': 'bg-red-100 text-red-800',
            'medium': 'bg-yellow-100 text-yellow-800',
            'low': 'bg-green-100 text-green-800'
        };
        return classes[priority] || 'bg-yellow-100 text-yellow-800';
    }

    // Helper: Create SVG icon for completed task
    function getCheckIcon() {
        return `
            <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
            </svg>
        `;
    }

    // タスク要素を作成（ドラッグ&ドロップ対応）
    function createTodoElement(todo) {
        const div = document.createElement('div');
        div.className = `todo-item border border-gray-200 rounded-lg p-4 hover:shadow-md transition duration-200 cursor-move priority-${todo.priority}`;
        div.dataset.id = todo.id;
        div.dataset.completed = todo.completed;
        div.dataset.priority = todo.priority;
        div.dataset.order = todo.order || 0;

        const createdDate = new Date(todo.created_at);
        const completedClass = todo.completed ? 'line-through text-gray-500' : '';

        div.innerHTML = `
            <div class="flex items-start justify-between">
                <div class="flex items-start space-x-3 flex-1">
                    <button class="todo-toggle mt-1 w-5 h-5 rounded border-2 border-gray-300 flex items-center justify-center
                                 ${todo.completed ? 'bg-green-500 border-green-500' : ''}"
                            data-id="${todo.id}">
                        ${todo.completed ? getCheckIcon() : ''}
                    </button>

                    <div class="flex-1">
                        <h3 class="text-lg font-medium text-gray-800 ${completedClass}">
                            ${escapeHtml(todo.title)}
                        </h3>
                        ${todo.description ? `
                            <p class="text-gray-600 mt-1 ${todo.completed ? 'line-through' : ''}">
                                ${escapeHtml(todo.description)}
                            </p>
                        ` : ''}

                        <div class="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                            <span class="priority-badge px-2 py-1 rounded-full text-xs font-medium ${getPriorityBadgeClass(todo.priority)}">
                                ${getPriorityLabel(todo.priority)}
                            </span>

                            <span class="text-xs">
                                作成: ${createdDate.toLocaleDateString('ja-JP')}
                            </span>
                        </div>
                    </div>
                </div>

                <div class="flex items-center space-x-2 ml-4">
                    <button class="edit-todo text-blue-500 hover:text-blue-700 p-1" data-id="${todo.id}">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                        </svg>
                    </button>
                    <button class="delete-todo text-red-500 hover:text-red-700 p-1" data-id="${todo.id}">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                        </svg>
                    </button>
                </div>
            </div>
        `;

        return div;
    }

    // Helper: Escape HTML to prevent XSS
    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    // メッセージ表示
    function showMessage(message, type) {
        // 既存のメッセージを削除
        const existingMessage = document.querySelector('.message');
        if (existingMessage) {
            existingMessage.remove();
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `message fixed top-4 right-4 px-4 py-2 rounded-md text-white z-50 ${
            type === 'success' ? 'bg-green-500' : 'bg-red-500'
        }`;
        messageDiv.textContent = message;

        document.body.appendChild(messageDiv);

        // 3秒後に自動削除
        setTimeout(() => {
            messageDiv.remove();
        }, 3000);
    }

    // ドラッグ&ドロップ機能の初期化
    function initializeSortable() {
        if (typeof Sortable !== 'undefined') {
            Sortable.create(todoList, {
                animation: 150,
                ghostClass: 'sortable-ghost',
                chosenClass: 'sortable-chosen',
                dragClass: 'sortable-drag',
                handle: '.todo-item',
                onEnd: updateTodoOrder
            });
        }
    }

    // タスクの順序を更新
    async function updateTodoOrder() {
        const todoItems = document.querySelectorAll('.todo-item');
        const todoOrders = Array.from(todoItems).map((item, index) => ({
            id: parseInt(item.dataset.id),
            order: index + 1
        }));

        try {
            const response = await fetch('/api/todos/reorder', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ todo_orders: todoOrders })
            });

            if (response.ok) {
                console.log('タスクの順序が更新されました');
            } else {
                throw new Error('タスクの順序更新に失敗しました');
            }
        } catch (error) {
            console.error('Error:', error);
            showMessage('タスクの順序更新に失敗しました', 'error');
        }
    }
    
    // 初期化時にフィルターを設定
    setFilter('all');
    
    // ドラッグ&ドロップ機能を初期化
    initializeSortable();
});
