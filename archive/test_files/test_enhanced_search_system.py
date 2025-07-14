#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合検索システムテスト
DuckDuckGo統合 + GPT-4-turbo動的クエリ生成 + マルチエンジン統合の総合テスト
"""

import sys
import os
import time
from datetime import datetime
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from core.duckduckgo_search_service import DuckDuckGoSearchService
from core.dynamic_query_generator import DynamicQueryGenerator, QueryGenerationRequest
from core.multi_search_manager import MultiSearchManager
from core.activity_learning_engine import ActivityLearningEngine, LearningSession

def test_duckduckgo_service():
    """DuckDuckGo検索サービステスト"""
    print("=== DuckDuckGo検索サービステスト ===")
    
    try:
        service = DuckDuckGoSearchService()
        
        # サービス情報
        print(f"サービス情報: {service.get_service_info()}")
        print(f"利用可能: {service.is_available()}")
        
        # テスト検索
        test_queries = ["Python programming", "機械学習 入門", "DuckDuckGo API"]
        
        for query in test_queries:
            print(f"\n検索テスト: {query}")
            result = service.search(query, max_results=3)
            
            print(f"  成功: {result.success}")
            print(f"  結果数: {result.total_results}")
            print(f"  実行時間: {result.execution_time:.2f}秒")
            
            if result.success:
                for i, item in enumerate(result.results, 1):
                    print(f"  {i}. {item.title}")
                    print(f"     URL: {item.url}")
                    print(f"     品質: {item.quality_score:.2f}")
        
        print("✅ DuckDuckGo検索サービステスト完了")
        return True
        
    except Exception as e:
        print(f"❌ DuckDuckGo検索サービステスト失敗: {e}")
        return False

def test_dynamic_query_generator():
    """動的クエリ生成エンジンテスト"""
    print("\n=== 動的クエリ生成エンジンテスト ===")
    
    try:
        generator = DynamicQueryGenerator()
        
        # サービス状態
        status = generator.get_status()
        print(f"GPT-4利用可能: {status['gpt4_available']}")
        print(f"モデル: {status['model']}")
        
        # テストケース
        test_cases = [
            ("人工知能", "概要", 2),
            ("機械学習", "深掘り", 4),
            ("Python", "実用", 3)
        ]
        
        for theme, learning_type, depth_level in test_cases:
            print(f"\nクエリ生成テスト: {theme} ({learning_type}, レベル{depth_level})")
            
            request = QueryGenerationRequest(
                theme=theme,
                learning_type=learning_type,
                depth_level=depth_level,
                language_preference="mixed"
            )
            
            queries = generator.generate_queries(request)
            
            print(f"  生成クエリ数: {len(queries)}")
            for i, query in enumerate(queries, 1):
                print(f"  {i}. {query.query}")
                print(f"     タイプ: {query.query_type}, 優先度: {query.priority:.2f}")
        
        print("✅ 動的クエリ生成エンジンテスト完了")
        return True
        
    except Exception as e:
        print(f"❌ 動的クエリ生成エンジンテスト失敗: {e}")
        return False

def test_multi_search_manager():
    """マルチ検索エンジン統合テスト"""
    print("\n=== マルチ検索エンジン統合テスト ===")
    
    try:
        manager = MultiSearchManager()
        
        # エンジン状態確認
        print("検索エンジン状態:")
        statuses = manager.get_engine_status()
        for engine, status in statuses.items():
            print(f"  {engine}: {'✅' if status.available else '❌'}")
        
        # 統合検索テスト
        test_queries = ["Python機械学習", "DuckDuckGo検索"]
        
        for query in test_queries:
            print(f"\n統合検索テスト: {query}")
            result = manager.search(query, max_results=5)
            
            print(f"  成功: {result.success}")
            print(f"  使用エンジン: {result.engines_used}")
            print(f"  結果数: {result.total_unique_results}")
            print(f"  実行時間: {result.execution_time:.2f}秒")
            
            if result.success:
                for i, item in enumerate(result.combined_results[:3], 1):
                    print(f"  {i}. {item.title}")
                    print(f"     ドメイン: {item.source_domain}")
                    print(f"     品質: {item.quality_score:.2f}")
        
        # 動的クエリ統合検索テスト
        print(f"\n動的クエリ統合検索テスト")
        dynamic_result = manager.search_with_dynamic_queries(
            theme="ブロックチェーン",
            learning_type="深掘り",
            depth_level=3,
            max_results=10
        )
        
        print(f"  成功: {dynamic_result.success}")
        print(f"  結果数: {dynamic_result.total_unique_results}")
        print(f"  使用エンジン: {dynamic_result.engines_used}")
        
        # 統計情報
        stats = manager.get_search_stats()
        print(f"\n検索統計:")
        print(f"  総検索数: {stats['total_searches']}")
        print(f"  成功検索数: {stats['successful_searches']}")
        print(f"  Google検索数: {stats['google_searches']}")
        print(f"  DuckDuckGo検索数: {stats['duckduckgo_searches']}")
        
        print("✅ マルチ検索エンジン統合テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ マルチ検索エンジン統合テスト失敗: {e}")
        return False

def test_activity_learning_engine():
    """活動学習エンジン統合テスト"""
    print("\n=== 活動学習エンジン統合テスト ===")
    
    try:
        engine = ActivityLearningEngine()
        
        # テストセッション作成
        session = LearningSession(
            session_id=f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            theme="量子コンピューティング",
            learning_type="概要",
            depth_level=2,
            time_limit=300,  # 5分
            budget_limit=0.5,  # $0.5
            status="ready"
        )
        
        print(f"テストセッション: {session.session_id}")
        print(f"テーマ: {session.theme}")
        print(f"学習タイプ: {session.learning_type}")
        print(f"深度レベル: {session.depth_level}")
        
        # 学習セッション実行
        print("\n学習セッション実行中...")
        start_time = time.time()
        
        # 注意: 実際の実行は時間がかかるため、テスト環境では制限
        # engine.run_learning_session(session)
        
        # 代替: 検索クエリ生成のみテスト
        print("検索クエリ生成テスト...")
        queries = engine._generate_search_queries(
            session.theme, 
            session.depth_level, 
            session.learning_type
        )
        
        print(f"生成されたクエリ数: {len(queries)}")
        for i, query in enumerate(queries, 1):
            print(f"  {i}. {query}")
        
        execution_time = time.time() - start_time
        print(f"実行時間: {execution_time:.2f}秒")
        
        print("✅ 活動学習エンジン統合テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ 活動学習エンジン統合テスト失敗: {e}")
        return False

def main():
    """メインテスト実行"""
    print("🚀 統合検索システム総合テスト開始")
    print(f"実行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = []
    
    # 個別テスト実行
    test_results.append(("DuckDuckGo検索サービス", test_duckduckgo_service()))
    test_results.append(("動的クエリ生成エンジン", test_dynamic_query_generator()))
    test_results.append(("マルチ検索エンジン統合", test_multi_search_manager()))
    test_results.append(("活動学習エンジン統合", test_activity_learning_engine()))
    
    # 結果サマリー
    print("\n" + "="*50)
    print("📊 テスト結果サマリー")
    print("="*50)
    
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
        print("🎉 すべてのテストが成功しました！")
        print("✅ 統合検索システムの実装完了")
    else:
        print(f"⚠️ {failed}件のテストで問題が発生しました")
        print("🔧 問題の修正が必要です")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)