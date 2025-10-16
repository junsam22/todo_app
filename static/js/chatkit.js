/**
 * ChatKit Integration Module
 * OpenAI ChatKitをオーバーレイ表示で統合するためのモジュール
 */

// 設定
const CHATKIT_CONFIG = {
    CDN_URL: 'https://cdn.platform.openai.com/deployments/chatkit/chatkit.js',
    SESSION_ENDPOINT: '/api/chatkit/create-session',
    LOAD_TIMEOUT: 10000, // 10秒
    CHECK_INTERVAL: 100, // 100ms
    MAX_CHECKS: 50 // 5秒間チェック
};

class ChatKitManager {
    constructor() {
        this.initialized = false;
        this.chatkitElement = null;
        this.elements = {};
    }

    /**
     * 初期化 - DOM要素を取得してイベントリスナーを設定
     */
    init() {
        // DOM要素を取得
        this.elements = {
            toggleBtn: document.getElementById('chat-toggle-btn'),
            chatIcon: document.getElementById('chat-icon'),
            closeIcon: document.getElementById('close-icon'),
            overlay: document.getElementById('chatkit-overlay'),
            closeBtn: document.getElementById('close-chat-btn'),
            container: document.getElementById('chatkit-container'),
            loading: document.getElementById('chatkit-loading')
        };

        // イベントリスナーを設定
        this.setupEventListeners();

        // ChatKitスクリプトのロード確認を開始
        this.checkChatKitLoaded();
    }

    /**
     * イベントリスナーの設定
     */
    setupEventListeners() {
        // トグルボタン
        if (this.elements.toggleBtn) {
            this.elements.toggleBtn.addEventListener('click', () => this.toggle());
        }

        // 閉じるボタン
        if (this.elements.closeBtn) {
            this.elements.closeBtn.addEventListener('click', () => this.close());
        }

        // オーバーレイクリックで閉じる
        this.elements.overlay.addEventListener('click', (e) => {
            if (e.target === this.elements.overlay) {
                this.close();
            }
        });

        // ESCキーで閉じる
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !this.elements.overlay.classList.contains('hidden')) {
                this.close();
            }
        });
    }

    /**
     * ChatKitスクリプトの読み込み確認
     */
    checkChatKitLoaded() {
        let checkCount = 0;

        const check = () => {
            if (window.customElements && window.customElements.get('openai-chatkit')) {
                console.log('✅ ChatKit loaded successfully');
                window.dispatchEvent(new CustomEvent('chatkit-ready'));
                return;
            }

            checkCount++;
            if (checkCount < CHATKIT_CONFIG.MAX_CHECKS) {
                setTimeout(check, CHATKIT_CONFIG.CHECK_INTERVAL);
            } else {
                console.error('❌ ChatKit failed to load');
                window.dispatchEvent(new CustomEvent('chatkit-error', {
                    detail: 'Failed to load ChatKit after timeout'
                }));
            }
        };

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', check);
        } else {
            check();
        }
    }

    /**
     * チャットを開く
     */
    async open() {
        this.elements.overlay.classList.remove('hidden');
        this.elements.chatIcon.classList.add('hidden');
        this.elements.closeIcon.classList.remove('hidden');

        if (!this.initialized) {
            await this.initializeChatKit();
        }
    }

    /**
     * チャットを閉じる
     */
    close() {
        this.elements.overlay.classList.add('hidden');
        this.elements.chatIcon.classList.remove('hidden');
        this.elements.closeIcon.classList.add('hidden');
    }

    /**
     * チャットの開閉をトグル
     */
    toggle() {
        if (this.elements.overlay.classList.contains('hidden')) {
            this.open();
        } else {
            this.close();
        }
    }

    /**
     * ChatKitを初期化
     */
    async initializeChatKit() {
        try {
            console.log('🚀 Initializing ChatKit...');

            // ChatKitの読み込みを待つ
            await this.waitForChatKitReady();

            // ローディングを非表示
            if (this.elements.loading) {
                this.elements.loading.style.display = 'none';
            }

            // ChatKit要素を作成
            this.chatkitElement = document.createElement('openai-chatkit');
            this.chatkitElement.style.width = '100%';
            this.chatkitElement.style.height = '100%';
            this.chatkitElement.style.display = 'block';

            // ChatKitの設定
            this.chatkitElement.setOptions({
                api: {
                    getClientSecret: this.getClientSecret.bind(this)
                }
            });

            this.elements.container.appendChild(this.chatkitElement);
            this.initialized = true;

            console.log('✅ ChatKit initialized successfully');

        } catch (error) {
            console.error('❌ ChatKit initialization failed:', error);
            this.showError(error.message);
        }
    }

    /**
     * ChatKitの読み込み完了を待つ
     */
    waitForChatKitReady() {
        return new Promise((resolve, reject) => {
            if (window.customElements && window.customElements.get('openai-chatkit')) {
                resolve();
                return;
            }

            const timeout = setTimeout(() => {
                reject(new Error('Timeout waiting for ChatKit'));
            }, CHATKIT_CONFIG.LOAD_TIMEOUT);

            window.addEventListener('chatkit-ready', () => {
                clearTimeout(timeout);
                resolve();
            }, { once: true });

            window.addEventListener('chatkit-error', (e) => {
                clearTimeout(timeout);
                reject(new Error(e.detail));
            }, { once: true });
        });
    }

    /**
     * クライアントシークレットを取得（ChatKitから呼ばれる）
     */
    async getClientSecret(currentClientSecret) {
        console.log('🔑 getClientSecret called', { hasExisting: !!currentClientSecret });

        try {
            // 既存のclient_secretがある場合はリフレッシュ
            if (currentClientSecret) {
                console.log('♻️ Refreshing session...');
                return await this.createSession({ refresh: true });
            }

            // 新しいセッションを作成
            console.log('🆕 Creating new session...');
            return await this.createSession({});

        } catch (error) {
            console.error('❌ Failed to get client secret:', error);
            throw error;
        }
    }

    /**
     * セッションを作成
     */
    async createSession(payload = {}) {
        const response = await fetch(CHATKIT_CONFIG.SESSION_ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Session creation failed: ${response.status} - ${errorText}`);
        }

        const data = await response.json();
        console.log('✅ Got client_secret');
        return data.client_secret;
    }

    /**
     * エラーを表示
     */
    showError(message) {
        if (this.elements.loading) {
            this.elements.loading.innerHTML = `
                <div class="text-center text-red-600 p-6">
                    <p class="text-lg font-semibold mb-2">エラーが発生しました</p>
                    <p class="text-sm mb-2">${message}</p>
                    <button onclick="location.reload()"
                            class="mt-4 px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600">
                        再読み込み
                    </button>
                </div>
            `;
        }
    }
}

// グローバルインスタンスを作成
window.chatKitManager = new ChatKitManager();

// DOMContentLoadedで初期化
document.addEventListener('DOMContentLoaded', () => {
    window.chatKitManager.init();
});
