#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSL2日本語表示テスト
"""

import sys
import os

# パス設定
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core'))

def main():
    print("🧪 WSL2日本語表示テスト")
    print("=" * 50)
    
    print("1. WSL2修正版GUI (推奨)")
    print("2. 元の日本語GUI") 
    print("3. 英語GUI")
    print("0. 終了")
    
    try:
        choice = input("\n選択 (1-3): ").strip()
        
        if choice == "1":
            print("\n🚀 WSL2修正版GUI起動...")
            from core.setsuna_gui_fixed import SetsunaGUIFixed
            gui = SetsunaGUIFixed()
            gui.run()
            
        elif choice == "2":
            print("\n🚀 元の日本語GUI起動...")
            from core.setsuna_gui import SetsunaGUI
            gui = SetsunaGUI()
            gui.run()
            
        elif choice == "3":
            print("\n🚀 英語GUI起動...")
            from core.setsuna_gui_en import SetsunaGUIEnglish
            gui = SetsunaGUIEnglish()
            gui.run()
            
        elif choice == "0":
            print("👋 終了します")
            
        else:
            print("❌ 無効な選択です")
            
    except Exception as e:
        print(f"❌ エラー: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())