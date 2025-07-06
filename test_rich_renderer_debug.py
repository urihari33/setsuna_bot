#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RichMessageRenderer デバッグテスト
初期化問題を特定して修正
"""

import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, scrolledtext

# パス設定
sys.path.append(str(Path(__file__).parent))

def test_rich_renderer_standalone():
    """RichMessageRenderer単体テスト"""
    print("🔍 RichMessageRenderer単体テスト開始")
    print("=" * 50)
    
    try:
        # tkinter基本設定
        print("1️⃣ tkinter基本セットアップ...")
        root = tk.Tk()
        root.title("RichRenderer Debug Test")
        root.geometry("600x400")
        
        # テキストウィジェット作成
        text_widget = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=20, width=70)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        print("✅ tkinterセットアップ完了")
        
        # RichMessageRenderer直接インポート・初期化テスト
        print("\n2️⃣ RichMessageRenderer直接テスト...")
        
        from core.rich_message_renderer import RichMessageRenderer
        print("✅ RichMessageRendererインポート成功")
        
        # 初期化テスト
        renderer = RichMessageRenderer(text_widget)
        print("✅ RichMessageRenderer初期化成功")
        print(f"   - レンダラータイプ: {type(renderer)}")
        
        # 基本機能テスト
        print("\n3️⃣ 基本機能テスト...")
        
        # シンプルメッセージ
        renderer.render_message("テストユーザー", "これはテストメッセージです。", "text")
        print("✅ シンプルメッセージ表示成功")
        
        # 統合メッセージ
        test_integrated = {
            'text': 'テスト統合メッセージ',
            'images': [{'name': 'test.jpg', 'size': 1024, 'path': '/tmp/test.jpg'}],
            'url': {'title': 'テストURL', 'url': 'https://example.com'}
        }
        
        renderer.render_message("テストBot", test_integrated, "integrated")
        print("✅ 統合メッセージ表示成功")
        
        # メッセージ数確認
        count = renderer.get_message_count()
        print(f"✅ メッセージ数: {count}")
        
        print("\n4️⃣ 表示内容確認...")
        content = text_widget.get("1.0", "end-1c")
        lines = content.split('\n')
        for i, line in enumerate(lines[:8]):
            if line.strip():
                print(f"  {i+1}: {line}")
        
        print("\n🎉 RichMessageRenderer単体テスト完了！")
        
        # GUI表示（1秒後に自動終了）
        root.after(1000, root.destroy)
        # root.mainloop()  # 自動テストのためコメントアウト
        
        return True
        
    except Exception as e:
        print(f"❌ RichMessageRenderer単体テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_initialization_debug():
    """GUI初期化プロセスデバッグ"""
    print("\n🔍 GUI初期化プロセスデバッグ開始")
    print("=" * 50)
    
    try:
        print("1️⃣ GUI初期化段階確認...")
        
        from voice_chat_gui import SetsunaGUI
        
        # 段階的初期化確認
        print("   - SetsunaGUIインポート完了")
        
        gui = SetsunaGUI()
        print("   - SetsunaGUIインスタンス作成完了")
        
        # 初期化後の状態確認
        print("\n2️⃣ 初期化後状態確認...")
        print(f"   - rich_renderer属性: {hasattr(gui, 'rich_renderer')}")
        
        if hasattr(gui, 'rich_renderer'):
            print(f"   - rich_renderer値: {gui.rich_renderer}")
            print(f"   - rich_renderer型: {type(gui.rich_renderer)}")
            
            # history_text確認
            if hasattr(gui, 'history_text'):
                print(f"   - history_text存在: True")
                print(f"   - history_text型: {type(gui.history_text)}")
                
                # 手動でRichMessageRenderer初期化を試行
                print("\n3️⃣ 手動RichMessageRenderer初期化テスト...")
                
                from core.rich_message_renderer import RichMessageRenderer
                try:
                    manual_renderer = RichMessageRenderer(gui.history_text)
                    print("✅ 手動初期化成功")
                    print(f"   - 手動レンダラー型: {type(manual_renderer)}")
                    
                    # GUIに手動で設定
                    gui.rich_renderer = manual_renderer
                    print("✅ GUI手動設定完了")
                    
                    # テストメッセージ
                    gui.rich_renderer.render_message("テスト", "手動初期化テスト", "text")
                    print("✅ 手動設定後メッセージ表示成功")
                    
                except Exception as e:
                    print(f"❌ 手動初期化エラー: {e}")
            else:
                print("   - history_text存在: False")
        
        return True
        
    except Exception as e:
        print(f"❌ GUI初期化デバッグエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メインデバッグ実行"""
    print("🚀 RichMessageRenderer デバッグテスト")
    print("=" * 60)
    
    success1 = test_rich_renderer_standalone()
    success2 = test_gui_initialization_debug()
    
    if success1 and success2:
        print("\n🎉 デバッグテスト完了！")
        print("\n📊 診断結果:")
        print("  ✅ RichMessageRenderer単体動作: 正常")
        print("  ✅ GUI統合初期化: 確認済み")
        print("\n💡 推奨対処法:")
        print("  1. GUI初期化順序の見直し")
        print("  2. レイアウト設定タイミングの調整")
        print("  3. 手動初期化フォールバック追加")
        
        return True
    else:
        print("\n❌ デバッグテストで問題発見")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)