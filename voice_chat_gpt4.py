#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPT-4統合音声対話システム
シンプル音声チャット + OpenAI GPT-4 + VOICEVOX
"""

import speech_recognition as sr
import threading
import time
from pynput import keyboard
from voice_synthesizer import VoiceVoxSynthesizer
from core.setsuna_chat import SetsunaChat

# グローバル状態
listening = False
current_keys = set()
required_keys = {keyboard.Key.ctrl_l, keyboard.Key.shift_l, keyboard.Key.alt_l}

# システムコンポーネント
voice_synthesizer = None
setsuna_chat = None
voice_recognizer = None
microphone = None

def simple_voice_recognition():
    """シンプルな音声認識（高速化版）"""
    global voice_recognizer, microphone
    
    try:
        print("🎤 録音開始...")
        # 事前初期化されたマイクロフォンを使用
        with microphone as source:
            print("🎤 話してください（15秒間）...")
            
            # 録音実行（15秒に延長）
            audio = voice_recognizer.listen(source, timeout=15, phrase_time_limit=15)
            print("✅ 録音完了")
            
            # データサイズチェック
            if hasattr(audio, 'frame_data'):
                data_size = len(audio.frame_data)
                print(f"🔍 音声データ: {data_size} bytes")
            
            # 音声認識実行
            print("🌐 音声認識中...")
            try:
                text = voice_recognizer.recognize_google(audio, language="ja-JP")
                print(f"✅ 認識成功: '{text}'")
                return text
            except sr.UnknownValueError:
                print("❌ 音声認識失敗（音声不明瞭）")
                return "音声が聞き取れませんでした"
            except sr.RequestError as e:
                print(f"❌ API呼び出しエラー: {e}")
                return "音声認識サービスエラー"
                
    except Exception as e:
        print(f"❌ 録音エラー: {e}")
        return "録音に失敗しました"

def on_key_press(key):
    """キー押下処理"""
    global listening
    current_keys.add(key)
    
    if required_keys.issubset(current_keys) and not listening:
        listening = True
        print("🎮 ホットキー検出: Ctrl+Shift+Alt")
        threading.Thread(target=handle_voice_chat, daemon=True).start()

def on_key_release(key):
    """キー離上処理"""
    global listening
    if key in current_keys:
        current_keys.remove(key)
    
    # メインキーが離されたら停止
    if key in required_keys:
        listening = False

def handle_voice_chat():
    """音声対話処理"""
    if listening:
        print("🗣️ 音声対話開始")
        
        # 音声認識
        user_input = simple_voice_recognition()
        
        if user_input and user_input not in ["音声が聞き取れませんでした", "音声認識サービスエラー", "録音に失敗しました"]:
            print(f"👤 あなた: {user_input}")
            
            # GPT-4応答生成
            if setsuna_chat:
                print("🤖 せつな思考中...")
                response = setsuna_chat.get_response(user_input)
                print(f"🤖 せつな: {response}")
                
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
    
    # 音声認識システム初期化（高速化のため事前初期化）
    print("🎤 音声認識システム初期化中...")
    try:
        voice_recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        # マイクロフォンの事前調整
        print("🔧 マイクロフォン調整中...")
        with microphone as source:
            voice_recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("✅ 音声認識システム初期化完了")
    except Exception as e:
        print(f"❌ 音声認識システム初期化失敗: {e}")
        print("⚠️ PyAudioライブラリが見つかりません")
        print("   以下のコマンドでインストールしてください:")
        print("   conda install pyaudio")
        print("   または")
        print("   pip install pyaudio")
        print("\n💡 PyAudioインストール後に再実行してください")
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
    print("   - Ctrl+Shift+Alt を同時押しで音声入力開始")
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