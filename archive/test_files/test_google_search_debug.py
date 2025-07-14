#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google検索デバッグツール
ActivityLearningEngineの検索統合問題を詳細調査
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.google_search_manager import GoogleSearchManager
from core.activity_learning_engine import ActivityLearningEngine
from core.config_manager import get_config_manager

def test_google_config():
    """Google設定の詳細確認"""
    print("=== Google設定確認 ===")
    
    config = get_config_manager()
    
    print(f"Google検索設定済み: {config.is_google_search_configured()}")
    print(f"Google APIキー: {'設定済み' if config.get_google_api_key() else '未設定'}")
    print(f"検索エンジンID: {'設定済み' if config.get_google_search_engine_id() else '未設定'}")
    
    if config.get_google_api_key():
        api_key = config.get_google_api_key()
        print(f"APIキー長: {len(api_key)}")
        print(f"APIキー先頭: {api_key[:10]}...")
    
    if config.get_google_search_engine_id():
        engine_id = config.get_google_search_engine_id()
        print(f"エンジンID: {engine_id}")
    
    print()
    
    # すべて設定済みならTrueを返す
    return (config.is_google_search_configured() and 
            config.get_google_api_key() and 
            config.get_google_search_engine_id())

def test_google_search_manager():
    """GoogleSearchManager単体テスト"""
    print("=== GoogleSearchManager テスト ===")
    
    try:
        manager = GoogleSearchManager()
        print("GoogleSearchManager初期化成功")
        
        # ステータス確認
        status = manager.get_status()
        print(f"検索準備完了: {status.get('ready', False)}")
        print(f"Google サービス利用可能: {status.get('google_service_available', False)}")
        print(f"設定有効: {status.get('config_valid', False)}")
        print(f"残り検索数: {status.get('quota_remaining', 'N/A')}")
        
        if not status.get('ready', False):
            print(f"準備未完了の理由: {status.get('not_ready_reason', '不明')}")
            return False
        
        # 実際の検索テスト
        print("\n--- 実際の検索テスト ---")
        test_query = "AI技術 最新動向"
        print(f"検索クエリ: {test_query}")
        
        search_result = manager.search(test_query, max_results=3)
        print(f"検索成功: {search_result.get('success', False)}")
        print(f"使用エンジン: {search_result.get('engine_used', 'N/A')}")
        print(f"結果数: {search_result.get('total_results', 0)}")
        print(f"実行時間: {search_result.get('execution_time', 0):.2f}秒")
        
        if search_result.get('error'):
            print(f"エラー: {search_result.get('error')}")
            print(f"制限到達: {search_result.get('quota_exceeded', False)}")
        
        # 結果詳細表示
        if search_result.get('results'):
            print(f"\n--- 検索結果詳細 ---")
            for i, result in enumerate(search_result['results'][:2], 1):
                print(f"{i}. {result.get('title', '無題')}")
                print(f"   URL: {result.get('url', 'N/A')}")
                print(f"   内容: {result.get('content', 'N/A')[:100]}...")
                print(f"   ソースタイプ: {result.get('source_type', 'N/A')}")
                print()
        
        return search_result.get('success', False)
        
    except Exception as e:
        print(f"GoogleSearchManager テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_activity_learning_engine():
    """ActivityLearningEngine検索統合テスト"""
    print("=== ActivityLearningEngine 検索統合テスト ===")
    
    try:
        # エンジン初期化
        engine = ActivityLearningEngine()
        print("ActivityLearningEngine初期化成功")
        
        # 検索マネージャーステータス確認
        search_status = engine.search_manager.get_status()
        print(f"検索マネージャー準備: {search_status.get('ready', False)}")
        
        # テストセッション作成
        session_id = engine.create_session(
            theme="Google検索テスト",
            learning_type="概要",
            depth_level=1,
            time_limit=120,  # 2分間
            budget_limit=0.5,
            tags=["テスト", "Google検索"]
        )
        
        print(f"テストセッション作成: {session_id}")
        
        # 検索クエリ生成テスト
        print("\n--- 検索クエリ生成テスト ---")
        queries = engine._generate_search_queries("Google検索テスト", 1)
        print(f"生成クエリ数: {len(queries)}")
        for i, query in enumerate(queries, 1):
            print(f"{i}. {query}")
        
        # 個別検索テスト
        print("\n--- Web検索実行テスト ---")
        if queries:
            test_query = queries[0]
            print(f"テスト検索: {test_query}")
            
            search_results = engine._perform_web_search(test_query)
            print(f"検索結果数: {len(search_results)}")
            
            if search_results:
                print("検索結果概要:")
                for i, result in enumerate(search_results[:2], 1):
                    print(f"{i}. {result.get('title', '無題')}")
                    print(f"   タイプ: {result.get('source_type', 'N/A')}")
                    print(f"   URL: {result.get('url', 'N/A')}")
                    print()
            else:
                print("⚠️ 検索結果が取得できませんでした")
        
        return len(search_results) > 0 if queries else False
        
    except Exception as e:
        print(f"ActivityLearningEngine テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_session_execution():
    """実際のセッション実行テスト"""
    print("=== セッション実行テスト ===")
    
    try:
        engine = ActivityLearningEngine()
        
        # プログレスコールバック設定
        def progress_callback(phase: str, progress: float, message: str):
            print(f"[進捗] {phase}: {progress:.1%} - {message}")
        
        engine.add_progress_callback(progress_callback)
        
        # 短時間セッション実行
        session_id = engine.create_session(
            theme="AI技術動向",
            learning_type="概要", 
            depth_level=1,
            time_limit=60,  # 1分間
            budget_limit=0.3,
            tags=["診断テスト"]
        )
        
        print(f"診断セッション開始: {session_id}")
        
        # セッション実行
        success = engine.start_session(session_id)
        
        if success:
            print("✅ セッション実行成功")
            
            # セッションファイル確認
            session_file = Path(f"D:/setsuna_bot/data/activity_knowledge/sessions/{session_id}.json")
            if session_file.exists():
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                print(f"\n--- セッションデータ分析 ---")
                metadata = session_data.get("session_metadata", {})
                print(f"ステータス: {metadata.get('status', 'N/A')}")
                print(f"収集アイテム: {metadata.get('collected_items', 0)}")
                print(f"処理アイテム: {metadata.get('processed_items', 0)}")
                print(f"コスト: ${metadata.get('current_cost', 0):.4f}")
                
                # collection_results確認
                collection_results = session_data.get("collection_results")
                if collection_results:
                    sources = collection_results.get("information_sources", [])
                    print(f"保存された収集結果: {len(sources)}件")
                    
                    if sources:
                        print("収集結果サンプル:")
                        for i, source in enumerate(sources[:2], 1):
                            print(f"{i}. {source.get('title', '無題')}")
                            print(f"   タイプ: {source.get('source_type', 'N/A')}")
                            print(f"   URL: {source.get('url', 'N/A')}")
                    else:
                        print("⚠️ collection_resultsは存在するが、情報ソースが空です")
                else:
                    print("❌ collection_resultsが存在しません")
            else:
                print(f"❌ セッションファイルが見つかりません: {session_file}")
            
            return True
        else:
            print("❌ セッション実行失敗")
            return False
            
    except Exception as e:
        print(f"セッション実行テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メイン診断実行"""
    print("🔍 Google検索データ収集問題 詳細診断ツール")
    print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 段階的テスト実行
    tests = [
        ("Google設定確認", test_google_config),
        ("GoogleSearchManager テスト", test_google_search_manager),
        ("ActivityLearningEngine テスト", test_activity_learning_engine),
        ("セッション実行テスト", test_session_execution)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results[test_name] = result
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"\n{test_name}: {status}")
        except Exception as e:
            results[test_name] = False
            print(f"\n{test_name}: ❌ ERROR - {e}")
        
        print("=" * 60)
    
    # 最終サマリー
    print(f"\n📊 診断結果サマリー:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    total_pass = sum(results.values())
    print(f"\n総合結果: {total_pass}/{len(results)} テスト通過")
    
    if total_pass == len(results):
        print("🎉 すべてのテストが通過しました！")
    else:
        print("🔧 一部のテストで問題が検出されました。修正が必要です。")

if __name__ == "__main__":
    main()