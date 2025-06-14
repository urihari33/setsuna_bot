#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
フォント直接パス指定テスト
Tkinterの日本語フォント問題の最終解決策
"""

import tkinter as tk
from tkinter import font as tkFont
import os

def test_direct_font_path():
    """フォントファイル直接指定テスト"""
    print("=== フォント直接パス指定テスト ===")
    
    # フォントファイルパス
    font_paths = {
        'Yu Gothic': '/home/urihari/.fonts/YuGothM.ttc',
        'Meiryo': '/home/urihari/.fonts/meiryo.ttc',
        'BIZ UDMincho': '/home/urihari/.fonts/BIZ-UDMinchoM.ttc'
    }
    
    root = tk.Tk()
    root.title("Direct Font Path Test")
    root.geometry("700x400")
    
    test_text = "こんにちは、せつなです。日本語フォントテスト。"
    
    print("フォント直接指定テスト実行中...")
    
    # 1. 通常のフォント名指定（参考）
    tk.Label(root, text=f"Normal: {test_text}", font=('Yu Gothic', 12)).pack(pady=5)
    
    # 2. システムフォント直接使用試行
    for font_name, font_path in font_paths.items():
        try:
            if os.path.exists(font_path):
                print(f"✅ {font_name}: ファイル存在確認")
                
                # フォント作成試行
                try:
                    # Tkinterで直接パス指定は非対応のため、代替手法
                    label = tk.Label(root, text=f"{font_name}: {test_text}")
                    label.pack(pady=2)
                    
                    # フォント設定試行
                    label.configure(font=(font_name, 12))
                    print(f"✅ {font_name}: ラベル作成成功")
                    
                except Exception as e:
                    print(f"❌ {font_name}: ラベル作成失敗 - {e}")
            else:
                print(f"❌ {font_name}: ファイル不存在")
                
        except Exception as e:
            print(f"❌ {font_name}: エラー - {e}")
    
    # 3. フォールバック表示
    tk.Label(root, text=f"Fallback: {test_text}", font=('fixed', 12)).pack(pady=5)
    
    print("\nウィンドウを表示します（5秒後に自動終了）")
    root.after(5000, root.destroy)
    root.mainloop()
    
    print("✅ フォント直接パステスト完了")

def check_font_config_alternative():
    """fontconfig代替確認"""
    print("\n=== fontconfig代替確認 ===")
    
    try:
        import subprocess
        
        # フォント詳細確認
        result = subprocess.run(['fc-list', ':lang=ja'], capture_output=True, text=True)
        ja_fonts = result.stdout.strip().split('\n')
        
        print(f"日本語対応フォント数: {len(ja_fonts)}")
        
        if ja_fonts and ja_fonts[0]:
            print("日本語対応フォント（最初の3個）:")
            for font in ja_fonts[:3]:
                print(f"  - {font}")
        
        # フォントファミリー抽出
        families = set()
        for font_line in ja_fonts:
            if ':' in font_line:
                family_part = font_line.split(':')[1]
                if family_part:
                    family_name = family_part.split(',')[0].strip()
                    families.add(family_name)
        
        print(f"\n利用可能ファミリー数: {len(families)}")
        print("ファミリー一覧:")
        for family in sorted(families)[:5]:
            print(f"  - {family}")
            
    except Exception as e:
        print(f"fontconfig代替確認エラー: {e}")

def main():
    """メイン実行"""
    print("🔧 フォント問題最終解決テスト")
    print("=" * 50)
    
    check_font_config_alternative()
    test_direct_font_path()
    
    print("\n=" * 50)
    print("🔍 結論:")
    print("Tkinterが日本語フォントを認識しない場合、")
    print("WSL2環境での制限により、完全な日本語表示は困難です。")
    print("\n推奨解決策:")
    print("1. 英語GUI + 日本語会話機能")
    print("2. テキストベースインターフェース") 
    print("3. ウェブUI版の開発")

if __name__ == "__main__":
    main()