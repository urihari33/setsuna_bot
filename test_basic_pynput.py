#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pynput基本機能テスト
WSL2環境での動作確認
"""

print("🔧 pynput基本機能テスト")
print("=" * 40)

# テスト1: インポート確認
print("テスト1: ライブラリインポート")
try:
    import pynput
    print(f"✅ pynput version: {pynput.__version__}")
except Exception as e:
    print(f"❌ pynput: {e}")

try:
    from pynput import keyboard
    print("✅ pynput.keyboard インポート成功")
except Exception as e:
    print(f"❌ pynput.keyboard: {e}")
    exit(1)

# テスト2: 環境情報確認
print("\nテスト2: 環境情報")
import os
import sys

print(f"OS: {os.name}")
print(f"Platform: {sys.platform}")
print(f"DISPLAY: {os.environ.get('DISPLAY', 'NOT SET')}")
print(f"WSL_DISTRO_NAME: {os.environ.get('WSL_DISTRO_NAME', 'NOT SET')}")

# テスト3: 簡単なキーボードリスナーテスト（非ブロッキング）
print("\nテスト3: 非ブロッキングキーボードテスト")

test_completed = False

def simple_on_press(key):
    global test_completed
    print(f"キー検出: {key}")
    test_completed = True
    return False  # リスナー停止

def simple_on_release(key):
    print(f"キー離上: {key}")

try:
    print("5秒間キーボードリスナーテスト...")
    
    listener = keyboard.Listener(
        on_press=simple_on_press,
        on_release=simple_on_release
    )
    
    listener.start()
    print("リスナー開始")
    
    # 5秒待機
    import time
    for i in range(5):
        time.sleep(1)
        print(f"待機中... {i+1}/5秒")
        if test_completed:
            break
    
    listener.stop()
    print("リスナー停止")
    
    if test_completed:
        print("✅ キーボード検出成功")
    else:
        print("❌ キーボード検出失敗")

except Exception as e:
    print(f"❌ キーボードリスナーエラー: {e}")

# テスト4: X11関連の確認
print("\nテスト4: X11/Display確認")
try:
    import subprocess
    result = subprocess.run(['xset', 'q'], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        print("✅ X11サーバー接続成功")
    else:
        print(f"❌ X11サーバーエラー: {result.stderr}")
except Exception as e:
    print(f"❌ X11確認エラー: {e}")

print("\n📋 診断結果:")
print("1. pynputライブラリが正常にインストールされているか")
print("2. WSL2のX11転送が正しく設定されているか")  
print("3. DISPLAYの環境変数が正しく設定されているか")
print("4. VcXsrvやX410などのX11サーバーが動作しているか")

print("\n🔧 pynput基本機能テスト完了")