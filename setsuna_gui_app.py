#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
せつなBot GUI アプリケーション
ミニマルGUIのメインランチャー
"""

import sys
import os

# coreモジュールのパスを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core'))

def main():
    """メイン関数"""
    print("🤖 せつなBot GUI アプリケーション")
    print("=" * 50)
    
    try:
        # WSL2環境チェック
        if _check_wsl2_gui_support():
            print("⚠️ WSL2環境でのGUI起動を試行します")
            print("問題が発生した場合は、main_working.py を使用してください")
            print()
        
        # GUI起動
        from core.setsuna_gui import SetsunaGUI
        
        print("🚀 せつなBot GUI を起動中...")
        gui = SetsunaGUI()
        gui.run()
        
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        print("\n🔧 解決方法:")
        print("1. 必要なパッケージをインストール: pip install tkinter")
        print("2. WSL2でGUIが使えない場合: main_working.py を使用")
        return 1
        
    except Exception as e:
        print(f"❌ GUI起動エラー: {e}")
        print("\n🔧 解決方法:")
        print("1. WSL2環境の場合: X11サーバーの設定を確認")
        print("2. 代替手段: main_working.py でテキスト会話")
        print("3. システムテスト: python test_system.py")
        return 1
    
    return 0

def _check_wsl2_gui_support():
    """WSL2環境のGUIサポートチェック"""
    try:
        # WSL環境かチェック
        with open('/proc/version', 'r') as f:
            version_info = f.read().lower()
            return 'microsoft' in version_info or 'wsl' in version_info
    except:
        return False

if __name__ == "__main__":
    exit(main())