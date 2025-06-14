#!/usr/bin/env python3
"""
音声入力機能のテスト（PyAudio不使用版）
"""

import sys

def test_speech_input():
    """修正した音声入力をテスト"""
    try:
        print("=== 音声入力テスト開始 ===")
        
        from speech_input import get_voice_input
        print("✅ speech_input モジュール インポート成功")
        
        print("\n🎤 音声入力テストを開始します")
        print("話しかけてください（5秒でテスト）...")
        
        # 短時間でテスト
        result = get_voice_input(timeout=5, phrase_time_limit=5)
        
        if result:
            print(f"✅ 音声認識成功: {result}")
        else:
            print("⚠️  音声が認識されませんでした（マイクやタイムアウトの可能性）")
        
        print("=== 音声入力テスト完了 ===")
        return True
        
    except Exception as e:
        print(f"❌ 音声入力テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_voice_synthesis():
    """音声合成のテスト"""
    try:
        print("\n=== 音声合成テスト開始 ===")
        
        from voicevox_speaker import speak_with_voicevox, test_voicevox_connection
        print("✅ voicevox_speaker モジュール インポート成功")
        
        # VOICEVOX接続確認
        if test_voicevox_connection():
            print("✅ VOICEVOX接続成功")
            
            test_text = "音声合成のテストです。"
            print(f"🔊 テスト音声: {test_text}")
            speak_with_voicevox(test_text)
            print("✅ 音声合成テスト完了")
            return True
        else:
            print("❌ VOICEVOX接続失敗")
            return False
            
    except Exception as e:
        print(f"❌ 音声合成テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_bot_response():
    """せつなの応答テスト"""
    try:
        print("\n=== せつな応答テスト開始 ===")
        
        from setsuna_bot import get_setsuna_response
        print("✅ setsuna_bot モジュール インポート成功")
        
        test_input = "こんにちは"
        print(f"💬 テスト入力: {test_input}")
        
        response = get_setsuna_response(test_input)
        if response:
            print(f"🤖 せつなの応答: {response}")
            print("✅ せつな応答テスト成功")
            return True
        else:
            print("❌ せつな応答生成失敗")
            return False
            
    except Exception as e:
        print(f"❌ せつな応答テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """全機能テスト"""
    print("=" * 60)
    print("🧪 Setsuna Bot 機能テスト")
    print("=" * 60)
    
    tests = [
        ("音声入力", test_speech_input),
        ("音声合成", test_voice_synthesis), 
        ("せつな応答", test_bot_response)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{'='*20} {name} テスト {'='*20}")
        success = test_func()
        results.append((name, success))
    
    print("\n" + "=" * 60)
    print("📊 テスト結果")
    print("=" * 60)
    
    for name, success in results:
        status = "✅ 成功" if success else "❌ 失敗"
        print(f"{name}: {status}")
    
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    print(f"\n総合結果: {success_count}/{total_count} 成功")
    
    if success_count == total_count:
        print("🎉 すべての機能が正常に動作しています！")
    else:
        print("⚠️  一部の機能に問題があります")

if __name__ == "__main__":
    main()