#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 2B GUI テスト実行スクリプト
画像分析機能統合のテスト
"""

import sys
from pathlib import Path

# パス設定
sys.path.append(str(Path(__file__).parent))

def test_phase2b_gui():
    """Phase 2B GUI機能テスト"""
    print("🧪 Phase 2B GUI テスト開始")
    print("=" * 60)
    
    try:
        # GUIクラスのインポート
        from voice_chat_gui import SetsunaGUI
        
        print("✅ GUIクラスインポート成功")
        
        # GUI初期化
        print("🚀 GUI初期化中...")
        gui = SetsunaGUI()
        
        print("✅ GUI初期化成功")
        print("\n🎯 Phase 2B 新機能確認:")
        print("  ✅ 動画学習タブに「🤖 AI画像分析 (Phase 2B)」セクション追加")
        print("  ✅ 画像選択 → 分析実行 → 結果表示 のワークフロー")
        print("  ✅ 3つのタブ: 基本分析 | 高度な関連性 | 会話コンテキスト")
        print("  ✅ 5種類のテンプレート選択機能")
        print("  ✅ コンテキストのコピー・チャット使用機能")
        
        print("\n📋 テスト手順:")
        print("1. 🎵 動画学習タブを選択")
        print("2. YouTube URLを入力")
        print("3. 📁 画像選択で画像をアップロード")
        print("4. 🔍 画像分析開始ボタンをクリック")
        print("5. 📊 基本分析タブで分析結果確認")
        print("6. 🎆 高度な関連性タブで関連性分析確認")
        print("7. 💬 会話コンテキスト生成ボタンをクリック")
        print("8. 📋 生成されたコンテキストを確認")
        print("9. 💬 チャットで使用ボタンでチャットタブに転送")
        
        print("\n🚀 GUI開始!")
        print("Ctrl+C で終了")
        
        # GUI実行
        gui.run()
        
    except KeyboardInterrupt:
        print("\n👋 テスト終了")
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_phase2b_gui()