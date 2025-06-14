#!/usr/bin/env python3
"""
Setsuna Bot システム全体チェックスクリプト
全モジュールの動作状況と問題を確認します
"""

import sys
import traceback
from datetime import datetime

def check_module(module_name, import_statement, test_function=None):
    """モジュールのインポートと動作テスト"""
    print(f"\n🔍 {module_name} チェック中...")
    try:
        exec(import_statement)
        print(f"✅ {module_name}: インポート成功")
        
        if test_function:
            test_function()
            print(f"✅ {module_name}: 機能テスト成功")
            
        return True
    except Exception as e:
        print(f"❌ {module_name}: エラー - {e}")
        return False

def test_openai():
    """OpenAI API設定テスト"""
    try:
        import openai
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key and api_key.startswith('sk-'):
            print("✅ OpenAI APIキー設定確認")
        else:
            print("⚠️  OpenAI APIキーが設定されていない可能性があります")
    except Exception as e:
        print(f"❌ OpenAI設定エラー: {e}")

def test_voicevox():
    """VOICEVOX接続テスト"""
    try:
        from voicevox_speaker import test_voicevox_connection
        if test_voicevox_connection():
            print("✅ VOICEVOX接続成功")
        else:
            print("⚠️  VOICEVOX接続失敗（Windows側で起動が必要）")
    except Exception as e:
        print(f"❌ VOICEVOX テストエラー: {e}")

def test_audio():
    """音声システムテスト"""
    try:
        import pygame.mixer
        pygame.mixer.init()
        print("✅ 音声システム（Pygame）初期化成功")
    except Exception as e:
        print(f"❌ 音声システムエラー: {e}")

def main():
    print("=" * 60)
    print("🤖 Setsuna Bot システムチェック")
    print(f"📅 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 基本モジュールチェック
    modules = [
        ("Core Dependencies", "import openai, speech_recognition, pynput, pygame", None),
        ("OpenAI", "import openai", test_openai),
        ("Speech Recognition", "import speech_recognition", None),
        ("Input Control", "import pynput", None),
        ("Audio Backend", "import pygame.mixer", test_audio),
        ("Environment", "from dotenv import load_dotenv; load_dotenv()", None),
    ]
    
    success_count = 0
    for name, import_stmt, test_func in modules:
        if check_module(name, import_stmt, test_func):
            success_count += 1
    
    print("\n" + "=" * 60)
    
    # アプリケーションモジュールチェック
    app_modules = [
        ("Setsuna Bot Core", "import setsuna_bot", None),
        ("VOICEVOX Speaker", "from voicevox_speaker import synthesize_voice", test_voicevox),
        ("Speech Input", "from speech_input import get_voice_input", None),
        ("Hotkey Mode", "import setsuna_hotkey_mode", None),
        ("GUI", "import setsuna_gui", None),
        ("Memory Manager", "import setsuna_memory_manager", None),
        ("Logger", "import setsuna_logger", None),
    ]
    
    app_success_count = 0
    for name, import_stmt, test_func in app_modules:
        if check_module(name, import_stmt, test_func):
            app_success_count += 1
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("📊 テスト結果サマリー")
    print("=" * 60)
    
    total_tests = len(modules) + len(app_modules)
    total_success = success_count + app_success_count
    
    print(f"✅ 成功: {total_success}/{total_tests}")
    print(f"❌ 失敗: {total_tests - total_success}/{total_tests}")
    
    if total_success == total_tests:
        print("\n🎉 すべてのテストが成功しました！")
        print("🚀 アプリケーションの起動準備が完了しています")
    else:
        print(f"\n⚠️  {total_tests - total_success}個のテストが失敗しました")
        print("📋 失敗した項目を確認して修正してください")
    
    print("\n🎯 次のステップ:")
    print("1. Windows側でVOICEVOXを起動:")
    print("   cd \"%LOCALAPPDATA%\\Programs\\VOICEVOX\\vv-engine\"")
    print("   run.exe --host 0.0.0.0 --port 50021")
    print("2. アプリケーション起動:")
    print("   python setsuna_gui.py")
    print("   または")
    print("   python setsuna_hotkey_mode.py")

if __name__ == "__main__":
    main()