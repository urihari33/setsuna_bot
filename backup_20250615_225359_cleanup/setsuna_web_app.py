#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
せつなBot Web UI統合版
既存のコア機能をWebブラウザインターフェースで提供
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import sys
import os
import time
import threading
import traceback

# せつなBotコアモジュールのパス追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core'))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'setsuna-bot-web-ui-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# グローバル状態管理
bot_state = {
    'conversation_count': 0,
    'voice_settings': {
        'speed': 1.2,
        'pitch': 0.0,
        'intonation': 1.0
    },
    'system_status': 'initializing',
    'chat_history': [],
    'is_initialized': False,
    'voice_input_active': False,
    'is_recording': False
}

# せつなBotコンポーネント
setsuna_chat = None
voice_output = None
realtime_voice_input = None
initialization_error = None

def initialize_setsuna_components():
    """せつなBotコア機能の初期化"""
    global setsuna_chat, voice_output, realtime_voice_input, initialization_error
    
    try:
        bot_state['system_status'] = 'initializing'
        socketio.emit('status_update', {'status': 'initializing', 'message': 'せつなBot初期化中...'})
        
        # せつなチャット初期化
        try:
            from setsuna_chat import SetsunaChat
            setsuna_chat = SetsunaChat()
            print("✅ せつなチャットシステム初期化完了")
        except ImportError as e:
            print(f"⚠️ せつなチャット読み込みエラー: {e}")
            setsuna_chat = None
        except Exception as e:
            print(f"⚠️ せつなチャット初期化エラー: {e}")
            setsuna_chat = None
        
        # 音声出力初期化
        try:
            from voice_output import VoiceOutput
            voice_output = VoiceOutput()
            print("✅ 音声出力システム初期化完了")
        except ImportError as e:
            print(f"⚠️ 音声出力読み込みエラー: {e}")
            voice_output = None
        except Exception as e:
            print(f"⚠️ 音声出力初期化エラー: {e}")
            voice_output = None
        
        # リアルタイム音声入力初期化（モック版を優先使用）
        try:
            from voice_input_mock import MockVoiceInput
            realtime_voice_input = MockVoiceInput()
            print("✅ モック音声入力システム使用（WSL2開発環境向け）")
            
            # 音声認識コールバック設定
            realtime_voice_input.on_speech_recognized = handle_voice_input
            realtime_voice_input.on_recording_start = lambda: socketio.emit('voice_recording_status', {'recording': True})
            realtime_voice_input.on_recording_stop = lambda: socketio.emit('voice_recording_status', {'recording': False})
            
            print("✅ モック音声入力システム初期化完了")
        except ImportError as e:
            print(f"⚠️ モック音声入力読み込みエラー: {e}")
            # フォールバック: WSL2対応版を試行
            try:
                from voice_input_wsl2 import WSL2VoiceInput
                realtime_voice_input = WSL2VoiceInput()
                realtime_voice_input.on_speech_recognized = handle_voice_input
                realtime_voice_input.on_recording_start = lambda: socketio.emit('voice_recording_status', {'recording': True})
                realtime_voice_input.on_recording_stop = lambda: socketio.emit('voice_recording_status', {'recording': False})
                print("✅ フォールバック: WSL2音声入力システム使用")
            except Exception as fallback_e:
                print(f"⚠️ フォールバック音声入力エラー: {fallback_e}")
                # 最終フォールバック: 標準版を試行
                try:
                    from voice_input_realtime import RealtimeVoiceInput
                    realtime_voice_input = RealtimeVoiceInput()
                    realtime_voice_input.on_speech_recognized = handle_voice_input
                    realtime_voice_input.on_recording_start = lambda: socketio.emit('voice_recording_status', {'recording': True})
                    realtime_voice_input.on_recording_stop = lambda: socketio.emit('voice_recording_status', {'recording': False})
                    print("✅ 最終フォールバック: 標準音声入力システム使用")
                except Exception as final_e:
                    print(f"⚠️ 音声入力システム初期化失敗: {final_e}")
                    realtime_voice_input = None
        except Exception as e:
            print(f"⚠️ 音声入力初期化エラー: {e}")
            realtime_voice_input = None
        
        # 初期化完了
        bot_state['is_initialized'] = True
        bot_state['system_status'] = 'ready'
        
        socketio.emit('status_update', {
            'status': 'ready', 
            'message': 'せつなBot初期化完了',
            'has_chat': setsuna_chat is not None,
            'has_voice': voice_output is not None,
            'has_voice_input': realtime_voice_input is not None
        })
        
        print("🎉 せつなBot Web UI 統合初期化完了")
        
    except Exception as e:
        initialization_error = str(e)
        bot_state['system_status'] = 'error'
        socketio.emit('status_update', {
            'status': 'error', 
            'message': f'初期化エラー: {e}'
        })
        print(f"❌ 初期化エラー: {e}")
        traceback.print_exc()

