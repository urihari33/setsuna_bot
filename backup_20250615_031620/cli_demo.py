#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
せつなBot CLI版デモ
シンプルなコマンドライン インターフェース
"""

import sys
import os
import time

# せつなBotコアモジュールのパス追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class SetsunaCLI:
    def __init__(self):
        self.conversation_count = 0
        self.voice_settings = {
            'speed': 1.2,
            'pitch': 0.0,
            'intonation': 1.0
        }
        
    def display_welcome(self):
        """ウェルカムメッセージ"""
        print("=" * 50)
        print("🤖 せつなBot - コマンドライン版")
        print("音声対話システム")
        print("=" * 50)
        print()
        print("利用可能なコマンド:")
        print("  chat    - テキスト会話開始")
        print("  status  - システム状態確認")
        print("  voice   - 音声設定変更")
        print("  test    - 音声テスト実行")
        print("  help    - ヘルプ表示")
        print("  exit    - 終了")
        print()
    
    def display_status(self):
        """システム状態表示"""
        print("\n📊 システム状態")
        print("-" * 30)
        print(f"対話回数: {self.conversation_count}回")
        print(f"音声設定:")
        print(f"  話速: {self.voice_settings['speed']:.1f}x")
        print(f"  音程: {self.voice_settings['pitch']:.2f}")
        print(f"  抑揚: {self.voice_settings['intonation']:.1f}")
        print()
    
    def voice_settings_menu(self):
        """音声設定メニュー"""
        print("\n🎛️ 音声設定")
        print("-" * 30)
        print("1. 話速調整")
        print("2. 音程調整")
        print("3. 抑揚調整")
        print("4. 設定確認")
        print("5. 戻る")
        
        while True:
            choice = input("\n選択 (1-5): ").strip()
            
            if choice == "1":
                self.adjust_speed()
            elif choice == "2":
                self.adjust_pitch()
            elif choice == "3":
                self.adjust_intonation()
            elif choice == "4":
                self.display_status()
            elif choice == "5":
                break
            else:
                print("❌ 無効な選択です")
    
    def adjust_speed(self):
        """話速調整"""
        print(f"\n現在の話速: {self.voice_settings['speed']:.1f}x")
        try:
            new_speed = float(input("新しい話速 (0.5-2.0): "))
            if 0.5 <= new_speed <= 2.0:
                self.voice_settings['speed'] = new_speed
                print(f"✅ 話速を{new_speed:.1f}xに設定しました")
            else:
                print("❌ 範囲外です (0.5-2.0)")
        except ValueError:
            print("❌ 数値を入力してください")
    
    def adjust_pitch(self):
        """音程調整"""
        print(f"\n現在の音程: {self.voice_settings['pitch']:.2f}")
        try:
            new_pitch = float(input("新しい音程 (-0.15-0.15): "))
            if -0.15 <= new_pitch <= 0.15:
                self.voice_settings['pitch'] = new_pitch
                print(f"✅ 音程を{new_pitch:.2f}に設定しました")
            else:
                print("❌ 範囲外です (-0.15-0.15)")
        except ValueError:
            print("❌ 数値を入力してください")
    
    def adjust_intonation(self):
        """抑揚調整"""
        print(f"\n現在の抑揚: {self.voice_settings['intonation']:.1f}")
        try:
            new_intonation = float(input("新しい抑揚 (0.5-2.0): "))
            if 0.5 <= new_intonation <= 2.0:
                self.voice_settings['intonation'] = new_intonation
                print(f"✅ 抑揚を{new_intonation:.1f}に設定しました")
            else:
                print("❌ 範囲外です (0.5-2.0)")
        except ValueError:
            print("❌ 数値を入力してください")
    
    def voice_test(self):
        """音声テスト"""
        print("\n🔊 音声テスト実行中...")
        print("現在の設定:")
        print(f"  話速: {self.voice_settings['speed']:.1f}x")
        print(f"  音程: {self.voice_settings['pitch']:.2f}")
        print(f"  抑揚: {self.voice_settings['intonation']:.1f}")
        
        # テストシミュレーション
        for i in range(3):
            print(f"テスト中{'.' * (i + 1)}")
            time.sleep(1)
        
        print("✅ 音声テスト完了")
    
    def chat_mode(self):
        """チャットモード"""
        print("\n💬 チャットモード開始")
        print("('exit'で終了)")
        print("-" * 30)
        print("🤖 せつな: こんにちは！何かお話ししましょうか？")
        
        while True:
            user_input = input("\n👤 あなた: ").strip()
            
            if user_input.lower() == 'exit':
                print("🤖 せつな: また今度お話ししましょうね！")
                break
            
            if not user_input:
                continue
            
            # 簡易応答生成
            response = self.generate_response(user_input)
            print(f"🤖 せつな: {response}")
            
            self.conversation_count += 1
    
    def generate_response(self, user_input):
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
    
    def display_help(self):
        """ヘルプ表示"""
        print("\n❓ ヘルプ")
        print("-" * 30)
        print("chat    - テキスト会話を開始します")
        print("status  - 現在のシステム状態を表示します")
        print("voice   - 音声設定メニューを開きます")
        print("test    - 音声テストを実行します")
        print("help    - このヘルプを表示します")
        print("exit    - プログラムを終了します")
        print()
    
    def run(self):
        """メインループ"""
        self.display_welcome()
        
        while True:
            command = input("せつなBot> ").strip().lower()
            
            if command == "chat":
                self.chat_mode()
            elif command == "status":
                self.display_status()
            elif command == "voice":
                self.voice_settings_menu()
            elif command == "test":
                self.voice_test()
            elif command == "help":
                self.display_help()
            elif command == "exit":
                print("\n👋 せつなBotを終了します")
                break
            elif command == "":
                continue
            else:
                print("❌ 無効なコマンドです。'help'でヘルプを表示")

def main():
    try:
        cli = SetsunaCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n\n👋 せつなBotを終了します")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    main()