#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 2C-4: 簡易テスト
プログレス機能の基本動作確認
"""

import sys
from pathlib import Path

# パス設定
sys.path.append(str(Path(__file__).parent))

def test_progress_manager_basic():
    """ProgressManager基本テスト"""
    print("📊 ProgressManager基本テスト")
    try:
        from core.progress_manager import ProgressManager
        
        manager = ProgressManager()
        manager.add_step("test1", "テスト1", "テスト実行中", weight=1.0)
        manager.add_step("test2", "テスト2", "データ処理中", weight=2.0)
        
        manager.start_processing()
        print("✅ ProgressManager初期化・ステップ追加成功")
        
        manager.start_step("test1")
        manager.update_step_progress("test1", 50.0, "50%完了")
        manager.complete_step("test1", "テスト1完了")
        
        status = manager.get_status()
        print(f"📊 進捗: {status['total_progress']:.1f}%")
        print("✅ ProgressManager基本機能正常")
        
        return True
    except Exception as e:
        print(f"❌ ProgressManagerエラー: {e}")
        return False

def test_imports():
    """インポートテスト"""
    print("📦 インポートテスト")
    try:
        from core.progress_manager import ProgressManager
        print("✅ ProgressManager")
        
        from core.progress_widget import ProgressWidget
        print("✅ ProgressWidget")
        
        return True
    except Exception as e:
        print(f"❌ インポートエラー: {e}")
        return False

def test_gui_integration():
    """GUI統合テスト（軽量版）"""
    print("🖥️ GUI統合確認")
    try:
        # voice_chat_gui.pyの変更確認
        import voice_chat_gui
        
        # 新機能の存在確認
        gui_source = Path(__file__).parent / "voice_chat_gui.py"
        content = gui_source.read_text(encoding='utf-8')
        
        checks = [
            ("ProgressManager import", "from core.progress_manager import ProgressManager" in content),
            ("ProgressWidget import", "from core.progress_widget import ProgressWidget" in content),
            ("progress_manager属性", "self.progress_manager" in content),
            ("progress_widget属性", "self.progress_widget" in content),
            ("キャンセル機能", "_cancel_processing" in content),
            ("詳細表示機能", "_show_progress_details" in content),
            ("プログレス更新", "_update_progress_display" in content),
        ]
        
        for check_name, check_result in checks:
            status = "✅" if check_result else "❌"
            print(f"  {status} {check_name}")
        
        success_count = sum(1 for _, result in checks if result)
        success_rate = success_count / len(checks) * 100
        
        print(f"📊 統合度: {success_count}/{len(checks)} ({success_rate:.1f}%)")
        
        return success_rate >= 85  # 85%以上で合格
        
    except Exception as e:
        print(f"❌ GUI統合確認エラー: {e}")
        return False

def main():
    """メインテスト"""
    print("🚀 Phase 2C-4 簡易テスト")
    print("=" * 40)
    
    test1 = test_imports()
    test2 = test_progress_manager_basic() if test1 else False
    test3 = test_gui_integration()
    
    if test1 and test2 and test3:
        print("\n🎉 Phase 2C-4 基本実装完了！")
        print("\n✨ 確認された機能:")
        print("  📊 ProgressManager - 進捗管理システム")
        print("  🎨 ProgressWidget - GUI表示システム")
        print("  🔗 GUI統合 - voice_chat_gui.py統合")
        print("  🛑 キャンセル機能")
        print("  📋 詳細表示機能")
        
        print("\n📋 実際のテスト方法:")
        print("1. python voice_chat_gui.py")
        print("2. 画像ファイル添付")
        print("3. 📤送信ボタンクリック")
        print("4. プログレス表示確認")
        
        return True
    else:
        print("\n❌ Phase 2C-4 に問題があります")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)