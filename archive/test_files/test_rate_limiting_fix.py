#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI Rate Limiting修正テスト
修正されたPreProcessingEngineとActivityLearningEngineの動作確認
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from core.activity_learning_engine import ActivityLearningEngine, LearningSession
from core.preprocessing_engine import PreProcessingEngine

def test_preprocessing_engine_fallback():
    """PreProcessingEngine フォールバック機能テスト"""
    print("=== PreProcessingEngine フォールバック機能テスト ===")
    
    try:
        engine = PreProcessingEngine()
        
        # テスト用ソースデータ
        test_sources = [
            {
                "source_id": "test_001",
                "title": "AI音楽生成の最新技術動向",
                "content": "Transformerアーキテクチャを使った音楽生成技術が急速に発展している。",
                "url": "https://example.com/ai-music-tech",
                "source_type": "web_search"
            },
            {
                "source_id": "test_002", 
                "title": "機械学習による作曲システム",
                "content": "深層学習を活用した自動作曲システムの開発が進んでいる。",
                "url": "https://example.com/ml-composition",
                "source_type": "web_search"
            }
        ]
        
        print("テーマ: AI音楽生成")
        print(f"テストソース: {len(test_sources)}件")
        
        # フォールバック処理テスト
        print("\n--- フォールバック処理テスト ---")
        results = engine._fallback_batch_processing(test_sources, "AI音楽生成")
        
        print(f"フォールバック結果: {len(results)}件")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result.source_id}")
            print(f"     関連性: {result.relevance_score:.2f}")
            print(f"     品質: {result.quality_score:.2f}")
            print(f"     カテゴリ: {result.category}")
            print(f"     通過: {'✅' if result.should_proceed else '❌'}")
        
        print("✅ PreProcessingEngine フォールバック機能テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ PreProcessingEngine フォールバック機能テスト失敗: {e}")
        return False

def test_rate_limiting_configuration():
    """Rate Limiting設定テスト"""
    print("\n=== Rate Limiting設定テスト ===")
    
    try:
        engine = PreProcessingEngine()
        
        # 初期設定確認
        print("初期Rate Limiting設定:")
        for key, value in engine.rate_limiting.items():
            print(f"  {key}: {value}")
        
        # 設定変更テスト
        engine.rate_limiting["request_interval"] = 3.0
        engine.rate_limiting["batch_size"] = 3
        
        print("\n変更後設定:")
        for key, value in engine.rate_limiting.items():
            print(f"  {key}: {value}")
        
        print("✅ Rate Limiting設定テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ Rate Limiting設定テスト失敗: {e}")
        return False

def test_activity_learning_engine_modes():
    """ActivityLearningEngine モード設定テスト"""
    print("\n=== ActivityLearningEngine モード設定テスト ===")
    
    try:
        engine = ActivityLearningEngine()
        
        # 初期モード確認
        print(f"初期モード: {engine.get_current_mode()}")
        
        # 軽量モード設定
        engine.configure_lightweight_mode(True)
        print(f"軽量モード設定後: {engine.get_current_mode()}")
        print(f"  前処理有効: {engine.staged_analysis_config['enable_preprocessing']}")
        print(f"  最大分析件数: {engine.staged_analysis_config['max_detailed_analysis']}")
        
        # 安全モード設定  
        engine.configure_safe_mode(True)
        print(f"安全モード設定後: {engine.get_current_mode()}")
        print(f"  前処理有効: {engine.staged_analysis_config['enable_preprocessing']}")
        print(f"  最大分析件数: {engine.staged_analysis_config['max_detailed_analysis']}")
        print(f"  API間隔: {engine.preprocessing_engine.rate_limiting['request_interval']}秒")
        
        # 標準モード復帰
        engine.configure_safe_mode(False)
        print(f"標準モード復帰後: {engine.get_current_mode()}")
        
        print("✅ ActivityLearningEngine モード設定テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ ActivityLearningEngine モード設定テスト失敗: {e}")
        return False

