#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日本語GUI動作テスト
フォント修正後の動作確認
"""

import sys
import os

# coreモジュールのパスを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core'))

def test_japanese_fonts():
    """日本語フォント動作テスト"""
    print("=== 日本語フォント動作テスト ===")
    
    try:
        import tkinter as tk
        import tkinter.font as tkFont
        
        root = tk.Tk()
        root.title("日本語フォントテスト")
        root.geometry("500x300")
        
        # テスト用日本語テキスト
        test_texts = [
            "こんにちは、せつなです",
            "音声対話システム",
            "システム状態: 待機中",
            "対話回数: 5回",
            "音声設定"
        ]
        
        # 各フォントでテスト
        fonts_to_test = [
            ("Yu Gothic", 12),
            ("Meiryo", 12),
            ("BIZ UDMincho", 12),
            ("TkDefaultFont", 12)
        ]
        
        row = 0
        for font_name, size in fonts_to_test:
            try:
                # フォント作成テスト
                test_font = tkFont.Font(family=font_name, size=size)
                
                # ラベル作成
                tk.Label(root, text=f"{font_name}:", font=("Arial", 10, "bold")).grid(
                    row=row, column=0, sticky=tk.W, padx=5, pady=2
                )
                
                for i, text in enumerate(test_texts):
                    label = tk.Label(root, text=text, font=(font_name, size))
                    label.grid(row=row, column=i+1, padx=5, pady=2)
                
                print(f"✅ {font_name}: 日本語表示成功")
                row += 1
                
            except Exception as e:
                print(f"❌ {font_name}: エラー - {e}")
        
        # 3秒後に自動終了
        root.after(3000, root.destroy)
        root.mainloop()
        
        print("✅ 日本語フォントテスト完了")
        return True
        
    except Exception as e:
        print(f"❌ フォントテストエラー: {e}")
        return False

def test_setsuna_gui_initialization():
    """せつなGUI初期化テスト"""
    print("\n=== せつなGUI初期化テスト ===")
    
    try:
        from core.setsuna_gui import SetsunaGUI
        
        print("フォント設定確認中...")
        
        # テスト用のGUIオブジェクト作成（表示なし）
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # ウィンドウ非表示
        
        # GUI初期化
        gui = SetsunaGUI()
        
        # フォント設定確認
        print(f"選択されたフォント: {gui.fonts}")
        
        # ウィンドウ破棄
        root.destroy()
        
        print("✅ せつなGUI初期化成功")
        return True
        
    except Exception as e:
        print(f"❌ GUI初期化エラー: {e}")
        return False

def main():
    """メイン関数"""
    print("🧪 日本語GUI修正後テスト")
    print("=" * 50)
    
    tests = [
        ("日本語フォント表示", test_japanese_fonts),
        ("せつなGUI初期化", test_setsuna_gui_initialization)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n🔬 {name}テスト実行中...")
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
        print("\n🎉 日本語GUI修正成功！")
        print("次のコマンドで日本語GUIを起動できます:")
        print("python -c \"from core.setsuna_gui import SetsunaGUI; SetsunaGUI().run()\"")
    else:
        print("\n⚠️ 一部テストが失敗しました")
        print("英語版GUI使用を推奨: python setsuna_gui_launcher.py → 1")
    
    return 0 if success_count == len(results) else 1

if __name__ == "__main__":
    exit(main())