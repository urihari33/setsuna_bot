#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPT-4統合音声対話システム
シンプル音声チャット + OpenAI GPT-4 + VOICEVOX
"""

import speech_recognition as sr
import threading
import time
import pyaudio
from pynput import keyboard
from voice_synthesizer import VoiceVoxSynthesizer
from core.setsuna_chat import SetsunaChat

# グローバル状態
listening = False
recording = False
current_keys = set()
required_keys = {keyboard.Key.ctrl_l, keyboard.Key.shift_l, keyboard.Key.alt_l}
fast_mode_keys = {keyboard.Key.ctrl_l, keyboard.Key.shift_l}  # 高速モード用キー
audio_frames = []
audio_stream = None
pyaudio_instance = None
current_mode = "full_search"  # デフォルトは通常モード

# システムコンポーネント
voice_synthesizer = None
setsuna_chat = None
voice_recognizer = None
microphone = None

def start_recording():
    """ホットキー制御での録音開始"""
    global recording, audio_frames, audio_stream, pyaudio_instance
    
    if recording:
        return
    
    try:
        print("🎤 録音開始...")
        print("🎤 話してください（ホットキーを離すまで録音継続）...")
        
        # PyAudio設定
        chunk = 1024
        sample_format = pyaudio.paInt16
        channels = 1
        fs = 44100
        
        # PyAudioインスタンス作成
        pyaudio_instance = pyaudio.PyAudio()
        
        # 録音ストリーム開始
        audio_stream = pyaudio_instance.open(
            format=sample_format,
            channels=channels,
            rate=fs,
            frames_per_buffer=chunk,
            input=True
        )
        
        recording = True
        audio_frames = []
        
        # 録音ループ（別スレッドで実行）
        threading.Thread(target=record_audio_loop, args=(chunk,), daemon=True).start()
        
    except Exception as e:
        print(f"❌ 録音開始エラー: {e}")
        recording = False

def record_audio_loop(chunk):
    """録音ループ（ホットキーが離されるまで継続）"""
    global recording, audio_frames, audio_stream
    
    while recording and audio_stream:
        try:
            data = audio_stream.read(chunk, exception_on_overflow=False)
            audio_frames.append(data)
        except Exception as e:
            print(f"⚠️ 録音データ読み取りエラー: {e}")
            break

def stop_recording_and_recognize():
    """録音停止・音声認識実行"""
    global recording, audio_frames, audio_stream, pyaudio_instance, voice_recognizer
    
    if not recording:
        return "録音されていません"
    
    try:
        # 録音停止
        recording = False
        print("✅ 録音完了")
        
        # ストリーム停止・クリーンアップ
        if audio_stream:
            audio_stream.stop_stream()
            audio_stream.close()
        if pyaudio_instance:
            pyaudio_instance.terminate()
        
        if not audio_frames:
            print("❌ 録音データなし")
            return "録音データがありません"
        
        # データサイズチェック
        total_frames = len(audio_frames)
        data_size = sum(len(frame) for frame in audio_frames)
        print(f"🔍 音声データ: {data_size} bytes ({total_frames} frames)")
        
        # AudioDataオブジェクトを直接作成（一時ファイル不要）
        sample_format = pyaudio.paInt16
        channels = 1
        fs = 44100
        
        print("🌐 音声認識中...")
        recognition_result = None
        
        try:
            # 録音データをバイト列に変換
            audio_data = b''.join(audio_frames)
            
            # speech_recognitionのAudioDataオブジェクトを直接作成
            audio = sr.AudioData(audio_data, fs, pyaudio.PyAudio().get_sample_size(sample_format))
            
            # Google音声認識API呼び出し
            text = voice_recognizer.recognize_google(audio, language="ja-JP")
            print(f"✅ 認識成功: '{text}'")
            recognition_result = text
                
        except sr.UnknownValueError:
            print("❌ 音声認識失敗（音声不明瞭）")
            recognition_result = "音声が聞き取れませんでした"
        except sr.RequestError as e:
            print(f"❌ API呼び出しエラー: {e}")
            recognition_result = "音声認識サービスエラー"
        except Exception as e:
            print(f"❌ 音声認識処理エラー: {e}")
            recognition_result = "音声認識に失敗しました"
        
        return recognition_result
                
    except Exception as e:
        print(f"❌ 音声認識エラー: {e}")
        return "音声認識に失敗しました"

def on_key_press(key):
    """キー押下処理"""
    global listening, recording, current_mode
    current_keys.add(key)
    
    # 通常モード（Ctrl+Shift+Alt）
    if required_keys.issubset(current_keys) and not listening and not recording:
        listening = True
        current_mode = "full_search"
        print("🎮 [通常モード] ホットキー検出: Ctrl+Shift+Alt - YouTube検索実行")
        start_recording()
    
    # 高速モード（Shift+Ctrl）
    elif fast_mode_keys.issubset(current_keys) and keyboard.Key.alt_l not in current_keys and not listening and not recording:
        listening = True
        current_mode = "fast_response"
        print("⚡ [高速モード] ホットキー検出: Shift+Ctrl - 既存知識で応答")
        start_recording()

def on_key_release(key):
    """キー離上処理"""
    global listening, recording
    if key in current_keys:
        current_keys.remove(key)
    
    # メインキーが離されたら録音停止・認識開始
    if (key in required_keys or key in fast_mode_keys) and recording:
        listening = False
        # 録音停止と音声認識を別スレッドで実行
        threading.Thread(target=handle_voice_recognition, daemon=True).start()

def handle_voice_recognition():
    """音声認識・対話処理"""
    global current_mode
    print(f"🗣️ 音声対話開始 - {current_mode}モード")
    
    # 音声認識実行
    user_input = stop_recording_and_recognize()
    
    if user_input and user_input not in ["音声が聞き取れませんでした", "音声認識サービスエラー", "録音に失敗しました", "録音されていません", "録音データがありません", "音声認識に失敗しました"]:
        print(f"👤 あなた: {user_input}")
        
        # GPT-4応答生成（モード情報を渡す）
        if setsuna_chat:
            if current_mode == "fast_response":
                print("⚡ せつな思考中（高速モード）...")
            else:
                print("🤖 せつな思考中（通常モード）...")
            response = setsuna_chat.get_response(user_input, mode=current_mode)
            print(f"🤖 せつな: {response}")
            
            # Phase 1: URL表示機能 - 動画推薦時のURL表示（応答フィルター付き）
            try:
                from url_display_manager import show_recommended_urls
                if setsuna_chat.context_builder and hasattr(setsuna_chat.context_builder, 'get_last_context'):
                    last_context = setsuna_chat.context_builder.get_last_context()
                    if last_context and last_context.get('videos'):
                        print(f"🔗 [URL表示] 推薦動画から応答言及分をフィルター中...")
                        # せつなの応答文を渡してフィルタリング
                        show_recommended_urls(last_context, response)
            except ImportError:
                # URL表示機能が利用できない場合はスキップ
                pass
            except Exception as e:
                print(f"⚠️ [URL表示] エラー: {e}")
            
            # 音声合成実行
            if voice_synthesizer:
                print("🎵 音声合成中...")
                wav_path = voice_synthesizer.synthesize_voice(response)
                if wav_path:
                    voice_synthesizer.play_voice(wav_path)
                    print("✅ 音声出力完了")
                else:
                    print("❌ 音声合成失敗")
            else:
                print("⚠️ 音声合成システムが初期化されていません")
        else:
            print("⚠️ GPT-4チャットシステムが初期化されていません")
    else:
        print("🤖 せつな: 音声がよく聞こえませんでした。もう一度お話しください。")
    
    print("✅ 音声対話完了\n")

def main():
    """メイン処理"""
    global voice_synthesizer, setsuna_chat, voice_recognizer, microphone
    
    print("🎮 GPT-4統合音声対話システム開始")
    print("="*60)
    
    # 音声認識システム初期化（ホットキー制御用）
    print("🎤 音声認識システム初期化中...")
    try:
        voice_recognizer = sr.Recognizer()
        print("✅ 音声認識システム初期化完了")
    except Exception as e:
        print(f"❌ 音声認識システム初期化失敗: {e}")
        print("⚠️ SpeechRecognitionライブラリが見つかりません")
        print("   以下のコマンドでインストールしてください:")
        print("   pip install SpeechRecognition")
        return
    
    # 音声合成システム初期化
    print("🔊 音声合成システム初期化中...")
    try:
        voice_synthesizer = VoiceVoxSynthesizer()
        print("✅ 音声合成システム初期化完了")
    except Exception as e:
        print(f"⚠️ 音声合成システム初期化失敗: {e}")
        print("   音声認識のみで続行します")
    
    # GPT-4チャットシステム初期化
    print("🤖 GPT-4チャットシステム初期化中...")
    try:
        setsuna_chat = SetsunaChat()
        print("✅ GPT-4チャットシステム初期化完了")
    except Exception as e:
        print(f"⚠️ GPT-4チャットシステム初期化失敗: {e}")
        print("   OPENAI_API_KEYが設定されているか確認してください")
        print("   シンプル応答モードで続行します")
    
    print("="*60)
    print("🎮 操作方法:")
    print("   - Ctrl+Shift+Alt を押している間録音")
    print("   - キーを離すと録音終了・音声認識開始")
    print("   - Ctrl+C で終了")
    print("="*60)
    print("🤖 せつな: 準備完了です。お話しください！")
    print("="*60)
    
    # キーボードリスナーを別スレッドで開始
    listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
    listener.start()
    
    try:
        # メインループでCtrl+Cを待機
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n👋 システム終了中...")
        listener.stop()
        print("✅ システム終了完了")

if __name__ == "__main__":
    main()