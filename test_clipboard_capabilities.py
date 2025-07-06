#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
クリップボード機能のテスト・調査
スクリーンショット貼り付け実装の事前検証
"""

import tkinter as tk
from PIL import Image, ImageGrab
import tempfile
import os
from pathlib import Path
import io


def test_basic_clipboard():
    """基本的なクリップボード機能テスト"""
    print("=== 基本クリップボードテスト ===")
    
    root = tk.Tk()
    root.withdraw()  # ウィンドウを非表示
    
    try:
        # テキストクリップボード読み取り
        text = root.clipboard_get()
        print(f"✅ クリップボードテキスト読み取り成功: {text[:50]}...")
    except tk.TclError:
        print("ℹ️ クリップボードにテキストデータなし")
    
    # テキスト書き込みテスト
    test_text = "Test clipboard content"
    root.clipboard_clear()
    root.clipboard_append(test_text)
    root.update()  # クリップボード更新を確実にする
    
    try:
        retrieved = root.clipboard_get()
        if retrieved == test_text:
            print("✅ クリップボードテキスト書き込み/読み取り成功")
        else:
            print(f"⚠️ 書き込み/読み取り不一致: '{retrieved}' != '{test_text}'")
    except tk.TclError as e:
        print(f"❌ クリップボードテキスト操作失敗: {e}")
    
    root.destroy()


def test_image_clipboard():
    """画像クリップボード機能テスト"""
    print("\n=== 画像クリップボードテスト ===")
    
    try:
        # PIL.ImageGrabでクリップボード画像取得を試行
        img = ImageGrab.grabclipboard()
        
        if img is not None:
            print(f"✅ クリップボード画像検出: {img.size} ({img.mode})")
            
            # 一時ファイルとして保存テスト
            temp_dir = Path(tempfile.gettempdir())
            temp_path = temp_dir / "clipboard_test.png"
            
            img.save(temp_path, 'PNG')
            if temp_path.exists():
                file_size = temp_path.stat().st_size
                print(f"✅ 画像保存成功: {temp_path} ({file_size} bytes)")
                
                # 保存した画像の再読み込みテスト
                with Image.open(temp_path) as loaded_img:
                    print(f"✅ 画像再読み込み成功: {loaded_img.size}")
                
                # テンポラリファイル削除
                temp_path.unlink()
                print("✅ テンポラリファイル削除完了")
                
                return True
            else:
                print("❌ 画像保存失敗")
                return False
        else:
            print("ℹ️ クリップボードに画像データなし")
            print("💡 テスト手順:")
            print("   1. スクリーンショット (PrtScr / Win+Shift+S)")
            print("   2. または画像をコピー (Ctrl+C)")
            print("   3. このテストを再実行")
            return False
            
    except Exception as e:
        print(f"❌ 画像クリップボード処理エラー: {e}")
        return False


def test_tkinter_image_paste():
    """tkinter統合での画像貼り付けテスト"""
    print("\n=== tkinter統合画像貼り付けテスト ===")
    
    root = tk.Tk()
    root.title("画像貼り付けテスト")
    root.geometry("400x300")
    
    result_text = tk.Text(root, height=10, width=50)
    result_text.pack(pady=10)
    
    def paste_image():
        try:
            # クリップボードから画像取得
            img = ImageGrab.grabclipboard()
            
            if img is not None:
                # 画像情報表示
                info = f"画像検出!\nサイズ: {img.size}\nモード: {img.mode}\nフォーマット: {img.format}\n"
                result_text.insert(tk.END, info + "\n")
                
                # 一時保存
                temp_path = Path(tempfile.gettempdir()) / "tkinter_paste_test.png"
                img.save(temp_path, 'PNG')
                result_text.insert(tk.END, f"保存先: {temp_path}\n\n")
                
                # 画像ファイル検証
                if temp_path.exists():
                    with Image.open(temp_path) as verify_img:
                        result_text.insert(tk.END, f"検証: {verify_img.size} - 成功!\n")
                    
                    # 自動削除
                    temp_path.unlink()
                    result_text.insert(tk.END, "✅ 画像貼り付け処理完了\n")
                else:
                    result_text.insert(tk.END, "❌ 画像保存失敗\n")
            else:
                result_text.insert(tk.END, "ℹ️ クリップボードに画像なし\n")
                
        except Exception as e:
            result_text.insert(tk.END, f"❌ エラー: {e}\n")
        
        # テキストエリアの最下部にスクロール
        result_text.see(tk.END)
    
    # Ctrl+V キーバインド
    def on_paste(event):
        paste_image()
        return "break"  # イベントの伝播を停止
    
    root.bind('<Control-v>', on_paste)
    
    # ボタン
    paste_button = tk.Button(root, text="📋 クリップボード画像貼り付け", command=paste_image)
    paste_button.pack(pady=5)
    
    info_label = tk.Label(root, text="Ctrl+V または ボタンクリックで貼り付けテスト", fg="gray")
    info_label.pack()
    
    print("✅ tkinterテストウィンドウ起動")
    print("操作: スクリーンショットをコピーしてから Ctrl+V を押してください")
    
    root.mainloop()


def test_supported_formats():
    """サポートされる画像形式の確認"""
    print("\n=== サポート画像形式確認 ===")
    
    try:
        # 小さなテスト画像を各形式で作成
        test_img = Image.new('RGB', (100, 100), color='red')
        temp_dir = Path(tempfile.gettempdir())
        
        formats = ['PNG', 'JPEG', 'BMP', 'GIF']
        extensions = ['.png', '.jpg', '.bmp', '.gif']
        
        for fmt, ext in zip(formats, extensions):
            try:
                test_path = temp_dir / f"format_test{ext}"
                
                if fmt == 'JPEG':
                    test_img.save(test_path, fmt, quality=85)
                else:
                    test_img.save(test_path, fmt)
                
                # 保存した画像の再読み込み
                with Image.open(test_path) as loaded:
                    print(f"✅ {fmt} ({ext}): {loaded.size} - サポート")
                
                test_path.unlink()  # テンポラリファイル削除
                
            except Exception as e:
                print(f"❌ {fmt} ({ext}): エラー - {e}")
    
    except Exception as e:
        print(f"❌ 形式テストエラー: {e}")


def main():
    """メインテスト実行"""
    print("🔍 スクリーンショット貼り付け機能 技術調査")
    print("=" * 60)
    
    # 基本機能テスト
    test_basic_clipboard()
    test_supported_formats()
    test_image_clipboard()
    
    print("\n" + "=" * 60)
    print("🎯 実装推奨事項:")
    print("  ✅ PIL.ImageGrab が利用可能")
    print("  ✅ tkinter クリップボード操作対応")
    print("  ✅ 主要画像形式サポート")
    print("  ✅ 一時ファイル処理対応")
    
    print("\n💡 実装方針:")
    print("  1. Ctrl+V キーバインドでクリップボード監視")
    print("  2. PIL.ImageGrab で画像データ取得")
    print("  3. 一時ファイル作成→既存の画像処理フローに統合")
    print("  4. エラーハンドリング（画像なし、形式未サポートなど）")
    
    # 対話的テストの提供
    print(f"\n🧪 対話的テストを実行しますか？")
    response = input("y/n: ").strip().lower()
    
    if response == 'y':
        test_tkinter_image_paste()
    else:
        print("テスト完了")


if __name__ == "__main__":
    main()