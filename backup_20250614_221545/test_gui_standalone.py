#!/usr/bin/env python3
"""
setsuna_gui.py のスタンドアローンテスト版
環境の問題で本体を実行できない場合のテスト用
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import os
import time
import threading
from datetime import datetime

class StandaloneGUITest:
    def __init__(self):
        self.root = None
        self.chat_display = None
        self.status_label = None
        self.last_modified_time = 0
        self.last_loaded_count = 0
        self.monitoring_active = False
        self.monitoring_thread = None
        
    def create_window(self):
        """テスト用ウィンドウを作成"""
        self.root = tk.Tk()
        self.root.title("せつなGUI - ファイル監視テスト")
        self.root.geometry("600x400")
        
        # チャット表示エリア
        self.chat_display = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            state=tk.DISABLED,
            height=15,
            font=("メイリオ", 10)
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # タグ設定
        self.chat_display.tag_configure("user", foreground="blue", font=("メイリオ", 10, "bold"))
        self.chat_display.tag_configure("setsuna", foreground="red", font=("メイリオ", 10, "bold"))
        self.chat_display.tag_configure("timestamp", foreground="gray", font=("メイリオ", 8))
        
        # ボタンフレーム
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="手動更新", command=self.manual_refresh).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="ファイル作成テスト", command=self.create_test_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="監視開始", command=self.start_monitoring).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="監視停止", command=self.stop_monitoring).pack(side=tk.LEFT, padx=5)
        
        # ステータス
        self.status_label = ttk.Label(self.root, text="待機中...", relief=tk.SUNKEN)
        self.status_label.pack(fill=tk.X, padx=10, pady=5)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def add_message(self, timestamp, speaker, content):
        """メッセージを表示に追加"""
        self.chat_display.config(state=tk.NORMAL)
        
        # タイムスタンプ
        self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # 発言者
        if speaker == "user":
            self.chat_display.insert(tk.END, "あなた: ", "user")
        else:
            self.chat_display.insert(tk.END, "せつな: ", "setsuna")
        
        # 内容
        self.chat_display.insert(tk.END, content + "\n\n")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        
    def manual_refresh(self):
        """手動でファイルを読み込み"""
        self.status_label.config(text="手動更新中...")
        
        try:
            if os.path.exists("chat_history.json"):
                with open("chat_history.json", "r", encoding="utf-8") as f:
                    messages = json.load(f)
                
                user_assistant_messages = [msg for msg in messages if msg["role"] in ["user", "assistant"]]
                current_count = len(user_assistant_messages)
                
                print(f"[TEST] ファイル読み込み - 現在: {current_count}, 前回: {self.last_loaded_count}")
                
                if current_count > self.last_loaded_count:
                    new_messages = user_assistant_messages[self.last_loaded_count:]
                    
                    for msg in new_messages:
                        speaker = "user" if msg["role"] == "user" else "setsuna"
                        content = f"🎤 {msg['content']}"
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        self.add_message(timestamp, speaker, content)
                    
                    self.last_loaded_count = current_count
                    self.status_label.config(text=f"更新完了 - {len(new_messages)}件追加")
                else:
                    self.status_label.config(text="新しいメッセージはありません")
            else:
                self.status_label.config(text="chat_history.json が見つかりません")
                
        except Exception as e:
            self.status_label.config(text=f"エラー: {str(e)}")
            print(f"[TEST] 更新エラー: {e}")
    
    def create_test_file(self):
        """テスト用ファイルを作成"""
        messages = [
            {"role": "system", "content": "システムメッセージ"},
            {"role": "user", "content": "テストメッセージ1"},
            {"role": "assistant", "content": "テスト応答1"},
            {"role": "user", "content": "テストメッセージ2"},
            {"role": "assistant", "content": "テスト応答2"}
        ]
        
        with open("chat_history.json", "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        
        self.status_label.config(text="テストファイルを作成しました")
        print("[TEST] テストファイル作成完了")
    
    def start_monitoring(self):
        """ファイル監視開始"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self._monitor_file, daemon=True)
            self.monitoring_thread.start()
            self.status_label.config(text="ファイル監視開始")
            print("[TEST] ファイル監視開始")
    
    def stop_monitoring(self):
        """ファイル監視停止"""
        self.monitoring_active = False
        self.status_label.config(text="ファイル監視停止")
        print("[TEST] ファイル監視停止")
    
    def _monitor_file(self):
        """ファイル監視スレッド"""
        while self.monitoring_active:
            try:
                if os.path.exists("chat_history.json"):
                    current_time = os.path.getmtime("chat_history.json")
                    
                    if self.last_modified_time == 0:
                        self.last_modified_time = current_time
                        print(f"[MONITOR] 初期ファイル時刻設定: {current_time}")
                    elif current_time > self.last_modified_time:
                        print(f"[MONITOR] ファイル変更検出: {current_time}")
                        self.last_modified_time = current_time
                        
                        # メインスレッドで更新
                        self.root.after(100, self.manual_refresh)
                
                time.sleep(1)
                
            except Exception as e:
                print(f"[MONITOR] 監視エラー: {e}")
                time.sleep(2)
    
    def on_closing(self):
        """ウィンドウ閉じる処理"""
        self.monitoring_active = False
        self.root.destroy()
    
    def run(self):
        """テスト実行"""
        self.create_window()
        
        # 初期ファイル読み込み
        self.manual_refresh()
        
        print("[TEST] GUIテスト開始")
        print("[TEST] - 手動更新: chat_history.jsonを読み込み")
        print("[TEST] - ファイル作成テスト: テスト用ファイルを作成")
        print("[TEST] - 監視開始/停止: 自動監視のテスト")
        
        self.root.mainloop()

if __name__ == "__main__":
    test_gui = StandaloneGUITest()
    test_gui.run()