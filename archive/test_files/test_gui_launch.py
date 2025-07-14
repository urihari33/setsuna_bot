#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI起動テスト
Phase 2C GUI動作確認
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_gui_launch():
    """GUI起動テスト"""
    try:
        print("=== Phase 2C GUI起動テスト ===")
        
        # 1. 依存関係チェック
        print("\n🔍 1. 依存関係チェック:")
        
        try:
            import tkinter as tk
            from tkinter import ttk
            print("✅ tkinter: 利用可能")
        except ImportError as e:
            print(f"❌ tkinter: 利用不可 - {e}")
            return False
        
        try:
            import threading
            import queue
            print("✅ threading, queue: 利用可能")
        except ImportError as e:
            print(f"❌ threading, queue: 利用不可 - {e}")
            return False
        
        # 2. コアモジュールインポートチェック
        print("\n🔍 2. コアモジュールインポートチェック:")
        
        try:
            from core.activity_learning_engine import ActivityLearningEngine
            print("✅ ActivityLearningEngine: インポート成功")
        except ImportError as e:
            print(f"❌ ActivityLearningEngine: インポート失敗 - {e}")
            return False
        
        try:
            from core.activity_proposal_engine import ActivityProposalEngine
            print("✅ ActivityProposalEngine: インポート成功")
        except ImportError as e:
            print(f"❌ ActivityProposalEngine: インポート失敗 - {e}")
            return False
        
        try:
            from core.knowledge_integration_system import KnowledgeIntegrationSystem
            print("✅ KnowledgeIntegrationSystem: インポート成功")
        except ImportError as e:
            print(f"❌ KnowledgeIntegrationSystem: インポート失敗 - {e}")
            return False
        
        try:
            from core.conversation_knowledge_provider import ConversationKnowledgeProvider
            print("✅ ConversationKnowledgeProvider: インポート成功")
        except ImportError as e:
            print(f"❌ ConversationKnowledgeProvider: インポート失敗 - {e}")
            return False
        
        try:
            from core.budget_safety_manager import BudgetSafetyManager
            print("✅ BudgetSafetyManager: インポート成功")
        except ImportError as e:
            print(f"❌ BudgetSafetyManager: インポート失敗 - {e}")
            return False
        
        # 3. GUIモジュールインポートチェック
        print("\n🔍 3. GUIモジュールインポートチェック:")
        
        try:
            from gui.learning_session_gui import LearningSessionGUI
            print("✅ LearningSessionGUI: インポート成功")
        except ImportError as e:
            print(f"❌ LearningSessionGUI: インポート失敗 - {e}")
            return False
        
        # 4. GUI初期化テスト
        print("\n🔍 4. GUI初期化テスト:")
        
        try:
            # テスト用のTkinterルートウィンドウ作成
            root = tk.Tk()
            root.withdraw()  # 表示しない
            
            # GUIクラス初期化（実際のGUI表示は行わない）
            print("  GUI初期化中...")
            
            # 初期化のコアコンポーネントのみテスト
            learning_engine = ActivityLearningEngine()
            proposal_engine = ActivityProposalEngine()
            integration_system = KnowledgeIntegrationSystem()
            conversation_provider = ConversationKnowledgeProvider()
            budget_manager = BudgetSafetyManager()
            
            print("✅ GUI初期化成功")
            print("  - ActivityLearningEngine: 初期化完了")
            print("  - ActivityProposalEngine: 初期化完了")
            print("  - KnowledgeIntegrationSystem: 初期化完了")
            print("  - ConversationKnowledgeProvider: 初期化完了")
            print("  - BudgetSafetyManager: 初期化完了")
            
            # クリーンアップ
            root.destroy()
            
        except Exception as e:
            print(f"❌ GUI初期化失敗: {e}")
            return False
        
        # 5. データディレクトリ作成チェック
        print("\n🔍 5. データディレクトリ作成チェック:")
        
        try:
            # Windows環境のパス設定
            if os.name == 'nt':
                gui_data_dir = Path("D:/setsuna_bot/data/gui")
            else:
                gui_data_dir = Path("/mnt/d/setsuna_bot/data/gui")
            
            gui_data_dir.mkdir(parents=True, exist_ok=True)
            
            if gui_data_dir.exists():
                print(f"✅ データディレクトリ作成成功: {gui_data_dir}")
            else:
                print(f"❌ データディレクトリ作成失敗: {gui_data_dir}")
                return False
                
        except Exception as e:
            print(f"❌ データディレクトリ作成失敗: {e}")
            return False
        
        # 6. 実際のGUI起動テスト（短時間）
        print("\n🔍 6. 実際のGUI起動テスト:")
        
        try:
            print("  GUI起動中... (3秒後に自動終了)")
            
            # 実際のGUI起動
            gui = LearningSessionGUI()
            
            # 3秒後に自動終了
            def auto_close():
                gui.root.after(3000, gui.root.quit)
            
            auto_close()
            gui.root.mainloop()
            
            print("✅ GUI起動テスト成功")
            
        except Exception as e:
            print(f"❌ GUI起動テスト失敗: {e}")
            return False
        
        print("\n" + "="*50)
        print("🎉 Phase 2C GUI起動テスト完了")
        print("="*50)
        print("✅ 全ての依存関係が正常に動作しています")
        print("✅ GUI起動準備が完了しました")
        print("")
        print("💡 GUI起動方法:")
        print("   python gui/learning_session_gui.py")
        print("")
        print("📋 実装された機能:")
        print("   🎓 セッション管理: 新規作成・開始・停止・履歴表示")
        print("   📊 リアルタイム監視: 進捗・統計・ログ表示")
        print("   💡 活動提案: 提案生成・一覧表示・詳細表示")
        print("   🧠 知識統合: 統合実行・知識一覧・詳細表示")
        print("   💰 予算管理: 制限設定・使用状況・履歴表示")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ GUI起動テスト中断: {e}")
        return False


if __name__ == "__main__":
    success = test_gui_launch()
    sys.exit(0 if success else 1)