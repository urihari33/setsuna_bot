#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
せつなBot システムテスト
音声入力なしのテキスト対話版
"""

import sys
import os

# coreモジュールのパスを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.voice_output import VoiceOutput
from core.setsuna_chat import SetsunaChat

def test_voice_output():
    """音声出力テスト"""
    print("\n=== 音声出力テスト ===")
    try:
        voice_output = VoiceOutput()
        test_text = "こんにちは、せつなです。音声出力のテストをしています。"
        voice_output.speak(test_text)
        print("✅ 音声出力テスト成功")
        return True
    except Exception as e:
        print(f"❌ 音声出力テストエラー: {e}")
        return False

def test_chat():
    """チャットテスト"""
    print("\n=== チャットテスト ===")
    try:
        setsuna_chat = SetsunaChat()
        
        test_inputs = [
            "こんにちは",
            "今日はいい天気ですね",
            "ありがとう"
        ]
        
        for user_input in test_inputs:
            print(f"👤 ユーザー: {user_input}")
            response = setsuna_chat.get_response(user_input)
            print(f"🤖 せつな: {response}")
        
        print("✅ チャットテスト成功")
        return True
    except Exception as e:
        print(f"❌ チャットテストエラー: {e}")
        return False

def test_integrated_chat():
    """統合チャットテスト（テキスト入力）"""
    print("\n=== 統合チャットテスト ===")
    
    try:
        voice_output = VoiceOutput()
        setsuna_chat = SetsunaChat()
        
        print("テキスト入力による対話テストを開始します")
        print("'quit'で終了します\n")
        
        while True:
            user_input = input("👤 あなた: ").strip()
            
            if user_input.lower() == 'quit' or user_input == '終了':
                print("👋 対話を終了します")
                break
                
            if not user_input:
                continue
            
            # GPT応答生成
            response = setsuna_chat.get_response(user_input)
            print(f"🤖 せつな: {response}")
            
            # 音声出力
            print("🔊 音声再生中...")
            voice_output.speak(response)
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ 統合テストエラー: {e}")
        return False

def main():
    """メイン関数"""
    print("🤖 せつなBot システムテスト")
    print("=" * 50)
    
    # 自動的に全テストを実行
    tests = [
        ("音声出力", test_voice_output),
        ("チャット", test_chat)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{name}テストを開始します...")
        try:
            success = test_func()
            results.append((name, success))
            status = "✅ 成功" if success else "❌ 失敗"
            print(f"{name}テスト: {status}")
        except Exception as e:
            results.append((name, False))
            print(f"{name}テスト: ❌ エラー - {e}")
    
    # 結果サマリー
    print("\n" + "=" * 30)
    print("🧪 テスト結果サマリー")
    print("=" * 30)
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    success_count = sum(1 for _, success in results if success)
    print(f"\n成功: {success_count}/{len(results)}")
    
    if success_count == len(results):
        print("\n🎉 全テスト成功！システムは正常に動作しています")
    else:
        print("\n⚠️ 一部テストが失敗しました")

if __name__ == "__main__":
    main()