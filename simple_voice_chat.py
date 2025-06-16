#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シンプル音声対話システム
トラブルシューティング用の確実動作版
"""

import speech_recognition as sr
import threading
import time
from pynput import keyboard
from voice_synthesizer import VoiceVoxSynthesizer

# グローバル状態
listening = False
current_keys = set()
required_keys = {keyboard.Key.ctrl_l, keyboard.Key.shift_l, keyboard.Key.alt_l}

# 音声合成システム初期化
voice_synthesizer = None

def simple_voice_recognition():
    """シンプルな音声認識"""
    recognizer = sr.Recognizer()
    
    try:
        print("🎤 マイク準備中...")
        with sr.Microphone() as source:
            print("🔧 ノイズ調整中...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("🎤 話してください（3秒間）...")
            
            # 録音実行
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
            print("✅ 録音完了")
            
            # データサイズチェック
            if hasattr(audio, 'frame_data'):
                data_size = len(audio.frame_data)
                print(f"🔍 音声データ: {data_size} bytes")
            
            # 音声認識実行
            print("🌐 音声認識中...")
            try:
                text = recognizer.recognize_google(audio, language="ja-JP")
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

def simple_chat_response(user_input):
    """シンプルな応答生成"""
    responses = {
        "こんにちは": "こんにちは！お疲れ様です。",
        "今日": "今日はいかがお過ごしですか？",
        "テスト": "音声認識テストですね。正常に動作しています！",
        "ありがとう": "どういたしまして。",
        "さようなら": "さようなら、また話しかけてくださいね。"
    }
    
    # キーワードマッチング
    for keyword, response in responses.items():
        if keyword in user_input:
            return response
    
    # デフォルト応答
    return f"「{user_input}」について考えてみますね。何か他にお話しできることはありますか？"

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
        
        if user_input:
            print(f"👤 あなた: {user_input}")
            
            # 応答生成
            response = simple_chat_response(user_input)
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
        
        print("✅ 音声対話完了\n")

def main():
    """メイン処理"""
    global voice_synthesizer
    
    print("🎮 シンプル音声対話システム開始")
    print("="*50)
    
    # 音声合成システム初期化
    print("🔊 音声合成システム初期化中...")
    try:
        voice_synthesizer = VoiceVoxSynthesizer()
        print("✅ 音声合成システム初期化完了")
    except Exception as e:
        print(f"⚠️ 音声合成システム初期化失敗: {e}")
        print("   音声認識のみで続行します")
    
    print("="*50)
    print("🎮 操作方法:")
    print("   - Ctrl+Shift+Alt を同時押しで音声入力開始")
    print("   - Ctrl+C で終了")
    print("="*50)
    
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