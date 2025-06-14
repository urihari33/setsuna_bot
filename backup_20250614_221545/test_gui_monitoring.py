#!/usr/bin/env python3
import json
import time
import os

# テスト用のチャット履歴を作成してGUI監視システムをテスト

def create_test_chat_history():
    """テスト用のチャット履歴を作成"""
    
    # 初期メッセージ
    initial_messages = [
        {
            "role": "system",
            "content": "【プロジェクト共有履歴】\n\nあなたは「片無せつな」として応答してください。"
        },
        {
            "role": "user", 
            "content": "テスト用メッセージ1"
        },
        {
            "role": "assistant",
            "content": "テスト応答1です...うん、わかりました"
        }
    ]
    
    # ファイルに保存
    with open("chat_history.json", "w", encoding="utf-8") as f:
        json.dump(initial_messages, f, ensure_ascii=False, indent=2)
    
    print(f"[TEST] Initial chat history created with {len(initial_messages)} messages")
    
    # 5秒後に新しいメッセージを追加
    time.sleep(5)
    
    print("[TEST] Adding new messages to simulate voice conversation...")
    
    # 新しいメッセージを追加（音声対話をシミュレート）
    new_messages = initial_messages + [
        {
            "role": "user",
            "content": "音声テストメッセージ"
        },
        {
            "role": "assistant", 
            "content": "音声応答です...聞こえてますか？"
        }
    ]
    
    # ファイルを更新
    with open("chat_history.json", "w", encoding="utf-8") as f:
        json.dump(new_messages, f, ensure_ascii=False, indent=2)
    
    print(f"[TEST] Updated chat history with {len(new_messages)} total messages")
    
    # さらに5秒後にもう一つ追加
    time.sleep(5)
    
    print("[TEST] Adding final test message...")
    
    final_messages = new_messages + [
        {
            "role": "user",
            "content": "最終テストメッセージ"
        },
        {
            "role": "assistant",
            "content": "最終応答です...テスト完了"
        }
    ]
    
    with open("chat_history.json", "w", encoding="utf-8") as f:
        json.dump(final_messages, f, ensure_ascii=False, indent=2)
    
    print(f"[TEST] Final chat history with {len(final_messages)} total messages")
    print("[TEST] Test completed - check GUI for updates")

if __name__ == "__main__":
    print("[TEST] Starting GUI monitoring test...")
    print("[TEST] Make sure setsuna_gui.py is running in another terminal")
    print("[TEST] This script will create and update chat_history.json")
    
    create_test_chat_history()