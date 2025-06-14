#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
せつなBot Flask Web UI版デモ
Webブラウザベースのインターフェース
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import sys
import os
import time
import threading

# せつなBotコアモジュールのパス追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'setsuna-bot-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# グローバル状態管理
bot_state = {
    'conversation_count': 0,
    'voice_settings': {
        'speed': 1.2,
        'pitch': 0.0,
        'intonation': 1.0
    },
    'system_status': 'ready',
    'chat_history': []
}

@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """システム状態API"""
    return jsonify({
        'status': bot_state['system_status'],
        'conversation_count': bot_state['conversation_count'],
        'voice_settings': bot_state['voice_settings']
    })

@app.route('/api/voice/settings', methods=['POST'])
def update_voice_settings():
    """音声設定更新API"""
    data = request.json
    
    if 'speed' in data and 0.5 <= data['speed'] <= 2.0:
        bot_state['voice_settings']['speed'] = data['speed']
    
    if 'pitch' in data and -0.15 <= data['pitch'] <= 0.15:
        bot_state['voice_settings']['pitch'] = data['pitch']
    
    if 'intonation' in data and 0.5 <= data['intonation'] <= 2.0:
        bot_state['voice_settings']['intonation'] = data['intonation']
    
    # 全クライアントに設定更新を通知
    socketio.emit('voice_settings_updated', bot_state['voice_settings'])
    
    return jsonify({'success': True, 'settings': bot_state['voice_settings']})

@app.route('/api/voice/test', methods=['POST'])
def voice_test():
    """音声テストAPI"""
    def test_worker():
        bot_state['system_status'] = 'testing'
        socketio.emit('status_update', {'status': 'testing', 'message': '音声テスト実行中...'})
        
        time.sleep(2)  # テストシミュレーション
        
        bot_state['system_status'] = 'ready'
        socketio.emit('status_update', {'status': 'ready', 'message': '音声テスト完了'})
    
    threading.Thread(target=test_worker, daemon=True).start()
    return jsonify({'success': True, 'message': '音声テストを開始しました'})

@socketio.on('send_message')
def handle_message(data):
    """チャットメッセージ処理"""
    user_message = data['message']
    
    # ユーザーメッセージを履歴に追加
    user_entry = {
        'type': 'user',
        'message': user_message,
        'timestamp': time.time()
    }
    bot_state['chat_history'].append(user_entry)
    
    # 応答生成
    response = generate_response(user_message)
    bot_entry = {
        'type': 'bot',
        'message': response,
        'timestamp': time.time()
    }
    bot_state['chat_history'].append(bot_entry)
    
    # 対話回数更新
    bot_state['conversation_count'] += 1
    
    # クライアントに応答送信
    emit('receive_message', {
        'user_message': user_message,
        'bot_response': response,
        'conversation_count': bot_state['conversation_count']
    }, broadcast=True)

@socketio.on('connect')
def handle_connect():
    """クライアント接続時"""
    print('クライアントが接続しました')
    emit('status_update', {
        'status': bot_state['system_status'],
        'conversation_count': bot_state['conversation_count'],
        'voice_settings': bot_state['voice_settings']
    })

@socketio.on('disconnect')
def handle_disconnect():
    """クライアント切断時"""
    print('クライアントが切断しました')

def generate_response(user_input):
    """簡易応答生成"""
    responses = {
        "こんにちは": "こんにちは！元気ですか？",
        "おはよう": "おはようございます！今日も良い一日にしましょう！",
        "ありがとう": "どういたしまして！いつでもお手伝いします。",
        "さようなら": "また今度お話ししましょうね！",
        "元気": "それは良かったです！私も元気です。",
        "疲れた": "お疲れ様です。少し休憩してくださいね。",
    }
    
    for keyword, response in responses.items():
        if keyword in user_input:
            return response
    
    return f"「{user_input}」についてお話しするのは楽しいですね！他に何かありますか？"