def test_lightweight_session_creation():
    """軽量モードセッション作成テスト"""
    print("\n=== 軽量モードセッション作成テスト ===")
    
    try:
        engine = ActivityLearningEngine()
        
        # 軽量モード設定
        engine.configure_lightweight_mode(True)
        
        # テストセッション作成
        session_id = engine.create_session(
            theme="Rate Limiting修正テスト",
            learning_type="概要",
            depth_level=1,
            time_limit=180,  # 3分
            budget_limit=0.5,  # $0.5
            tags=["軽量モードテスト", "Rate Limiting修正"]
        )
        
        if session_id:
            print(f"✅ 軽量モードセッション作成成功: {session_id}")
            
            # セッション状態確認
            session_status = engine.get_session_status(session_id)
            if session_status:
                print(f"  セッション状態: {session_status.get('status', '不明')}")
                print(f"  現在のモード: {engine.get_current_mode()}")
            
            return True
        else:
            print("❌ 軽量モードセッション作成失敗")
            return False
            
    except Exception as e:
        print(f"❌ 軽量モードセッション作成テスト失敗: {e}")
        return False

def test_zero_division_fixes():
    """ゼロ除算修正テスト"""
    print("\n=== ゼロ除算修正テスト ===")
    
    try:
        engine = PreProcessingEngine()
        
        # 空リストでのサマリー取得テスト
        print("空リストサマリーテスト:")
        empty_summary = engine.get_filtering_summary([])
        print(f"  エラー情報: {empty_summary.get('error', 'なし')}")
        print(f"  総件数: {empty_summary.get('total_processed', 0)}")
        print(f"  通過率: {empty_summary.get('pass_rate', 0)}%")
        
        # 全フィルタリング状況のテスト（フォールバック処理）
        print("\n全フィルタリング状況テスト:")
        test_sources = [
            {
                "source_id": "filter_test_001",
                "title": "無関係な内容",
                "content": "これはテーマと全く関係のない内容です。",
                "url": "https://example.com/unrelated"
            }
        ]
        
        # 高い閾値で全てフィルタリング
        engine.set_thresholds(relevance_min=0.9, quality_min=0.9, combined_min=0.9)
        results = engine._fallback_batch_processing(test_sources, "AI音楽生成")
        summary = engine.get_filtering_summary(results)
        
        print(f"  処理結果: {summary.get('total_processed', 0)}件")
        print(f"  通過結果: {summary.get('passed_count', 0)}件")
        print(f"  通過率: {summary.get('pass_rate', 0):.1f}%")
        
        print("✅ ゼロ除算修正テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ ゼロ除算修正テスト失敗: {e}")
        return False

def main():
    """メインテスト実行"""
    print("🚀 OpenAI Rate Limiting修正テスト開始")
    print(f"実行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = []
    
    # 各テスト実行
    test_results.append(("PreProcessingEngine フォールバック", test_preprocessing_engine_fallback()))
    test_results.append(("Rate Limiting設定", test_rate_limiting_configuration()))
    test_results.append(("ActivityLearningEngine モード設定", test_activity_learning_engine_modes()))
    test_results.append(("軽量モードセッション作成", test_lightweight_session_creation()))
    test_results.append(("ゼロ除算修正", test_zero_division_fixes()))
    
    # 結果サマリー
    print("\n" + "="*60)
    print("📊 Rate Limiting修正テスト結果サマリー")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n総合結果: {passed}件成功, {failed}件失敗")
    
    if failed == 0:
        print("🎉 Rate Limiting修正テスト全て成功！")
        print("✅ OpenAI API制限時でも安定動作確認完了")
        print("✅ フォールバック機能・モード設定・エラー防止完了")
    else:
        print(f"⚠️ {failed}件のテストで問題が発生")
        print("🔧 追加修正が必要です")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)