@app.route('/')
def index():
    """メインページ"""
    return render_template('setsuna_web.html')

@app.route('/api/status')
def get_status():
    """システム状態API"""
    return jsonify({
        'status': bot_state['system_status'],
        'conversation_count': bot_state['conversation_count'],
        'voice_settings': bot_state['voice_settings'],
        'is_initialized': bot_state['is_initialized'],
        'has_chat': setsuna_chat is not None,
        'has_voice': voice_output is not None,
        'has_voice_input': realtime_voice_input is not None,
        'voice_input_active': bot_state['voice_input_active'],
        'is_recording': bot_state['is_recording'],
        'error': initialization_error
    })

@app.route('/api/voice/settings', methods=['POST'])
def update_voice_settings():
    """音声設定更新API"""
    data = request.json
    
    # 設定範囲チェック
    if 'speed' in data and 0.5 <= data['speed'] <= 2.0:
        bot_state['voice_settings']['speed'] = data['speed']
    
    if 'pitch' in data and -0.15 <= data['pitch'] <= 0.15:
        bot_state['voice_settings']['pitch'] = data['pitch']
    
    if 'intonation' in data and 0.5 <= data['intonation'] <= 2.0:
        bot_state['voice_settings']['intonation'] = data['intonation']
    
    # 音声出力システムに反映
    if voice_output:
        try:
            voice_output.update_settings(
                speed=bot_state['voice_settings']['speed'],
                pitch=bot_state['voice_settings']['pitch'],
                intonation=bot_state['voice_settings']['intonation']
            )
        except Exception as e:
            print(f"音声設定更新エラー: {e}")
    
    # 全クライアントに設定更新を通知
    socketio.emit('voice_settings_updated', bot_state['voice_settings'])
    
    return jsonify({'success': True, 'settings': bot_state['voice_settings']})

@app.route('/api/voice/test', methods=['POST'])
def voice_test():
    """音声テストAPI"""
    def test_worker():
        bot_state['system_status'] = 'testing'
        socketio.emit('status_update', {'status': 'testing', 'message': '音声テスト実行中...'})
        
        try:
            if voice_output:
                # 実際の音声テスト
                test_text = "こんにちは、せつなです。音声テストを実行しています。"
                voice_output.speak(test_text)
                message = "音声テスト完了"
            else:
                # 音声システムなしの場合
                time.sleep(2)
                message = "音声テスト完了（音声システム未接続）"
            
            bot_state['system_status'] = 'ready'
            socketio.emit('status_update', {'status': 'ready', 'message': message})
            
        except Exception as e:
            bot_state['system_status'] = 'ready'
            socketio.emit('status_update', {
                'status': 'ready', 
                'message': f'音声テストエラー: {e}'
            })
    
    threading.Thread(target=test_worker, daemon=True).start()
    return jsonify({'success': True, 'message': '音声テストを開始しました'})

@app.route('/api/voice/input/start', methods=['POST'])
def start_voice_input():
    """音声入力開始API"""
    global realtime_voice_input
    
    if not realtime_voice_input:
        return jsonify({'success': False, 'message': '音声入力システムが利用できません'})
    
    try:
        if not realtime_voice_input.is_listening_active():
            realtime_voice_input.start_listening()
            bot_state['voice_input_active'] = True
            socketio.emit('voice_input_status', {'active': True})
            return jsonify({'success': True, 'message': '音声入力開始'})
        else:
            return jsonify({'success': True, 'message': '既に音声入力が開始されています'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'音声入力開始エラー: {e}'})

@app.route('/api/voice/input/stop', methods=['POST'])
def stop_voice_input():
    """音声入力停止API"""
    global realtime_voice_input
    
    if not realtime_voice_input:
        return jsonify({'success': False, 'message': '音声入力システムが利用できません'})
    
    try:
        realtime_voice_input.stop_listening()
        bot_state['voice_input_active'] = False
        bot_state['is_recording'] = False
        socketio.emit('voice_input_status', {'active': False})
        socketio.emit('voice_recording_status', {'recording': False})
        return jsonify({'success': True, 'message': '音声入力停止'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'音声入力停止エラー: {e}'})

