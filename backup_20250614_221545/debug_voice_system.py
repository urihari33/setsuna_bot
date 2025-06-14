#!/usr/bin/env python3
"""音声システムの詳細診断スクリプト"""

import sys
import os
import requests
import subprocess

def check_voicevox():
    """VOICEVOX接続チェック"""
    try:
        response = requests.get("http://127.0.0.1:50021/version", timeout=3)
        print(f"✅ VOICEVOX接続OK (ステータス: {response.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ VOICEVOX接続失敗: エンジンが停止中")
        return False
    except Exception as e:
        print(f"❌ VOICEVOX接続エラー: {e}")
        return False

def check_simpleaudio():
    """simpleaudioモジュールチェック"""
    try:
        import simpleaudio
        print("✅ simpleaudio利用可能")
        return True
    except ImportError:
        print("❌ simpleaudioが見つかりません")
        return False

def check_voicevox_module():
    """voicevox_speakerモジュールチェック"""
    try:
        from voicevox_speaker import voice_settings
        print(f"✅ voicevox_speaker利用可能 (設定: {voice_settings})")
        return True
    except ImportError as e:
        print(f"❌ voicevox_speakerインポートエラー: {e}")
        return False

def check_audio_alternative():
    """代替音声再生手段のチェック"""
    alternatives = []
    
    # pygame check
    try:
        import pygame
        alternatives.append("pygame")
    except ImportError:
        pass
    
    # playsound check  
    try:
        import playsound
        alternatives.append("playsound")
    except ImportError:
        pass
        
    # winsound check (Windows only)
    if sys.platform == 'win32':
        try:
            import winsound
            alternatives.append("winsound")
        except ImportError:
            pass
    
    if alternatives:
        print(f"💡 代替音声再生: {', '.join(alternatives)}が利用可能")
    else:
        print("⚠️  代替音声再生手段が見つかりません")
    
    return alternatives

def main():
    print("🔍 音声システム診断開始...")
    print("=" * 50)
    
    # システム情報
    print(f"OS: {sys.platform}")
    print(f"Python: {sys.version}")
    print(f"作業ディレクトリ: {os.getcwd()}")
    print("=" * 50)
    
    # 各種チェック
    voicevox_ok = check_voicevox()
    simpleaudio_ok = check_simpleaudio()
    module_ok = check_voicevox_module()
    alternatives = check_audio_alternative()
    
    print("=" * 50)
    print("📋 診断結果:")
    
    if voicevox_ok and simpleaudio_ok and module_ok:
        print("✅ 音声システム正常 - 全て動作するはずです")
    elif voicevox_ok and module_ok and alternatives:
        print("⚠️  simpleaudioなしでも代替手段で動作可能")
    else:
        print("❌ 音声システムに問題があります")
        
        if not voicevox_ok:
            print("  → VOICEVOXエンジンを起動してください")
        if not simpleaudio_ok and not alternatives:
            print("  → 音声再生ライブラリをインストールしてください")
        if not module_ok:
            print("  → voicevox_speakerモジュールを確認してください")

if __name__ == "__main__":
    main()