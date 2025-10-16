/**
 * ChatKit Integration Module
 * OpenAI ChatKitをオーバーレイ表示で統合するためのモジュール
 */

// 設定
const CHATKIT_CONFIG = {
    CDN_URL: 'https://cdn.platform.openai.com/deployments/chatkit/chatkit.js',
    SESSION_ENDPOINT: '/api/chatkit/create-session',
    LOAD_TIMEOUT: 10000, // 10秒
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

        console.log('✅ ChatKitManager initialized');
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
     * チャットを開く
     */
    async open() {
        console.log('📖 Opening chat...');
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
        console.log('📕 Closing chat...');
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

            // ChatKitスクリプトの読み込みを確認
            await this.waitForChatKit();

            console.log('📦 ChatKit script loaded');

            // ローディング表示を残したままChatKit要素を作成
            this.chatkitElement = document.createElement('openai-chatkit');

            // スタイル設定（より明示的に）
            Object.assign(this.chatkitElement.style, {
                width: '100%',
                height: '100%',
                display: 'block',
                position: 'absolute',
                top: '0',
                left: '0',
                right: '0',
                bottom: '0',
                zIndex: '1',
                visibility: 'visible',
                opacity: '1'
            });

            console.log('📍 Appending ChatKit element to DOM...');

            // DOMに追加
            this.elements.container.appendChild(this.chatkitElement);

            console.log('🔍 ChatKit element appended, checking visibility...');
            setTimeout(() => {
                console.log('Element dimensions:', {
                    width: this.chatkitElement.offsetWidth,
                    height: this.chatkitElement.offsetHeight,
                    display: window.getComputedStyle(this.chatkitElement).display,
                    visibility: window.getComputedStyle(this.chatkitElement).visibility
                });
            }, 100);

            console.log('⚙️ Configuring ChatKit with setOptions...');

            // setOptionsを呼ぶ（DOM追加後、nextTickで）
            await new Promise(resolve => setTimeout(resolve, 0));

            this.chatkitElement.setOptions({
                api: {
                    getClientSecret: async (currentSecret) => {
                        console.log('🔑 getClientSecret called', {
                            hasCurrentSecret: !!currentSecret
                        });

                        try {
                            const response = await fetch(CHATKIT_CONFIG.SESSION_ENDPOINT, {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify(currentSecret ? { refresh: true } : {})
                            });

                            if (!response.ok) {
                                const errorText = await response.text();
                                console.error('❌ Session creation failed:', response.status, errorText);
                                throw new Error(`Session creation failed: ${response.status}`);
                            }

                            const data = await response.json();

                            if (!data.client_secret) {
                                console.error('❌ No client_secret in response:', data);
                                throw new Error('No client_secret in response');
                            }

                            console.log('✅ Got client_secret successfully');

                            // ローディングを非表示（少し遅延させる）
                            setTimeout(() => {
                                if (this.elements.loading) {
                                    this.elements.loading.style.display = 'none';
                                }
                            }, 500);

                            return data.client_secret;

                        } catch (error) {
                            console.error('❌ getClientSecret error:', error);
                            this.showError(error.message || 'Failed to create session');
                            throw error;
                        }
                    }
                }
            });

            this.initialized = true;
            console.log('✅ ChatKit initialized successfully');

        } catch (error) {
            console.error('❌ ChatKit initialization failed:', error);
            this.showError(error.message || 'Failed to initialize ChatKit');
        }
    }

    /**
     * ChatKitスクリプトの読み込みを待つ
     */
    async waitForChatKit() {
        // すでに読み込まれている場合
        if (window.customElements && window.customElements.get('openai-chatkit')) {
            console.log('✅ ChatKit already loaded');
            return;
        }

        console.log('⏳ Waiting for ChatKit to load...');

        return new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                reject(new Error('ChatKit script load timeout'));
            }, CHATKIT_CONFIG.LOAD_TIMEOUT);

            const checkInterval = setInterval(() => {
                if (window.customElements && window.customElements.get('openai-chatkit')) {
                    clearTimeout(timeout);
                    clearInterval(checkInterval);
                    resolve();
                }
            }, 100);
        });
    }

    /**
     * エラーを表示
     */
    showError(message) {
        console.error('💥 Showing error to user:', message);

        if (this.elements.loading) {
            this.elements.loading.innerHTML = `
                <div class="text-center text-red-600 p-6">
                    <svg class="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    <p class="text-lg font-semibold mb-2">エラーが発生しました</p>
                    <p class="text-sm mb-4">${this.escapeHtml(message)}</p>
                    <button onclick="location.reload()"
                            class="mt-4 px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600">
                        再読み込み
                    </button>
                </div>
            `;
        }
    }

    /**
     * HTMLエスケープ（XSS対策）
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// グローバルインスタンスを作成
window.chatKitManager = new ChatKitManager();

// DOMContentLoadedで初期化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.chatKitManager.init();
    });
} else {
    window.chatKitManager.init();
}
