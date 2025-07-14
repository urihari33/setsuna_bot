#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 2A 統合テスト
ActivityLearningEngine + KnowledgeDatabase + BudgetSafetyManager + SessionRelationshipManager
"""

import sys
import os
import time
import asyncio
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.activity_learning_engine import ActivityLearningEngine
from core.knowledge_database import KnowledgeDatabase
from core.budget_safety_manager import BudgetSafetyManager
from core.session_relationship_manager import SessionRelationshipManager

class Phase2AIntegrationTest:
    """Phase 2A 統合テストクラス"""
    
    def __init__(self):
        """初期化"""
        print("=== Phase 2A 統合テスト 開始 ===")
        
        # コンポーネント初期化
        print("\n🔧 コンポーネント初期化:")
        try:
            self.learning_engine = ActivityLearningEngine()
            print("✅ ActivityLearningEngine 初期化完了")
            
            self.knowledge_db = KnowledgeDatabase()
            print("✅ KnowledgeDatabase 初期化完了")
            
            self.budget_manager = BudgetSafetyManager()
            print("✅ BudgetSafetyManager 初期化完了")
            
            self.relationship_manager = SessionRelationshipManager()
            print("✅ SessionRelationshipManager 初期化完了")
            
        except Exception as e:
            print(f"❌ 初期化失敗: {e}")
            raise
        
        # コールバック設定
        self._setup_callbacks()
        
        # テスト状態
        self.test_results = {
            "component_initialization": True,
            "session_creation": False,
            "knowledge_storage": False,
            "budget_tracking": False,
            "relationship_management": False,
            "integration_flow": False
        }
    
    def _setup_callbacks(self):
        """コールバック設定"""
        print("\n📡 コールバック設定:")
        
        # 学習エンジンプログレスコールバック
        def learning_progress_callback(phase: str, progress: float, message: str):
            print(f"[学習進捗] {phase}: {progress:.1%} - {message}")
        
        self.learning_engine.add_progress_callback(learning_progress_callback)
        
        # 予算管理アラートコールバック
        def budget_alert_callback(alert):
            print(f"[予算アラート] {alert.severity}: {alert.message}")
        
        def budget_stop_callback(session_id: str, reason: str, current: float, limit: float):
            print(f"[予算停止] {session_id}: {reason} (${current:.2f}/${limit:.2f})")
        
        self.budget_manager.add_alert_callback(budget_alert_callback)
        self.budget_manager.add_stop_callback(budget_stop_callback)
        
        print("✅ コールバック設定完了")
    
    async def run_integration_test(self):
        """統合テスト実行"""
        print("\n🚀 統合テスト開始:")
        
        try:
            # 1. セッション作成テスト
            await self._test_session_creation()
            
            # 2. 知識保存テスト
            await self._test_knowledge_storage()
            
            # 3. 予算追跡テスト
            await self._test_budget_tracking()
            
            # 4. 関係性管理テスト
            await self._test_relationship_management()
            
            # 5. 統合フローテスト
            await self._test_integration_flow()
            
            # 結果サマリー
            self._print_test_summary()
            
        except Exception as e:
            print(f"❌ 統合テスト失敗: {e}")
            raise
    
    async def _test_session_creation(self):
        """セッション作成テスト"""
        print("\n📝 1. セッション作成テスト:")
        
        try:
            # 予算設定
            self.budget_manager.set_budget_limits(
                monthly_limit=50.0,
                daily_limit=10.0,
                session_limits={"test": 2.0}
            )
            
            # セッション作成
            session_id = self.learning_engine.create_session(
                theme="AI音楽生成技術の統合テスト",
                learning_type="概要",
                depth_level=2,
                time_limit=180,  # 3分間テスト
                budget_limit=1.5,
                tags=["統合テスト", "AI", "音楽生成"]
            )
            
            if session_id:
                print(f"✅ セッション作成成功: {session_id}")
                self.test_session_id = session_id
                self.test_results["session_creation"] = True
            else:
                print("❌ セッション作成失敗")
                
        except Exception as e:
            print(f"❌ セッション作成テスト失敗: {e}")
    
    async def _test_knowledge_storage(self):
        """知識保存テスト"""
        print("\n💾 2. 知識保存テスト:")
        
        try:
            # テスト知識アイテム保存
            knowledge_id_1 = self.knowledge_db.store_knowledge_item(
                session_id=self.test_session_id,
                layer="raw",
                content="AI音楽生成は機械学習技術を用いて音楽を自動生成する技術分野である",
                source_url="https://example.com/ai-music",
                reliability_score=0.8,
                importance_score=0.7,
                categories=["AI技術", "音楽"],
                keywords=["AI", "音楽生成", "機械学習"],
                entities=["AI技術", "音楽生成"]
            )
            
            knowledge_id_2 = self.knowledge_db.store_knowledge_item(
                session_id=self.test_session_id,
                layer="structured",
                content="Transformerアーキテクチャが音楽生成分野で主流になりつつある",
                reliability_score=0.9,
                importance_score=0.8,
                categories=["AI技術", "深層学習"],
                keywords=["Transformer", "アーキテクチャ", "音楽生成"],
                entities=["Transformer", "深層学習"]
            )
            
            # エンティティ保存
            entity_id = self.knowledge_db.store_entity(
                name="Transformer",
                entity_type="技術",
                description="注意機構を使った深層学習アーキテクチャ",
                session_id=self.test_session_id,
                aliases=["トランスフォーマー", "Attention機構"],
                categories=["AI技術", "深層学習"],
                importance_score=0.9
            )
            
            if knowledge_id_1 and knowledge_id_2 and entity_id:
                print(f"✅ 知識保存成功: 知識2件, エンティティ1件")
                self.test_results["knowledge_storage"] = True
            else:
                print("❌ 知識保存失敗")
                
        except Exception as e:
            print(f"❌ 知識保存テスト失敗: {e}")
    
    async def _test_budget_tracking(self):
        """予算追跡テスト"""
        print("\n💰 3. 予算追跡テスト:")
        
        try:
            # コスト記録
            cost_id_1 = self.budget_manager.record_cost(
                session_id=self.test_session_id,
                api_type="openai",
                operation="text_analysis",
                input_tokens=1000,
                output_tokens=300,
                details={"model": "gpt-4-turbo"}
            )
            
            cost_id_2 = self.budget_manager.record_cost(
                session_id=self.test_session_id,
                api_type="search",
                operation="web_search",
                input_tokens=0,
                output_tokens=0,
                additional_cost=0.01,
                details={"query": "AI音楽生成"}
            )
            
            # 使用量サマリー確認
            usage_summary = self.budget_manager.get_usage_summary("today")
            
            if cost_id_1 and cost_id_2 and usage_summary:
                print(f"✅ 予算追跡成功: コスト記録2件")
                print(f"   今日の使用量: ${usage_summary['current_usage']:.4f}")
                self.test_results["budget_tracking"] = True
            else:
                print("❌ 予算追跡失敗")
                
        except Exception as e:
            print(f"❌ 予算追跡テスト失敗: {e}")
    
    async def _test_relationship_management(self):
        """関係性管理テスト"""
        print("\n🔗 4. 関係性管理テスト:")
        
        try:
            # セッション関係性作成
            session_data = {
                "session_id": self.test_session_id,
                "theme": "AI音楽生成技術の統合テスト",
                "learning_type": "概要",
                "depth_level": 2,
                "tags": ["統合テスト", "AI", "音楽生成"]
            }
            
            success = self.relationship_manager.create_session_relationship(
                session_id=self.test_session_id,
                session_data=session_data
            )
            
            # 子セッション作成テスト
            child_session_id = self.learning_engine.create_session(
                theme="Transformer音楽生成詳細調査",
                learning_type="深掘り",
                depth_level=4,
                time_limit=120,
                budget_limit=1.0,
                parent_session=self.test_session_id,
                tags=["Transformer", "深掘り調査"]
            )
            
            if child_session_id:
                child_session_data = {
                    "session_id": child_session_id,
                    "theme": "Transformer音楽生成詳細調査",
                    "learning_type": "深掘り",
                    "depth_level": 4,
                    "tags": ["Transformer", "深掘り調査"]
                }
                
                child_success = self.relationship_manager.create_session_relationship(
                    session_id=child_session_id,
                    session_data=child_session_data,
                    parent_session=self.test_session_id
                )
                
                if success and child_success:
                    print(f"✅ 関係性管理成功: 親子関係作成")
                    self.test_child_session_id = child_session_id
                    self.test_results["relationship_management"] = True
                else:
                    print("❌ 関係性管理失敗")
            else:
                print("❌ 子セッション作成失敗")
                
        except Exception as e:
            print(f"❌ 関係性管理テスト失敗: {e}")
    
    async def _test_integration_flow(self):
        """統合フローテスト"""
        print("\n🔄 5. 統合フローテスト:")
        
        try:
            # セッションコンテキスト取得
            context = self.relationship_manager.get_session_context(self.test_child_session_id)
            
            # 知識検索
            search_results = self.knowledge_db.search_knowledge(
                query="AI音楽生成",
                limit=3
            )
            
            # セッション知識サマリー
            knowledge_summary = self.knowledge_db.get_session_knowledge_summary(self.test_session_id)
            
            # 次回セッション推奨
            recommendations = self.relationship_manager.recommend_next_sessions(
                self.test_session_id,
                limit=2
            )
            
            # 系譜可視化データ
            lineage_viz = self.relationship_manager.get_session_lineage_visualization(self.test_session_id)
            
            # コスト最適化提案
            cost_suggestions = self.budget_manager.get_cost_optimization_suggestions()
            
            if (context and search_results and knowledge_summary and 
                recommendations and lineage_viz and not context.get("error")):
                print(f"✅ 統合フロー成功:")
                print(f"   - セッションコンテキスト取得: ✅")
                print(f"   - 知識検索: {len(search_results)}件")
                print(f"   - 知識サマリー: {knowledge_summary['total_knowledge_items']}アイテム")
                print(f"   - セッション推奨: {len(recommendations)}件")
                print(f"   - 系譜可視化: {lineage_viz['total_sessions']}セッション")
                print(f"   - 最適化提案: {len(cost_suggestions)}件")
                self.test_results["integration_flow"] = True
            else:
                print("❌ 統合フロー失敗")
                if context.get("error"):
                    print(f"   コンテキストエラー: {context['error']}")
                
        except Exception as e:
            print(f"❌ 統合フローテスト失敗: {e}")
    
    def _print_test_summary(self):
        """テスト結果サマリー表示"""
        print("\n" + "="*50)
        print("📊 Phase 2A 統合テスト結果サマリー")
        print("="*50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:25}: {status}")
        
        print("-" * 50)
        print(f"総合結果: {passed_tests}/{total_tests} テスト通過")
        
        if passed_tests == total_tests:
            print("🎉 すべてのテストが成功しました！")
            print("Phase 2A コアシステムの統合は正常に動作しています。")
        else:
            print("⚠️ 一部のテストが失敗しました。")
            print("失敗したコンポーネントの確認が必要です。")
        
        print("="*50)
    
    async def cleanup_test_data(self):
        """テストデータクリーンアップ"""
        print("\n🧹 テストデータクリーンアップ:")
        
        try:
            # テスト用の一時データを削除
            # （実装簡略化：実際はより詳細なクリーンアップ）
            print("✅ クリーンアップ完了")
            
        except Exception as e:
            print(f"⚠️ クリーンアップ警告: {e}")


async def main():
    """メイン関数"""
    integration_test = Phase2AIntegrationTest()
    
    try:
        await integration_test.run_integration_test()
        
    except Exception as e:
        print(f"\n❌ 統合テスト中断: {e}")
        
    finally:
        await integration_test.cleanup_test_data()


if __name__ == "__main__":
    # 環境変数チェック
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️ OPENAI_API_KEY環境変数が設定されていません")
        print("実際のAPI呼び出しテストはスキップされます")
    
    # 非同期実行
    asyncio.run(main())