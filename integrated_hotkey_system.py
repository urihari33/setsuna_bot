#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合ホットキーシステム
安全な音声入力と従来のホットキー検出を統合
"""

from pynput import keyboard
import threading
import time
from typing import Optional


class IntegratedHotkeySystem:
    """安全な音声入力と統合されたホットキーシステム"""
    
    def __init__(self, safe_voice_integration):
        self.safe_voice = safe_voice_integration
        
        # ホットキー状態
        self.is_listening = False
        self.pressed_keys = set()
        self.keyboard_listener = None
        
        # ホットキー設定
        self.target_keys = {
            keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r,
            keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r,
            keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r
        }
        
        print("🎮 統合ホットキーシステム初期化完了")
    
    def _is_hotkey_pressed(self, pressed_keys):
        """Ctrl+Shift+Alt 組み合わせ検出"""
        # Ctrl系キーの検出
        ctrl_keys = [keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r]
        ctrl_pressed = any(k in pressed_keys for k in ctrl_keys)
        
        # Shift系キーの検出
        shift_keys = [keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r]
        shift_pressed = any(k in pressed_keys for k in shift_keys)
        
        # Alt系キーの検出
        alt_keys = [keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r]
        alt_pressed = any(k in pressed_keys for k in alt_keys)
        
        return ctrl_pressed and shift_pressed and alt_pressed
    
    def start_listening(self) -> bool:
        """ホットキー監視開始"""
        if self.is_listening:
            print("⚠️ 既にホットキー監視中です")
            return False
        
        try:
            self.is_listening = True
            
            # キーボードリスナー開始
            self.keyboard_listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self.keyboard_listener.start()
            
            print("🎮 統合ホットキー監視開始: Ctrl+Shift+Alt で音声入力")
            return True
            
        except Exception as e:
            print(f"❌ ホットキー監視開始エラー: {e}")
            self.is_listening = False
            return False
    
    def stop_listening(self):
        """ホットキー監視停止"""
        if not self.is_listening:
            return
        
        print("🛑 統合ホットキー監視停止中...")
        self.is_listening = False
        
        # 録音中の場合は停止
        if self.safe_voice.voice_input.is_recording:
            self.safe_voice.on_hotkey_release()
        
        # キーボードリスナー停止
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        
        print("✅ 統合ホットキー監視停止完了")
    
    def _on_key_press(self, key):
        """キー押下イベント処理"""
        try:
            self.pressed_keys.add(key)
            
            # ホットキー組み合わせ検出
            if (self._is_hotkey_pressed(self.pressed_keys) and 
                not self.safe_voice.hotkey_pressed):
                
                print("🎮 ★ 統合ホットキー検出: 安全な録音開始 ★")
                self.safe_voice.on_hotkey_press()
        
        except Exception as e:
            print(f"❌ キー押下処理エラー: {e}")
    
    def _on_key_release(self, key):
        """キー離上イベント処理"""
        try:
            if key in self.pressed_keys:
                self.pressed_keys.remove(key)
            
            # ホットキー解除検出
            if (self.safe_voice.hotkey_pressed and 
                not self._is_hotkey_pressed(self.pressed_keys)):
                
                print("🛑 統合ホットキー解除: 安全な録音停止")
                self.safe_voice.on_hotkey_release()
        
        except Exception as e:
            print(f"❌ キー離上処理エラー: {e}")
    
    def get_status(self) -> dict:
        """システム状態取得"""
        voice_status = self.safe_voice.voice_input.get_status() if self.safe_voice else {}
        
        return {
            'is_listening': self.is_listening,
            'hotkey_pressed': self._is_hotkey_pressed(self.pressed_keys),
            'voice_system_status': voice_status,
            'integration_version': 'integrated_v1.0'
        }


# テスト実行部分
if __name__ == "__main__":
    print("🧪 統合ホットキーシステム テスト開始")
    
    # テスト用の簡易Bot
    import asyncio
    
    class TestBot:
        def __init__(self):
            self.loop = asyncio.new_event_loop()
            self.received_messages = []
            
            # バックグラウンドでループ実行
            self.loop_thread = threading.Thread(target=self._run_loop, daemon=True)
            self.loop_thread.start()
            time.sleep(0.5)
        
        def _run_loop(self):
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()
        
        async def handle_voice_input(self, text):
            print(f"TestBot受信: {text}")
            self.received_messages.append(text)
            return f"処理完了: {text}"
    
    # 統合システムのテスト
    try:
        from windows_voice_input import SafeHotkeyVoiceIntegration
        
        test_bot = TestBot()
        safe_voice = SafeHotkeyVoiceIntegration(test_bot)
        integrated_system = IntegratedHotkeySystem(safe_voice)
        
        print("統合システムテスト開始...")
        print("Ctrl+Shift+Alt を押してテストしてください")
        print("Ctrl+C で終了")
        
        integrated_system.start_listening()
        
        # メインループ
        while True:
            time.sleep(1)
            status = integrated_system.get_status()
            if status['voice_system_status'].get('is_recording'):
                print("🔴 録音中...")
            
    except KeyboardInterrupt:
        print("\n終了中...")
        if 'integrated_system' in locals():
            integrated_system.stop_listening()
        print(f"✅ 終了完了 - 受信メッセージ数: {len(test_bot.received_messages)}件")
    except ImportError as e:
        print(f"❌ テスト実行エラー: {e}")
        print("windows_voice_input.py が必要です")