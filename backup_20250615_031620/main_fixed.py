#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
せつなBot メインエントリーポイント（修正版）
PyAudio問題を回避した音声対話システム
"""

import sys
import os

# coreモジュールのパスを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core'))

def main():
    """メイン関数"""
    print("🤖 せつなBot - 音声対話システム（修正版）")
    print("=" * 50)
    
    try:
        # PyAudio問題を回避したモック音声入力版を使用
        print("⚠️ PyAudio問題のため、モック音声入力版で動作します")
        print("実際の音声入力: test_system.py を使用してください")
        print()
        
        # 直接インポート
        from voice_output import VoiceOutput
        from setsuna_chat import SetsunaChat
        from voice_input_mock import VoiceInput
        
        print("=== システム初期化 ===")
        
        # 各モジュールの初期化
        print("[初期化] 音声入力システム（モック版）...")
        voice_input = VoiceInput()
        
        print("[初期化] 音声出力システム...")
        voice_output = VoiceOutput()
        
        print("[初期化] チャットシステム...")
        setsuna_chat = SetsunaChat()
        
        print("✅ せつなBot 初期化完了！")
        print()
        
        # デモ対話実行
        print("=== デモ音声対話 ===")
        print("モック音声入力で5回の対話を実行します...")
        print()
        
        conversation_count = 0
        max_conversations = 5
        
        while conversation_count < max_conversations:
            print(f"💬 対話 #{conversation_count + 1}")
            print("-" * 30)
            
            # 1. 音声入力（モック）
            print("🎤 音声入力中...")
            user_input = voice_input.listen()
            
            if not user_input:
                print("⏰ 音声入力終了")
                break
            
            print(f"👤 ユーザー: {user_input}")
            
            # 2. GPT応答生成
            print("🤔 せつなが考え中...")
            setsuna_response = setsuna_chat.get_response(user_input)
            print(f"🤖 せつな: {setsuna_response}")
            
            # 3. 音声出力
            print("🔊 音声再生中...")
            voice_output.speak(setsuna_response)
            
            conversation_count += 1
            print(f"✅ 対話完了\n")
        
        print("=== 対話終了 ===")
        print(f"総対話数: {conversation_count}回")
        print("👋 ありがとうございました！")
        
    except KeyboardInterrupt:
        print("\n👋 プログラムを終了しました")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        print("\n🔧 解決方法:")
        print("1. VOICEVOX が起動しているか確認")
        print("2. .env ファイルの OPENAI_API_KEY を確認")
        print("3. test_system.py での動作確認")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())