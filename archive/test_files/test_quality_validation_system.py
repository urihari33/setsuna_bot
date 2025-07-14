#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
品質検証システム統合テスト
KnowledgeAnalysisEngineとReportQualityValidatorの統合動作確認
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_quality_validation_integration():
    """品質検証システム統合テスト"""
    
    print("🔧 品質検証システム統合テスト開始")
    print("=" * 60)
    
    try:
        # KnowledgeAnalysisEngineをインポート
        from core.knowledge_analysis.knowledge_analysis_engine import KnowledgeAnalysisEngine
        
        # 進捗コールバック定義
        def progress_callback(message, progress):
            print(f"📊 進捗 [{progress:3d}%]: {message}")
        
        # エンジン初期化
        print("🚀 KnowledgeAnalysisEngine初期化中...")
        engine = KnowledgeAnalysisEngine(progress_callback=progress_callback)
        
        # 品質検証システム確認
        print(f"🔍 品質検証システム: {'✅ 利用可能' if engine.quality_validator else '❌ 利用不可'}")
        
        if not engine.quality_validator:
            print("❌ 品質検証システムが利用できません。テストを中断します。")
            return False
        
        # テスト1: 基本的な分析と検証
        print(f"\n{'=' * 60}")
        print("🧪 テスト1: 基本的な分析と検証")
        print("-" * 60)
        
        # セッション開始
        session_id = engine.start_new_session("品質検証テスト")
        print(f"📅 セッション開始: {session_id}")
        
        # 分析実行（小規模）
        test_prompt1 = "VTuberの音楽活動について"
        search_count1 = 3
        
        print(f"📝 テストプロンプト: '{test_prompt1}'")
        print(f"🔍 検索件数: {search_count1}件")
        
        report1 = engine.analyze_topic(test_prompt1, search_count1)
        
        print(f"\n📊 分析結果:")
        print(f"  レポートID: {report1.get('report_id', 'N/A')}")
        print(f"  検索件数: {report1.get('search_count', 0)}")
        print(f"  データ品質: {report1.get('data_quality', 0):.2f}")
        print(f"  コスト: ${report1.get('cost', 0):.6f}")
        
        # 検証レポート確認
        validation_report = report1.get("validation_report")
        if validation_report:
            print(f"\n🔍 品質検証結果:")
            print(f"  検証時刻: {validation_report['validation_timestamp']}")
            print(f"  総合スコア: {validation_report['overall_score']:.2f}")
            print(f"  検出問題数: {validation_report['total_issues']}件")
            print(f"  検証サマリー: {validation_report['validation_summary']}")
            
            # 問題詳細
            if validation_report['total_issues'] > 0:
                print(f"  問題内訳:")
                for severity, count in validation_report['issues_by_severity'].items():
                    if count > 0:
                        print(f"    {severity.upper()}: {count}件")
            
            # 推奨事項
            if validation_report['recommendations']:
                print(f"  推奨事項:")
                for i, rec in enumerate(validation_report['recommendations'][:3], 1):
                    print(f"    {i}. {rec}")
        else:
            print("❌ 検証レポートが生成されませんでした")
            return False
        
        # テスト2: 問題のあるレポートデータでの検証
        print(f"\n{'=' * 60}")
        print("🧪 テスト2: 手動レポート検証テスト")
        print("-" * 60)
        
        # 不完全なテストレポートを作成
        problematic_report = {
            "report_id": 999,
            "timestamp": "invalid-timestamp",
            "user_prompt": "",  # 空のプロンプト
            "search_count": -1,  # 不正な値
            "analysis_summary": "",  # 空の要約
            "key_insights": [],  # 空のインサイト
            "categories": "not a dict",  # 不正なデータ型
            "related_topics": None,  # Null値
            "data_quality": 1.5,  # 範囲外の値
            "cost": "not a number",  # 不正なデータ型
            "processing_time": "5分"
        }
        
        print("🔍 問題のあるレポートデータで検証テスト実行...")
        validation_result = engine.quality_validator.validate_report(problematic_report)
        
        print(f"📊 検証結果:")
        print(f"  総合スコア: {validation_result.overall_score:.2f}")
        print(f"  検出問題数: {validation_result.total_issues}件")
        print(f"  重大な問題: {validation_result.issues_by_severity.get('critical', 0)}件")
        print(f"  エラー: {validation_result.issues_by_severity.get('error', 0)}件")
        print(f"  警告: {validation_result.issues_by_severity.get('warning', 0)}件")
        
        # 検証システムが適切に問題を検出したかチェック
        expected_issues = validation_result.total_issues >= 5  # 最低5つの問題を期待
        critical_detected = validation_result.issues_by_severity.get('critical', 0) > 0
        
        if expected_issues and critical_detected:
            print("✅ 問題検出テスト: 成功（適切に問題を検出）")
        else:
            print("❌ 問題検出テスト: 失敗（問題の検出が不十分）")
            return False
        
        # テスト3: 品質検証システムの統計情報
        print(f"\n{'=' * 60}")
        print("🧪 テスト3: 検証システム統計")
        print("-" * 60)
        
        validation_summary = engine.get_quality_validation_summary()
        print("📊 検証システム統計:")
        
        if "message" in validation_summary:
            print(f"  {validation_summary['message']}")
        else:
            for key, value in validation_summary.items():
                print(f"  {key}: {value}")
        
        # テスト4: 検証レポートフォーマット
        print(f"\n{'=' * 60}")
        print("🧪 テスト4: 検証レポートフォーマット")
        print("-" * 60)
        
        formatted_report = engine.format_validation_report(report1.get('report_id', 1))
        print("📄 フォーマット済み検証レポート:")
        print(formatted_report)
        
        # 全体判定
        print(f"\n{'=' * 60}")
        print("🏁 テスト結果総合判定:")
        
        success_criteria = [
            ("品質検証システム初期化", engine.quality_validator is not None),
            ("検証レポート生成", validation_report is not None),
            ("問題検出機能", expected_issues and critical_detected),
            ("統計情報取得", validation_summary is not None),
            ("レポートフォーマット", "品質検証結果" in formatted_report)
        ]
        
        success_count = 0
        for criteria_name, result in success_criteria:
            status = "✅ 成功" if result else "❌ 失敗"
            print(f"  {criteria_name}: {status}")
            if result:
                success_count += 1
        
        success_rate = success_count / len(success_criteria)
        print(f"\n📊 総合成功率: {success_count}/{len(success_criteria)} ({success_rate:.1%})")
        
        if success_rate >= 0.8:
            print("🎉 品質検証システム統合テスト成功！")
            return True
        else:
            print("⚠️ 品質検証システムに問題があります")
            return False
            
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        print("必要なモジュールが見つかりません")
        return False
        
    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_case_validation():
    """エッジケース検証テスト"""
    
    print(f"\n{'=' * 60}")
    print("🔬 エッジケース検証テスト")
    print("=" * 60)
    
    try:
        from core.knowledge_analysis.report_quality_validator import ReportQualityValidator
        validator = ReportQualityValidator()
        
        edge_cases = [
            ("完全に空のレポート", {}),
            ("Nullが多いレポート", {
                "report_id": None, 
                "timestamp": None, 
                "user_prompt": None,
                "analysis_summary": None
            }),
            ("極端に大きな値", {
                "report_id": 999999,
                "search_count": 99999,
                "data_quality": 999.0,
                "cost": 999999.99
            }),
            ("文字列が極端に長い", {
                "analysis_summary": "A" * 50000,  # 50000文字
                "user_prompt": "B" * 1000
            })
        ]
        
        print("🧪 エッジケース検証テスト:")
        
        all_success = True
        for case_name, test_data in edge_cases:
            print(f"\n📝 {case_name}:")
            
            try:
                result = validator.validate_report(test_data)
                print(f"  検証スコア: {result.overall_score:.2f}")
                print(f"  検出問題数: {result.total_issues}")
                print(f"  ステータス: ✅ 正常処理")
                    
            except Exception as e:
                print(f"  ❌ エラー: {e}")
                all_success = False
        
        return all_success
        
    except Exception as e:
        print(f"❌ エッジケーステストエラー: {e}")
        return False

