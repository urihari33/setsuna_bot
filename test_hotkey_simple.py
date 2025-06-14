#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡易ホットキーテスト - WSL2対応
エンターキーでのホットキーシミュレーション
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
from voice_input_mock import VoiceInput

class SimpleHotkeyTest:
    def __init__(self):
        """簡易ホットキーテストの初期化"""
        print("🤖 せつなBot 簡易ホットキーテスト")
        print("=" * 50)
        
        # コアシステム初期化
        print("[初期化] 音声出力システム...")
        self.voice_output = VoiceOutput()
        
        print("[初期化] チャットシステム...")
        self.setsuna_chat = SetsunaChat()
        
        print("[初期化] モック音声入力システム...")
        self.voice_input = VoiceInput()
        
        self.conversation_count = 0
        print("✅ 初期化完了！")
    
    def simulate_hotkey_conversation(self):
        """ホットキー対話のシミュレーション"""
        print(f"\n🔥 ホットキーシミュレーション (#{self.conversation_count + 1})")
        print("=" * 40)
        
        try:
            # 起動音声（初回のみ）
            if self.conversation_count == 0:
                print("🔊 起動音声...")
                self.voice_output.speak("はい、何でしょうか？")
            
            # 1. 音声入力（モック）
            print("🎤 音声入力中...")
            user_input = self.voice_input.listen()
            
            if not user_input:
                print("⏰ 音声入力なし")
                return False
            
            print(f"👤 ユーザー: {user_input}")
            
            # 2. GPT応答生成
            print("🤔 せつなが考え中...")
            setsuna_response = self.setsuna_chat.get_response(user_input)
            print(f"🤖 せつな: {setsuna_response}")
            
            # 3. 音声出力
            print("🔊 音声再生中...")
            self.voice_output.speak(setsuna_response)
            
            self.conversation_count += 1
            print(f"✅ 対話完了 (総対話数: {self.conversation_count})")
            return True
            
        except Exception as e:
            print(f"❌ 対話エラー: {e}")
            return False
    
    def run_test(self):
        """テスト実行"""
        print("\n📋 簡易ホットキーテスト開始")
        print("-" * 50)
        print("💡 Enterキーを押してホットキーをシミュレーション")
        print("💬 モック音声入力で対話が実行されます")
        print("⏹️  'quit' と入力で終了")
        print("-" * 50)
        
        try:
            while True:
                user_action = input("\nEnterでホットキー実行 (quit=終了): ").strip()
                
                if user_action.lower() in ['quit', 'q', '終了']:
                    break
                
                # ホットキー対話を実行
                self.simulate_hotkey_conversation()
                
        except KeyboardInterrupt:
            print("\n👋 テストを終了します")
        
        print(f"\n📊 テスト結果: {self.conversation_count}回の対話")
        print("👋 ありがとうございました！")

def main():
    """メイン関数"""
    try:
        test = SimpleHotkeyTest()
        test.run_test()
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())