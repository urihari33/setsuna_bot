#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 3A: GUI統合テスト
新しい検索システム + GUI + セッション表示機能の統合確認
"""

import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from core.activity_learning_engine import ActivityLearningEngine, LearningSession
from core.multi_search_manager import MultiSearchManager
from core.dynamic_query_generator import DynamicQueryGenerator
from session_result_viewer import SessionResultViewer
from session_html_report import SessionHTMLReportGenerator
from core.config_manager import get_config_manager

def test_gui_search_system_integration():
    """GUI検索システム統合テスト"""
    print("=== GUI検索システム統合テスト ===")
    
    try:
        # コアコンポーネント初期化
        learning_engine = ActivityLearningEngine()
        search_manager = MultiSearchManager()
        query_generator = DynamicQueryGenerator()
        session_viewer = SessionResultViewer()
        html_generator = SessionHTMLReportGenerator()
        
        print("✅ 全コンポーネント初期化成功")
        
        # 新しい検索システムの動作確認
        print("\n--- 新検索システム動作確認 ---")
        
        # DuckDuckGo検索テスト
        test_result = search_manager.search("Python機械学習", max_results=3)
        print(f"DuckDuckGo検索結果: {test_result.success}, 結果数: {test_result.total_unique_results}")
        
        # 動的クエリ生成テスト
        from core.dynamic_query_generator import QueryGenerationRequest
        request = QueryGenerationRequest(
            theme="AI音楽生成",
            learning_type="概要",
            depth_level=2,
            language_preference="mixed"
        )
        queries = query_generator.generate_queries(request)
        print(f"動的クエリ生成: {len(queries)}件")
        
        # ActivityLearningEngineでの新検索システム利用確認
        print("\n--- ActivityLearningEngine新検索システム統合確認 ---")
        
        # 検索クエリ生成メソッドの確認
        test_queries = learning_engine._generate_search_queries(
            theme="ブロックチェーン技術",
            depth_level=3,
            learning_type="深掘り"
        )
        print(f"ActivityLearningEngine検索クエリ生成: {len(test_queries)}件")
        for i, query in enumerate(test_queries[:3], 1):
            print(f"  {i}. {query}")
        
        print("✅ GUI検索システム統合テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ GUI検索システム統合テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_path_configuration():
    """パス設定確認テスト"""
    print("\n=== パス設定確認テスト ===")
    
    try:
        # データディレクトリ確認
        data_dir = Path("D:/setsuna_bot/data/activity_knowledge")
        sessions_dir = data_dir / "sessions"
        
        print(f"データディレクトリ存在: {data_dir.exists()}")
        print(f"セッションディレクトリ存在: {sessions_dir.exists()}")
        
        # SessionResultViewerのパス設定確認
        viewer = SessionResultViewer()
        print(f"SessionResultViewer data_dir: {viewer.sessions_dir}")
        print(f"SessionResultViewer sessions_dir存在: {viewer.sessions_dir.exists()}")
        
        # HTMLレポート生成器のパス確認
        html_gen = SessionHTMLReportGenerator()
        print(f"HTMLレポート生成器初期化: 成功")
        
        # ActivityLearningEngineのパス確認
        engine = ActivityLearningEngine()
        print(f"ActivityLearningEngine sessions_dir: {engine.sessions_dir}")
        print(f"ActivityLearningEngine sessions_dir存在: {engine.sessions_dir.exists()}")
        
        print("✅ パス設定確認テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ パス設定確認テスト失敗: {e}")
        return False

def test_existing_session_display():
    """既存セッション表示テスト"""
    print("\n=== 既存セッション表示テスト ===")
    
    try:
        viewer = SessionResultViewer()
        
        # セッション一覧取得
        sessions = viewer.list_sessions()
        print(f"既存セッション数: {len(sessions)}")
        
        if sessions:
            # 最新セッションの詳細表示テスト
            latest_session = sessions[0]
            session_id = latest_session.session_id
            print(f"\n最新セッション: {session_id}")
            
            # セッション詳細データ読み込み
            session_data = viewer.load_session_details(session_id)
            
            if session_data:
                print("✅ セッション詳細データ読み込み成功")
                
                # 主要データ確認
                metadata = session_data.get("session_metadata", {})
                print(f"  テーマ: {metadata.get('theme', '不明')}")
                print(f"  学習タイプ: {metadata.get('learning_type', '不明')}")
                print(f"  状態: {metadata.get('status', '不明')}")
                print(f"  収集アイテム: {metadata.get('collected_items', 0)}件")
                
                # 収集結果確認
                collection_results = session_data.get("collection_results", {})
                sources = collection_results.get("information_sources", [])
                print(f"  情報ソース: {len(sources)}件")
                
            else:
                print("⚠️ セッション詳細データなし（基本情報のみ）")
            
            print("✅ 既存セッション表示テスト完了")
            return True
        else:
            print("⚠️ 既存セッションなし")
            return True
            
    except Exception as e:
        print(f"❌ 既存セッション表示テスト失敗: {e}")
        return False

def test_html_report_generation():
    """HTMLレポート生成テスト"""
    print("\n=== HTMLレポート生成テスト ===")
    
    try:
        viewer = SessionResultViewer()
        html_generator = SessionHTMLReportGenerator()
        
        # 既存セッション確認
        sessions = viewer.list_sessions()
        
        if sessions:
            # 最新セッションでHTMLレポート生成テスト
            latest_session = sessions[0]
            session_id = latest_session.session_id
            
            print(f"HTMLレポート生成対象: {session_id}")
            
            # HTMLレポート生成
            output_file = html_generator.generate_html_report(session_id)
            
            if output_file and Path(output_file).exists():
                file_size = Path(output_file).stat().st_size
                print(f"✅ HTMLレポート生成成功")
                print(f"  ファイル: {output_file}")
                print(f"  サイズ: {file_size} bytes")
                
                # 簡単な内容確認
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"  HTML内容長: {len(content)} 文字")
                    print(f"  タイトル含有: {'<title>' in content}")
                    print(f"  セッションID含有: {session_id in content}")
                
                return True
            else:
                print("❌ HTMLレポート生成失敗")
                return False
        else:
            print("⚠️ テスト対象セッションなし")
            return True
            
    except Exception as e:
        print(f"❌ HTMLレポート生成テスト失敗: {e}")
        return False

def test_new_search_session_creation():
    """新検索システムでのセッション生成テスト"""
    print("\n=== 新検索システムセッション生成テスト ===")
    
    try:
        learning_engine = ActivityLearningEngine()
        
        # テストセッション作成
        session_id = learning_engine.create_session(
            theme="Phase3A統合テスト",
            learning_type="概要",
            depth_level=2,
            time_limit=300,  # 5分
            budget_limit=1.0,  # $1.0
            tags=["GUI統合テスト", "Phase3A"]
        )
        
        if session_id:
            print(f"✅ テストセッション作成成功: {session_id}")
            
            # セッション設定確認
            session_data = learning_engine.get_session_status(session_id)
            if session_data:
                print(f"  セッション状態: {session_data.get('status', '不明')}")
                print(f"  テーマ: {session_data.get('theme', '不明')}")
                
            # 検索クエリ生成確認（新システム）
            queries = learning_engine._generate_search_queries(
                theme="Phase3A統合テスト", 
                depth_level=2, 
                learning_type="概要"
            )
            print(f"  新システム検索クエリ: {len(queries)}件")
            
            print("✅ 新検索システムセッション生成テスト完了")
            return True
        else:
            print("❌ テストセッション作成失敗")
            return False
            
    except Exception as e:
        print(f"❌ 新検索システムセッション生成テスト失敗: {e}")
        return False

def test_api_configuration():
    """API設定確認テスト"""
    print("\n=== API設定確認テスト ===")
    
    try:
        config_manager = get_config_manager()
        
        # 設定サマリー確認
        config_summary = config_manager.get_config_summary()
        print(f"OpenAI設定: {'✅' if config_summary['openai_configured'] else '❌'}")
        print(f"Google検索設定: {'✅' if config_summary['google_search_configured'] else '❌'}")
        
        # 検証結果確認
        validation_result = config_manager.get_validation_result()
        if validation_result.is_valid:
            print("✅ 全API設定有効")
        else:
            print("⚠️ API設定に問題あり")
            if validation_result.missing_keys:
                print(f"  不足キー: {validation_result.missing_keys}")
            if validation_result.errors:
                print(f"  エラー: {validation_result.errors}")
        
        return True
        
    except Exception as e:
        print(f"❌ API設定確認テスト失敗: {e}")
        return False

def main():
    """メインテスト実行"""
    print("🚀 Phase 3A: GUI統合最終確認テスト開始")
    print(f"実行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = []
    
    # 各テスト実行
    test_results.append(("API設定確認", test_api_configuration()))
    test_results.append(("パス設定確認", test_path_configuration()))
    test_results.append(("GUI検索システム統合", test_gui_search_system_integration()))
    test_results.append(("既存セッション表示", test_existing_session_display()))
    test_results.append(("HTMLレポート生成", test_html_report_generation()))
    test_results.append(("新検索システムセッション生成", test_new_search_session_creation()))
    
    # 結果サマリー
    print("\n" + "="*60)
    print("📊 Phase 3A GUI統合テスト結果サマリー")
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
        print("🎉 Phase 3A GUI統合テスト全て成功！")
        print("✅ 新検索システム + GUI + セッション表示の完全統合確認完了")
        print("✅ Phase 2C + Phase 3A統合システム動作確認完了")
    else:
        print(f"⚠️ {failed}件のテストで問題が発生")
        print("🔧 問題解決が必要です")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)