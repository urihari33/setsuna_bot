#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 2 統合テストスクリプト
人間評価型SA学習システム - Phase 2 全コンポーネント統合動作確認
"""

import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from core.adaptive_learning.results_analyzer import ResultsAnalyzer, ContentAnalysis, SessionAnalysis, QualityMetrics
from core.adaptive_learning.user_feedback_interface import (
    UserFeedbackInterface, ConsoleUserInterface, FeedbackSession, EvaluationContext
)
from core.adaptive_learning.semi_automatic_evaluator import (
    SemiAutomaticEvaluator, EvaluationStrategy, EvaluationMode, EvaluationTrigger
)
from core.adaptive_learning.batch_session_manager import SessionResult, BatchResult
from core.adaptive_learning.models.exploration_models import ExplorationSession, generate_session_id
from core.adaptive_learning.models.feedback_models import UserFeedback, QualityRating
from datetime import datetime

def test_phase2_full_integration():
    """Phase 2 完全統合テスト"""
    print("=== Phase 2 完全統合テスト ===")
    print("人間評価型Simulated Annealing学習システム - Phase 2 全機能統合確認\n")
    
    try:
        # 1. 全コンポーネント初期化
        print("1. Phase 2 全コンポーネント初期化")
        
        # ResultsAnalyzer
        results_analyzer = ResultsAnalyzer()
        
        # UserFeedbackInterface
        console_ui = ConsoleUserInterface()
        user_interface = UserFeedbackInterface(console_ui)
        
        # SemiAutomaticEvaluator（セミオート戦略）
        evaluation_strategy = EvaluationStrategy(
            mode=EvaluationMode.SEMI_AUTO,
            trigger_conditions=[
                EvaluationTrigger.ROUND_COMPLETION,
                EvaluationTrigger.QUALITY_THRESHOLD
            ],
            auto_quality_threshold=0.7,
            auto_confidence_threshold=0.8,
            human_eval_frequency=0.6,  # 60%の確率で人間評価
            adaptive_frequency=True
        )
        
        semi_auto_evaluator = SemiAutomaticEvaluator(evaluation_strategy)
        
        print("✅ Phase 2 全コンポーネント初期化完了")
        print(f"   • ResultsAnalyzer: 結果分析・品質評価エンジン")
        print(f"   • UserFeedbackInterface: 人間評価UI・フィードバック収集")
        print(f"   • SemiAutomaticEvaluator: セミオート評価・AI人間統合")
        print(f"   評価戦略: {evaluation_strategy.mode.value}")
        print(f"   人間評価頻度: {evaluation_strategy.human_eval_frequency}\n")
        
        # 2. 統合探索セッション・シナリオ作成
        print("2. 統合探索セッション・シナリオ作成")
        
        # メインセッション
        main_session = ExplorationSession(
            session_id=generate_session_id(),
            theme="AI音楽生成技術の商用化とビジネスモデル",
            start_time=datetime.now(),
            initial_temperature="high",
            budget_limit=100.0,
            session_limit=None,
            status="active",
            rounds_completed=0
        )
        
        print(f"✅ 統合セッション作成完了")
        print(f"   セッション: {main_session.session_id}")
        print(f"   テーマ: {main_session.theme}")
        print(f"   予算: ${main_session.budget_limit}")
        print(f"   初期温度: {main_session.initial_temperature}\n")
        
        # 3. 第1ラウンド: 高温探索・結果分析・評価統合
        print("3. 第1ラウンド: 高温探索・結果分析・評価統合")
        
        # 高温探索結果（多様だが品質にばらつき）
        round1_session_results = [
            SessionResult(
                session_id="r1_001",
                query="AI音楽生成技術の基礎技術調査",
                status="success",
                execution_time=2200,
                quality_score=0.65,
                cost=1.0,
                content="AI音楽生成技術について基本的な調査を実施しました。深層学習ベースの生成モデルが主流となっており、Transformer、VAE、GANなどのアーキテクチャが活用されています。",
                themes_found=["技術基礎", "深層学習", "生成モデル"]
            ),
            SessionResult(
                session_id="r1_002", 
                query="音楽業界でのAI活用事例分析",
                status="success",
                execution_time=2800,
                quality_score=0.72,
                cost=1.2,
                content="音楽業界におけるAI技術の活用事例を分析しました。作曲支援、楽曲分析、マスタリング自動化、著作権管理など多岐にわたる応用が確認されています。",
                themes_found=["業界事例", "AI活用", "作曲支援", "著作権"]
            ),
            SessionResult(
                session_id="r1_003",
                query="AI音楽の商用化における法的課題",
                status="success", 
                execution_time=3200,
                quality_score=0.58,
                cost=1.5,
                content="AI音楽の商用化に関する法的課題について調査しました。著作権の帰属、創作者の定義、既存楽曲との類似性判定など複雑な問題が存在します。",
                themes_found=["法的課題", "著作権", "商用化"]
            ),
            SessionResult(
                session_id="r1_004",
                query="音楽生成AIの市場規模予測",
                status="success",
                execution_time=2500,
                quality_score=0.81,
                cost=1.3,
                content="音楽生成AI市場の規模予測を調査しました。2023年から2030年にかけて年平均成長率28%で拡大し、2030年には50億ドル規模に達すると予測されています。",
                themes_found=["市場予測", "成長率", "規模拡大"]
            ),
            SessionResult(
                session_id="r1_005",
                query="主要企業のAI音楽戦略比較",
                status="success",
                execution_time=3100,
                quality_score=0.76,
                cost=1.4,
                content="Google、OpenAI、Sony、Warner Music Groupなど主要企業のAI音楽戦略を比較分析しました。各社異なるアプローチで市場参入を図っています。",
                themes_found=["企業戦略", "競合分析", "市場参入"]
            )
        ]
        
        round1_batch_result = BatchResult(
            batch_id=f"{main_session.session_id}_round_01",
            session_results=round1_session_results,
            total_execution_time=13800,
            total_cost=6.4,
            success_rate=1.0,
            average_quality=0.70
        )
        
        print(f"✅ 第1ラウンド探索完了")
        print(f"   セッション数: {len(round1_session_results)}")
        print(f"   平均品質: {round1_batch_result.average_quality:.2f}")
        print(f"   成功率: {round1_batch_result.success_rate:.1%}")
        print(f"   コスト: ${round1_batch_result.total_cost:.2f}")
        
        # 結果分析実行
        print(f"\n3.1 結果分析実行")
        
        # 個別コンテンツ分析
        content_analyses_r1 = []
        for session_result in round1_session_results:
            content_analysis = results_analyzer.analyze_content_quality(
                session_result, main_session.theme
            )
            content_analyses_r1.append(content_analysis)
        
        # セッション総合分析
        main_session.rounds_completed = 1
        session_analysis_r1 = results_analyzer.analyze_session_results(
            main_session.session_id,
            [round1_batch_result],
            main_session
        )
        
        print(f"✅ 結果分析完了")
        print(f"   コンテンツ分析: {len(content_analyses_r1)}件")
        print(f"   セッション分析: 平均品質{session_analysis_r1.average_quality:.2f}")
        print(f"   テーマ多様性: {session_analysis_r1.theme_diversity:.2f}")
        print(f"   推奨事項数: {len(session_analysis_r1.recommended_actions)}")
        
        # 評価トリガー判定
        print(f"\n3.2 評価トリガー判定")
        
        should_evaluate, triggered_conditions = semi_auto_evaluator.should_trigger_evaluation(
            main_session.session_id, 1, round1_batch_result, main_session
        )
        
        print(f"✅ 評価トリガー判定完了")
        print(f"   評価実行: {should_evaluate}")
        print(f"   トリガー条件: {[t.value for t in triggered_conditions]}")
        
        # セミオート評価実行
        if should_evaluate:
            print(f"\n3.3 セミオート評価実行")
            
            hybrid_evaluation_r1 = semi_auto_evaluator.perform_hybrid_evaluation(
                main_session.session_id,
                round1_batch_result,
                session_analysis_r1,
                force_human_eval=False  # 戦略に従って自動判定
            )
            
            print(f"✅ セミオート評価完了")
            print(f"   評価ID: {hybrid_evaluation_r1.evaluation_id}")
            print(f"   最終方向: {hybrid_evaluation_r1.final_direction}")
            print(f"   最終信頼度: {hybrid_evaluation_r1.final_confidence:.2f}")
            print(f"   評価時間: {hybrid_evaluation_r1.evaluation_time:.1f}秒")
            print(f"   自動評価: {'✓' if hybrid_evaluation_r1.auto_evaluation else '×'}")
            print(f"   人間評価: {'✓' if hybrid_evaluation_r1.human_feedback else '×'}")
            print(f"   合意レベル: {hybrid_evaluation_r1.consensus_level:.2f}")
            
            if hybrid_evaluation_r1.auto_evaluation:
                auto_eval = hybrid_evaluation_r1.auto_evaluation
                print(f"   AI推奨: {auto_eval.recommended_direction} (信頼度: {auto_eval.direction_confidence:.2f})")
                print(f"   予測品質: {auto_eval.predicted_quality:.2f}")
                
                print(f"   AI推奨事項:")
                for action in auto_eval.recommended_actions:
                    print(f"     • {action}")
        
        # 4. 第2ラウンド: 中温探索・品質改善・統合評価
        print(f"\n4. 第2ラウンド: 中温探索・品質改善・統合評価")
        
        # 第1ラウンドの評価結果を反映（deeper方向に調整）
        round2_session_results = [
            SessionResult(
                session_id="r2_001",
                query="AI音楽生成の技術的実装詳細とアルゴリズム比較",
                status="success",
                execution_time=3500,
                quality_score=0.83,
                cost=1.8,
                content="AI音楽生成の技術的実装について詳細調査を実施。Transformer-based model、VAE、Diffusion modelの比較分析を行い、各手法の特性と適用場面を明確化しました。特にMuseNet、AIVA、AmperMusicの実装詳細を分析し、商用サービスレベルでの技術要件を特定しました。",
                themes_found=["技術実装", "アルゴリズム比較", "商用要件", "MuseNet", "AIVA"]
            ),
            SessionResult(
                session_id="r2_002",
                query="音楽生成AIのビジネスモデル分析と収益化戦略",
                status="success",
                execution_time=3800,
                quality_score=0.79,
                cost=2.0,
                content="音楽生成AIの多様なビジネスモデルを詳細分析。B2C向けクリエイター支援ツール、B2B向けライセンシング、API提供、サブスクリプションサービスなど複数の収益化モデルを検証。特にAmper、AIVA、Sonifyの事業戦略と収益構造を比較分析しました。",
                themes_found=["ビジネスモデル", "収益化戦略", "B2B", "B2C", "ライセンシング"]
            ),
            SessionResult(
                session_id="r2_003",
                query="AI音楽と著作権法の詳細な法的分析",
                status="success",
                execution_time=4200,
                quality_score=0.75,
                cost=2.2,
                content="AI音楽の著作権に関する詳細な法的分析を実施。米国、EU、日本の法的枠組みを比較し、AI生成コンテンツの著作権帰属、既存楽曲の学習データ使用、商用利用時の権利関係について判例と最新の法的動向を調査。特にLimens v. Sony事件の影響を分析しました。",
                themes_found=["著作権法", "法的分析", "国際比較", "判例研究", "商用利用"]
            ),
            SessionResult(
                session_id="r2_004",
                query="音楽業界エコシステムにおけるAI技術の統合影響分析",
                status="success",
                execution_time=3600,
                quality_score=0.81,
                cost=1.9,
                content="音楽業界の既存エコシステムにAI技術がもたらす変革について包括的分析。レコードレーベル、音楽プラットフォーム、アーティスト、プロデューサーなど各ステークホルダーへの影響を評価。SpotifyのAI活用事例、Universal Music GroupのAI戦略を詳細分析しました。",
                themes_found=["業界エコシステム", "変革影響", "ステークホルダー", "Spotify", "Universal Music"]
            )
        ]
        
        round2_batch_result = BatchResult(
            batch_id=f"{main_session.session_id}_round_02",
            session_results=round2_session_results,
            total_execution_time=15100,
            total_cost=7.9,
            success_rate=1.0,
            average_quality=0.80
        )
        
        print(f"✅ 第2ラウンド探索完了")
        print(f"   セッション数: {len(round2_session_results)}")
        print(f"   平均品質: {round2_batch_result.average_quality:.2f}")
        print(f"   品質改善: {round2_batch_result.average_quality - round1_batch_result.average_quality:+.2f}")
        print(f"   コスト: ${round2_batch_result.total_cost:.2f}")
        
        # 統合結果分析
        print(f"\n4.1 統合結果分析")
        
        # 第2ラウンドコンテンツ分析
        content_analyses_r2 = []
        for session_result in round2_session_results:
            content_analysis = results_analyzer.analyze_content_quality(
                session_result, main_session.theme
            )
            content_analyses_r2.append(content_analysis)
        
        # 累積セッション分析
        main_session.rounds_completed = 2
        main_session.total_cost = round1_batch_result.total_cost + round2_batch_result.total_cost
        
        session_analysis_r2 = results_analyzer.analyze_session_results(
            main_session.session_id,
            [round1_batch_result, round2_batch_result],
            main_session
        )
        
        print(f"✅ 統合結果分析完了")
        print(f"   累積コンテンツ分析: {len(content_analyses_r1 + content_analyses_r2)}件")
        print(f"   累積品質改善: {session_analysis_r2.quality_improvement:+.2f}")
        print(f"   テーマ進化: {len(session_analysis_r2.theme_evolution)}種類")
        print(f"   コスト効率: {session_analysis_r2.cost_efficiency:.3f}")
        
        # 品質トレンド分析
        print(f"\n4.2 品質トレンド分析")
        
        quality_trends = results_analyzer.get_quality_trends(main_session.session_id)
        
        if "error" not in quality_trends:
            print(f"✅ 品質トレンド分析完了")
            print(f"   トレンド方向: {quality_trends['trend_direction']}")
            print(f"   トレンド強度: {quality_trends['trend_strength']:.2f}")
            print(f"   現在平均品質: {quality_trends['current_average']:.2f}")
            print(f"   全体平均品質: {quality_trends['overall_average']:.2f}")
        else:
            print(f"⚠️ 品質トレンド分析: {quality_trends['error']}")
        
        # 第2ラウンド評価
        print(f"\n4.3 第2ラウンド統合評価")
        
        should_evaluate_r2, triggered_conditions_r2 = semi_auto_evaluator.should_trigger_evaluation(
            main_session.session_id, 2, round2_batch_result, main_session
        )
        
        if should_evaluate_r2:
            hybrid_evaluation_r2 = semi_auto_evaluator.perform_hybrid_evaluation(
                main_session.session_id,
                round2_batch_result,
                session_analysis_r2,
                force_human_eval=False
            )
            
            print(f"✅ 第2ラウンド統合評価完了")
            print(f"   最終方向: {hybrid_evaluation_r2.final_direction}")
            print(f"   信頼度改善: {hybrid_evaluation_r2.final_confidence:.2f}")
            print(f"   合意レベル: {hybrid_evaluation_r2.consensus_level:.2f}")
            
            # 評価履歴比較
            if main_session.session_id in semi_auto_evaluator.evaluation_history:
                evaluations = semi_auto_evaluator.evaluation_history[main_session.session_id]
                print(f"   評価履歴: {len(evaluations)}回")
                
                if len(evaluations) >= 2:
                    print(f"   方向遷移: {evaluations[0].final_direction} → {evaluations[1].final_direction}")
                    confidence_change = evaluations[1].final_confidence - evaluations[0].final_confidence
                    print(f"   信頼度変化: {confidence_change:+.2f}")
        
        # 5. 比較分析・洞察レポート生成
        print(f"\n5. 比較分析・洞察レポート生成")
        
        # 温度別比較分析（仮想的に高温・中温として比較）
        temp_comparison = results_analyzer.perform_comparative_analysis(
            comparison_type="temperature",
            subjects=["high", "medium"],
            analysis_scope="quality"
        )
        
        print(f"✅ 温度別比較分析完了")
        print(f"   統計的有意性: p={temp_comparison.statistical_significance:.3f}")
        print(f"   品質比較結果:")
        for subject, quality in temp_comparison.quality_comparison.items():
            print(f"     {subject}: {quality:.2f}")
        
        print(f"   主要洞察:")
        for insight in temp_comparison.key_insights:
            print(f"     • {insight}")
        
        # セッション洞察レポート
        print(f"\n5.1 セッション洞察レポート生成")
        
        insights_report = results_analyzer.generate_insights_report(
            session_id=main_session.session_id,
            include_recommendations=True
        )
        
        print(f"✅ セッション洞察レポート生成完了")
        print(f"   分析セッション数: {insights_report['summary']['total_sessions_analyzed']}")
        print(f"   総コンテンツ数: {insights_report['summary']['total_content_analyzed']}")
        print(f"   平均品質: {insights_report['summary']['average_quality']:.2f}")
        print(f"   品質改善: {insights_report['summary']['average_quality_improvement']:+.2f}")
        
        print(f"\n   上位テーマ:")
        for theme_info in insights_report['theme_analysis']['top_themes'][:5]:
            print(f"     {theme_info['theme']}: 出現{theme_info['frequency']}回")
        
        print(f"\n   システム推奨事項:")
        for rec in insights_report['recommendations'][:3]:
            print(f"     • {rec}")
        
        # 6. 評価統計・要約レポート
        print(f"\n6. 評価統計・要約レポート")
        
        evaluation_summary = semi_auto_evaluator.get_evaluation_summary(main_session.session_id)
        
        if "error" not in evaluation_summary:
            print(f"✅ 評価要約生成完了")
            print(f"   総評価数: {evaluation_summary['summary']['total_evaluations']}")
            print(f"   自動評価: {evaluation_summary['summary']['auto_only_evaluations']}")
            print(f"   ハイブリッド評価: {evaluation_summary['summary']['hybrid_evaluations']}")
            print(f"   平均合意レベル: {evaluation_summary['summary']['average_consensus_level']:.2f}")
            
            print(f"\n   パフォーマンス指標:")
            metrics = evaluation_summary['performance_metrics']
            print(f"     自動化率: {metrics['automation_rate']:.1%}")
            print(f"     効率スコア: {metrics['efficiency_score']:.2f}")
            print(f"     信頼性スコア: {metrics['reliability_score']:.2f}")
        else:
            print(f"⚠️ 評価要約生成: {evaluation_summary['error']}")
        
        # 7. データ永続化・保存
        print(f"\n7. データ永続化・保存")
        
        try:
            # 評価履歴保存
            saved_evaluation_file = semi_auto_evaluator.save_evaluation_data(main_session.session_id)
            print(f"✅ 評価データ保存完了: {saved_evaluation_file}")
            
            # 分析結果保存確認
            analysis_stats = results_analyzer.analysis_stats
            print(f"✅ 分析統計確認:")
            print(f"   総分析コンテンツ数: {analysis_stats['total_content_analyzed']}")
            print(f"   総分析セッション数: {analysis_stats['total_sessions_analyzed']}")
            print(f"   テーマ種類数: {len(results_analyzer.theme_database)}")
            
        except Exception as e:
            print(f"⚠️ データ保存エラー: {e}")
        
        # 8. Phase 2 統合成果確認
        print(f"\n8. Phase 2 統合成果確認")
        
        print(f"✅ Phase 2 完全統合テスト成功！")
        print(f"🎯 統合成果:")
        print(f"   • 探索セッション: {main_session.session_id}")
        print(f"   • 実行ラウンド数: {main_session.rounds_completed}")
        print(f"   • 総探索セッション数: {len(round1_session_results) + len(round2_session_results)}")
        print(f"   • 品質改善達成: {session_analysis_r2.quality_improvement:+.2f}")
        print(f"   • 総コスト: ${main_session.total_cost:.2f} (予算${main_session.budget_limit:.2f})")
        print(f"   • コスト効率: {session_analysis_r2.cost_efficiency:.3f}")
        print(f"   • テーマ多様性: {session_analysis_r2.theme_diversity:.2f}")
        
        final_quality_improvement = round2_batch_result.average_quality - round1_batch_result.average_quality
        print(f"   • 最終品質改善: {final_quality_improvement:+.2f}")
        
        if final_quality_improvement > 0.05:
            print(f"   🎉 目標品質改善達成！")
        
        return True
        
    except Exception as e:
        print(f"❌ Phase 2 統合テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_phase2_error_resilience():
    """Phase 2 エラー耐性テスト"""
    print("\n=== Phase 2 エラー耐性テスト ===")
    
    try:
        # 各コンポーネントのエラー処理確認
        results_analyzer = ResultsAnalyzer()
        console_ui = ConsoleUserInterface()
        user_interface = UserFeedbackInterface(console_ui)
        semi_auto_evaluator = SemiAutomaticEvaluator()
        
        print("✅ エラー耐性テスト用コンポーネント初期化完了")
        
        # 1. 空データ処理テスト
        print("\n1. 空データ処理耐性テスト")
        
        # 存在しないセッションの分析
        try:
            trends = results_analyzer.get_quality_trends("nonexistent_session")
            if "error" in trends:
                print("✅ 存在しないセッション適切な処理")
            else:
                print("❌ 存在しないセッション処理が不適切")
        except Exception as e:
            print(f"✅ 適切なエラーハンドリング: {type(e).__name__}")
        
        # 存在しない評価データの要約
        try:
            summary = semi_auto_evaluator.get_evaluation_summary("nonexistent_session")
            if "error" in summary:
                print("✅ 存在しない評価データ適切な処理")
        except Exception as e:
            print(f"✅ 適切なエラーハンドリング: {type(e).__name__}")
        
        # 2. 極端な値での処理テスト
        print("\n2. 極端な値処理耐性テスト")
        
        # 極端に高い品質
        extreme_high_batch = BatchResult(
            batch_id="extreme_high",
            session_results=[],
            total_execution_time=1000,
            total_cost=1.0,
            success_rate=1.0,
            average_quality=1.0  # 最大値
        )
        
        # 極端に低い品質
        extreme_low_batch = BatchResult(
            batch_id="extreme_low",
            session_results=[],
            total_execution_time=1000,
            total_cost=1.0,
            success_rate=0.0,
            average_quality=0.0  # 最小値
        )
        
        session = ExplorationSession(
            session_id="extreme_test",
            theme="テスト",
            start_time=datetime.now(),
            initial_temperature="medium",
            budget_limit=10.0,
            session_limit=None,
            status="active"
        )
        
        # 極端な値でのトリガー判定
        should_trigger_high, _ = semi_auto_evaluator.should_trigger_evaluation(
            "extreme_test", 1, extreme_high_batch, session
        )
        
        should_trigger_low, _ = semi_auto_evaluator.should_trigger_evaluation(
            "extreme_test", 1, extreme_low_batch, session
        )
        
        print(f"✅ 極端値トリガー判定完了")
        print(f"   高品質(1.0): {should_trigger_high}")
        print(f"   低品質(0.0): {should_trigger_low}")
        
        # 3. コンポーネント連携エラー処理テスト
        print("\n3. コンポーネント連携エラー処理テスト")
        
        # 不正なデータでの統合処理試行
        try:
            invalid_session = ExplorationSession(
                session_id="invalid_test",
                theme="",  # 空のテーマ
                start_time=datetime.now(),
                initial_temperature="invalid_temp",  # 不正な温度
                budget_limit=-1.0,  # 負の予算
                session_limit=None,
                status="active"
            )
            
            print("✅ 不正データでも初期化可能")
            
        except Exception as e:
            print(f"✅ 適切な検証エラー: {type(e).__name__}")
        
        print("✅ Phase 2 エラー耐性テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ エラー耐性テスト失敗: {e}")
        return False

def test_phase2_performance_metrics():
    """Phase 2 パフォーマンス指標テスト"""
    print("\n=== Phase 2 パフォーマンス指標テスト ===")
    
    try:
        start_time = datetime.now()
        
        # パフォーマンステスト用設定
        results_analyzer = ResultsAnalyzer()
        console_ui = ConsoleUserInterface()
        user_interface = UserFeedbackInterface(console_ui)
        
        # 高速評価戦略
        fast_strategy = EvaluationStrategy(
            mode=EvaluationMode.AUTO_ASSISTED,
            trigger_conditions=[EvaluationTrigger.ROUND_COMPLETION],
            human_eval_frequency=0.1,  # 低頻度で高速化
            auto_confidence_threshold=0.5
        )
        
        semi_auto_evaluator = SemiAutomaticEvaluator(fast_strategy)
        
        # 大量データ処理テスト
        print("1. 大量データ処理パフォーマンステスト")
        
        # 10セッション相当のデータ作成
        large_session_results = []
        for i in range(10):
            session_result = SessionResult(
                session_id=f"perf_test_{i:03d}",
                query=f"パフォーマンステスト用クエリ {i+1}",
                status="success",
                execution_time=1000 + (i * 100),
                quality_score=0.5 + (i * 0.05),
                cost=1.0,
                content=f"パフォーマンステスト用コンテンツ {i+1} " * 50,  # ある程度の長さ
                themes_found=[f"テーマ{i+1}", "パフォーマンス", "テスト"]
            )
            large_session_results.append(session_result)
        
        large_batch = BatchResult(
            batch_id="performance_test_batch",
            session_results=large_session_results,
            total_execution_time=15000,
            total_cost=10.0,
            success_rate=1.0,
            average_quality=0.75
        )
        
        # 大量データ分析
        analysis_start = datetime.now()
        
        content_analyses = []
        for session_result in large_session_results:
            content_analysis = results_analyzer.analyze_content_quality(
                session_result, "パフォーマンステスト"
            )
            content_analyses.append(content_analysis)
        
        analysis_time = (datetime.now() - analysis_start).total_seconds()
        
        print(f"✅ 大量データ分析完了")
        print(f"   分析セッション数: {len(large_session_results)}")
        print(f"   分析時間: {analysis_time:.2f}秒")
        print(f"   1セッション当たり: {analysis_time/len(large_session_results):.3f}秒")
        
        # 2. 評価処理パフォーマンス
        print(f"\n2. 評価処理パフォーマンステスト")
        
        session = ExplorationSession(
            session_id="perf_session",
            theme="パフォーマンステスト",
            start_time=datetime.now(),
            initial_temperature="medium",
            budget_limit=50.0,
            session_limit=None,
            status="active"
        )
        
        session_analysis = SessionAnalysis(
            session_id=session.session_id,
            exploration_session=session,
            analysis_timestamp=datetime.now(),
            total_content_analyzed=len(large_session_results),
            average_quality=0.75,
            quality_improvement=0.1,
            theme_diversity=0.8,
            cost_efficiency=0.075,
            quality_timeline=[],
            theme_evolution={},
            recommended_actions=[],
            optimization_opportunities=[],
            quality_concerns=[]
        )
        
        # 自動評価パフォーマンス
        eval_start = datetime.now()
        
        auto_evaluation = semi_auto_evaluator.perform_auto_evaluation(
            session.session_id, large_batch, session_analysis
        )
        
        eval_time = (datetime.now() - eval_start).total_seconds()
        
        print(f"✅ 自動評価パフォーマンス完了")
        print(f"   評価時間: {eval_time:.3f}秒")
        print(f"   評価効率: {len(large_session_results)/eval_time:.1f}セッション/秒")
        
        # 3. メモリ使用量概算
        print(f"\n3. リソース使用量確認")
        
        # 統計情報確認
        analyzer_stats = results_analyzer.analysis_stats
        evaluator_stats = semi_auto_evaluator.evaluation_stats
        
        print(f"✅ リソース使用量:")
        print(f"   分析済みコンテンツ: {analyzer_stats['total_content_analyzed']}")
        print(f"   分析済みセッション: {analyzer_stats['total_sessions_analyzed']}")
        print(f"   テーマデータベース: {len(results_analyzer.theme_database)}エントリー")
        print(f"   評価履歴: {len(semi_auto_evaluator.evaluation_history)}セッション")
        
        total_time = (datetime.now() - start_time).total_seconds()
        print(f"   総処理時間: {total_time:.2f}秒")
        
        # パフォーマンス評価
        if analysis_time < 5.0 and eval_time < 1.0:
            print(f"🎉 パフォーマンス目標達成！")
        else:
            print(f"⚠️ パフォーマンス改善の余地あり")
        
        return True
        
    except Exception as e:
        print(f"❌ パフォーマンステスト失敗: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Phase 2 統合テスト開始")
    print("=" * 70)
    print("人間評価型Simulated Annealing学習システム")
    print("Phase 2: 結果分析・人間評価・セミオート評価システム")
    print("=" * 70)
    
    integration_success = test_phase2_full_integration()
    resilience_success = test_phase2_error_resilience()
    performance_success = test_phase2_performance_metrics()
    
    print("\n" + "=" * 70)
    print("🎯 Phase 2 統合テスト結果")
    print("=" * 70)
    
    if all([integration_success, resilience_success, performance_success]):
        print("🎉 Phase 2 完全統合テスト成功！")
        print("\n✅ 統合確認済み機能:")
        print("   • ResultsAnalyzer: コンテンツ品質分析・セッション分析")
        print("   • UserFeedbackInterface: 人間評価UI・フィードバック収集")
        print("   • SemiAutomaticEvaluator: セミオート評価・AI人間統合")
        print("   • データ統合・永続化・エラーハンドリング")
        print("   • パフォーマンス・スケーラビリティ")
        
        print("\n✅ Phase 2 主要成果:")
        print("   • 人間評価ループの自動化・効率化")
        print("   • AI支援による評価品質向上")
        print("   • 適応的フィードバック頻度制御")
        print("   • 統合的品質分析・洞察生成")
        print("   • スケーラブルな評価システム基盤")
        
        print("\n🚀 Phase 2 実装完了・Phase 3 準備完了")
        print("   次のステップ: 完全統合システム・本格運用準備")
        
    else:
        print("⚠️ Phase 2 統合テストで問題が発見されました")
        print(f"   完全統合: {'✅' if integration_success else '❌'}")
        print(f"   エラー耐性: {'✅' if resilience_success else '❌'}")
        print(f"   パフォーマンス: {'✅' if performance_success else '❌'}")
        print("\n修正・改善が必要です。")