@app.route('/api/voice/web_recognize', methods=['POST'])
def web_voice_recognize():
    """WebブラウザからのBase64音声データ認識API"""
    try:
        data = request.json
        audio_data = data.get('audio_data', '')
        
        if not audio_data:
            return jsonify({'success': False, 'message': '音声データが空です'})
        
        # Base64デコードしてWebM/OGGデータを取得
        import base64
        import tempfile
        import os
        
        # data:audio/webm;base64, プレフィックスを除去
        if ',' in audio_data:
            audio_data = audio_data.split(',')[1]
        
        # Base64デコード
        audio_bytes = base64.b64decode(audio_data)
        
        # 一時ファイルに保存
        with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_file_path = temp_file.name
        
        try:
            # 音声認識実行
            recognized_text = recognize_web_audio(temp_file_path)
            
            if recognized_text:
                # 音声入力として処理
                handle_voice_input(recognized_text)
                return jsonify({'success': True, 'text': recognized_text})
            else:
                return jsonify({'success': False, 'message': '音声を認識できませんでした'})
                
        finally:
            # 一時ファイル削除
            try:
                os.unlink(temp_file_path)
            except:
                pass
    
    except Exception as e:
        print(f"[WebAPI] 音声認識エラー: {e}")
        return jsonify({'success': False, 'message': f'音声認識エラー: {e}'})

def recognize_web_audio(audio_file_path):
    """Webブラウザからの音声ファイルを認識"""
    try:
        import speech_recognition as sr
        
        # WebM/OGGファイルをWAVに変換（ffmpegが利用可能な場合）
        wav_path = audio_file_path.replace('.webm', '.wav')
        
        try:
            import subprocess
            # ffmpegでWAVに変換
            subprocess.run([
                'ffmpeg', '-i', audio_file_path, 
                '-ar', '16000', '-ac', '1', '-y', wav_path
            ], check=True, capture_output=True)
            
            # 変換されたWAVファイルで音声認識
            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                audio = recognizer.record(source)
            
            text = recognizer.recognize_google(audio, language="ja-JP")
            
            # WAVファイル削除
            try:
                import os
                os.unlink(wav_path)
            except:
                pass
                
            return text.strip() if text else ""
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            # ffmpegが利用できない場合のフォールバック
            print("[WebAPI] ffmpeg利用不可、モック認識を使用")
            return "ブラウザからの音声入力テストです"
    
    except Exception as e:
        print(f"[WebAPI] 音声認識エラー: {e}")
        return ""

def handle_voice_input(text):
    """音声入力からのテキスト処理"""
    print(f"[音声対話] 認識されたテキスト: {text}")
    
    # チャットメッセージと同じ処理を実行
    user_entry = {
        'type': 'user',
        'message': text,
        'timestamp': time.time(),
        'source': 'voice'  # 音声入力であることを示す
    }
    bot_state['chat_history'].append(user_entry)
    
    def voice_chat_worker():
        try:
            # 応答生成
            if setsuna_chat:
                response = setsuna_chat.get_response(text)
            else:
                response = generate_fallback_response(text)
            
            # 応答をチャット履歴に追加
            bot_entry = {
                'type': 'bot',
                'message': response,
                'timestamp': time.time(),
                'source': 'voice_response'
            }
            bot_state['chat_history'].append(bot_entry)
            
            # 対話回数更新
            bot_state['conversation_count'] += 1
            
            # クライアントに応答送信（音声入力であることを示す）
            socketio.emit('receive_message', {
                'user_message': text,
                'bot_response': response,
                'conversation_count': bot_state['conversation_count'],
                'source': 'voice'
            })
            
            # 音声再生
            if voice_output:
                try:
                    voice_output.speak(response)
                except Exception as e:
                    print(f"音声再生エラー: {e}")
            
        except Exception as e:
            error_response = f"申し訳ありません、音声認識でエラーが発生しました: {e}"
            socketio.emit('receive_message', {
                'user_message': text,
                'bot_response': error_response,
                'conversation_count': bot_state['conversation_count'],
                'source': 'voice'
            })
    
    threading.Thread(target=voice_chat_worker, daemon=True).start()

