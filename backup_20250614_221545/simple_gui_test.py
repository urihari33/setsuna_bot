#!/usr/bin/env python3
"""
簡単なGUIテスト - 基本的なtkinter動作確認
"""

import tkinter as tk
from tkinter import ttk
import sys

def test_simple_gui():
    try:
        print("=== GUI テスト開始 ===")
        
        # ルートウィンドウ作成
        root = tk.Tk()
        root.title("Setsuna Bot GUI Test")
        root.geometry("400x300")
        
        # ラベル追加
        label = tk.Label(root, text="GUI正常動作テスト", font=("Arial", 16))
        label.pack(pady=20)
        
        # ボタン追加
        def on_button_click():
            print("ボタンがクリックされました")
            label.config(text="ボタンクリック成功！")
        
        button = tk.Button(root, text="テストボタン", command=on_button_click)
        button.pack(pady=10)
        
        # 閉じるボタン
        def close_app():
            print("GUI テスト終了")
            root.destroy()
        
        close_button = tk.Button(root, text="閉じる", command=close_app)
        close_button.pack(pady=10)
        
        print("GUI ウィンドウを表示中...")
        print("ウィンドウが表示されたら、ボタンをテストして 'x' で閉じてください")
        
        # ウィンドウ表示
        root.mainloop()
        
        print("=== GUI テスト正常終了 ===")
        return True
        
    except Exception as e:
        print(f"=== GUI テストエラー ===")
        print(f"エラー内容: {e}")
        print(f"エラータイプ: {type(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_gui()
    if success:
        print("\n✅ 基本的なGUI機能は正常です")
    else:
        print("\n❌ GUI機能に問題があります")
    
    sys.exit(0 if success else 1)