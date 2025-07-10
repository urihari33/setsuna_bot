#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ファイル消失問題修正テスト
セッション終了時のデータ保持確認
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.activity_learning_engine import ActivityLearningEngine

def test_data_persistence():
    """データ永続化テスト"""
    print("=== データ永続化テスト ===")
    
    try:
        # エンジン初期化
        engine = ActivityLearningEngine()
        print("✅ ActivityLearningEngine初期化成功")
        
        # セッション作成
        session_id = engine.create_session(
            theme="データ永続化テスト",
            learning_type="概要",
            depth_level=1,
            time_limit=60,  # 60秒
            budget_limit=0.3,
            tags=["修正テスト", "データ保持"]
        )
        
        print(f"📝 セッション作成: {session_id}")
        
        # セッションファイルパス
        session_file = Path(f"D:/setsuna_bot/data/activity_knowledge/sessions/{session_id}.json")
        print(f"📁 セッションファイル: {session_file}")
        
        # セッション開始
        print("🚀 セッション開始...")
        success = engine.start_session(session_id)
        
        if not success:
            print("❌ セッション開始失敗")
            return False
        
        print("✅ セッション開始成功")
        
        # データ監視
        print("📊 データ収集監視中...")
        max_wait = 90  # 最大90秒待機
        wait_time = 0
        check_interval = 10  # 10秒間隔
        
        data_snapshots = []  # データの変化を記録
        
        while wait_time < max_wait:
            time.sleep(check_interval)
            wait_time += check_interval
            
            if session_file.exists():
                try:
                    file_size = session_file.stat().st_size
                    
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    # データスナップショット
                    snapshot = {
                        "time": wait_time,
                        "file_size": file_size,
                        "status": session_data.get("session_metadata", {}).get("status", "unknown"),
                        "phase": session_data.get("session_metadata", {}).get("current_phase", "unknown"),
                        "collected_items": session_data.get("session_metadata", {}).get("collected_items", 0),
                        "has_collection_results": "collection_results" in session_data,
                        "sources_count": len(session_data.get("collection_results", {}).get("information_sources", [])),
                        "data_keys": list(session_data.keys())
                    }
                    
                    data_snapshots.append(snapshot)
                    
                    print(f"📊 {wait_time}秒時点: {snapshot['status']}/{snapshot['phase']} - "
                          f"収集{snapshot['collected_items']}件, ソース{snapshot['sources_count']}件, "
                          f"ファイル{snapshot['file_size']}bytes")
                    
                    # セッション完了チェック
                    if snapshot['status'] in ["completed", "error", "cancelled"]:
                        print(f"🎯 セッション終了: {snapshot['status']}")
                        break
                        
                except (json.JSONDecodeError, Exception) as e:
                    print(f"⚠️ ファイル読み取りエラー ({wait_time}秒): {e}")
            else:
                print(f"⏳ ファイル待機中... ({wait_time}秒)")
        
        # 最終検証
        print(f"\n📋 最終検証:")
        if session_file.exists():
            final_size = session_file.stat().st_size
            print(f"最終ファイルサイズ: {final_size} bytes")
            
            # 最終データ分析
            with open(session_file, 'r', encoding='utf-8') as f:
                final_data = json.load(f)
            
            print(f"\n✅ 最終データ構造:")
            for key in final_data.keys():
                if key == "collection_results":
                    sources = final_data[key].get("information_sources", [])
                    print(f"  {key}: {len(sources)}件のソース")
                elif key == "analysis_results":
                    analyzed = final_data[key].get("analyzed_content", [])
                    print(f"  {key}: {len(analyzed)}件の分析")
                else:
                    print(f"  {key}: 存在")
            
            # データ変化履歴分析
            print(f"\n📈 データ変化履歴:")
            for i, snapshot in enumerate(data_snapshots, 1):
                print(f"{i:2d}. {snapshot['time']:2d}秒: {snapshot['file_size']:6d}bytes "
                      f"({snapshot['status']}/{snapshot['phase']}) "
                      f"ソース{snapshot['sources_count']}件")
            
            # データ損失チェック
            final_sources = len(final_data.get("collection_results", {}).get("information_sources", []))
            max_sources = max([s['sources_count'] for s in data_snapshots] + [0])
            
            if final_sources == 0 and max_sources > 0:
                print(f"\n❌ データ損失検出! 最大{max_sources}件 → 最終0件")
                return False
            elif final_sources >= max_sources:
                print(f"\n✅ データ保持成功! 最大{max_sources}件 → 最終{final_sources}件")
                return True
            else:
                print(f"\n⚠️ 部分的データ損失: 最大{max_sources}件 → 最終{final_sources}件")
                return False
        else:
            print("❌ セッションファイルが存在しません")
            return False
    
    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メイン実行"""
    print("🔧 ファイル消失問題修正テスト")
    print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    result = test_data_persistence()
    
    print("=" * 60)
    if result:
        print("🎉 修正成功！データが正常に保持されました")
        print("✅ セッション終了時のファイル消失問題が解決されました")
    else:
        print("❌ 修正効果を確認できませんでした")
        print("🔧 追加の調査が必要です")

if __name__ == "__main__":
    main()