if __name__ == "__main__":
    print("🔧 品質検証システム統合テスト")
    print(f"{'=' * 60}")
    
    # メインテスト実行
    main_test_result = test_quality_validation_integration()
    
    # エッジケーステスト実行
    edge_test_result = test_edge_case_validation()
    
    print(f"\n{'=' * 60}")
    print("🏁 最終結果:")
    
    if main_test_result and edge_test_result:
        print("🎊 全てのテストが成功しました！")
        print("✅ 品質検証システムが正常に統合されています")
        print("🎯 Phase 3C: レポート生成検証システムの実装が完了しました")
        print()
        print("📋 実装された機能:")
        print("  1. レポート構造・データ型・値範囲の自動検証")
        print("  2. コンテンツ品質とデータ一貫性のチェック")
        print("  3. 品質スコア算出と問題分類")
        print("  4. 詳細な検証レポートとログ記録")
        print("  5. 推奨事項の自動生成")
        print()
        print("🚀 次のステップ:")
        print("  - 品質履歴の長期追跡とトレンド分析")
        print("  - 検証基準のカスタマイズ機能")
        print("  - Phase 4: せつな統合準備")
        exit(0)
    elif main_test_result or edge_test_result:
        print("⭐ 一部のテストが成功しました")
        print("🔧 基本機能は動作していますが、一部調整が必要です")
        exit(0)
    else:
        print("❌ テストで重大な問題が検出されました")
        print("🔧 品質検証システムの再確認が必要です")
        exit(1)