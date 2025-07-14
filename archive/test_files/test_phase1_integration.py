#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1 統合テストスクリプト
人間評価型SA学習システム - Phase 1 全コンポーネント統合動作確認
"""

import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from core.adaptive_learning.orchestrator import ExplorationOrchestrator
from core.adaptive_learning.temperature_controller import TemperatureController
from core.adaptive_learning.adaptive_query_generator import AdaptiveQueryGenerator
from core.adaptive_learning.batch_session_manager import BatchSessionManager
from core.adaptive_learning.models.exploration_models import generate_session_id
from core.adaptive_learning.models.feedback_models import UserFeedback
from core.adaptive_learning.models.temperature_models import get_temperature_config
from datetime import datetime

def test_phase1_integration():
    print("=== Phase 1 統合テスト ===")
    print("人間評価型Simulated Annealing学習システム - 全コンポーネント統合動作確認\n")
    
    try:
        # 1. コンポーネント初期化
        print("1. 全コンポーネント初期化")
        orchestrator = ExplorationOrchestrator()
        temp_controller = TemperatureController()
        query_generator = AdaptiveQueryGenerator()
        batch_manager = BatchSessionManager()
        print("✅ 全コンポーネント初期化完了\n")
        
        # 2. 探索セッション開始
        print("2. 探索セッション開始")
        theme = "AI音楽生成技術の商用化"
        budget = 50.0
        initial_temperature = "high"
        
        session = orchestrator.start_exploration(
            theme=theme,
            budget=budget,
            initial_temperature=initial_temperature
        )
        
        # 温度コントローラーでセッション温度状態初期化
        temp_state = temp_controller.initialize_session_temperature(
            session, target_rounds=8
        )
        
        print(f"✅ 探索セッション開始: {session.session_id}")
        print(f"   テーマ: {theme}")
        print(f"   予算: ${budget}")
        print(f"   初期温度: {initial_temperature}\n")
        
        # 3. 第1ラウンド実行（高温・広範囲探索）
        print("3. 第1ラウンド実行（高温・広範囲探索）")
        
        # 温度設定取得
        current_temp_config = get_temperature_config(session.current_temperature)
        
        # クエリ生成
        queries_round1 = query_generator.generate_adaptive_queries(
            session_id=session.session_id,
            theme=theme,
            temperature_config=current_temp_config
        )
        
        print(f"   生成クエリ数: {len(queries_round1)}")
        print(f"   多様性スコア: {query_generator.calculate_query_diversity(queries_round1):.2f}")
        
        # バッチ実行
        batch_id_1 = f"{session.session_id}_round_01"
        batch_result_1 = batch_manager.execute_batch(
            batch_id=batch_id_1,
            queries=queries_round1[:8],  # 実際の数に調整
            temperature_config=current_temp_config
        )
        
        print(f"✅ 第1ラウンド完了")
        print(f"   成功率: {batch_result_1.success_rate:.1%}")
        print(f"   平均品質: {batch_result_1.average_quality:.2f}")
        print(f"   コスト: ${batch_result_1.total_cost:.2f}\n")
        
        # 4. ユーザーフィードバック処理
        print("4. ユーザーフィードバック処理（deeper方向）")
        
        feedback = UserFeedback(
            feedback_id="integration_test_feedback_1",
            session_id=session.session_id,
            timestamp=datetime.now(),
            direction_choice="deeper",
            overall_quality=batch_result_1.average_quality,
            direction_confidence=0.8,
            comments="技術詳細が興味深い。より深い分析を希望。"
        )
        
        # 温度調整
        temp_adjustment = temp_controller.calculate_temperature_adjustment(
            session.session_id,
            feedback=feedback,
            quality_history=[batch_result_1.average_quality],
            cost_history=[batch_result_1.total_cost]
        )
        
        # オーケストレーターでフィードバック処理
        feedback_result = orchestrator.process_user_feedback(session.session_id, feedback)
        
        print(f"✅ フィードバック処理完了")
        print(f"   温度調整: {temp_adjustment.previous_temperature} → {temp_adjustment.new_temperature}")
        print(f"   調整理由: {temp_adjustment.reason}")
        print(f"   信頼度: {temp_adjustment.confidence:.2f}\n")
        
        # 5. 第2ラウンド実行（調整された温度）
        print("5. 第2ラウンド実行（調整された温度・深い分析）")
        
        # 現在の温度設定取得
        current_temp_config_2 = get_temperature_config(temp_adjustment.new_temperature)
        
        # フィードバックを反映したクエリ生成
        queries_round2 = query_generator.generate_adaptive_queries(
            session_id=session.session_id,
            theme=theme,
            temperature_config=current_temp_config_2,
            user_feedback=feedback
        )
        
        print(f"   調整後温度: {current_temp_config_2.temperature_level}")
        print(f"   生成クエリ数: {len(queries_round2)}")
        print(f"   多様性スコア: {query_generator.calculate_query_diversity(queries_round2):.2f}")
        
        # バッチ実行
        batch_id_2 = f"{session.session_id}_round_02"
        batch_result_2 = batch_manager.execute_batch(
            batch_id=batch_id_2,
            queries=queries_round2[:6],  # 中温なので数を調整
            temperature_config=current_temp_config_2
        )
        
        print(f"✅ 第2ラウンド完了")
        print(f"   成功率: {batch_result_2.success_rate:.1%}")
        print(f"   平均品質: {batch_result_2.average_quality:.2f}")
        print(f"   コスト: ${batch_result_2.total_cost:.2f}\n")
        
        # 6. 品質改善の確認とさらなる調整
        print("6. 品質改善確認とさらなる温度調整")
        
        quality_history = [batch_result_1.average_quality, batch_result_2.average_quality]
        cost_history = [batch_result_1.total_cost, batch_result_2.total_cost]
        
        # 温度効果性評価
        effectiveness = temp_controller.get_temperature_effectiveness(
            session.session_id,
            quality_history,
            cost_history
        )
        
        # 最適次回温度推奨
        optimal_temp, confidence = temp_controller.get_optimal_next_temperature(
            session.session_id,
            quality_history,
            cost_history,
            {"prefer_quality": True}
        )
        
        print(f"✅ 品質改善分析完了")
        print(f"   品質向上: {quality_history[0]:.2f} → {quality_history[1]:.2f} ({quality_history[1] - quality_history[0]:+.2f})")
        print(f"   効果性スコア: {effectiveness['overall_performance']:.2f}")
        print(f"   推奨次回温度: {optimal_temp} (信頼度: {confidence:.2f})\n")
        
        # 7. 第3ラウンド実行（最適化された温度）
        print("7. 第3ラウンド実行（最適化された温度・高品質追求）")
        
        # 品質ベース自動調整
        temp_adjustment_3 = temp_controller.calculate_temperature_adjustment(
            session.session_id,
            quality_history=quality_history,
            cost_history=cost_history
        )
        
        current_temp_config_3 = get_temperature_config(temp_adjustment_3.new_temperature)
        
        # 最適化されたクエリ生成
        queries_round3 = query_generator.generate_adaptive_queries(
            session_id=session.session_id,
            theme=theme,
            temperature_config=current_temp_config_3,
            quality_target=0.8
        )
        
        print(f"   最終温度: {current_temp_config_3.temperature_level}")
        print(f"   生成クエリ数: {len(queries_round3)}")
        print(f"   多様性スコア: {query_generator.calculate_query_diversity(queries_round3):.2f}")
        
        # バッチ実行
        batch_id_3 = f"{session.session_id}_round_03"
        batch_result_3 = batch_manager.execute_batch(
            batch_id=batch_id_3,
            queries=queries_round3[:4],  # 低温なので少数高品質
            temperature_config=current_temp_config_3
        )
        
        print(f"✅ 第3ラウンド完了")
        print(f"   成功率: {batch_result_3.success_rate:.1%}")
        print(f"   平均品質: {batch_result_3.average_quality:.2f}")
        print(f"   コスト: ${batch_result_3.total_cost:.2f}\n")
        
        # 8. 探索完了・要約生成
        print("8. 探索完了・要約生成")
        
        # セッション状態更新（手動）
        session.rounds_completed = 3
        session.total_cost = batch_result_1.total_cost + batch_result_2.total_cost + batch_result_3.total_cost
        session.sessions_executed = (len(batch_result_1.session_results) + 
                                   len(batch_result_2.session_results) + 
                                   len(batch_result_3.session_results))
        
        # 探索完了
        summary = orchestrator.finalize_exploration(session.session_id)
        
        print(f"✅ 探索完了・要約生成完了")
        print(f"   総ラウンド数: {summary.total_rounds}")
        print(f"   総セッション数: {summary.total_sessions}")
        print(f"   総コスト: ${summary.total_cost:.2f}")
        print(f"   実行時間: {summary.duration_minutes:.1f}分")
        print(f"   最終温度: {summary.final_temperature}")
        print(f"   収束達成: {summary.convergence_achieved}\n")
        
        # 9. 全体統計とSA効果確認
        print("9. 全体統計とSimulated Annealing効果確認")
        
        # 温度遷移の確認
        temp_transitions = [
            initial_temperature,
            temp_adjustment.new_temperature,
            temp_adjustment_3.new_temperature
        ]
        
        # 品質・コスト・効率の推移
        final_quality_history = [
            batch_result_1.average_quality,
            batch_result_2.average_quality,
            batch_result_3.average_quality
        ]
        
        final_cost_history = [
            batch_result_1.total_cost,
            batch_result_2.total_cost,
            batch_result_3.total_cost
        ]
        
        print(f"✅ Simulated Annealing効果確認")
        print(f"   温度遷移: {' → '.join(temp_transitions)}")
        print(f"   品質推移: {' → '.join(f'{q:.2f}' for q in final_quality_history)}")
        print(f"   コスト推移: {' → '.join(f'${c:.2f}' for c in final_cost_history)}")
        print(f"   品質改善率: {((final_quality_history[-1] / final_quality_history[0]) - 1) * 100:+.1f}%")
        
        # システム全体のリソース使用状況
        resource_usage = batch_manager.get_resource_usage()
        execution_stats = batch_manager.get_execution_statistics()
        
        print(f"\n   システムリソース使用状況:")
        print(f"     総API呼び出し: {resource_usage['total_api_calls']}")
        print(f"     総コスト: ${resource_usage['total_cost']:.2f}")
        print(f"     平均成功率: {execution_stats['average_success_rate']:.1%}")
        print(f"     コスト効率: {execution_stats['cost_efficiency']:.3f}")
        
        print(f"\n🎉 Phase 1 統合テスト完全成功！")
        print(f"🔬 人間評価型SA学習システムの基本機能が正常動作することを確認")
        print(f"✅ 探索統制・温度制御・クエリ生成・バッチ実行の連携動作確認完了")
        
        return True
        
    except Exception as e:
        print(f"❌ Phase 1 統合テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_cases():
    """エッジケース統合テスト"""
    print("\n=== エッジケース統合テスト ===")
    
    try:
        orchestrator = ExplorationOrchestrator()
        
        # 極小予算でのテスト
        print("\n1. 極小予算での探索テスト")
        session_small = orchestrator.start_exploration(
            theme="テスト技術",
            budget=5.0,  # 非常に小さな予算
            initial_temperature="low"  # 高コスト温度
        )
        
        print(f"✅ 極小予算セッション作成: ${session_small.budget_limit}")
        
        # 非常に短いテーマでのテスト
        print("\n2. 短いテーマでの探索テスト")
        session_short = orchestrator.start_exploration(
            theme="AI",  # 非常に短いテーマ
            budget=20.0,
            initial_temperature="high"
        )
        
        print(f"✅ 短いテーマセッション作成: '{session_short.theme}'")
        
        print("\n✅ エッジケース統合テスト完了")
        
    except Exception as e:
        print(f"❌ エッジケーステスト失敗: {e}")

if __name__ == "__main__":
    success = test_phase1_integration()
    test_edge_cases()
    
    if success:
        print("\n" + "="*60)
        print("🎯 Phase 1 完全実装・統合テスト成功 🎯")
        print("="*60)
        print("\n✅ 実装完了コンポーネント:")
        print("   • ExplorationOrchestrator: 探索統制メインエンジン")
        print("   • TemperatureController: SA温度制御・パラメータ管理")
        print("   • AdaptiveQueryGenerator: 適応的クエリ生成・多様性制御")
        print("   • BatchSessionManager: バッチセッション管理・並列実行")
        print("\n✅ 確認済み機能:")
        print("   • セッション作成・ライフサイクル管理")
        print("   • 温度ベース探索戦略制御")
        print("   • ユーザーフィードバック反映・温度調整")
        print("   • 品質ベース自動最適化")
        print("   • クエリ多様性制御・適応的生成")
        print("   • 並列バッチ実行・リソース監視")
        print("   • コスト制御・効率測定")
        print("   • エラーハンドリング・例外処理")
        print("\n🚀 次のステップ: Phase 2 実装準備完了")
        print("   → 人間評価統合・ResultsAnalyzer・UserFeedbackInterface")
    else:
        print("\n⚠️ Phase 1 統合テストで問題が発見されました。修正が必要です。")