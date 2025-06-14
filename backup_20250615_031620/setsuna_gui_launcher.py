#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
せつなBot GUI ランチャー
日本語文字化け対応版
"""

import sys
import os

# coreモジュールのパスを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core'))

def main():
    """メイン関数"""
    print("🤖 せつなBot GUI ランチャー")
    print("=" * 50)
    
    # WSL2環境チェック
    is_wsl2 = _check_wsl2_environment()
    if is_wsl2:
        print("📍 WSL2環境を検出しました")
        print("⚠️ 文字化けが発生する場合があります")
        print()
    
    # GUI版選択
    print("利用可能なGUI版:")
    print("1. 英語版GUI (推奨)")
    print("2. 日本語版GUI (実験的)")
    print("3. シンプルCLI版")
    print("0. 終了")
    print()
    
    try:
        while True:
            choice = input("選択してください (1-3, 0=終了): ").strip()
            
            if choice == "0":
                print("👋 ランチャーを終了します")
                break
            elif choice == "1":
                launch_english_gui()
                break
            elif choice == "2":
                launch_japanese_gui()
                break
            elif choice == "3":
                launch_cli_version()
                break
            else:
                print("❌ 無効な選択です。1-3を入力してください。")
                
    except KeyboardInterrupt:
        print("\n👋 プログラムを終了しました")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return 1
    
    return 0

def launch_english_gui():
    """英語版GUI起動"""
    print("\n🚀 英語版GUI起動中...")
    
    try:
        from setsuna_gui_en import SetsunaGUIEnglish
        
        print("✅ English GUI starting...")
        gui = SetsunaGUIEnglish()
        gui.run()
        
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        print("代替手段: python main_working.py")
        
    except Exception as e:
        print(f"❌ GUI起動エラー: {e}")
        print("WSL2環境ではGUIが制限される場合があります")

def launch_japanese_gui():
    """日本語版GUI起動"""
    print("\n🚀 日本語版GUI起動中...")
    print("⚠️ 文字化けする場合は英語版をお試しください")
    
    try:
        from setsuna_gui import SetsunaGUI
        
        print("✅ 日本語GUI起動...")
        gui = SetsunaGUI()
        gui.run()
        
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        print("代替手段: python main_working.py")
        
    except Exception as e:
        print(f"❌ GUI起動エラー: {e}")
        print("WSL2環境ではGUIが制限される場合があります")

def launch_cli_version():
    """CLI版起動"""
    print("\n🚀 シンプルCLI版起動中...")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, "main_working.py"], 
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        
    except Exception as e:
        print(f"❌ CLI版起動エラー: {e}")

def _check_wsl2_environment():
    """WSL2環境チェック"""
    try:
        with open('/proc/version', 'r') as f:
            version_info = f.read().lower()
            return 'microsoft' in version_info or 'wsl' in version_info
    except:
        return False

if __name__ == "__main__":
    exit(main())