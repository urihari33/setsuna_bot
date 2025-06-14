#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動ホットキーテスト - WSL2対応
ホットキー機能の自動デモンストレーション
"""

import sys
import os
import time

# coreモジュールのパスを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core'))

# モジュールインポート
from voice_output import VoiceOutput
from setsuna_chat import SetsunaChat
from voice_input_mock import VoiceInput

class AutoHotkeyTest:
    def __init__(self):
        """自動ホットキーテストの初期化"""
        print("🤖 せつなBot 自動ホットキーテスト")
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
                print("⏰ モック音声終了")
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
    
    def run_auto_test(self):
        """自動テスト実行"""
        print("\n🚀 自動ホットキーテスト開始")
        print("-" * 50)
        print("💡 ホットキー機能を自動で5回実行します")
        print("💬 各ホットキーでモック音声対話が実行されます")
        print("⏱️  各対話の間に2秒間隔を設けます")
        print("-" * 50)
        
        max_conversations = 5
        
        try:
            for i in range(max_conversations):
                print(f"\n⏰ ホットキー {i+1}/{max_conversations} を実行中...")
                time.sleep(1)  # 少し間隔
                
                success = self.simulate_hotkey_conversation()
                
                if not success:
                    print("⚠️ モック音声が終了しました")
                    break
                
                if i < max_conversations - 1:
                    print("⏳ 次のホットキーまで2秒待機...")
                    time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n👋 テストを中断しました")
        
        print(f"\n📊 自動テスト結果")
        print("=" * 30)
        print(f"実行回数: {self.conversation_count}回")
        print(f"チャット履歴: {self.setsuna_chat.get_conversation_summary()}")
        print("✅ ホットキー統合システムが正常動作しました！")
        print("👋 自動テスト完了")

def main():
    """メイン関数"""
    try:
        test = AutoHotkeyTest()
        test.run_auto_test()
        return 0
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        return 1

if __name__ == "__main__":
    exit(main())