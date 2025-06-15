#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ホットキー検出テスト
段階的にホットキー機能をテスト
"""

import time
import threading
from datetime import datetime

print("🧪 ホットキー検出テスト開始")
print("=" * 50)

# Phase 1: pynputライブラリのインポートテスト
print("Phase 1: pynputライブラリテスト")
try:
    from pynput import keyboard
    print("✅ pynput正常にインポートされました")
except ImportError as e:
    print(f"❌ pynputインポートエラー: {e}")
    exit(1)

# Phase 2: 基本的なキーボードリスナーテスト
print("\nPhase 2: 基本キーボードリスナーテスト")

pressed_keys = set()
target_keys = {keyboard.Key.ctrl, keyboard.Key.shift, keyboard.Key.alt}
hotkey_detected = False

def on_press(key):
    global hotkey_detected
    try:
        pressed_keys.add(key)
        print(f"🔽 キー押下: {key} ({datetime.now().strftime('%H:%M:%S.%f')[:-3]})")
        
        # 現在押されているキーを表示
        key_names = []
        for k in pressed_keys:
            if hasattr(k, 'name'):
                key_names.append(k.name)
            else:
                key_names.append(str(k))
        print(f"   現在のキー: {', '.join(key_names)}")
        
        # ホットキー検出
        if target_keys.issubset(pressed_keys):
            if not hotkey_detected:
                hotkey_detected = True
                print("🎮 ★★★ ホットキー検出成功！★★★")
        
    except Exception as e:
        print(f"❌ キー押下処理エラー: {e}")

def on_release(key):
    global hotkey_detected
    try:
        if key in pressed_keys:
            pressed_keys.remove(key)
        print(f"🔼 キー離上: {key} ({datetime.now().strftime('%H:%M:%S.%f')[:-3]})")
        
        # ホットキー解除検出
        if hotkey_detected and not target_keys.issubset(pressed_keys):
            hotkey_detected = False
            print("🛑 ホットキー解除検出")
        
        # ESCで終了
        if key == keyboard.Key.esc:
            print("🚪 ESCキーで終了")
            return False
            
    except Exception as e:
        print(f"❌ キー離上処理エラー: {e}")

print("キーボードリスナーを開始します...")
print("📋 テスト手順:")
print("1. 任意のキーを押してキー検出をテスト")
print("2. Ctrl+Shift+Alt を同時に押してホットキーテスト")
print("3. ESCキーでテスト終了")
print("4. 30秒後に自動終了")
print()

# タイムアウト設定
def timeout_handler():
    time.sleep(30)
    print("\n⏰ 30秒タイムアウト - テスト終了")
    return False

timeout_thread = threading.Thread(target=timeout_handler, daemon=True)
timeout_thread.start()

try:
    # キーボードリスナー開始
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        print("✅ キーボードリスナー開始")
        listener.join()
        
except Exception as e:
    print(f"❌ キーボードリスナーエラー: {e}")

print("\n📊 テスト結果まとめ:")
print(f"   - pynputライブラリ: ✅ 正常")
print(f"   - キーボードリスナー: {'✅ 正常' if 'listener' in locals() else '❌ 失敗'}")
print(f"   - ホットキー検出: {'✅ 成功' if hotkey_detected else '❌ 未検出'}")
print("\n🧪 ホットキー検出テスト完了")