#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VcXsrv設定後の日本語GUI最終テスト
"""

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
import sys

def main():
    print("=== VcXsrv設定後 日本語GUI最終テスト ===")
    
    root = tk.Tk()
    root.title("VcXsrv日本語フォント設定テスト")
    root.geometry("700x500")
    
    # メインフレーム
    main_frame = ttk.Frame(root)
    main_frame.pack(padx=20, pady=20, fill='both', expand=True)
    
    # タイトル
    title_label = tk.Label(
        main_frame, 
        text="VcXsrv日本語フォントテスト", 
        font=('Arial', 16, 'bold'),
        fg='blue'
    )
    title_label.pack(pady=(0, 20))
    
    # フォントテスト結果表示エリア
    result_frame = ttk.LabelFrame(main_frame, text="フォントテスト結果")
    result_frame.pack(fill='both', expand=True, pady=10)
    
    # 利用可能フォント確認
    families = tkFont.families()
    jp_fonts = [f for f in families if any(jp in f.lower() for jp in ['meiryo', 'yugoth', 'gothic', 'yu', 'noto'])]
    
    print(f"検出された日本語フォント: {jp_fonts}")
    
    # テストするフォントと文字列
    test_cases = [
        ("デフォルト", None, "せつなBot - ステータス"),
        ("Meiryo", "Meiryo", "メイリオフォント - システム状態"),
        ("Yu Gothic", "Yu Gothic", "Yu Gothic - 対話回数"),
        ("Yu Gothic UI", "Yu Gothic UI", "Yu Gothic UI - 音声設定"),
        ("Noto Sans CJK JP", "Noto Sans CJK JP", "Noto CJK - 操作パネル"),
    ]
    
    y_pos = 10
    for font_name, font_family, test_text in test_cases:
        # フォント名表示
        name_label = tk.Label(
            result_frame, 
            text=f"{font_name}:",
            anchor='w',
            width=15
        )
        name_label.place(x=10, y=y_pos)
        
        # テストテキスト表示
        try:
            if font_family:
                font = tkFont.Font(family=font_family, size=12)
                actual_font = font.actual()
                
                # 実際に適用されたフォント確認
                if actual_font['family'] == font_family or font_family in actual_font['family']:
                    bg_color = 'lightgreen'  # 成功
                    status = "✅"
                else:
                    bg_color = 'lightcoral'  # フォールバック
                    status = "❌"
                    
                test_label = tk.Label(
                    result_frame,
                    text=f"{status} {test_text}",
                    font=font,
                    bg=bg_color,
                    anchor='w'
                )
                
                # 実際のフォント情報を表示
                info_text = f"実際: {actual_font['family']}"
                
            else:
                # デフォルトフォント
                test_label = tk.Label(
                    result_frame,
                    text=f"⚪ {test_text}",
                    bg='lightgray',
                    anchor='w'
                )
                info_text = "デフォルト"
                
            test_label.place(x=150, y=y_pos, width=350)
            
            # フォント情報表示
            info_label = tk.Label(
                result_frame,
                text=info_text,
                font=('Arial', 8),
                fg='gray',
                anchor='w'
            )
            info_label.place(x=520, y=y_pos)
            
            print(f"{font_name}: {info_text}")
            
        except Exception as e:
            error_label = tk.Label(
                result_frame,
                text=f"❌ エラー: {str(e)[:30]}",
                bg='pink',
                anchor='w'
            )
            error_label.place(x=150, y=y_pos, width=350)
            print(f"{font_name}: エラー - {e}")
            
        y_pos += 30
    
    # 説明テキスト
    info_text = """
テスト結果の見方:
✅ 緑色: 指定したフォントが正常に適用
❌ 赤色: フォールバック（fixedフォント等）に変更
⚪ 灰色: デフォルトフォント

VcXsrvを再起動後にこのテストを実行してください。
    """
    
    info_label = tk.Label(
        main_frame,
        text=info_text,
        justify='left',
        font=('Arial', 9),
        bg='lightyellow'
    )
    info_label.pack(side='bottom', fill='x', pady=10)
    
    print("\n=== GUI表示中（15秒間） ===")
    print("ウィンドウのタイトルは正常に日本語表示されるはずです")
    print("各フォントの色で設定成功/失敗を確認してください")
    
    # 15秒後に自動終了
    root.after(15000, root.destroy)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    
    print("=== テスト完了 ===")

if __name__ == "__main__":
    main()