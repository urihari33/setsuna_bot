#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
せつなBot 日本語GUI 起動ファイル
"""

import sys
import os

# パス設定
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core'))

def main():
    print("🤖 せつなBot 日本語GUI 起動中...")
    print("=" * 50)
    
    try:
        from core.setsuna_gui import SetsunaGUI
        
        print("✅ 日本語フォント対応版")
        print("✅ Yu Gothic フォント使用")
        print("🚀 GUIウィンドウを開きます...")
        print()
        print("※ ウィンドウが開いたら以下をお試しください:")
        print("  1. 初期化完了まで待機")
        print("  2. 音声テストボタンで確認")
        print("  3. テキスト会話ボタンで対話開始")
        print()
        
        # GUI起動
        gui = SetsunaGUI()
        gui.run()
        
    except Exception as e:
        print(f"❌ GUI起動エラー: {e}")
        print("\n代替方法:")
        print("python main_working.py")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())