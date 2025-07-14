#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
デバッグシステム統合テスト
実装したデバッグログ機能の動作確認
"""

import sys
import os
import time
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_debug_logger():
    """デバッグロガーテスト"""
    print("=== デバッグロガーテスト ===")
    
    try:
        from core.debug_logger import get_debug_logger
        
        # テスト用ロガー作成
        logger = get_debug_logger("test_session", "DEBUG_TEST")
        
        # 各レベルのログテスト
        logger.debug("デバッグメッセージテスト", {'test_data': 'debug_value'})
        logger.info("情報メッセージテスト", {'test_data': 'info_value'})
        logger.warning("警告メッセージテスト", {'test_data': 'warning_value'})
        logger.error("エラーメッセージテスト", {'test_data': 'error_value'})
        
        # 専用ログ機能テスト
        logger.log_web_search(
            "テストクエリ",
            "https://api.duckduckgo.com/?q=test",
            200,
            5,
            {"test": "data"}
        )
        
        logger.log_session_phase(
            "test_phase",
            "completed",
            0.5,
            {"test_details": "test_value"}
        )
        
        # ログサマリー取得
        summary = logger.get_log_summary()
        print(f"✅ デバッグロガーテスト完了: {summary['total_logs']}件のログ")
        
        # 終了
        logger.close()
        
        return True
        
    except Exception as e:
        print(f"❌ デバッグロガーテストエラー: {e}")
        return False

def test_enhanced_learning_engine():
    """強化された学習エンジンテスト"""
    print("\n=== 強化された学習エンジンテスト ===")
    
    try:
        from core.activity_learning_engine import ActivityLearningEngine
        
        # エンジン初期化
        engine = ActivityLearningEngine()
        
        # テストセッション作成
        session_id = engine.create_session(
            theme="デバッグテスト",
            learning_type="概要",
            depth_level=2,
            time_limit=30,  # 30秒間テスト
            budget_limit=0.1,
            tags=["デバッグテスト"]
        )
        
        print(f"✅ テストセッション作成: {session_id}")
        
        # セッション開始
        success = engine.start_session(session_id)
        
        if success:
            print("✅ セッション開始成功")
            
            # 少し待機
            time.sleep(5)
            
            # セッション状態確認
            status = engine.get_session_status(session_id)
            if status:
                print(f"✅ セッション状態確認: {status['status']}")
            
            # 30秒後に状態確認
            time.sleep(30)
            
            final_status = engine.get_session_status(session_id)
            if final_status:
                print(f"✅ 最終状態: {final_status['status']}")
                print(f"   収集アイテム: {final_status['progress']['collected_items']}")
                print(f"   コスト: ${final_status['progress']['current_cost']:.2f}")
        
        return success
        
    except Exception as e:
        print(f"❌ 学習エンジンテストエラー: {e}")
        return False

def test_web_search_debug():
    """Web検索デバッグテスト"""
    print("\n=== Web検索デバッグテスト ===")
    
    try:
        from test_web_search_debug import WebSearchDebugger
        
        # デバッガー初期化
        debugger = WebSearchDebugger()
        
        # 単一クエリテスト
        result = debugger.test_single_query("AI技術")
        
        if result.success:
            print(f"✅ Web検索テスト成功: {result.results_count}件の結果")
        else:
            print(f"❌ Web検索テスト失敗: {result.error_message}")
        
        return result.success
        
    except Exception as e:
        print(f"❌ Web検索デバッグテストエラー: {e}")
        return False

def test_session_analyzer():
    """セッション分析ツールテスト"""
    print("\n=== セッション分析ツールテスト ===")
    
    try:
        from debug_session_analyzer import DebugSessionAnalyzer
        
        # 分析ツール初期化
        analyzer = DebugSessionAnalyzer()
        
        # 利用可能セッション確認
        sessions = analyzer.list_available_sessions()
        print(f"✅ 利用可能セッション: {len(sessions)}件")
        
        if sessions:
            # 最新セッション分析
            result = analyzer.analyze_session(sessions[0])
            
            if result and result.status == "completed":
                print(f"✅ セッション分析成功: {len(result.issues)}件の問題を検出")
                
                # 簡単なサマリー表示
                print(f"   問題: {result.issues[:2]}")  # 最初の2件
                print(f"   推奨事項: {result.recommendations[:2]}")  # 最初の2件
                
                return True
            else:
                print(f"❌ セッション分析失敗: {result.status if result else 'None'}")
        
        return False
        
    except Exception as e:
        print(f"❌ セッション分析ツールテストエラー: {e}")
        return False

def main():
    """メイン関数"""
    print("🔍 デバッグシステム統合テスト開始")
    print("=" * 50)
    
    test_results = {
        "debug_logger": False,
        "enhanced_learning_engine": False,
        "web_search_debug": False,
        "session_analyzer": False
    }
    
    # 各テスト実行
    test_results["debug_logger"] = test_debug_logger()
    test_results["enhanced_learning_engine"] = test_enhanced_learning_engine()
    test_results["web_search_debug"] = test_web_search_debug()
    test_results["session_analyzer"] = test_session_analyzer()
    
    # 結果サマリー
    print("\n" + "=" * 50)
    print("📊 デバッグシステムテスト結果")
    print("=" * 50)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:30}: {status}")
    
    print("-" * 50)
    print(f"総合結果: {passed_tests}/{total_tests} テスト通過")
    
    if passed_tests == total_tests:
        print("🎉 デバッグシステムが正常に動作しています！")
        print("\n💡 次のステップ:")
        print("  1. 実際の学習セッションを実行してデバッグログを確認")
        print("  2. debug_session_analyzer.py で問題を分析")
        print("  3. test_web_search_debug.py でWeb検索の詳細調査")
        
    elif passed_tests >= total_tests * 0.7:
        print("⚠️ デバッグシステムが部分的に動作しています")
        print("一部の機能で問題がありますが、基本的な機能は使用可能です")
        
    else:
        print("❌ デバッグシステムに重大な問題があります")
        print("複数の機能が動作していません。設定を確認してください")
    
    print("=" * 50)

if __name__ == "__main__":
    main()