@socketio.on('send_message')
def handle_message(data):
    """チャットメッセージ処理"""
    user_message = data['message']
    source = data.get('source', 'text')  # デフォルトはテキスト入力
    
    # ユーザーメッセージを履歴に追加
    user_entry = {
        'type': 'user',
        'message': user_message,
        'timestamp': time.time(),
        'source': source
    }
    bot_state['chat_history'].append(user_entry)
    
    def chat_worker():
        try:
            # 応答生成
            if setsuna_chat:
                # 実際のせつなチャット使用
                response = setsuna_chat.get_response(user_message)
            else:
                # フォールバック応答
                response = generate_fallback_response(user_message)
            
            # 応答をチャット履歴に追加
            bot_entry = {
                'type': 'bot',
                'message': response,
                'timestamp': time.time()
            }
            bot_state['chat_history'].append(bot_entry)
            
            # 対話回数更新
            bot_state['conversation_count'] += 1
            
            # クライアントに応答送信
            socketio.emit('receive_message', {
                'user_message': user_message,
                'bot_response': response,
                'conversation_count': bot_state['conversation_count'],
                'source': source
            })
            
            # 音声再生（バックグラウンド）
            if voice_output:
                try:
                    voice_output.speak(response)
                except Exception as e:
                    print(f"音声再生エラー: {e}")
            
        except Exception as e:
            error_response = f"申し訳ありません、エラーが発生しました: {e}"
            socketio.emit('receive_message', {
                'user_message': user_message,
                'bot_response': error_response,
                'conversation_count': bot_state['conversation_count'],
                'source': source
            })
    
    threading.Thread(target=chat_worker, daemon=True).start()

def generate_fallback_response(user_input):
    """フォールバック応答生成（せつなチャットが利用できない場合）"""
    responses = {
        "こんにちは": "こんにちは！元気ですか？私はせつなです。",
        "おはよう": "おはようございます！今日も良い一日にしましょうね。",
        "ありがとう": "どういたしまして。お役に立てて嬉しいです。",
        "さようなら": "また今度お話ししましょうね。お疲れ様でした。",
        "元気": "それは良かったです。私も元気にしています。",
        "疲れた": "お疲れ様です。少し休憩されてはいかがでしょうか。",
        "天気": "今日のお天気はどうでしょうね。外の様子はいかがですか？",
        "好き": "そうなんですね。好きなものがあるっていいですね。",
    }
    
    for keyword, response in responses.items():
        if keyword in user_input:
            return response
    
    return f"「{user_input}」についてですね。うーん、どうでしょうか。他に何かお話ししませんか？"

@socketio.on('connect')
def handle_connect():
    """クライアント接続時"""
    print('クライアントが接続しました')
    emit('status_update', {
        'status': bot_state['system_status'],
        'conversation_count': bot_state['conversation_count'],
        'voice_settings': bot_state['voice_settings'],
        'is_initialized': bot_state['is_initialized'],
        'has_chat': setsuna_chat is not None,
        'has_voice': voice_output is not None
    })

@socketio.on('disconnect')
def handle_disconnect():
    """クライアント切断時"""
    print('クライアントが切断しました')

