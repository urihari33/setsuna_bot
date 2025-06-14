#!/usr/bin/env python3
"""
音声対話ログ機能のテスト用スクリプト
setsuna_gui.pyの音声対話ログ機能が正常に動作するかテストします
"""

import json
import os
import time
from datetime import datetime

def test_voice_logging():
    """音声対話ログ機能をテスト"""
    
    print("=== 音声対話ログ機能テスト ===")
    
    # テスト用のchat_history.jsonを作成
    test_messages = [
        {
            "role": "system",
            "content": "テスト用システムプロンプト"
        },
        {
            "role": "user", 
            "content": "これはテスト音声入力です"
        },
        {
            "role": "assistant",
            "content": "テスト音声応答です。音声対話のログ機能をテストしています。"
        }
    ]
    
    # 既存のchat_history.jsonをバックアップ
    backup_file = None
    if os.path.exists("chat_history.json"):
        backup_file = f"chat_history_backup_{int(time.time())}.json"
        os.rename("chat_history.json", backup_file)
        print(f"既存のchat_history.jsonを{backup_file}にバックアップしました")
    
    try:
        # テスト用ファイルを作成
        with open("chat_history.json", "w", encoding="utf-8") as f:
            json.dump(test_messages, f, ensure_ascii=False, indent=2)
        
        print("テスト用chat_history.jsonを作成しました")
        print("内容:")
        for i, msg in enumerate(test_messages):
            if msg["role"] != "system":
                print(f"  {i}. {msg['role']}: {msg['content']}")
        
        print("\nsetsuna_gui.pyを起動して音声対話ログ機能をテストしてください。")
        print("GUIで以下を確認してください：")
        print("1. デバッグタブで「音声対話ファイル変更検出」が表示される")
        print("2. チャット欄に🎤マークが付いたメッセージが表示される")
        print("3. セッションログに「VOICE_INPUT」「VOICE_RESPONSE」が記録される")
        
        input("テスト完了後、Enterキーを押してください...")
        
    finally:
        # テストファイルを削除
        if os.path.exists("chat_history.json"):
            os.remove("chat_history.json")
            print("テスト用ファイルを削除しました")
        
        # バックアップを復元
        if backup_file and os.path.exists(backup_file):
            os.rename(backup_file, "chat_history.json")
            print("元のchat_history.jsonを復元しました")

if __name__ == "__main__":
    test_voice_logging()