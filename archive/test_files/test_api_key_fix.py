#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI API Key修正テスト
全コンポーネントのAPI Key設定確認
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class APIKeyFixTest:
    """API Key修正テストクラス"""
    
    def __init__(self):
        """初期化"""
        print("=== OpenAI API Key修正テスト ===")
        self.test_results = {
            "learning_engine_api_test": False,
            "preprocessing_engine_api_test": False,
            "proposal_engine_api_test": False,
            "integration_system_api_test": False,
            "gui_api_check_test": False
        }
    
    def run_api_key_tests(self):
        """API Key修正テスト実行"""
        print("\n🔑 API Key修正テスト開始:")
        
        try:
            # 1. ActivityLearningEngine APIテスト
            self._test_learning_engine_api()
            
            # 2. PreprocessingEngine APIテスト
            self._test_preprocessing_engine_api()
            
            # 3. ActivityProposalEngine APIテスト
            self._test_proposal_engine_api()
            
            # 4. KnowledgeIntegrationSystem APIテスト
            self._test_integration_system_api()
            
            # 5. GUI API Key確認テスト
            self._test_gui_api_check()
            
            # 結果サマリー
            self._print_test_summary()
            
        except Exception as e:
            print(f"❌ API Keyテスト失敗: {e}")
            raise
    
    def _test_learning_engine_api(self):
        """ActivityLearningEngine APIテスト"""
        print("\n📚 1. ActivityLearningEngine APIテスト:")
        
        try:
            from core.activity_learning_engine import ActivityLearningEngine
            
            # インスタンス作成
            engine = ActivityLearningEngine()
            
            # API設定確認
            api_configured = engine.openai_client is not None
            
            print(f"✅ ActivityLearningEngine API設定: {'成功' if api_configured else '失敗'}")
            
            # 前処理エンジン確認
            preprocessing_configured = engine.preprocessing_engine.openai_client is not None
            print(f"✅ PreProcessingEngine API設定: {'成功' if preprocessing_configured else '失敗'}")
            
            # 統計情報取得テスト
            stats = engine.get_preprocessing_statistics()
            print(f"✅ 前処理統計情報取得: {'成功' if stats else '失敗'}")
            
            self.test_results["learning_engine_api_test"] = api_configured and preprocessing_configured
            
        except Exception as e:
            print(f"❌ ActivityLearningEngine APIテスト失敗: {e}")
    
    def _test_preprocessing_engine_api(self):
        """PreprocessingEngine APIテスト"""
        print("\n🔄 2. PreprocessingEngine APIテスト:")
        
        try:
            from core.preprocessing_engine import PreProcessingEngine
            
            # インスタンス作成
            engine = PreProcessingEngine()
            
            # API設定確認
            api_configured = engine.openai_client is not None
            
            print(f"✅ PreProcessingEngine API設定: {'成功' if api_configured else '失敗'}")
            
            # 統計情報取得テスト
            stats = engine.get_statistics()
            print(f"✅ 統計情報取得: {'成功' if stats else '失敗'}")
            
            self.test_results["preprocessing_engine_api_test"] = api_configured
            
        except Exception as e:
            print(f"❌ PreprocessingEngine APIテスト失敗: {e}")
    
    def _test_proposal_engine_api(self):
        """ActivityProposalEngine APIテスト"""
        print("\n💡 3. ActivityProposalEngine APIテスト:")
        
        try:
            from core.activity_proposal_engine import ActivityProposalEngine
            
            # インスタンス作成
            engine = ActivityProposalEngine()
            
            # API設定確認
            api_configured = engine.openai_client is not None
            
            print(f"✅ ActivityProposalEngine API設定: {'成功' if api_configured else '失敗'}")
            
            # 統計情報取得テスト
            stats = engine.get_proposal_statistics()
            print(f"✅ 提案統計情報取得: {'成功' if stats else '失敗'}")
            
            self.test_results["proposal_engine_api_test"] = api_configured
            
        except Exception as e:
            print(f"❌ ActivityProposalEngine APIテスト失敗: {e}")
    
    def _test_integration_system_api(self):
        """KnowledgeIntegrationSystem APIテスト"""
        print("\n🧠 4. KnowledgeIntegrationSystem APIテスト:")
        
        try:
            from core.knowledge_integration_system import KnowledgeIntegrationSystem
            
            # インスタンス作成
            system = KnowledgeIntegrationSystem()
            
            # API設定確認
            api_configured = system.openai_client is not None
            
            print(f"✅ KnowledgeIntegrationSystem API設定: {'成功' if api_configured else '失敗'}")
            
            # テスト用統合実行
            test_session_data = {
                "test_session_001": {
                    "session_id": "test_session_001",
                    "theme": "API修正テスト",
                    "knowledge_items": [
                        {
                            "item_id": "test_item_001",
                            "content": "API修正テスト用の知識アイテム",
                            "categories": ["テスト", "API修正"],
                            "keywords": ["API", "修正", "テスト"],
                            "entities": ["API", "修正"],
                            "importance_score": 8.0,
                            "reliability_score": 0.9
                        }
                    ]
                }
            }
            
            # 知識統合テスト
            integrated_knowledge = system.integrate_multi_session_knowledge(
                session_ids=["test_session_001"],
                session_data=test_session_data,
                integration_scope="basic"
            )
            
            print(f"✅ 知識統合テスト: {'成功' if integrated_knowledge else '失敗'}")
            
            self.test_results["integration_system_api_test"] = api_configured
            
        except Exception as e:
            print(f"❌ KnowledgeIntegrationSystem APIテスト失敗: {e}")
    
    def _test_gui_api_check(self):
        """GUI API Key確認テスト"""
        print("\n🖥️ 5. GUI API Key確認テスト:")
        
        try:
            # 基本的なインポートテスト
            from gui.learning_session_gui import LearningSessionGUI
            print("✅ GUI モジュールインポート成功")
            
            # 各コンポーネントの個別テスト
            from core.activity_learning_engine import ActivityLearningEngine
            from core.activity_proposal_engine import ActivityProposalEngine
            from core.knowledge_integration_system import KnowledgeIntegrationSystem
            from core.conversation_knowledge_provider import ConversationKnowledgeProvider
            from core.budget_safety_manager import BudgetSafetyManager
            
            # 各コンポーネントのAPI設定確認
            learning_engine = ActivityLearningEngine()
            proposal_engine = ActivityProposalEngine()
            integration_system = KnowledgeIntegrationSystem()
            conversation_provider = ConversationKnowledgeProvider()
            budget_manager = BudgetSafetyManager()
            
            # API設定状態確認
            learning_status = learning_engine.openai_client is not None
            proposal_status = proposal_engine.openai_client is not None
            integration_status = integration_system.openai_client is not None
            
            print(f"✅ 学習エンジンAPI: {'設定済み' if learning_status else '未設定'}")
            print(f"✅ 提案エンジンAPI: {'設定済み' if proposal_status else '未設定'}")
            print(f"✅ 統合システムAPI: {'設定済み' if integration_status else '未設定'}")
            
            # 統計情報取得テスト
            try:
                learning_stats = learning_engine.get_preprocessing_statistics()
                proposal_stats = proposal_engine.get_proposal_statistics()
                knowledge_stats = conversation_provider.get_knowledge_statistics()
                budget_stats = budget_manager.get_budget_status()
                
                print(f"✅ 学習統計: {'取得成功' if learning_stats else '取得失敗'}")
                print(f"✅ 提案統計: {'取得成功' if proposal_stats else '取得失敗'}")
                print(f"✅ 知識統計: {'取得成功' if knowledge_stats else '取得失敗'}")
                print(f"✅ 予算統計: {'取得成功' if budget_stats else '取得失敗'}")
                
            except Exception as stats_error:
                print(f"⚠️ 統計情報取得エラー: {stats_error}")
            
            self.test_results["gui_api_check_test"] = learning_status and proposal_status and integration_status
            
        except Exception as e:
            print(f"❌ GUI API確認テスト失敗: {e}")
    
    def _print_test_summary(self):
        """テスト結果サマリー表示"""
        print("\n" + "="*60)
        print("📊 OpenAI API Key修正テスト 結果サマリー")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        
        test_names = {
            "learning_engine_api_test": "ActivityLearningEngine APIテスト",
            "preprocessing_engine_api_test": "PreprocessingEngine APIテスト",
            "proposal_engine_api_test": "ActivityProposalEngine APIテスト",
            "integration_system_api_test": "KnowledgeIntegrationSystem APIテスト",
            "gui_api_check_test": "GUI API確認テスト"
        }
        
        for test_key, result in self.test_results.items():
            test_name = test_names.get(test_key, test_key)
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:40}: {status}")
        
        print("-" * 60)
        print(f"総合結果: {passed_tests}/{total_tests} テスト通過")
        
        if passed_tests == total_tests:
            print("🎉 OpenAI API Key修正が完全成功しました！")
            print("全コンポーネントでAPI Key設定が正常に動作しています。")
            
            # 修正内容サマリー
            print("\n💡 修正内容:")
            print("  ✅ 複数の環境変数パターン対応 (OPENAI_API_KEY, OPENAI_KEY)")
            print("  ✅ 実際のAPI接続テスト追加")
            print("  ✅ 詳細なエラーメッセージ提供")
            print("  ✅ GUI API Key確認機能追加")
            print("  ✅ 統計情報取得メソッド追加")
            
            print("\n🚀 次のステップ:")
            print("  - 実際の学習セッションテスト実行")
            print("  - 段階的分析パイプラインの動作確認")
            print("  - GUI統合システムの最終テスト")
            
        elif passed_tests >= total_tests * 0.8:
            print("⚠️ API Key修正が部分的に成功しました。")
            print("基本機能は動作していますが、一部に改善が必要です。")
            
        else:
            print("❌ API Key修正が失敗しました。")
            print("複数のコンポーネントで問題があり、修正が必要です。")
            print("\n🔧 対処方法:")
            print("  - 環境変数 OPENAI_API_KEY が正しく設定されているか確認")
            print("  - OpenAI APIキーが有効であることを確認")
            print("  - ネットワーク接続を確認")
        
        print("="*60)


def main():
    """メイン関数"""
    api_test = APIKeyFixTest()
    
    try:
        api_test.run_api_key_tests()
        
    except Exception as e:
        print(f"\n❌ テスト中断: {e}")


if __name__ == "__main__":
    main()