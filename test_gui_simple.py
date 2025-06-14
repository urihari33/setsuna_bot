#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
せつなBot 簡易GUIテスト
WSL2環境での基本GUI動作確認
"""

import sys
import os

# coreモジュールのパスを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_tkinter_basic():
    """Tkinter基本動作テスト"""
    try:
        import tkinter as tk
        print("✅ tkinter インポート成功")
        
        # 簡単なウィンドウ作成テスト
        root = tk.Tk()
        root.title("せつなBot GUI テスト")
        root.geometry("300x200")
        
        label = tk.Label(root, text="🤖 せつなBot GUI テスト\n\nこのウィンドウが表示されればGUI動作可能です", justify=tk.CENTER)
        label.pack(expand=True)
        
        close_button = tk.Button(root, text="閉じる", command=root.destroy)
        close_button.pack(pady=10)
        
        print("✅ GUI ウィンドウを表示します（3秒後に自動終了）")
        
        # 3秒後に自動終了
        root.after(3000, root.destroy)
        root.mainloop()
        
        print("✅ GUI基本テスト成功")
        return True
        
    except Exception as e:
        print(f"❌ GUI基本テストエラー: {e}")
        return False

def test_gui_components():
    """GUI コンポーネントテスト"""
    try:
        print("\n🧪 GUI コンポーネントテスト開始")
        
        # せつなGUI のインポートテスト
        sys.path.append('core')
        from core.setsuna_gui import SetsunaGUI
        print("✅ せつなGUI クラスインポート成功")
        
        return True
        
    except Exception as e:
        print(f"❌ GUI コンポーネントテストエラー: {e}")
        return False

def main():
    """メイン関数"""
    print("🧪 せつなBot 簡易GUIテスト")
    print("=" * 40)
    
    # 環境チェック
    try:
        with open('/proc/version', 'r') as f:
            version_info = f.read().lower()
            if 'microsoft' in version_info or 'wsl' in version_info:
                print("📍 WSL2環境を検出")
                print("⚠️ GUI表示にはX11サーバーが必要です")
            else:
                print("📍 Linux環境を検出")
    except:
        print("📍 環境情報取得失敗")
    
    print()
    
    # テスト実行
    tests = [
        ("Tkinter基本", test_tkinter_basic),
        ("GUI コンポーネント", test_gui_components)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"🔬 {name}テスト実行中...")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name}テストで例外: {e}")
            results.append((name, False))
    
    # 結果サマリー
    print("\n" + "=" * 30)
    print("🧪 テスト結果")
    print("=" * 30)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    success_count = sum(1 for _, result in results if result)
    print(f"\n成功: {success_count}/{len(results)}")
    
    if success_count == len(results):
        print("\n🎉 全テスト成功！GUI システムが利用可能です")
        print("次のコマンドでGUIを起動してください:")
        print("python setsuna_gui_app.py")
    else:
        print("\n⚠️ 一部テストが失敗しました")
        print("WSL2環境ではGUIが制限される場合があります")
        print("代替手段: python main_working.py")
    
    return 0 if success_count == len(results) else 1

if __name__ == "__main__":
    exit(main())