#!/usr/bin/env python3
"""
VOICEVOX接続テストスクリプト
WSL2環境からWindows側のVOICEVOXサーバーへの接続確認
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from voicevox_speaker import test_voicevox_connection, synthesize_voice, VOICEVOX_URL, WINDOWS_HOST_IP

def main():
    print("=" * 50)
    print("VOICEVOX接続テストスクリプト")
    print("=" * 50)
    
    print(f"検出されたWindowsホストIP: {WINDOWS_HOST_IP}")
    print(f"VOICEVOX接続先: {VOICEVOX_URL}")
    print()
    
    # 接続テスト
    if test_voicevox_connection():
        print("✅ VOICEVOX接続成功!")
        print()
        
        # 簡単な音声合成テスト
        print("🎤 音声合成テスト開始...")
        test_text = "こんにちは、せつなです。音声合成のテストをしています。"
        
        audio_path = synthesize_voice(test_text)
        if audio_path:
            print(f"✅ 音声合成成功: {audio_path}")
            print("🔊 音声再生テストを実行してください：")
            print(f"   play {audio_path}")
        else:
            print("❌ 音声合成失敗")
    else:
        print("❌ VOICEVOX接続失敗")
        print()
        print("💡 対処法:")
        print("1. Windows側でVOICEVOXを起動してください")
        print("2. VOICEVOXの設定で「API機能を有効にする」を確認してください")
        print("3. Windowsファイアウォールの設定を確認してください")
        print("4. 以下コマンドでWindowsからのアクセスを許可してください:")
        print("   netsh advfirewall firewall add rule name=\"VOICEVOX\" dir=in action=allow protocol=TCP localport=50021")

if __name__ == "__main__":
    main()