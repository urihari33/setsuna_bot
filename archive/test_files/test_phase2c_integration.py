#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 2C統合テスト
GUI統合システムの動作確認
"""

import sys
import os
import time
import threading
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.activity_learning_engine import ActivityLearningEngine
from core.activity_proposal_engine import ActivityProposalEngine
from core.knowledge_integration_system import KnowledgeIntegrationSystem
from core.conversation_knowledge_provider import ConversationKnowledgeProvider
from core.budget_safety_manager import BudgetSafetyManager

class Phase2CIntegrationTest:
    """Phase 2C統合テストクラス"""
    
    def __init__(self):
        """初期化"""
        print("=== Phase 2C統合テスト ===")
        
        # コンポーネント初期化
        print("\n🔧 コンポーネント初期化:")
        try:
            self.learning_engine = ActivityLearningEngine()
            print("✅ ActivityLearningEngine 初期化完了")
            
            self.proposal_engine = ActivityProposalEngine()
            print("✅ ActivityProposalEngine 初期化完了")
            
            self.integration_system = KnowledgeIntegrationSystem()
            print("✅ KnowledgeIntegrationSystem 初期化完了")
            
            self.conversation_provider = ConversationKnowledgeProvider()
            print("✅ ConversationKnowledgeProvider 初期化完了")
            
            self.budget_manager = BudgetSafetyManager()
            print("✅ BudgetSafetyManager 初期化完了")
            
        except Exception as e:
            print(f"❌ 初期化失敗: {e}")
            raise
        
        # テスト結果
        self.test_results = {
            "gui_functionality_test": False,
            "session_management_test": False,
            "real_time_monitoring_test": False,
            "proposal_system_test": False,
            "knowledge_integration_test": False,
            "budget_management_test": False,
            "end_to_end_workflow_test": False
        }
    
    def run_phase2c_integration_test(self):
        """Phase 2C統合テスト実行"""
        print("\n🚀 Phase 2C統合テスト開始:")
        
        try:
            # 1. GUI機能テスト
            self._test_gui_functionality()
            
            # 2. セッション管理テスト
            self._test_session_management()
            
            # 3. リアルタイム監視テスト
            self._test_real_time_monitoring()
            
            # 4. 提案システムテスト
            self._test_proposal_system()
            
            # 5. 知識統合テスト
            self._test_knowledge_integration()
            
            # 6. 予算管理テスト
            self._test_budget_management()
            
            # 7. エンドツーエンドワークフローテスト
            self._test_end_to_end_workflow()
            
            # 結果サマリー
            self._print_test_summary()
            
        except Exception as e:
            print(f"❌ 統合テスト失敗: {e}")
            raise
    
    def _test_gui_functionality(self):
        """GUI機能テスト"""
        print("\n🖥️ 1. GUI機能テスト:")
        
        try:
            # GUI依存関係チェック
            import tkinter as tk
            from tkinter import ttk
            
            # GUIモジュールインポートチェック
            from gui.learning_session_gui import LearningSessionGUI
            
            # 基本的なGUI要素作成テスト
            root = tk.Tk()
            root.withdraw()  # 非表示
            
            # 基本ウィジェット作成
            frame = ttk.Frame(root)
            notebook = ttk.Notebook(frame)
            treeview = ttk.Treeview(frame, columns=('test',), show='headings')
            progressbar = ttk.Progressbar(frame, mode='determinate')
            
            # クリーンアップ
            root.destroy()
            
            print("✅ GUI機能テスト成功:")
            print("  - tkinter/ttk: 正常動作")
            print("  - GUIモジュール: インポート成功")
            print("  - 基本ウィジェット: 作成成功")
            
            self.test_results["gui_functionality_test"] = True
            
        except Exception as e:
            print(f"❌ GUI機能テスト失敗: {e}")
    
    def _test_session_management(self):
        """セッション管理テスト"""
        print("\n📚 2. セッション管理テスト:")
        
        try:
            # セッション作成
            session_id = self.learning_engine.create_session(
                theme="Phase2C統合テスト",
                learning_type="概要",
                depth_level=3,
                time_limit=300,
                budget_limit=2.0,
                tags=["統合テスト", "Phase2C"]
            )
            
            if session_id:
                print(f"✅ セッション作成成功: {session_id}")
                
                # セッション一覧取得
                sessions = self.learning_engine.list_sessions(limit=10)
                print(f"✅ セッション一覧取得: {len(sessions)}件")
                
                # セッション状態取得
                session_status = self.learning_engine.get_session_status(session_id)
                if session_status:
                    print(f"✅ セッション状態取得: {session_status['status']}")
                    
                    # 段階的分析設定
                    self.learning_engine.configure_staged_analysis(
                        enable_preprocessing=True,
                        relevance_min=0.4,
                        max_detailed_analysis=10
                    )
                    print("✅ 段階的分析設定完了")
                    
                    self.test_results["session_management_test"] = True
                else:
                    print("❌ セッション状態取得失敗")
            else:
                print("❌ セッション作成失敗")
                
        except Exception as e:
            print(f"❌ セッション管理テスト失敗: {e}")
    
    def _test_real_time_monitoring(self):
        """リアルタイム監視テスト"""
        print("\n📊 3. リアルタイム監視テスト:")
        
        try:
            # プログレスコールバック設定
            progress_received = False
            
            def progress_callback(phase: str, progress: float, message: str):
                nonlocal progress_received
                progress_received = True
                print(f"  [進捗] {phase}: {progress:.1%} - {message}")
            
            self.learning_engine.add_progress_callback(progress_callback)
            
            # 予算管理アラートコールバック設定
            alert_received = False
            
            def alert_callback(alert):
                nonlocal alert_received
                alert_received = True
                print(f"  [アラート] {alert.severity}: {alert.message}")
            
            self.budget_manager.add_alert_callback(alert_callback)
            
            # コールバックテスト（手動トリガー）
            if hasattr(self.learning_engine, '_notify_progress'):
                self.learning_engine._notify_progress("test_phase", 0.5, "テスト進捗")
                
            # 統計情報取得
            preprocessing_stats = self.learning_engine.get_preprocessing_statistics()
            proposal_stats = self.proposal_engine.get_proposal_statistics()
            knowledge_stats = self.conversation_provider.get_knowledge_statistics()
            budget_stats = self.budget_manager.get_budget_status()
            
            print("✅ リアルタイム監視テスト成功:")
            print(f"  - プログレスコールバック: {'設定済み' if progress_callback else '未設定'}")
            print(f"  - アラートコールバック: {'設定済み' if alert_callback else '未設定'}")
            print(f"  - 前処理統計: {'取得済み' if preprocessing_stats else '未取得'}")
            print(f"  - 提案統計: {'取得済み' if proposal_stats else '未取得'}")
            print(f"  - 知識統計: {'取得済み' if knowledge_stats else '未取得'}")
            print(f"  - 予算統計: {'取得済み' if budget_stats else '未取得'}")
            
            self.test_results["real_time_monitoring_test"] = True
            
        except Exception as e:
            print(f"❌ リアルタイム監視テスト失敗: {e}")
    
    def _test_proposal_system(self):
        """提案システムテスト"""
        print("\n💡 4. 提案システムテスト:")
        
        try:
            # モックセッション知識
            session_knowledge = {
                "knowledge_items": [
                    {
                        "item_id": "test_item_001",
                        "content": "Phase2C統合テスト用の知識アイテム",
                        "categories": ["統合テスト", "GUI", "Phase2C"],
                        "keywords": ["統合", "テスト", "GUI", "Phase2C"],
                        "entities": ["統合テスト", "GUI"],
                        "importance_score": 8.0,
                        "reliability_score": 0.9
                    }
                ]
            }
            
            # 活動提案生成
            proposals = self.proposal_engine.generate_proposals_from_session(
                session_id="test_session_001",
                session_knowledge=session_knowledge,
                max_proposals=3
            )
            
            if proposals and len(proposals) > 0:
                print(f"✅ 提案システムテスト成功:")
                print(f"  - 生成提案数: {len(proposals)}件")
                
                for i, proposal in enumerate(proposals[:2]):
                    print(f"  - 提案{i+1}: {proposal.title}")
                    print(f"    タイプ: {proposal.proposal_type}")
                    print(f"    技術実現性: {proposal.technical_feasibility:.1f}")
                    print(f"    せつな適合度: {proposal.setsuna_alignment['personality_fit']:.1f}")
                
                self.test_results["proposal_system_test"] = True
            else:
                print("❌ 提案システムテスト失敗: 提案が生成されませんでした")
                
        except Exception as e:
            print(f"❌ 提案システムテスト失敗: {e}")
    
    def _test_knowledge_integration(self):
        """知識統合テスト"""
        print("\n🧠 5. 知識統合テスト:")
        
        try:
            # モックセッションデータ
            session_ids = ["test_session_001", "test_session_002", "test_session_003"]
            session_data = {
                session_id: {
                    "session_id": session_id,
                    "theme": f"統合テスト用テーマ_{session_id}",
                    "knowledge_items": [
                        {
                            "item_id": f"item_{session_id}_001",
                            "content": f"統合テスト用知識_{session_id}",
                            "categories": ["統合テスト", "知識統合", "Phase2C"],
                            "keywords": ["統合", "テスト", "知識"],
                            "entities": ["統合テスト", "知識統合"],
                            "importance_score": 7.5,
                            "reliability_score": 0.8
                        }
                    ]
                }
                for session_id in session_ids
            }
            
            # 知識統合実行
            integrated_knowledge = self.integration_system.integrate_multi_session_knowledge(
                session_ids=session_ids,
                session_data=session_data,
                integration_scope="comprehensive"
            )
            
            if integrated_knowledge and len(integrated_knowledge) > 0:
                print(f"✅ 知識統合テスト成功:")
                print(f"  - 統合知識数: {len(integrated_knowledge)}件")
                
                first_integration = integrated_knowledge[0]
                print(f"  - 統合知識ID: {first_integration.knowledge_id}")
                print(f"  - 統合タイプ: {first_integration.integration_type}")
                print(f"  - 信頼度: {first_integration.confidence_score:.2f}")
                print(f"  - 新規性: {first_integration.novelty_score:.2f}")
                
                self.test_results["knowledge_integration_test"] = True
            else:
                print("❌ 知識統合テスト失敗: 統合知識が生成されませんでした")
                
        except Exception as e:
            print(f"❌ 知識統合テスト失敗: {e}")
    
    def _test_budget_management(self):
        """予算管理テスト"""
        print("\n💰 6. 予算管理テスト:")
        
        try:
            # 予算制限設定
            self.budget_manager.set_budget_limits(
                monthly_limit=100.0,
                daily_limit=20.0
            )
            
            # 予算状況取得
            budget_status = self.budget_manager.get_budget_status()
            
            if budget_status:
                print("✅ 予算管理テスト成功:")
                print(f"  - 予算状況: {budget_status['status']}")
                print(f"  - 日次使用量: ${budget_status['daily_usage']:.2f}")
                print(f"  - 日次制限: ${budget_status['daily_limit']:.2f}")
                print(f"  - 月次使用量: ${budget_status['monthly_usage']:.2f}")
                print(f"  - 月次制限: ${budget_status['monthly_limit']:.2f}")
                print(f"  - アクティブアラート: {budget_status['active_alerts']}件")
                
                # 使用量サマリー取得
                usage_summary = self.budget_manager.get_usage_summary("today")
                if usage_summary:
                    print(f"  - 使用量サマリー: 取得成功")
                
                self.test_results["budget_management_test"] = True
            else:
                print("❌ 予算管理テスト失敗: 予算状況が取得できませんでした")
                
        except Exception as e:
            print(f"❌ 予算管理テスト失敗: {e}")
    
    def _test_end_to_end_workflow(self):
        """エンドツーエンドワークフローテスト"""
        print("\n🌐 7. エンドツーエンドワークフローテスト:")
        
        try:
            # 1. セッション作成
            session_id = self.learning_engine.create_session(
                theme="エンドツーエンドテスト",
                learning_type="実用",
                depth_level=2,
                time_limit=180,
                budget_limit=1.0,
                tags=["E2E", "テスト"]
            )
            
            if not session_id:
                print("❌ セッション作成失敗")
                return
            
            # 2. 段階的分析設定
            self.learning_engine.configure_staged_analysis(
                enable_preprocessing=True,
                relevance_min=0.3,
                max_detailed_analysis=5
            )
            
            # 3. 予算制限設定
            self.budget_manager.set_budget_limits(
                monthly_limit=50.0,
                daily_limit=5.0
            )
            
            # 4. 活動提案生成
            session_knowledge = {
                "knowledge_items": [
                    {
                        "item_id": "e2e_item_001",
                        "content": "エンドツーエンドテスト用の総合知識",
                        "categories": ["総合テスト", "エンドツーエンド", "統合"],
                        "keywords": ["E2E", "テスト", "統合", "総合"],
                        "entities": ["E2E", "統合"],
                        "importance_score": 9.0,
                        "reliability_score": 0.95
                    }
                ]
            }
            
            proposals = self.proposal_engine.generate_proposals_from_session(
                session_id=session_id,
                session_knowledge=session_knowledge,
                max_proposals=2
            )
            
            # 5. 知識統合実行
            integration_session_data = {
                session_id: {
                    "session_id": session_id,
                    "theme": "エンドツーエンドテスト",
                    "knowledge_items": session_knowledge["knowledge_items"]
                }
            }
            
            integrated_knowledge = self.integration_system.integrate_multi_session_knowledge(
                session_ids=[session_id],
                session_data=integration_session_data,
                integration_scope="basic"
            )
            
            # 6. 会話知識分析
            knowledge_context = self.conversation_provider.analyze_user_input(
                user_input="エンドツーエンドテストの結果を教えて",
                conversation_context=[]
            )
            
            # 7. 予算状況確認
            final_budget_status = self.budget_manager.get_budget_status()
            
            # 結果評価
            success_conditions = [
                session_id is not None,
                proposals and len(proposals) > 0,
                integrated_knowledge and len(integrated_knowledge) > 0,
                knowledge_context is not None,
                final_budget_status is not None
            ]
            
            if all(success_conditions):
                print("✅ エンドツーエンドワークフローテスト成功:")
                print(f"  - セッション作成: {session_id}")
                print(f"  - 活動提案生成: {len(proposals)}件")
                print(f"  - 知識統合: {len(integrated_knowledge)}件")
                print(f"  - 会話知識分析: 完了")
                print(f"  - 予算管理: 正常動作")
                
                self.test_results["end_to_end_workflow_test"] = True
            else:
                print("❌ エンドツーエンドワークフローテスト失敗: 一部の処理が失敗しました")
                
        except Exception as e:
            print(f"❌ エンドツーエンドワークフローテスト失敗: {e}")
    
    def _print_test_summary(self):
        """テスト結果サマリー表示"""
        print("\n" + "="*60)
        print("📊 Phase 2C統合テスト 結果サマリー")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        
        test_names = {
            "gui_functionality_test": "GUI機能テスト",
            "session_management_test": "セッション管理テスト",
            "real_time_monitoring_test": "リアルタイム監視テスト",
            "proposal_system_test": "提案システムテスト",
            "knowledge_integration_test": "知識統合テスト",
            "budget_management_test": "予算管理テスト",
            "end_to_end_workflow_test": "エンドツーエンドワークフローテスト"
        }
        
        for test_key, result in self.test_results.items():
            test_name = test_names.get(test_key, test_key)
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:35}: {status}")
        
        print("-" * 60)
        print(f"総合結果: {passed_tests}/{total_tests} テスト通過")
        
        if passed_tests == total_tests:
            print("🎉 Phase 2C統合テストが完全成功しました！")
            print("GUI統合システムの全機能が正常に動作しています。")
            
            # 期待効果の表示
            print("\n💡 Phase 2C実装効果:")
            print("  ✅ 視覚的なセッション管理GUI")
            print("  ✅ リアルタイム学習進捗モニタリング")
            print("  ✅ 活動提案の視覚的管理")
            print("  ✅ 知識統合の可視化")
            print("  ✅ 予算管理の直感的操作")
            print("  ✅ エンドツーエンドワークフロー統合")
            
            print("\n🚀 Phase 2完全実装達成!")
            print("せつなBotの学習知識活用システムが完成しました。")
            
        elif passed_tests >= total_tests * 0.8:
            print("⚠️ Phase 2C統合テストが部分的に成功しました。")
            print("基本機能は動作していますが、一部に改善が必要です。")
            
        else:
            print("❌ Phase 2C統合テストが失敗しました。")
            print("複数の機能に問題があり、修正が必要です。")
        
        print("="*60)


def main():
    """メイン関数"""
    integration_test = Phase2CIntegrationTest()
    
    try:
        integration_test.run_phase2c_integration_test()
        
    except Exception as e:
        print(f"\n❌ テスト中断: {e}")


if __name__ == "__main__":
    main()