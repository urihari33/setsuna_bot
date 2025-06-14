#!/usr/bin/env python3
"""
ファイル監視システムの外部テスト
GUIが動作中にこのスクリプトを実行して、ファイル更新が正しく検出されるかテスト
"""

import json
import time
import os

def test_file_monitoring():
    """ファイル監視システムをテストする"""
    
    print("=== ファイル監視テスト開始 ===")
    print("注意: setsuna_gui.py または test_gui_standalone.py が動作中であることを確認してください")
    
    # 既存ファイルの確認
    if os.path.exists("chat_history.json"):
        print("既存のchat_history.jsonを確認...")
        with open("chat_history.json", "r", encoding="utf-8") as f:
            existing_messages = json.load(f)
        print(f"現在のメッセージ数: {len(existing_messages)}")
    else:
        print("chat_history.json が見つかりません。新規作成します...")
        existing_messages = [
            {
                "role": "system",
                "content": "【プロジェクト共有履歴】\\n\\nあなたは「片無せつな」として応答してください。"
            }
        ]
    
    # テスト1: 新しいユーザーメッセージを追加
    print("\\nテスト1: ユーザーメッセージを追加...")
    test_messages_1 = existing_messages + [
        {
            "role": "user",
            "content": "ファイル監視テスト - メッセージ1"
        }
    ]
    
    with open("chat_history.json", "w", encoding="utf-8") as f:
        json.dump(test_messages_1, f, ensure_ascii=False, indent=2)
    
    print("ユーザーメッセージを追加しました。GUIに表示されているか確認してください。")
    time.sleep(3)
    
    # テスト2: せつなの応答を追加
    print("\\nテスト2: せつなの応答を追加...")
    test_messages_2 = test_messages_1 + [
        {
            "role": "assistant", 
            "content": "ファイル監視テストの応答です...うん、ちゃんと動いてるかな"
        }
    ]
    
    with open("chat_history.json", "w", encoding="utf-8") as f:
        json.dump(test_messages_2, f, ensure_ascii=False, indent=2)
    
    print("せつなの応答を追加しました。GUIに表示されているか確認してください。")
    time.sleep(3)
    
    # テスト3: 複数メッセージを一度に追加
    print("\\nテスト3: 複数メッセージを一度に追加...")
    test_messages_3 = test_messages_2 + [
        {
            "role": "user",
            "content": "複数メッセージテスト - ユーザー"
        },
        {
            "role": "assistant",
            "content": "複数メッセージテスト - せつな応答"
        },
        {
            "role": "user", 
            "content": "最終テストメッセージ"
        },
        {
            "role": "assistant",
            "content": "最終応答です...テスト完了かも"
        }
    ]
    
    with open("chat_history.json", "w", encoding="utf-8") as f:
        json.dump(test_messages_3, f, ensure_ascii=False, indent=2)
    
    print("複数メッセージを追加しました。GUIに全て表示されているか確認してください。")
    
    print("\\n=== テスト完了 ===")
    print(f"最終メッセージ数: {len(test_messages_3)}")
    print("GUIで手動更新ボタンを押して、全てのメッセージが表示されることを確認してください。")

if __name__ == "__main__":
    try:
        test_file_monitoring()
    except KeyboardInterrupt:
        print("\\nテストが中断されました。")
    except Exception as e:
        print(f"\\nテスト中にエラーが発生しました: {e}")