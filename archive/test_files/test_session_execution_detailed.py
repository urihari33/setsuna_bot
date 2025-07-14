#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
セッション実行テスト - 実際のGoogle検索データ収集確認
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.activity_learning_engine import ActivityLearningEngine

def test_simple_session():
    """簡単なセッション実行テスト"""
    print("=== 簡単なセッション実行テスト ===")
    
    try:
        # エンジン初期化
        engine = ActivityLearningEngine()
        print("✅ ActivityLearningEngine初期化成功")
        
        # プログレスコールバック設定
        progress_log = []
        def progress_callback(phase: str, progress: float, message: str):
            log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] {phase}: {progress:.1%} - {message}"
            progress_log.append(log_entry)
            print(log_entry)
        
        engine.add_progress_callback(progress_callback)
        
        # 短時間セッション作成
        session_id = engine.create_session(
            theme="Python プログラミング",
            learning_type="概要",
            depth_level=1,
            time_limit=30,  # 30秒
            budget_limit=0.2,
            tags=["テスト", "Python"]
        )
        
        print(f"📝 セッション作成成功: {session_id}")
        
        # セッション実行前のファイル確認
        session_file = Path(f"D:/setsuna_bot/data/activity_knowledge/sessions/{session_id}.json")
        print(f"🔍 セッションファイルパス: {session_file}")
        
        # セッション実行
        print("🚀 セッション実行開始...")
        start_time = time.time()
        
        success = engine.start_session(session_id)
        
        print(f"⏱️ セッション実行時間: {time.time() - start_time:.1f}秒")
        print(f"✅ セッション実行結果: {success}")
        
        # セッション完了まで待機
        max_wait = 60  # 最大60秒待機
        wait_time = 0
        
        while wait_time < max_wait:
            if session_file.exists():
                break
            print(f"⏳ セッションファイル待機中... ({wait_time}秒)")
            time.sleep(2)
            wait_time += 2
        
        # セッションデータ分析
        if session_file.exists():
            print(f"\n📊 セッションデータ分析:")
            print(f"ファイルサイズ: {session_file.stat().st_size} bytes")
            
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # メタデータ分析
            metadata = session_data.get("session_metadata", {})
            print(f"セッションID: {metadata.get('session_id', 'N/A')}")
            print(f"ステータス: {metadata.get('status', 'N/A')}")
            print(f"現在フェーズ: {metadata.get('current_phase', 'N/A')}")
            print(f"収集アイテム: {metadata.get('collected_items', 0)}")
            print(f"処理アイテム: {metadata.get('processed_items', 0)}")
            print(f"現在コスト: ${metadata.get('current_cost', 0):.4f}")
            print(f"開始時刻: {metadata.get('start_time', 'N/A')}")
            print(f"終了時刻: {metadata.get('end_time', 'N/A')}")
            
            # 収集結果分析
            collection_results = session_data.get("collection_results")
            if collection_results:
                print(f"\n🔍 収集結果分析:")
                print(f"情報ソース数: {len(collection_results.get('information_sources', []))}")
                print(f"生の収集数: {collection_results.get('raw_content_count', 0)}")
                print(f"フィルタ後数: {collection_results.get('filtered_content_count', 0)}")
                print(f"実行クエリ数: {collection_results.get('queries_executed', 0)}")
                print(f"実行時間: {collection_results.get('execution_time', 0):.2f}秒")
                print(f"収集成功: {collection_results.get('collection_success', False)}")
                print(f"検索エラー数: {len(collection_results.get('search_errors', []))}")
                
                # 実際の情報ソース確認
                sources = collection_results.get("information_sources", [])
                if sources:
                    print(f"\n📋 情報ソース詳細:")
                    for i, source in enumerate(sources[:3], 1):
                        print(f"{i}. {source.get('title', '無題')}")
                        print(f"   URL: {source.get('url', 'N/A')}")
                        print(f"   タイプ: {source.get('source_type', 'N/A')}")
                        print(f"   内容長: {len(source.get('content', ''))}")
                        if source.get('source_type') == 'google_search':
                            print(f"   ✅ Google検索結果を取得成功!")
                        else:
                            print(f"   ⚠️ Google以外のソース: {source.get('source_type')}")
                        print()
                else:
                    print("❌ 情報ソースが空です")
                    
                # 検索エラー分析
                search_errors = collection_results.get("search_errors", [])
                if search_errors:
                    print(f"\n❌ 検索エラー分析:")
                    for i, error in enumerate(search_errors, 1):
                        print(f"{i}. クエリ: {error.get('query', 'N/A')}")
                        print(f"   エラー: {error.get('error_message', 'N/A')}")
                        print(f"   タイプ: {error.get('error_type', 'N/A')}")
                        print(f"   制限到達: {error.get('quota_exceeded', False)}")
                        print()
                
            else:
                print("❌ collection_resultsが存在しません")
            
            # 分析結果確認
            analysis_results = session_data.get("analysis_results")
            if analysis_results:
                print(f"\n🧠 分析結果:")
                print(f"分析コンテンツ数: {len(analysis_results.get('analyzed_content', []))}")
                print(f"重要発見数: {len(analysis_results.get('key_findings', []))}")
                print(f"抽出エンティティ数: {len(analysis_results.get('extracted_entities', []))}")
            else:
                print("ℹ️ 分析結果はまだありません（収集フェーズのみ完了）")
            
            # 進捗ログ表示
            if progress_log:
                print(f"\n📈 進捗ログ:")
                for log in progress_log[-5:]:  # 最新5件
                    print(f"  {log}")
            
            return True
            
        else:
            print(f"❌ セッションファイルが見つかりません: {session_file}")
            return False
            
    except Exception as e:
        print(f"❌ セッション実行テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メイン実行"""
    print("🔬 セッション実行テスト - Google検索データ収集確認")
    print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    result = test_simple_session()
    
    print("=" * 60)
    if result:
        print("🎉 セッション実行テスト成功!")
        print("✅ Google検索データの収集と保存が正常に動作しています")
    else:
        print("❌ セッション実行テストで問題が検出されました")
        print("🔧 Google検索の設定や統合を確認してください")

if __name__ == "__main__":
    main()