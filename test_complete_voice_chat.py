#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完全音声対話システムテスト
音声入力 → GPT-4応答 → VOICEVOX音声出力 のフル統合テスト
"""

import time
import threading
from windows_voice_input import SafeWindowsVoiceInput, SafeHotkeyVoiceIntegration
from voice_synthesizer import VoiceVoxSynthesizer
from pynput import keyboard

def test_complete_voice_flow():
    """完全音声対話フローのテスト"""
    print("🧪 完全音声対話システム統合テスト開始")
    print("=" * 60)
    
    # テスト用Bot
    class TestBot:
        def __init__(self):
            self.received_messages = []
        
        async def handle_voice_input(self, text):
            print(f"TestBot受信: {text}")
            self.received_messages.append(text)
            return f"処理完了: {text}"
    
    # システム初期化
    print("1. システム初期化中...")
    test_bot = TestBot()
    voice_system = SafeWindowsVoiceInput(test_bot)
    
    # VOICEVOX接続確認
    print("\n2. VOICEVOX接続テスト...")
    if voice_system.voice_synthesizer:
        connection_ok = voice_system.voice_synthesizer.test_connection()
        if connection_ok:
            print("✅ VOICEVOX接続成功")
        else:
            print("⚠️ VOICEVOX接続失敗 - 音声合成なしで継続")
    else:
        print("⚠️ VOICEVOX初期化失敗 - 音声合成なしで継続")
    
    # 音声入力→応答→音声出力テスト
    print("\n3. 完全音声対話フローテスト開始...")
    print("   🎤 5秒間の音声録音を開始します...")
    
    start_time = time.time()
    
    # 録音開始
    recording_success = voice_system.start_recording()
    
    if recording_success:
        # 録音停止・認識・応答・音声合成まで含む
        recognized_text = voice_system.stop_recording()
        
        end_time = time.time()
        
        print(f"\n4. テスト結果:")
        print(f"   - 録音成功: {recording_success}")
        print(f"   - 認識結果: '{recognized_text}'")
        print(f"   - せつなの応答: '{voice_system.last_setsuna_response}'")
        print(f"   - 総処理時間: {end_time - start_time:.2f}s")
        
        if recognized_text and voice_system.last_setsuna_response:
            print("\n✅ 完全音声対話フローテスト成功")
            print("   音声入力 → GPT-4応答 → VOICEVOX音声出力 が正常動作")
            
            # 音声合成完了まで少し待機
            print("\n   🔊 音声合成・再生完了まで待機中...")
            time.sleep(5)
            
            return True
        else:
            print("\n❌ 音声認識または応答生成に失敗")
            return False
    else:
        print("\n❌ 録音開始に失敗")
        return False

def test_voice_synthesis_only():
    """音声合成のみのテスト"""
    print("\n🧪 VOICEVOX音声合成単体テスト")
    print("-" * 40)
    
    synthesizer = VoiceVoxSynthesizer()
    
    test_texts = [
        "こんにちは、せつなです。",
        "音声合成のテストを行っています。",
        "システムは正常に動作していますか？"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n{i}. テスト音声: '{text}'")
        success = synthesizer.test_synthesis(text)
        if success:
            print(f"   ✅ 音声合成・再生成功")
        else:
            print(f"   ❌ 音声合成・再生失敗")
        
        time.sleep(2)  # 次のテストまで間隔

def manual_test_mode():
    """手動テストモード（ホットキー付き）"""
    print("\n🎮 手動テストモード開始")
    print("=" * 60)
    print("Ctrl+Shift+Alt を同時押しで音声入力開始")
    print("Ctrl+C で終了")
    
    # テスト用Bot
    class TestBot:
        def __init__(self):
            self.received_messages = []
    
    test_bot = TestBot()
    hotkey_system = SafeHotkeyVoiceIntegration(test_bot)
    
    # ホットキー設定
    current_keys = set()
    required_keys = {keyboard.Key.ctrl_l, keyboard.Key.shift_l, keyboard.Key.alt_l}
    
    def on_key_press(key):
        current_keys.add(key)
        if required_keys.issubset(current_keys):
            print("\n🎮 ホットキー検出: 音声録音開始")
            hotkey_system.on_hotkey_press()
    
    def on_key_release(key):
        if key in current_keys:
            current_keys.remove(key)
        if key in required_keys:
            print("🛑 ホットキー解除: 音声録音停止・処理開始")
            hotkey_system.on_hotkey_release()
    
    try:
        print("⌨️ ホットキーリスナー開始...")
        with keyboard.Listener(on_press=on_key_press, on_release=on_key_release) as listener:
            listener.join()
    except KeyboardInterrupt:
        print("\n👋 手動テストモード終了")

def main():
    """メイン処理"""
    print("🎯 完全音声対話システム テストスイート")
    print("=" * 60)
    
    while True:
        print("\nテストメニュー:")
        print("1. 完全音声対話フローテスト（自動）")
        print("2. VOICEVOX音声合成単体テスト")
        print("3. 手動テストモード（ホットキー操作）")
        print("4. 終了")
        
        try:
            choice = input("\n選択してください (1-4): ").strip()
            
            if choice == "1":
                success = test_complete_voice_flow()
                if success:
                    print("\n🎉 統合テスト完了")
                else:
                    print("\n💥 統合テストで問題が発生しました")
            
            elif choice == "2":
                test_voice_synthesis_only()
            
            elif choice == "3":
                manual_test_mode()
            
            elif choice == "4":
                print("\n👋 テスト終了")
                break
            
            else:
                print("⚠️ 無効な選択です")
                
        except KeyboardInterrupt:
            print("\n\n👋 テスト中断")
            break
        except Exception as e:
            print(f"\n❌ テストエラー: {e}")

if __name__ == "__main__":
    main()