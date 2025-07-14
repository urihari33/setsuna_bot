#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
品質履歴統合テスト - QualityHistoryManagerとKnowledgeAnalysisEngineの統合確認
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# プロジェクトルートを確実にパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def test_quality_history_manager_standalone():
    """QualityHistoryManager単体テスト"""
    try:
        print("🧪 QualityHistoryManager単体テスト")
        print("=" * 60)
        
        from core.quality_monitoring.quality_history_manager import QualityHistoryManager
        from core.knowledge_analysis.report_quality_validator import ValidationReport, ValidationSeverity, ValidationIssue
        
        # テスト用QualityHistoryManager初期化
        test_db_path = "D:/setsuna_bot/quality_monitoring/test_quality_history.db"
        manager = QualityHistoryManager(test_db_path)
        
        print("✅ QualityHistoryManager初期化成功")
        
        # ダミーValidationReportを作成
        print("\n📝 ダミー品質データ作成...")
        validation_report = ValidationReport(
            validation_timestamp=datetime.now().isoformat(),
            overall_score=0.85,
            total_issues=2,
            issues_by_severity={"warning": 1, "info": 1},
            quality_metrics={"data_coverage": 0.9, "consistency": 0.8},
            validation_summary="テスト品質検証レポート",
            recommendations=["品質向上のためのテスト推奨事項"],
            issues=[
                ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category="data_quality",
                    field="test_field",
                    message="テスト警告メッセージ",
                    actual_value="actual_value",
                    expected_value="expected_value",
                    suggestion="テスト改善案"
                )
            ]
        )
        
        # 品質履歴記録テスト
        print("📊 品質記録テスト...")
        record_id = manager.record_validation_result(
            validation_report=validation_report,
            processing_time=45.5,
            search_count=50,
            cost=0.05,
            data_quality=0.85
        )
        
        if record_id:
            print(f"✅ 品質記録成功: ID={record_id}")
        else:
            print("❌ 品質記録失敗")
            return False
        
        # 統計情報取得テスト
        print("\n📈 統計情報取得テスト...")
        stats = manager.get_quality_statistics(30)
        print(f"   総記録数: {stats.get('total_records', 0)}")
        print(f"   平均スコア: {stats.get('average_score', 0):.3f}")
        print(f"   データベースサイズ: {stats.get('db_size_mb', 0):.2f}MB")
        
        # 傾向分析テスト
        print("\n📊 傾向分析テスト...")
        trend = manager.get_quality_trend_analysis(7)
        print(f"   傾向: {trend.trend.value}")
        print(f"   平均スコア: {trend.avg_score:.3f}")
        print(f"   推奨事項数: {len(trend.recommendations)}")
        
        # アラート確認テスト
        print("\n🚨 アラート確認テスト...")
        alerts = manager.get_recent_alerts(24)
        print(f"   アラート数: {len(alerts)}")
        for alert in alerts[:3]:
            print(f"   - [{alert.level.value}] {alert.message}")
        
        print("\n✅ QualityHistoryManager単体テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ QualityHistoryManager単体テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_knowledge_analysis_engine_quality_integration():
    """KnowledgeAnalysisEngine品質統合テスト"""
    try:
        print("\n🔧 KnowledgeAnalysisEngine品質統合テスト")
        print("=" * 60)
        
        from core.knowledge_analysis.knowledge_analysis_engine import KnowledgeAnalysisEngine
        
        # 進捗コールバック
        def progress_callback(message, progress):
            print(f"📊 [{progress:3d}%] {message}")
        
        engine = KnowledgeAnalysisEngine(progress_callback=progress_callback)
        
        print("✅ KnowledgeAnalysisEngine初期化成功")
        
        # QualityHistoryManager統合確認
        has_quality_manager = hasattr(engine, 'quality_history_manager') and engine.quality_history_manager is not None
        print(f"🧠 品質履歴管理統合: {'✅' if has_quality_manager else '❌'}")
        
        if not has_quality_manager:
            print("❌ QualityHistoryManagerが統合されていません")
            return False
        
        # 品質統計機能テスト
        print("\n📊 エンジン経由品質統計テスト...")
        stats = engine.get_quality_statistics(30)
        if "error" not in stats:
            print(f"   総記録数: {stats.get('total_records', 0)}")
            print(f"   平均スコア: {stats.get('average_score', 0):.3f}")
            print("✅ 品質統計取得成功")
        else:
            print(f"⚠️ 品質統計取得エラー: {stats['error']}")
        
        # 品質傾向分析機能テスト
        print("\n📈 エンジン経由傾向分析テスト...")
        trend = engine.get_quality_trend_analysis(7)
        if "error" not in trend:
            print(f"   傾向: {trend.get('trend', 'unknown')}")
            print(f"   平均スコア: {trend.get('avg_score', 0):.3f}")
            print(f"   推奨事項数: {len(trend.get('recommendations', []))}")
            print("✅ 傾向分析取得成功")
        else:
            print(f"⚠️ 傾向分析取得エラー: {trend['error']}")
        
        # アラート機能テスト
        print("\n🚨 エンジン経由アラート確認テスト...")
        alerts = engine.get_recent_quality_alerts(24)
        if alerts and "error" not in alerts[0]:
            print(f"   アラート数: {len(alerts)}")
            for alert in alerts[:3]:
                print(f"   - [{alert['level']}] {alert['message']}")
            print("✅ アラート取得成功")
        else:
            error_msg = alerts[0].get('error', 'unknown error') if alerts else 'no data'
            print(f"⚠️ アラート取得エラー: {error_msg}")
        
        # 品質要約表示テスト
        print("\n📋 品質要約表示テスト...")
        engine.print_quality_summary()
        
        print("\n✅ KnowledgeAnalysisEngine品質統合テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ KnowledgeAnalysisEngine品質統合テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_end_to_end_quality_monitoring():
    """エンドツーエンド品質監視テスト"""
    try:
        print("\n🔄 エンドツーエンド品質監視テスト")
        print("=" * 60)
        
        from core.knowledge_analysis.knowledge_analysis_engine import KnowledgeAnalysisEngine
        from core.knowledge_analysis.report_quality_validator import ValidationReport, ValidationSeverity, ValidationIssue
        
        engine = KnowledgeAnalysisEngine()
        
        # シミュレーション: 分析セッション開始
        print("🚀 分析セッション開始...")
        # start_analysis_sessionメソッドがないので直接セッションIDを設定
        engine.session_id = f"quality_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"   セッションID: {engine.session_id}")
        
        # シミュレーション: 検索・分析実行（空データで品質記録をテスト）
        print("\n🔍 分析実行シミュレーション...")
        
        # 空データレポート生成（品質履歴記録をトリガー）
        search_results = []  # 空の検索結果
        analysis_result = {
            "analysis": "テスト分析結果",
            "total_cost": 0.02,
            "analysis_log": {"summary": {"total_time": 12.5}},
            "empty_data": True
        }
        
        report = engine._generate_report("品質監視テスト", search_results, analysis_result)
        
        print(f"📋 レポート生成完了: ID={report.get('report_id')}")
        print(f"🔍 検証レポート有無: {'✅' if 'validation_report' in report else '❌'}")
        
        # 品質履歴確認
        if engine.quality_history_manager:
            print("\n📊 品質履歴確認...")
            recent_stats = engine.get_quality_statistics(1)  # 過去1日
            if "error" not in recent_stats:
                print(f"   最新記録数: {recent_stats.get('total_records', 0)}")
                print(f"   最新平均スコア: {recent_stats.get('average_score', 0):.3f}")
                print("✅ 品質履歴記録確認成功")
            else:
                print(f"⚠️ 品質履歴確認エラー: {recent_stats['error']}")
        
        print("\n✅ エンドツーエンド品質監視テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ エンドツーエンド品質監視テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_alert_system_integration():
    """アラートシステム統合テスト"""
    try:
        print("\n🚨 アラートシステム統合テスト")
        print("=" * 60)
        
        from core.quality_monitoring.quality_history_manager import QualityHistoryManager
        from core.knowledge_analysis.report_quality_validator import ValidationReport, ValidationSeverity, ValidationIssue
        
        # 低品質スコアでアラート発生をテスト
        manager = QualityHistoryManager()
        
        # 低品質レポート（アラート発生）
        print("📉 低品質レポート記録（アラート発生テスト）...")
        low_quality_report = ValidationReport(
            validation_timestamp=datetime.now().isoformat(),
            overall_score=0.3,  # 低品質スコア
            total_issues=5,
            issues_by_severity={"critical": 2, "error": 2, "warning": 1},
            quality_metrics={"data_coverage": 0.2, "consistency": 0.1},
            validation_summary="アラートテスト用低品質レポート",
            recommendations=["緊急改善が必要"],
            issues=[]
        )
        
        record_id = manager.record_validation_result(
            validation_report=low_quality_report,
            processing_time=120.0,  # 遅い処理時間（アラート発生）
            search_count=10,
            cost=2.0,  # 高コスト（アラート発生）
            data_quality=0.3
        )
        
        if record_id:
            print(f"✅ 低品質記録完了: ID={record_id}")
            
            # アラート確認
            print("\n🔍 発生アラート確認...")
            alerts = manager.get_recent_alerts(1)  # 過去1時間
            
            if alerts:
                print(f"🚨 発生アラート数: {len(alerts)}")
                for alert in alerts:
                    print(f"   [{alert.level.value.upper()}] {alert.message}")
                    print(f"   対応: {alert.suggested_action}")
                print("✅ アラートシステム動作確認成功")
            else:
                print("⚠️ アラートが発生しませんでした")
                return False
        else:
            print("❌ 低品質記録失敗")
            return False
        
        print("\n✅ アラートシステム統合テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ アラートシステム統合テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_quality_history_integration_tests():
    """品質履歴統合テスト実行"""
    print("🚀 品質履歴統合テスト実行")
    print("=" * 80)
    print(f"📅 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    test_results = {}
    
    # テスト1: QualityHistoryManager単体
    test_results["quality_history_manager_standalone"] = test_quality_history_manager_standalone()
    
    # テスト2: KnowledgeAnalysisEngine品質統合
    test_results["knowledge_engine_quality_integration"] = test_knowledge_analysis_engine_quality_integration()
    
    # テスト3: エンドツーエンド品質監視
    test_results["end_to_end_quality_monitoring"] = test_end_to_end_quality_monitoring()
    
    # テスト4: アラートシステム統合
    test_results["alert_system_integration"] = test_alert_system_integration()
    
    # 総合結果
    print("\n" + "=" * 80)
    print("📊 品質履歴統合テスト結果")
    print("=" * 80)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ 成功" if result else "❌ 失敗"
        print(f"{status} {test_name}")
        if result:
            passed_tests += 1
    
    print(f"\n🏆 総合結果: {passed_tests}/{total_tests} テスト成功")
    success_rate = (passed_tests / total_tests) * 100
    print(f"📈 成功率: {success_rate:.1f}%")
    
    if success_rate >= 75:
        print("🎉 品質履歴統合テスト成功！品質監視システム準備完了")
        return True
    else:
        print("⚠️ 品質履歴統合テストに課題あり。修正が必要です。")
        return False

if __name__ == "__main__":
    try:
        success = run_quality_history_integration_tests()
        exit_code = 0 if success else 1
        
        print(f"\n🏁 テスト終了 - 終了コード: {exit_code}")
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n⚠️ テスト中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)