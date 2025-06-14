#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
せつなBot ホットキー統合システム
Ctrl+Shift+Alt → 音声対話の完全版
"""

import sys
import os
import time
import threading

# coreモジュールのパスを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core'))

# モジュールインポート
from voice_output import VoiceOutput
from setsuna_chat import SetsunaChat
from hotkey_listener import HotkeyListener

# 音声入力は実装状況に応じて選択
try:
    from voice_input import VoiceInput
    VOICE_INPUT_AVAILABLE = True
except:
    from voice_input_mock import VoiceInput
    VOICE_INPUT_AVAILABLE = False

class SetsunaHotkeySystem:
    def __init__(self):
        """せつなBot ホットキーシステムの初期化"""
        print("🤖 せつなBot ホットキーシステム初期化中...")
        print("=" * 60)
        
        # コアシステム初期化
        self._initialize_core_systems()
        
        # ホットキーリスナー初期化
        self.hotkey_listener = HotkeyListener(callback=self.on_hotkey_pressed)
        
        # 状態管理
        self.is_processing = False
        self.conversation_count = 0
        
        print("✅ せつなBot ホットキーシステム初期化完了！")
        print()
        
    def _initialize_core_systems(self):
        """コアシステムの初期化"""
        try:
            print("[初期化] 音声入力システム...")
            self.voice_input = VoiceInput()
            
            print("[初期化] 音声出力システム...")
            self.voice_output = VoiceOutput()
            
            print("[初期化] チャットシステム...")
            self.setsuna_chat = SetsunaChat()
            
            if not VOICE_INPUT_AVAILABLE:
                print("⚠️ PyAudio問題のため、モック音声入力を使用中")
            
        except Exception as e:
            print(f"❌ コアシステム初期化エラー: {e}")
            raise
    
    def on_hotkey_pressed(self):
        """ホットキー押下時のコールバック"""
        if self.is_processing:
            print("⏳ 処理中のため、ホットキーを無視します")
            return
        
        self.is_processing = True
        
        try:
            print("\n" + "=" * 50)
            print(f"🔥 せつなBot起動！ (#{self.conversation_count + 1})")
            print("=" * 50)
            
            # 起動音声（オプション）
            if self.conversation_count == 0:
                self.voice_output.speak("はい、何でしょうか？")
            
            # 音声対話実行
            success = self._execute_voice_conversation()
            
            if success:
                self.conversation_count += 1
                print(f"✅ 対話完了 (総対話数: {self.conversation_count})")
            else:
                print("❌ 対話失敗")
            
        except Exception as e:
            print(f"❌ ホットキー処理エラー: {e}")
        finally:
            self.is_processing = False
            print("⏳ 次のホットキー待機中...\n")
    
    def _execute_voice_conversation(self):
        """音声対話の実行"""
        try:
            # 1. 音声入力
            print("🎤 音声入力開始...")
            if VOICE_INPUT_AVAILABLE:
                user_input = self.voice_input.listen(timeout=10, phrase_limit=15)
            else:
                # モック版の場合は固定メッセージ
                mock_messages = [
                    "こんにちは",
                    "今日の天気はどうですか？", 
                    "ありがとう",
                    "元気にしてる？",
                    "また話しましょう"
                ]
                user_input = mock_messages[self.conversation_count % len(mock_messages)]
                print(f"[モック] 音声入力: {user_input}")
                time.sleep(1)  # リアルっぽく
            
            if not user_input:
                print("⏰ 音声が認識されませんでした")
                return False
            
            print(f"👤 ユーザー: {user_input}")
            
            # 2. GPT応答生成
            print("🤔 せつなが考え中...")
            setsuna_response = self.setsuna_chat.get_response(user_input)
            
            if not setsuna_response:
                print("❌ 応答生成に失敗しました")
                return False
            
            print(f"🤖 せつな: {setsuna_response}")
            
            # 3. 音声出力
            print("🔊 音声再生中...")
            self.voice_output.speak(setsuna_response)
            
            return True
            
        except Exception as e:
            print(f"❌ 音声対話エラー: {e}")
            return False
    
    def start(self):
        """ホットキーシステム開始"""
        print("🚀 せつなBot ホットキーシステム開始")
        print("-" * 60)
        print("📋 使用方法:")
        print("  💡 Ctrl+Shift+Alt (左キー) を同時押し")
        print("  💬 音声で話しかけてください")
        print("  🎤 10秒でタイムアウトします")
        print("  🔄 何度でも使用可能")
        print("  ⏹️  Ctrl+C で終了")
        print("-" * 60)
        
        if not VOICE_INPUT_AVAILABLE:
            print("⚠️ モック音声入力モードで動作中")
            print("   ホットキーを押すと自動的にテスト対話が実行されます")
            print()
        
        try:
            # ホットキーリスニング開始
            self.hotkey_listener.start_listening()
            
            # メインループ（Ctrl+Cまで待機）
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n👋 せつなBot を終了中...")
            self.stop()
    
    def stop(self):
        """ホットキーシステム停止"""
        print("⏹️ ホットキーリスニング停止中...")
        self.hotkey_listener.stop_listening()
        
        print("📊 セッション統計:")
        print(f"  総対話数: {self.conversation_count}回")
        print(f"  チャット履歴: {self.setsuna_chat.get_conversation_summary()}")
        print("👋 ありがとうございました！")

def main():
    """メイン関数"""
    print("🤖 せつなBot - ホットキー統合システム")
    print("=" * 60)
    
    try:
        # システム初期化
        setsuna_system = SetsunaHotkeySystem()
        
        # システム開始
        setsuna_system.start()
        
    except KeyboardInterrupt:
        print("\n👋 プログラムを終了しました")
    except Exception as e:
        print(f"❌ システムエラー: {e}")
        print("\n🔧 解決方法:")
        print("1. VOICEVOX が起動しているか確認")
        print("2. .env ファイルの OPENAI_API_KEY を確認")
        print("3. 管理者権限で実行してみる")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())