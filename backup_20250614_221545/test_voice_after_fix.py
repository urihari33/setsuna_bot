#!/usr/bin/env python3
"""VOICEVOXエンジン起動後のテストスクリプト"""

import requests
import json

from voicevox_speaker import speak_with_voicevox

def test_voice_system():
    # VOICEVOX接続テスト
    try:
        response = requests.get("http://127.0.0.1:50021/version", timeout=3)
        print(f"✅ VOICEVOX接続成功: {response.json()}")
        
        # 実際の音声テスト
        print("🎤 音声テスト開始...")
        speak_with_voicevox("音声システムのテストです。正常に動作しています。")
        print("✅ 音声テスト完了！")
        
    except requests.exceptions.ConnectionError:
        print("❌ VOICEVOXエンジンが起動していません")
        print("→ VOICEVOX.exeを起動してから再度実行してください")
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    test_voice_system()