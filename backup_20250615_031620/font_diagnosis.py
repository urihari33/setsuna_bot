#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
フォント診断ツール
WSL2環境での日本語フォント問題を詳細調査
"""

import sys
import os
import subprocess

def check_system_locale():
    """システムロケール確認"""
    print("=== システムロケール確認 ===")
    try:
        result = subprocess.run(['locale'], capture_output=True, text=True)
        print("現在のロケール設定:")
        print(result.stdout)
        
        # UTF-8サポート確認
        result = subprocess.run(['locale', '-a'], capture_output=True, text=True)
        utf8_locales = [line for line in result.stdout.split('\n') if 'utf8' in line.lower() or 'utf-8' in line.lower()]
        print(f"UTF-8対応ロケール数: {len(utf8_locales)}")
        if utf8_locales:
            print("利用可能なUTF-8ロケール（最初の5個）:")
            for locale in utf8_locales[:5]:
                print(f"  - {locale}")
        
    except Exception as e:
        print(f"ロケール確認エラー: {e}")

def check_fontconfig():
    """fontconfig設定確認"""
    print("\n=== fontconfig設定確認 ===")
    
    try:
        # フォント一覧
        result = subprocess.run(['fc-list'], capture_output=True, text=True)
        fonts = result.stdout.split('\n')
        print(f"システム認識フォント総数: {len(fonts)}")
        
        # 日本語フォント検索
        jp_fonts = [f for f in fonts if any(keyword in f.lower() for keyword in ['jp', 'japan', 'cjk', 'gothic', 'mincho', 'meiryo', 'yu'])]
        print(f"日本語関連フォント数: {len(jp_fonts)}")
        
        if jp_fonts:
            print("日本語関連フォント:")
            for font in jp_fonts[:10]:  # 最初の10個
                print(f"  - {font}")
        
        # 特定フォント詳細確認
        test_fonts = ['Yu Gothic', 'Meiryo', 'BIZ UDMincho']
        for font_name in test_fonts:
            result = subprocess.run(['fc-match', font_name], capture_output=True, text=True)
            print(f"fc-match '{font_name}': {result.stdout.strip()}")
            
    except Exception as e:
        print(f"fontconfig確認エラー: {e}")

def check_tkinter_fonts():
    """Tkinterフォント確認"""
    print("\n=== Tkinterフォント確認 ===")
    
    try:
        import tkinter as tk
        import tkinter.font as tkFont
        
        root = tk.Tk()
        root.withdraw()
        
        # 利用可能フォント
        families = tkFont.families()
        print(f"Tkinter認識フォント数: {len(families)}")
        print("全Tkinterフォント:")
        for font in sorted(families):
            print(f"  - {font}")
        
        # 日本語フォントテスト
        print("\n日本語フォント動作テスト:")
        test_fonts = ['Yu Gothic', 'Meiryo', 'BIZ UDMincho', 'TkDefaultFont', 'fixed']
        for font_name in test_fonts:
            try:
                font_obj = tkFont.Font(family=font_name, size=12)
                print(f"✅ {font_name}: 作成成功")
                
                # フォント詳細情報
                actual_family = font_obj.actual('family')
                actual_size = font_obj.actual('size')
                print(f"   実際のフォント: {actual_family}, サイズ: {actual_size}")
                
            except Exception as e:
                print(f"❌ {font_name}: エラー - {e}")
        
        root.destroy()
        
    except Exception as e:
        print(f"Tkinterフォント確認エラー: {e}")

def check_character_support():
    """文字サポート確認"""
    print("\n=== 文字サポート確認 ===")
    
    # テスト文字列
    test_chars = {
        'ひらがな': 'あいうえお',
        'カタカナ': 'アイウエオ',
        '漢字': '日本語',
        '英数字': 'Hello123',
        '記号': '！？（）'
    }
    
    print("文字エンコーディングテスト:")
    for category, text in test_chars.items():
        try:
            # UTF-8エンコード/デコードテスト
            encoded = text.encode('utf-8')
            decoded = encoded.decode('utf-8')
            
            print(f"✅ {category}: {text}")
            print(f"   UTF-8バイト: {len(encoded)}")
            print(f"   文字数: {len(text)}")
            
        except Exception as e:
            print(f"❌ {category}: エラー - {e}")

def check_display_capability():
    """ディスプレイ機能確認"""
    print("\n=== ディスプレイ機能確認 ===")
    
    try:
        # DISPLAY環境変数
        display = os.environ.get('DISPLAY', 'なし')
        print(f"DISPLAY環境変数: {display}")
        
        # X11接続テスト
        result = subprocess.run(['xset', 'q'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ X11接続: 正常")
        else:
            print("❌ X11接続: 失敗")
            
    except subprocess.TimeoutExpired:
        print("⏰ X11接続: タイムアウト")
    except Exception as e:
        print(f"ディスプレイ確認エラー: {e}")

def font_rendering_test():
    """フォントレンダリングテスト"""
    print("\n=== フォントレンダリングテスト ===")
    
    try:
        import tkinter as tk
        import tkinter.font as tkFont
        
        root = tk.Tk()
        root.title("Font Rendering Test")
        root.geometry("600x400")
        
        # テスト文字列
        test_text = "こんにちは、せつなです"
        
        # 各フォントでテスト
        fonts_to_test = [
            ('TkDefaultFont', 12),
            ('fixed', 12),
            ('DejaVu Sans', 12),
            ('Yu Gothic', 12),
            ('Meiryo', 12)
        ]
        
        print("フォントレンダリングテスト実行中...")
        for i, (font_family, size) in enumerate(fonts_to_test):
            try:
                label = tk.Label(
                    root, 
                    text=f"{font_family}: {test_text}",
                    font=(font_family, size)
                )
                label.pack(pady=5)
                print(f"✅ {font_family}: ラベル作成成功")
                
            except Exception as e:
                print(f"❌ {font_family}: ラベル作成失敗 - {e}")
        
        print("\nウィンドウを3秒間表示します...")
        root.after(3000, root.destroy)
        root.mainloop()
        
        print("✅ フォントレンダリングテスト完了")
        
    except Exception as e:
        print(f"フォントレンダリングテストエラー: {e}")

def main():
    """メイン診断実行"""
    print("🔍 フォント診断ツール")
    print("=" * 60)
    
    # 診断実行
    check_system_locale()
    check_fontconfig() 
    check_tkinter_fonts()
    check_character_support()
    check_display_capability()
    
    print("\n" + "=" * 60)
    print("詳細レンダリングテストを実行しますか？ (y/N): ", end="")
    
    try:
        response = input().strip().lower()
        if response.startswith('y'):
            font_rendering_test()
    except:
        print("スキップします")
    
    print("\n🔍 診断完了")
    print("=" * 60)

if __name__ == "__main__":
    main()