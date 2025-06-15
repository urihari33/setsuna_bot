#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音声録音テスト - Windows環境
複数の音声録音手法をテスト
"""

import os
import time
import tempfile
import subprocess
import wave
from datetime import datetime

print("🎤 音声録音テスト - Windows環境")
print("=" * 45)

def test_1_basic_audio_file_creation():
    """テスト1: 基本的な音声ファイル作成"""
    print("\n📋 テスト1: 基本的な音声ファイル作成")
    
    try:
        # 一時ファイル作成テスト
        temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_wav.close()
        print(f"✅ 一時ファイル作成成功: {temp_wav.name}")
        
        # ファイル権限確認
        if os.path.exists(temp_wav.name):
            print("✅ ファイルアクセス権限: 正常")
        else:
            print("❌ ファイルアクセス権限: 問題あり")
        
        # クリーンアップ
        os.unlink(temp_wav.name)
        print("✅ ファイル削除: 正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 基本ファイル操作エラー: {e}")
        return False

def test_2_windows_sound_recorder():
    """テスト2: Windows SoundRecorderコマンド"""
    print("\n📋 テスト2: Windows SoundRecorderコマンド")
    
    try:
        # SoundRecorderの存在確認
        cmd = ["where", "SoundRecorder.exe"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print("✅ SoundRecorder.exe発見")
            print(f"   パス: {result.stdout.strip()}")
        else:
            print("❌ SoundRecorder.exe未発見")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ SoundRecorder確認エラー: {e}")
        return False

def test_3_powershell_audio():
    """テスト3: PowerShell音声機能"""
    print("\n📋 テスト3: PowerShell音声機能")
    
    try:
        # PowerShell音声ライブラリ確認
        ps_cmd = [
            "powershell", "-Command",
            "Add-Type -AssemblyName System.Speech; Write-Host 'PowerShell音声ライブラリ利用可能'"
        ]
        
        result = subprocess.run(ps_cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ PowerShell音声ライブラリ: 利用可能")
            print(f"   出力: {result.stdout.strip()}")
        else:
            print("❌ PowerShell音声ライブラリ: 利用不可")
            print(f"   エラー: {result.stderr.strip()}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ PowerShell音声テストエラー: {e}")
        return False

def test_4_simple_recording_simulation():
    """テスト4: 簡単な録音シミュレーション"""
    print("\n📋 テスト4: 簡単な録音シミュレーション")
    
    try:
        print("5秒間の録音シミュレーション開始...")
        
        # タイムアウト処理の簡単なテスト
        start_time = datetime.now()
        
        # 5秒間のシミュレーション（実際の録音なし）
        for i in range(5):
            time.sleep(1)
            print(f"   録音中... {i+1}/5秒")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"✅ 録音シミュレーション完了")
        print(f"   実行時間: {duration:.2f}秒")
        
        return True
        
    except Exception as e:
        print(f"❌ 録音シミュレーションエラー: {e}")
        return False

def test_5_speech_recognition_import():
    """テスト5: 音声認識ライブラリテスト"""
    print("\n📋 テスト5: 音声認識ライブラリテスト")
    
    try:
        import speech_recognition as sr
        print("✅ speech_recognition: インポート成功")
        
        # Recognizer作成テスト
        recognizer = sr.Recognizer()
        print("✅ Recognizer: 作成成功")
        
        # 設定確認
        print(f"   energy_threshold: {recognizer.energy_threshold}")
        print(f"   pause_threshold: {recognizer.pause_threshold}")
        
        return True
        
    except Exception as e:
        print(f"❌ 音声認識ライブラリエラー: {e}")
        return False

def test_6_microphone_permissions():
    """テスト6: マイクロフォン権限確認"""
    print("\n📋 テスト6: マイクロフォン権限確認")
    
    try:
        import speech_recognition as sr
        
        # マイクロフォンリスト取得
        print("利用可能なマイクロフォン:")
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            print(f"   {index}: {name}")
        
        # デフォルトマイクロフォンテスト
        mic = sr.Microphone()
        print("✅ デフォルトマイクロフォン: アクセス可能")
        
        return True
        
    except Exception as e:
        print(f"❌ マイクロフォン権限エラー: {e}")
        return False

# テスト実行
print("Windows環境での音声録音機能を段階的にテストします\n")

tests = [
    ("基本ファイル操作", test_1_basic_audio_file_creation),
    ("Windows SoundRecorder", test_2_windows_sound_recorder),
    ("PowerShell音声機能", test_3_powershell_audio),
    ("録音シミュレーション", test_4_simple_recording_simulation),
    ("音声認識ライブラリ", test_5_speech_recognition_import),
    ("マイクロフォン権限", test_6_microphone_permissions),
]

results = {}

for test_name, test_func in tests:
    try:
        success = test_func()
        results[test_name] = success
    except Exception as e:
        print(f"❌ {test_name}で予期しないエラー: {e}")
        results[test_name] = False

# 結果まとめ
print("\n" + "=" * 45)
print("📊 テスト結果まとめ:")

all_passed = True
for test_name, success in results.items():
    status = "✅ 成功" if success else "❌ 失敗"
    print(f"   {test_name}: {status}")
    if not success:
        all_passed = False

print(f"\n🎯 総合結果: {'✅ 全テスト成功' if all_passed else '⚠️ 一部テスト失敗'}")

if all_passed:
    print("\n🎉 音声録音環境が整っています！")
    print("📋 次のステップ:")
    print("   1. 実際のホットキー + 音声録音統合テスト")
    print("   2. SimpleHotkeyVoiceクラスの修正")
    print("   3. Discord bot完全統合")
else:
    print("\n🔧 修正が必要な項目があります")
    print("   失敗したテストの詳細を確認してください")

print("\n🎤 音声録音テスト完了")