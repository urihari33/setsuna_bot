#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
せつなBot 実用版メインシステム
実際に会話できるバージョン
"""

import sys
import os

# coreモジュールのパスを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core'))

def main():
    """メイン関数"""
    print("🤖 せつなBot - 実用版会話システム")
    print("=" * 60)
    
    # 使用可能なモードを表示
    modes = {
        "1": ("テキスト会話モード", "text_chat_mode"),
        "2": ("ホットキーモード（モック音声）", "hotkey_mock_mode"), 
        "3": ("自動デモモード", "auto_demo_mode"),
        "4": ("システムテスト", "system_test_mode")
    }
    
    print("利用可能なモード:")
    for key, (name, _) in modes.items():
        print(f"  {key}. {name}")
    print("  0. 終了")
    print("=" * 60)
    
    try:
        while True:
            choice = input("\nモードを選択してください (1-4, 0=終了): ").strip()
            
            if choice == "0":
                print("👋 せつなBotを終了します")
                break
            elif choice == "1":
                text_chat_mode()
            elif choice == "2":
                hotkey_mock_mode()
            elif choice == "3":
                auto_demo_mode()
            elif choice == "4":
                system_test_mode()
            else:
                print("❌ 無効な選択です。1-4を入力してください。")
                
    except KeyboardInterrupt:
        print("\n👋 プログラムを終了しました")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return 1
    
    return 0

def text_chat_mode():
    """テキスト会話モード"""
    print("\n🗨️  テキスト会話モード開始")
    print("-" * 40)
    
    try:
        from voice_output import VoiceOutput
        from setsuna_chat import SetsunaChat
        
        voice_output = VoiceOutput()
        setsuna_chat = SetsunaChat()
        
        print("✅ 初期化完了")
        print("💬 テキストで入力してください (quit=終了)")
        print("🔊 せつなの応答は音声でも再生されます")
        print()
        
        conversation_count = 0
        
        while True:
            user_input = input("👤 あなた: ").strip()
            
            if user_input.lower() in ['quit', 'q', '終了', 'exit']:
                print("👋 テキスト会話を終了します")
                break
                
            if not user_input:
                continue
            
            print("🤔 せつなが考え中...")
            response = setsuna_chat.get_response(user_input)
            print(f"🤖 せつな: {response}")
            
            print("🔊 音声再生中...")
            voice_output.speak(response)
            
            conversation_count += 1
            print()
        
        print(f"📊 会話数: {conversation_count}回")
        
    except Exception as e:
        print(f"❌ テキスト会話エラー: {e}")

def hotkey_mock_mode():
    """ホットキーモック音声モード"""
    print("\n🔥 ホットキーモック音声モード開始")
    print("-" * 40)
    
    try:
        from test_hotkey_auto import AutoHotkeyTest
        
        test = AutoHotkeyTest()
        print("✅ 初期化完了")
        print("💡 Enterキーでホットキーをシミュレーション")
        print("🎤 モック音声で対話が実行されます")
        print("💬 quit と入力で終了")
        print()
        
        while True:
            user_action = input("Enterでホットキー実行 (quit=終了): ").strip()
            
            if user_action.lower() in ['quit', 'q', '終了']:
                break
            
            success = test.simulate_hotkey_conversation()
            if not success:
                print("⚠️ モック音声が終了しました")
                break
                
        print("👋 ホットキーモックモードを終了します")
        
    except Exception as e:
        print(f"❌ ホットキーモックエラー: {e}")

def auto_demo_mode():
    """自動デモモード"""
    print("\n🚀 自動デモモード開始")
    print("-" * 40)
    
    try:
        from test_hotkey_auto import AutoHotkeyTest
        
        test = AutoHotkeyTest()
        test.run_auto_test()
        
    except Exception as e:
        print(f"❌ 自動デモエラー: {e}")

def system_test_mode():
    """システムテストモード"""
    print("\n🧪 システムテストモード開始")
    print("-" * 40)
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, "test_system.py"], 
                              capture_output=False, text=True)
        
        if result.returncode == 0:
            print("✅ システムテスト完了")
        else:
            print("❌ システムテストでエラーが発生しました")
            
    except Exception as e:
        print(f"❌ システムテストエラー: {e}")

if __name__ == "__main__":
    exit(main())