# HTMLテンプレートを作成
html_template = '''
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 せつなBot - Web UI</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body {
            font-family: 'Hiragino Sans', 'Yu Gothic', sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f0f2f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 1fr 300px;
            gap: 20px;
        }
        .main-panel {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .sidebar {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            height: fit-content;
        }
        .title {
            color: #1976d2;
            margin-bottom: 20px;
            text-align: center;
        }
        .chat-container {
            height: 400px;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            overflow-y: auto;
            margin-bottom: 15px;
            background-color: #fafafa;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 8px;
        }
        .user-message {
            background-color: #e3f2fd;
            text-align: right;
        }
        .bot-message {
            background-color: #f1f8e9;
        }
        .input-container {
            display: flex;
            gap: 10px;
        }
        #messageInput {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            transition: background-color 0.3s;
        }
        .btn-primary {
            background-color: #1976d2;
            color: white;
        }
        .btn-primary:hover {
            background-color: #1565c0;
        }
        .btn-secondary {
            background-color: #757575;
            color: white;
        }
        .btn-secondary:hover {
            background-color: #616161;
        }
        .settings-section {
            margin-bottom: 20px;
        }
        .settings-section h3 {
            margin-bottom: 10px;
            color: #333;
        }
        .slider-container {
            margin-bottom: 15px;
        }
        .slider-container label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        .slider-container input {
            width: 100%;
            margin-bottom: 5px;
        }
        .slider-value {
            text-align: center;
            color: #666;
            font-size: 12px;
        }
        .status-section {
            text-align: center;
        }
        .status-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            color: white;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .status-ready { background-color: #4caf50; }
        .status-testing { background-color: #ff9800; }
        .status-error { background-color: #f44336; }
    </style>
</head>
<body>
    <div class="container">
        <div class="main-panel">
            <h1 class="title">🤖 せつなBot - 音声対話システム</h1>
            
            <div class="chat-container" id="chatContainer">
                <div class="message bot-message">
                    <strong>🤖 せつな:</strong> こんにちは！何かお話ししましょうか？
                </div>
            </div>
            
            <div class="input-container">
                <input type="text" id="messageInput" placeholder="メッセージを入力...">
                <button class="btn btn-primary" onclick="sendMessage()">送信</button>
            </div>
        </div>
        
        <div class="sidebar">
            <div class="status-section">
                <h3>📊 システム状態</h3>
                <div class="status-badge status-ready" id="statusBadge">待機中</div>
                <div>対話回数: <span id="conversationCount">0</span>回</div>
            </div>
            
            <div class="settings-section">
                <h3>🎛️ 音声設定</h3>
                
                <div class="slider-container">
                    <label>話速</label>
                    <input type="range" id="speedSlider" min="0.5" max="2.0" step="0.1" value="1.2">
                    <div class="slider-value" id="speedValue">1.2x</div>
                </div>
                
                <div class="slider-container">
                    <label>音程</label>
                    <input type="range" id="pitchSlider" min="-0.15" max="0.15" step="0.01" value="0.0">
                    <div class="slider-value" id="pitchValue">0.00</div>
                </div>
                
                <div class="slider-container">
                    <label>抑揚</label>
                    <input type="range" id="intonationSlider" min="0.5" max="2.0" step="0.1" value="1.0">
                    <div class="slider-value" id="intonationValue">1.0</div>
                </div>
            </div>
            
            <div class="settings-section">
                <button class="btn btn-secondary" onclick="voiceTest()" style="width: 100%; margin-bottom: 10px;">
                    🔊 音声テスト
                </button>
                <button class="btn btn-secondary" onclick="resetSettings()" style="width: 100%;">
                    🔄 設定リセット
                </button>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        
        // 音声設定スライダーイベント
        document.getElementById('speedSlider').addEventListener('input', updateVoiceSettings);
        document.getElementById('pitchSlider').addEventListener('input', updateVoiceSettings);
        document.getElementById('intonationSlider').addEventListener('input', updateVoiceSettings);
        
        // Enter キーでメッセージ送信
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            if (message) {
                socket.emit('send_message', {message: message});
                input.value = '';
            }
        }
        
        function updateVoiceSettings() {
            const speed = parseFloat(document.getElementById('speedSlider').value);
            const pitch = parseFloat(document.getElementById('pitchSlider').value);
            const intonation = parseFloat(document.getElementById('intonationSlider').value);
            
            document.getElementById('speedValue').textContent = speed.toFixed(1) + 'x';
            document.getElementById('pitchValue').textContent = pitch.toFixed(2);
            document.getElementById('intonationValue').textContent = intonation.toFixed(1);
            
            fetch('/api/voice/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    speed: speed,
                    pitch: pitch,
                    intonation: intonation
                })
            });
        }
        
        function voiceTest() {
            fetch('/api/voice/test', {
                method: 'POST'
            });
        }
        
        function resetSettings() {
            document.getElementById('speedSlider').value = 1.2;
            document.getElementById('pitchSlider').value = 0.0;
            document.getElementById('intonationSlider').value = 1.0;
            updateVoiceSettings();
        }
        
        // Socket.IO イベントリスナー
        socket.on('receive_message', function(data) {
            const chatContainer = document.getElementById('chatContainer');
            
            // ユーザーメッセージ
            const userDiv = document.createElement('div');
            userDiv.className = 'message user-message';
            userDiv.innerHTML = '<strong>👤 あなた:</strong> ' + data.user_message;
            chatContainer.appendChild(userDiv);
            
            // ボットメッセージ
            const botDiv = document.createElement('div');
            botDiv.className = 'message bot-message';
            botDiv.innerHTML = '<strong>🤖 せつな:</strong> ' + data.bot_response;
            chatContainer.appendChild(botDiv);
            
            // 対話回数更新
            document.getElementById('conversationCount').textContent = data.conversation_count;
            
            // スクロール
            chatContainer.scrollTop = chatContainer.scrollHeight;
        });
        
        socket.on('status_update', function(data) {
            const statusBadge = document.getElementById('statusBadge');
            statusBadge.className = 'status-badge status-' + data.status;
            
            if (data.status === 'ready') {
                statusBadge.textContent = '待機中';
            } else if (data.status === 'testing') {
                statusBadge.textContent = 'テスト中';
            }
            
            if (data.conversation_count !== undefined) {
                document.getElementById('conversationCount').textContent = data.conversation_count;
            }
        });
    </script>
</body>
</html>
'''

# テンプレートディレクトリ作成
os.makedirs('templates', exist_ok=True)
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

if __name__ == '__main__':
    print("🚀 せつなBot Web UI版起動中...")
    print("ブラウザで http://localhost:5000 にアクセスしてください")
    print("Ctrl+C で終了")
    
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n👋 せつなBot Web UI版を終了します")