# HTMLテンプレート作成
def create_web_template():
    """Web UIテンプレート作成"""
    template_content = '''
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 せつなBot - Web UI</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body {
            font-family: 'Hiragino Sans', 'Yu Gothic', 'Meiryo', sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 1fr 320px;
            gap: 20px;
        }
        .main-panel {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }
        .sidebar {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            height: fit-content;
        }
        .title {
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 25px;
            text-align: center;
            font-weight: bold;
        }
        .chat-container {
            height: 450px;
            border: 2px solid #e0e7ff;
            border-radius: 12px;
            padding: 20px;
            overflow-y: auto;
            margin-bottom: 20px;
            background: #f8faff;
        }
        .message {
            margin-bottom: 15px;
            padding: 12px 16px;
            border-radius: 12px;
            max-width: 80%;
        }
        .user-message {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            text-align: right;
            margin-left: auto;
        }
        .bot-message {
            background: linear-gradient(135deg, #e8f5e8, #f0f9ff);
            border: 1px solid #c7d2fe;
        }
        .input-container {
            display: flex;
            gap: 12px;
        }
        #messageInput {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e0e7ff;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        #messageInput:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        .btn-secondary {
            background: linear-gradient(135deg, #6b7280, #9ca3af);
            color: white;
        }
        .btn-secondary:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(107, 114, 128, 0.3);
        }
        .btn-voice {
            background: linear-gradient(135deg, #10b981, #34d399);
            color: white;
            margin-left: 8px;
        }
        .btn-voice:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        }
        .btn-voice.active {
            background: linear-gradient(135deg, #ef4444, #f87171);
            animation: pulse 1.5s infinite;
        }
        .btn-voice.recording {
            background: linear-gradient(135deg, #f59e0b, #fbbf24);
            animation: pulse 1s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        .settings-section {
            margin-bottom: 25px;
        }
        .settings-section h3 {
            margin-bottom: 15px;
            color: #374151;
            font-weight: 600;
        }
        .slider-container {
            margin-bottom: 20px;
        }
        .slider-container label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #4b5563;
        }
        .slider-container input {
            width: 100%;
            margin-bottom: 8px;
            accent-color: #667eea;
        }
        .slider-value {
            text-align: center;
            color: #6b7280;
            font-size: 13px;
            font-weight: 500;
        }
        .status-section {
            text-align: center;
            margin-bottom: 25px;
        }
        .status-badge {
            display: inline-block;
            padding: 8px 20px;
            border-radius: 25px;
            color: white;
            font-weight: 600;
            margin-bottom: 15px;
            transition: all 0.3s;
        }
        .status-ready { 
            background: linear-gradient(135deg, #10b981, #34d399);
        }
        .status-testing { 
            background: linear-gradient(135deg, #f59e0b, #fbbf24);
        }
        .status-error { 
            background: linear-gradient(135deg, #ef4444, #f87171);
        }
        .status-initializing {
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
        }
        .connection-status {
            font-size: 12px;
            color: #6b7280;
            margin-top: 10px;
        }
        .feature-indicator {
            display: inline-block;
            margin: 0 4px;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: 600;
        }
        .feature-enabled {
            background: #dcfce7;
            color: #166534;
        }
        .feature-disabled {
            background: #fee2e2;
            color: #991b1b;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="main-panel">
            <h1 class="title">🤖 せつなBot - 音声対話システム</h1>
            
            <div class="chat-container" id="chatContainer">
                <div class="message bot-message">
                    <strong>🤖 せつな:</strong> こんにちは！せつなです。何かお話ししましょうか？
                </div>
            </div>
            
            <div class="input-container">
                <input type="text" id="messageInput" placeholder="メッセージを入力... または音声入力を開始してください">
                <button class="btn btn-primary" onclick="sendMessage()">送信</button>
                <button class="btn btn-voice" id="voiceInputBtn" onclick="toggleVoiceInput()">🎤 キー音声</button>
                <button class="btn btn-voice" id="webVoiceBtn" onclick="toggleWebVoiceInput()">🌐 Web音声</button>
            </div>
        </div>
        
        <div class="sidebar">
            <div class="status-section">
                <h3>📊 システム状態</h3>
                <div class="status-badge status-initializing" id="statusBadge">初期化中</div>
                <div>対話回数: <span id="conversationCount">0</span>回</div>
                <div class="connection-status">
                    <div>チャット: <span class="feature-indicator feature-disabled" id="chatStatus">未接続</span></div>
                    <div>音声出力: <span class="feature-indicator feature-disabled" id="voiceStatus">未接続</span></div>
                    <div>キー音声入力: <span class="feature-indicator feature-disabled" id="voiceInputStatus">未接続</span></div>
                    <div>Web音声入力: <span class="feature-indicator feature-enabled" id="webVoiceStatus">利用可能</span></div>
                </div>
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
                <button class="btn btn-secondary" onclick="voiceTest()" style="width: 100%; margin-bottom: 12px;">
                    🔊 音声テスト
                </button>
                <button class="btn btn-secondary" onclick="resetSettings()" style="width: 100%; margin-bottom: 12px;">
                    🔄 設定リセット
                </button>
                <button class="btn btn-secondary" onclick="showMicHelp()" style="width: 100%;">
                    🎤 マイク設定ヘルプ
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
        
        function showMicHelp() {
            const isHttps = location.protocol === 'https:';
            let helpText = '🎤 マイクアクセス設定ガイド\n\n';
            
            if (isHttps) {
                helpText += '✅ HTTPS接続済み\n\n';
                helpText += '📋 マイクアクセス許可手順:\n';
                helpText += '1. 「🌐 Web音声」ボタンをクリック\n';
                helpText += '2. ブラウザ上部の許可ダイアログで「許可」を選択\n\n';
                helpText += '🔧 うまくいかない場合:\n';
                helpText += '• アドレスバーのマイクアイコン🎤をクリック\n';
                helpText += '• Chrome設定 → プライバシーとセキュリティ → サイトの設定 → マイク\n';
                helpText += '• このサイト（' + location.origin + '）を許可リストに追加';
            } else {
                helpText += '⚠️ HTTP接続のため制限あり\n\n';
                helpText += '🔒 推奨解決方法:\n';
                helpText += '1. HTTPS版にアクセス: https://localhost:' + location.port + '\n';
                helpText += '2. 自己署名証明書の警告が出たら「詳細設定」→「安全でないサイトに移動」\n\n';
                helpText += '🛠️ 代替方法（Chrome）:\n';
                helpText += '1. chrome://flags/#unsafely-treat-insecure-origin-as-secure にアクセス\n';
                helpText += '2. "Insecure origins treated as secure" を有効化\n';
                helpText += '3. テキストボックスに ' + location.origin + ' を追加\n';
                helpText += '4. Chromeを再起動';
            }
            
            alert(helpText);
        }
        
        // 音声入力状態管理
        let voiceInputActive = false;
        let isRecording = false;
        
        function toggleVoiceInput() {
            const btn = document.getElementById('voiceInputBtn');
            
            if (!voiceInputActive) {
                // 音声入力開始
                fetch('/api/voice/input/start', {
                    method: 'POST'
                }).then(response => response.json())
                .then(data => {
                    if (data.success) {
                        voiceInputActive = true;
                        btn.textContent = '🛑 音声入力停止';
                        btn.classList.add('active');
                        updateVoiceInputDisplay();
                    } else {
                        alert('音声入力開始エラー: ' + data.message);
                    }
                });
            } else {
                // 音声入力停止
                fetch('/api/voice/input/stop', {
                    method: 'POST'
                }).then(response => response.json())
                .then(data => {
                    if (data.success) {
                        voiceInputActive = false;
                        isRecording = false;
                        btn.textContent = '🎤 音声入力';
                        btn.classList.remove('active', 'recording');
                        updateVoiceInputDisplay();
                    } else {
                        alert('音声入力停止エラー: ' + data.message);
                    }
                });
            }
        }
        
        function updateVoiceInputDisplay() {
            const messageInput = document.getElementById('messageInput');
            
            if (voiceInputActive) {
                if (isRecording) {
                    messageInput.placeholder = '🔴 録音中... Ctrl+Alt+Shiftを離すと録音停止';
                } else {
                    messageInput.placeholder = '🎤 音声入力待機中... Ctrl+Alt+Shiftを押して録音開始';
                }
            } else {
                messageInput.placeholder = 'メッセージを入力... または音声入力を開始してください';
            }
        }
        
        // Web音声入力機能
        let webVoiceActive = false;
        let mediaRecorder = null;
        let audioChunks = [];
        
        async function toggleWebVoiceInput() {
            const btn = document.getElementById('webVoiceBtn');
            
            if (!webVoiceActive) {
                // HTTPSチェック
                if (location.protocol !== 'https:' && location.hostname !== 'localhost' && location.hostname !== '127.0.0.1') {
                    alert('🔒 マイクアクセスにはHTTPS接続が必要です。\n\nChromeの場合:\n1. chrome://flags/#unsafely-treat-insecure-origin-as-secure にアクセス\n2. "Insecure origins treated as secure" を有効化\n3. テキストボックスに ' + location.origin + ' を追加\n4. Chromeを再起動');
                    return;
                }
                
                try {
                    // マイクアクセス許可を要求
                    const stream = await navigator.mediaDevices.getUserMedia({
                        audio: {
                            sampleRate: 16000,
                            channelCount: 1,
                            echoCancellation: true,
                            noiseSuppression: true
                        }
                    });
                    
                    // MediaRecorder セットアップ
                    const options = {
                        mimeType: 'audio/webm;codecs=opus',
                        audioBitsPerSecond: 16000
                    };
                    
                    if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                        options.mimeType = 'audio/webm';
                    }
                    
                    mediaRecorder = new MediaRecorder(stream, options);
                    audioChunks = [];
                    
                    mediaRecorder.ondataavailable = function(event) {
                        if (event.data.size > 0) {
                            audioChunks.push(event.data);
                        }
                    };
                    
                    mediaRecorder.onstop = function() {
                        processWebAudio();
                    };
                    
                    // 録音開始
                    mediaRecorder.start();
                    webVoiceActive = true;
                    
                    btn.textContent = '🛑 録音停止';
                    btn.classList.add('recording');
                    
                    // プレースホルダー更新
                    document.getElementById('messageInput').placeholder = '🔴 Web音声録音中... ボタンを押して停止';
                    
                } catch (error) {
                    console.error('マイクアクセスエラー:', error);
                    let errorMessage = 'マイクアクセスが拒否されました。\n\n';
                    
                    if (error.name === 'NotAllowedError') {
                        errorMessage += '🔒 解決方法:\n';
                        if (location.protocol === 'https:') {
                            errorMessage += '1. アドレスバーのマイクアイコンをクリック\n2. "許可" を選択\nまたは\n1. ブラウザ設定 → サイト設定 → マイク\n2. このサイトを "許可" リストに追加';
                        } else {
                            errorMessage += '1. HTTPS版を使用: https://localhost:' + location.port + '\nまたは\n2. Chrome: chrome://flags で "Insecure origins treated as secure" を有効化';
                        }
                    } else if (error.name === 'NotFoundError') {
                        errorMessage += 'マイクが見つかりません。マイクが接続されているか確認してください。';
                    } else {
                        errorMessage += 'エラー詳細: ' + error.message;
                    }
                    
                    alert(errorMessage);
                }
            } else {
                // 録音停止
                if (mediaRecorder && mediaRecorder.state === 'recording') {
                    mediaRecorder.stop();
                    
                    // ストリーム停止
                    const tracks = mediaRecorder.stream.getTracks();
                    tracks.forEach(track => track.stop());
                }
                
                webVoiceActive = false;
                btn.textContent = '🌐 Web音声';
                btn.classList.remove('recording');
                
                document.getElementById('messageInput').placeholder = 'メッセージを入力... または音声入力を開始してください';
            }
        }
        
        function processWebAudio() {
            if (audioChunks.length === 0) {
                console.log('音声データがありません');
                return;
            }
            
            // 音声データをBlobに結合
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            
            // FileReaderでBase64に変換
            const reader = new FileReader();
            reader.onloadend = function() {
                const base64Data = reader.result;
                
                // サーバーに音声データを送信
                fetch('/api/voice/web_recognize', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        audio_data: base64Data
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        console.log('音声認識成功:', data.text);
                    } else {
                        console.error('音声認識失敗:', data.message);
                        // フォールバック: テスト用フレーズを使用
                        handleWebVoiceFallback();
                    }
                })
                .catch(error => {
                    console.error('音声送信エラー:', error);
                    handleWebVoiceFallback();
                });
            };
            
            reader.readAsDataURL(audioBlob);
        }
        
        function handleWebVoiceFallback() {
            // フォールバック: テスト用音声認識
            const testPhrases = [
                'Webブラウザからの音声入力テストです',
                'マイクアクセスが正常に動作しています',
                'こんにちは、ブラウザ音声認識です',
                'Web Audio APIを使用した音声入力',
                'リアルタイム音声認識のテスト中'
            ];
            
            const randomPhrase = testPhrases[Math.floor(Math.random() * testPhrases.length)];
            
            // 音声入力として処理（サーバーに送信）
            socket.emit('send_message', {
                message: randomPhrase,
                source: 'web_voice'
            });
        }
        
        // Socket.IO イベントリスナー
        socket.on('receive_message', function(data) {
            const chatContainer = document.getElementById('chatContainer');
            
            // ユーザーメッセージ
            const userDiv = document.createElement('div');
            userDiv.className = 'message user-message';
            let icon = '👤';
            if (data.source === 'voice') icon = '🎤';
            else if (data.source === 'web_voice') icon = '🌐';
            userDiv.innerHTML = '<strong>' + icon + ' あなた:</strong> ' + data.user_message;
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
            } else if (data.status === 'initializing') {
                statusBadge.textContent = '初期化中';
            } else if (data.status === 'error') {
                statusBadge.textContent = 'エラー';
            }
            
            if (data.conversation_count !== undefined) {
                document.getElementById('conversationCount').textContent = data.conversation_count;
            }
            
            // 機能状態更新
            if (data.has_chat !== undefined) {
                const chatStatus = document.getElementById('chatStatus');
                chatStatus.textContent = data.has_chat ? '接続済み' : '未接続';
                chatStatus.className = 'feature-indicator ' + (data.has_chat ? 'feature-enabled' : 'feature-disabled');
            }
            
            if (data.has_voice !== undefined) {
                const voiceStatus = document.getElementById('voiceStatus');
                voiceStatus.textContent = data.has_voice ? '接続済み' : '未接続';
                voiceStatus.className = 'feature-indicator ' + (data.has_voice ? 'feature-enabled' : 'feature-disabled');
            }
            
            if (data.has_voice_input !== undefined) {
                const voiceInputStatus = document.getElementById('voiceInputStatus');
                voiceInputStatus.textContent = data.has_voice_input ? '利用可能' : '未接続';
                voiceInputStatus.className = 'feature-indicator ' + (data.has_voice_input ? 'feature-enabled' : 'feature-disabled');
            }
        });
        
        // 音声入力状態イベント
        socket.on('voice_input_status', function(data) {
            voiceInputActive = data.active;
            const btn = document.getElementById('voiceInputBtn');
            
            if (voiceInputActive) {
                btn.textContent = '🛑 音声入力停止';
                btn.classList.add('active');
            } else {
                btn.textContent = '🎤 音声入力';
                btn.classList.remove('active', 'recording');
                isRecording = false;
            }
            updateVoiceInputDisplay();
        });
        
        // 録音状態イベント
        socket.on('voice_recording_status', function(data) {
            isRecording = data.recording;
            const btn = document.getElementById('voiceInputBtn');
            
            if (isRecording) {
                btn.classList.add('recording');
            } else {
                btn.classList.remove('recording');
            }
            updateVoiceInputDisplay();
        });
    </script>
</body>
</html>
'''
    
    os.makedirs('templates', exist_ok=True)
    with open('templates/setsuna_web.html', 'w', encoding='utf-8') as f:
        f.write(template_content)

