#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ホットキー検出テスト - 柔軟検出版
Left/Rightキーを区別しない柔軟なホットキー検出
"""

import time
import threading
from datetime import datetime

print("🧪 ホットキー検出テスト - 柔軟検出版")
print("=" * 50)

try:
    from pynput import keyboard
    print("✅ pynput正常にインポートされました")
except ImportError as e:
    print(f"❌ pynputインポートエラー: {e}")
    exit(1)

pressed_keys = set()
hotkey_detected = False

def is_hotkey_pressed(pressed_keys):
    """柔軟なホットキー検出 - Left/Rightを区別しない"""
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

def get_key_status(pressed_keys):
    """現在のキー状態を表示用に整理"""
    # Ctrl系キーの確認
    ctrl_keys = [keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r]
    ctrl_status = "Ctrl" if any(k in pressed_keys for k in ctrl_keys) else "---"
    
    # Shift系キーの確認
    shift_keys = [keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r]
    shift_status = "Shift" if any(k in pressed_keys for k in shift_keys) else "-----"
    
    # Alt系キーの確認
    alt_keys = [keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r]
    alt_status = "Alt" if any(k in pressed_keys for k in alt_keys) else "---"
    
    return f"[{ctrl_status}] + [{shift_status}] + [{alt_status}]"

def on_press(key):
    global hotkey_detected
    try:
        pressed_keys.add(key)
        
        # キー状態表示
        status = get_key_status(pressed_keys)
        print(f"🔽 {key} → {status}")
        
        # ホットキー検出
        if is_hotkey_pressed(pressed_keys):
            if not hotkey_detected:
                hotkey_detected = True
                print("🎮 ★★★ ホットキー検出成功！ ★★★")
                print("     Ctrl + Shift + Alt 組み合わせ確認")
        
    except Exception as e:
        print(f"❌ キー押下処理エラー: {e}")

def on_release(key):
    global hotkey_detected
    try:
        if key in pressed_keys:
            pressed_keys.remove(key)
        
        # キー状態表示
        status = get_key_status(pressed_keys)
        print(f"🔼 {key} → {status}")
        
        # ホットキー解除検出
        if hotkey_detected and not is_hotkey_pressed(pressed_keys):
            hotkey_detected = False
            print("🛑 ホットキー解除検出")
        
        # ESCで終了
        if key == keyboard.Key.esc:
            print("🚪 ESCキーで終了")
            return False
            
    except Exception as e:
        print(f"❌ キー離上処理エラー: {e}")

print("📋 テスト手順:")
print("1. 任意のキーを押してキー検出をテスト")
print("2. Ctrl+Shift+Alt を同時に押してホットキーテスト")
print("   (Left/Rightのどちらでも検出されます)")
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
        print("✅ 柔軟ホットキー検出リスナー開始")
        listener.join()
        
except Exception as e:
    print(f"❌ キーボードリスナーエラー: {e}")

print("\n📊 テスト結果まとめ:")
print(f"   - 柔軟キー検出: ✅ 実装")
print(f"   - ホットキー検出: {'✅ 成功' if hotkey_detected else '❌ 未検出'}")

if hotkey_detected:
    print("\n🎉 ホットキー検出が成功しました！")
    print("   この検出ロジックをSimpleHotkeyVoiceに適用できます")
else:
    print("\n🤔 ホットキー検出ができませんでした")
    print("   他の原因を調査する必要があります")

print("\n🧪 柔軟ホットキー検出テスト完了")