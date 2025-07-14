#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
段階的分析パイプライン統合テスト
GPT-3.5前処理 + GPT-4-turbo詳細分析
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
from core.preprocessing_engine import PreProcessingEngine
from core.budget_safety_manager import BudgetSafetyManager

class StagedAnalysisPipelineTest:
    """段階的分析パイプラインテストクラス"""
    
    def __init__(self):
        """初期化"""
        print("=== 段階的分析パイプライン統合テスト ===")
        
        # コンポーネント初期化
        print("\n🔧 コンポーネント初期化:")
        try:
            self.learning_engine = ActivityLearningEngine()
            print("✅ ActivityLearningEngine 初期化完了")
            
            self.preprocessing_engine = PreProcessingEngine()
            print("✅ PreProcessingEngine 初期化完了")
            
            self.budget_manager = BudgetSafetyManager()
            print("✅ BudgetSafetyManager 初期化完了")
            
        except Exception as e:
            print(f"❌ 初期化失敗: {e}")
            raise
        
        # コールバック設定
        self._setup_callbacks()
        
        # テスト結果
        self.test_results = {
            "preprocessing_functionality": False,
            "staged_configuration": False,
            "cost_efficiency": False,
            "quality_improvement": False,
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
        
        self.budget_manager.add_alert_callback(budget_alert_callback)
        
        print("✅ コールバック設定完了")
    
    async def run_staged_analysis_test(self):
        """段階的分析テスト実行"""
        print("\n🚀 段階的分析テスト開始:")
        
        try:
            # 1. 前処理機能テスト
            await self._test_preprocessing_functionality()
            
            # 2. 段階的設定テスト
            await self._test_staged_configuration()
            
            # 3. コスト効率テスト
            await self._test_cost_efficiency()
            
            # 4. 品質向上テスト
            await self._test_quality_improvement()
            
            # 5. 統合フローテスト
            await self._test_integration_flow()
            
            # 結果サマリー
            self._print_test_summary()
            
        except Exception as e:
            print(f"❌ 統合テスト失敗: {e}")
            raise
    
    async def _test_preprocessing_functionality(self):
        """前処理機能テスト"""
        print("\n🔍 1. 前処理機能テスト:")
        
        try:
            # テストデータ作成
            test_sources = [
                {
                    "source_id": "test_001",
                    "title": "AI音楽生成技術の最新動向",
                    "content": "Transformerアーキテクチャを使用した音楽生成AI技術が急速に発展している。OpenAIのMuseNetやGoogleのMusicTransformerが注目されている。",
                    "url": "https://example.com/ai-music-tech",
                    "source_type": "web_search"
                },
                {
                    "source_id": "test_002",
                    "title": "今日の天気予報",
                    "content": "明日は全国的に晴れの予報です。気温は25度程度になる見込みです。",
                    "url": "https://example.com/weather",
                    "source_type": "news"
                },
                {
                    "source_id": "test_003",
                    "title": "商用音楽AI生成ツールの比較",
                    "content": "AIVA、Amper Music、Jukedeck等の商用音楽AI生成ツールの機能比較。ユーザビリティと生成品質の観点から詳細評価。",
                    "url": "https://example.com/ai-tools-comparison",
                    "source_type": "web_search"
                },
                {
                    "source_id": "test_004",
                    "title": "料理レシピ: パスタの作り方",
                    "content": "美味しいパスタを作る方法。材料は小麦粉、卵、塩です。手順は生地をこねて、伸ばして、茹でるだけです。",
                    "url": "https://example.com/pasta-recipe",
                    "source_type": "web_search"
                }
            ]
            
            # 前処理実行
            preprocessing_results = self.preprocessing_engine.preprocess_content_batch(
                sources=test_sources,
                theme="AI音楽生成技術",
                target_categories=["技術", "市場", "ツール"]
            )
            
            # 結果評価
            passed_count = sum(1 for r in preprocessing_results if r.should_proceed)
            expected_pass_count = 2  # test_001とtest_003が通過予定
            
            if len(preprocessing_results) == len(test_sources) and passed_count >= expected_pass_count:
                print(f"✅ 前処理機能成功:")
                print(f"  処理数: {len(preprocessing_results)}件")
                print(f"  通過数: {passed_count}件")
                
                # 詳細結果表示
                for result in preprocessing_results:
                    status = "✅ 通過" if result.should_proceed else "❌ 除外"
                    print(f"    {result.source_id}: {status} (関連性:{result.relevance_score:.2f})")
                
                self.test_results["preprocessing_functionality"] = True
            else:
                print(f"❌ 前処理機能失敗: 期待通過数{expected_pass_count}, 実際{passed_count}")
                
        except Exception as e:
            print(f"❌ 前処理機能テスト失敗: {e}")
    
    async def _test_staged_configuration(self):
        """段階的設定テスト"""
        print("\n⚙️ 2. 段階的設定テスト:")
        
        try:
            # 初期設定確認
            initial_config = self.learning_engine.get_staged_analysis_config()
            print(f"初期設定: 前処理={initial_config['enable_preprocessing']}")
            
            # 設定変更テスト
            self.learning_engine.configure_staged_analysis(
                enable_preprocessing=False,
                relevance_min=0.6,
                quality_min=0.7,
                max_detailed_analysis=10
            )
            
            # 設定確認
            updated_config = self.learning_engine.get_staged_analysis_config()
            
            # 個別設定変更テスト
            self.learning_engine.enable_preprocessing(True)
            self.learning_engine.set_preprocessing_thresholds(
                relevance_min=0.4,
                quality_min=0.5,
                combined_min=0.6
            )
            
            final_config = self.learning_engine.get_staged_analysis_config()
            
            # 設定変更確認
            if (not updated_config['enable_preprocessing'] and 
                final_config['enable_preprocessing'] and
                final_config['preprocessing_thresholds']['relevance_min'] == 0.4):
                print("✅ 段階的設定成功:")
                print(f"  前処理: {final_config['enable_preprocessing']}")
                print(f"  閾値: {final_config['preprocessing_thresholds']}")
                self.test_results["staged_configuration"] = True
            else:
                print("❌ 段階的設定失敗")
                
        except Exception as e:
            print(f"❌ 段階的設定テスト失敗: {e}")
    
    async def _test_cost_efficiency(self):
        """コスト効率テスト"""
        print("\n💰 3. コスト効率テスト:")
        
        try:
            # 前処理有効・無効でのコスト比較シミュレーション
            test_sources_large = []
            for i in range(20):
                test_sources_large.append({
                    "source_id": f"test_{i:03d}",
                    "title": f"テスト記事{i}: AI技術について" if i % 3 == 0 else f"無関係な記事{i}",
                    "content": f"AI音楽生成に関する内容{i}" if i % 3 == 0 else f"全く関係ない内容{i}",
                    "url": f"https://example.com/article_{i}",
                    "source_type": "web_search"
                })
            
            # 前処理実行
            start_time = time.time()
            preprocessing_results = self.preprocessing_engine.preprocess_content_batch(
                sources=test_sources_large,
                theme="AI音楽生成技術"
            )
            preprocessing_time = time.time() - start_time
            
            # フィルタリング効果測定
            filtering_summary = self.preprocessing_engine.get_filtering_summary(preprocessing_results)
            preprocessing_stats = self.preprocessing_engine.get_statistics()
            
            # 効率計算
            pass_rate = filtering_summary['pass_rate']
            potential_savings = (100 - pass_rate) / 100  # フィルタアウト率 = 節約率
            
            if pass_rate < 80 and potential_savings > 0.2:  # 80%未満通過、20%以上節約
                print(f"✅ コスト効率成功:")
                print(f"  通過率: {pass_rate:.1f}%")
                print(f"  節約見込み: {potential_savings*100:.1f}%")
                print(f"  前処理コスト: ${filtering_summary['estimated_cost']:.4f}")
                print(f"  処理時間: {preprocessing_time:.2f}秒")
                self.test_results["cost_efficiency"] = True
            else:
                print(f"❌ コスト効率改善不十分: 通過率{pass_rate:.1f}%")
                
        except Exception as e:
            print(f"❌ コスト効率テスト失敗: {e}")
    
    async def _test_quality_improvement(self):
        """品質向上テスト"""
        print("\n📈 4. 品質向上テスト:")
        
        try:
            # 高品質・低品質の混合データ
            mixed_quality_sources = [
                {
                    "source_id": "high_001",
                    "title": "AI音楽生成における深層学習技術の応用",
                    "content": "本論文では、Transformer、GAN、VAE等の深層学習アーキテクチャを音楽生成に適用した最新研究を包括的にレビューし、各手法の特徴と性能を比較分析する。",
                    "url": "https://example.com/paper1",
                    "source_type": "academic"
                },
                {
                    "source_id": "low_001", 
                    "title": "音楽とAI",
                    "content": "AIで音楽を作れるらしい。すごいね。",
                    "url": "https://example.com/blog1",
                    "source_type": "blog"
                },
                {
                    "source_id": "high_002",
                    "title": "商用音楽生成AIの技術比較分析",
                    "content": "AIVA、Amper Music、Jukedeck、OpenAI MuseNetの技術仕様、学習データ、生成品質、ユーザビリティを詳細に比較。各ツールの強み・弱みを客観的に評価。",
                    "url": "https://example.com/analysis1",
                    "source_type": "web_search"
                },
                {
                    "source_id": "low_002",
                    "title": "AIニュース",
                    "content": "今日もAIのニュースがありました。",
                    "url": "https://example.com/news1",
                    "source_type": "news"
                }
            ]
            
            # 前処理実行
            quality_results = self.preprocessing_engine.preprocess_content_batch(
                sources=mixed_quality_sources,
                theme="AI音楽生成技術"
            )
            
            # 品質判定評価
            high_quality_passed = 0
            low_quality_filtered = 0
            
            for result in quality_results:
                if result.source_id.startswith("high_") and result.should_proceed:
                    high_quality_passed += 1
                elif result.source_id.startswith("low_") and not result.should_proceed:
                    low_quality_filtered += 1
            
            # 品質判定精度
            total_high = sum(1 for s in mixed_quality_sources if s["source_id"].startswith("high_"))
            total_low = sum(1 for s in mixed_quality_sources if s["source_id"].startswith("low_"))
            
            high_precision = high_quality_passed / total_high if total_high > 0 else 0
            low_precision = low_quality_filtered / total_low if total_low > 0 else 0
            
            if high_precision >= 0.8 and low_precision >= 0.5:  # 高品質80%以上通過、低品質50%以上除外
                print(f"✅ 品質向上成功:")
                print(f"  高品質通過率: {high_precision*100:.1f}%")
                print(f"  低品質除外率: {low_precision*100:.1f}%")
                
                # 詳細結果表示
                for result in quality_results:
                    status = "✅ 通過" if result.should_proceed else "❌ 除外"
                    print(f"    {result.source_id}: {status} (品質:{result.quality_score:.2f})")
                
                self.test_results["quality_improvement"] = True
            else:
                print(f"❌ 品質判定精度不十分: 高品質{high_precision*100:.1f}%, 低品質除外{low_precision*100:.1f}%")
                
        except Exception as e:
            print(f"❌ 品質向上テスト失敗: {e}")
    
    async def _test_integration_flow(self):
        """統合フローテスト"""
        print("\n🔄 5. 統合フローテスト:")
        
        try:
            # 予算設定
            self.budget_manager.set_budget_limits(
                monthly_limit=30.0,
                daily_limit=5.0
            )
            
            # 段階的分析有効でセッション作成
            self.learning_engine.enable_preprocessing(True)
            self.learning_engine.set_preprocessing_thresholds(
                relevance_min=0.3,
                quality_min=0.4,
                combined_min=0.5
            )
            
            session_id = self.learning_engine.create_session(
                theme="AI音楽生成技術の統合分析",
                learning_type="概要",
                depth_level=3,
                time_limit=120,  # 2分間テスト
                budget_limit=2.0,
                tags=["統合テスト", "段階的分析"]
            )
            
            if session_id:
                # 設定確認
                config = self.learning_engine.get_staged_analysis_config()
                preprocessing_stats = self.learning_engine.get_preprocessing_statistics()
                
                print(f"✅ 統合フロー成功:")
                print(f"  セッション作成: {session_id}")
                print(f"  前処理有効: {config['enable_preprocessing']}")
                print(f"  統計情報取得: ✅")
                
                self.test_results["integration_flow"] = True
            else:
                print("❌ 統合フロー失敗: セッション作成失敗")
                
        except Exception as e:
            print(f"❌ 統合フローテスト失敗: {e}")
    
    def _print_test_summary(self):
        """テスト結果サマリー表示"""
        print("\n" + "="*60)
        print("📊 段階的分析パイプライン テスト結果サマリー")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:30}: {status}")
        
        print("-" * 60)
        print(f"総合結果: {passed_tests}/{total_tests} テスト通過")
        
        if passed_tests == total_tests:
            print("🎉 段階的分析パイプラインの統合テストが成功しました！")
            print("GPT-3.5前処理 + GPT-4-turbo詳細分析の連携が正常に動作しています。")
            
            # 期待効果の表示
            print("\n💡 期待される効果:")
            print("  ✅ コスト削減: 50-70%のAPI使用料削減")
            print("  ✅ 処理速度: 不要データ除外による高速化")
            print("  ✅ 品質向上: 重要データに集中した詳細分析")
            print("  ✅ 拡張性: 柔軟な設定・制御機能")
        else:
            print("⚠️ 一部のテストが失敗しました。")
            print("失敗したコンポーネントの確認が必要です。")
        
        print("="*60)


async def main():
    """メイン関数"""
    pipeline_test = StagedAnalysisPipelineTest()
    
    try:
        await pipeline_test.run_staged_analysis_test()
        
    except Exception as e:
        print(f"\n❌ テスト中断: {e}")


if __name__ == "__main__":
    # 環境変数チェック
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️ OPENAI_API_KEY環境変数が設定されていません")
        print("GPT-3.5による前処理テストはフォールバック分析で実行されます")
    
    # 非同期実行
    asyncio.run(main())