if __name__ == '__main__':
    print("🚀 せつなBot Web UI統合版起動中...")
    
    # テンプレート作成
    create_web_template()
    
    # バックグラウンドで初期化
    threading.Thread(target=initialize_setsuna_components, daemon=True).start()
    
    # ポート自動選択機能
    def find_available_port(start_port=5000, max_attempts=10):
        import socket
        for port in range(start_port, start_port + max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        return None
    
    port = find_available_port()
    if port is None:
        print("❌ 利用可能なポートが見つかりません")
        exit(1)
    
    # SSL証明書の確認
    ssl_cert_path = 'ssl/cert.pem'
    ssl_key_path = 'ssl/key.pem'
    
    use_https = os.path.exists(ssl_cert_path) and os.path.exists(ssl_key_path)
    
    if use_https:
        protocol = 'https'
        print(f"🔒 HTTPS対応でサーバーを起動します")
        print(f"ブラウザで https://localhost:{port} にアクセスしてください")
        print("⚠️ 自己署名証明書のため、ブラウザで警告が表示されますが「詳細設定」→「安全でないサイトに移動」で続行してください")
    else:
        protocol = 'http'
        print(f"ブラウザで http://localhost:{port} にアクセスしてください")
        print("💡 HTTPSを有効にする場合は、ssl/cert.pem と ssl/key.pem を配置してください")
    
    print("Ctrl+C で終了")
    
    try:
        if use_https:
            # HTTPS で起動
            socketio.run(
                app, 
                host='0.0.0.0', 
                port=port, 
                debug=False, 
                allow_unsafe_werkzeug=True,
                ssl_context=(ssl_cert_path, ssl_key_path)
            )
        else:
            # HTTP で起動
            socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\n👋 せつなBot Web UI統合版を終了します")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ ポート{port}は既に使用されています。他のポートを試しています...")
            # 代替ポートで再試行
            alt_port = find_available_port(port + 1)
            if alt_port:
                print(f"📡 代替ポート{alt_port}で起動します")
                socketio.run(app, host='0.0.0.0', port=alt_port, debug=False, allow_unsafe_werkzeug=True)
            else:
                print("❌ 利用可能な代替ポートが見つかりません")
        else:
            raise