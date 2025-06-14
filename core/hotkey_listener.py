#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
グローバルホットキーリスナー - 新せつなBot
Ctrl+Shift+Altでの音声対話開始
"""

import threading
import time
from pynput import keyboard

class HotkeyListener:
    def __init__(self, callback=None):
        """
        ホットキーリスナーの初期化
        
        Args:
            callback: ホットキー押下時に呼び出される関数
        """
        # ホットキー組み合わせ (Ctrl+Shift+Alt - 左キー)
        self.hotkey_combination = {
            keyboard.Key.ctrl_l,
            keyboard.Key.shift_l, 
            keyboard.Key.alt_l
        }
        
        # 現在押下中のキー
        self.current_keys = set()
        
        # コールバック関数
        self.callback = callback
        
        # リスナー制御
        self.listener = None
        self.is_active = False
        self.is_processing = False  # 重複実行防止
        
        print("[ホットキー] Ctrl+Shift+Alt (左キー) でせつなBot起動")
    
    def on_key_press(self, key):
        """キー押下イベント処理"""
        self.current_keys.add(key)
        
        # ホットキー組み合わせチェック
        if self.hotkey_combination.issubset(self.current_keys):
            if not self.is_processing and self.callback:
                self.is_processing = True
                print("\n🔥 ホットキー検出！")
                
                # 別スレッドでコールバック実行（UIブロック防止）
                threading.Thread(
                    target=self._execute_callback,
                    daemon=True
                ).start()
    
    def on_key_release(self, key):
        """キー離しイベント処理"""
        try:
            self.current_keys.discard(key)
        except KeyError:
            pass
    
    def _execute_callback(self):
        """コールバック実行（別スレッド）"""
        try:
            if self.callback:
                self.callback()
        except Exception as e:
            print(f"[ホットキー] コールバックエラー: {e}")
        finally:
            # 少し間隔を空けて重複実行を防止
            time.sleep(1)
            self.is_processing = False
    
    def start_listening(self):
        """ホットキーリスニング開始"""
        if self.is_active:
            print("[ホットキー] 既にリスニング中です")
            return
        
        try:
            self.listener = keyboard.Listener(
                on_press=self.on_key_press,
                on_release=self.on_key_release
            )
            
            self.listener.start()
            self.is_active = True
            print("[ホットキー] ✅ グローバルホットキーリスニング開始")
            
        except Exception as e:
            print(f"[ホットキー] ❌ リスニング開始エラー: {e}")
    
    def stop_listening(self):
        """ホットキーリスニング停止"""
        if not self.is_active:
            return
        
        try:
            if self.listener:
                self.listener.stop()
                self.listener = None
            
            self.is_active = False
            self.current_keys.clear()
            print("[ホットキー] リスニング停止")
            
        except Exception as e:
            print(f"[ホットキー] 停止エラー: {e}")
    
    def is_listening(self):
        """リスニング状態の確認"""
        return self.is_active
    
    def wait_for_stop(self):
        """リスニング停止まで待機"""
        if self.listener:
            self.listener.join()

# テスト用
if __name__ == "__main__":
    print("=== ホットキーテスト ===")
    print("Ctrl+Shift+Alt (左キー) を押してください")
    print("Ctrl+C で終了")
    
    def test_callback():
        print("🎉 ホットキーが押されました！")
        print("せつなBotが起動するはずです")
    
    hotkey_listener = HotkeyListener(callback=test_callback)
    
    try:
        hotkey_listener.start_listening()
        
        # メインスレッドで待機
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n終了中...")
        hotkey_listener.stop_listening()
        print("ホットキーテスト終了")