#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
セッション完了待機修正テスト
非同期処理の問題を解決
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

def test_session_completion_wait():
    """セッション完了待機のテスト"""
    print("=== セッション完了待機テスト ===")
    
    try:
        # エンジン初期化
        engine = ActivityLearningEngine()
        print("✅ ActivityLearningEngine初期化成功")
        
        # セッション作成
        session_id = engine.create_session(
            theme="セッション完了テスト",
            learning_type="概要",
            depth_level=1,
            time_limit=90,  # 90秒
            budget_limit=0.3,
            tags=["完了テスト"]
        )
        
        print(f"📝 セッション作成: {session_id}")
        
        # セッションファイルパス確認
        session_file = Path(f"D:/setsuna_bot/data/activity_knowledge/sessions/{session_id}.json")
        print(f"📁 セッションファイル: {session_file}")
        
        # セッション開始
        print("🚀 セッション開始...")
        start_time = time.time()
        
        success = engine.start_session(session_id)
        
        if not success:
            print("❌ セッション開始失敗")
            return False
        
        print(f"✅ セッション開始成功")
        
        # セッション完了待機（改善版）
        print("⏳ セッション完了待機中...")
        max_wait = 120  # 最大2分待機
        wait_time = 0
        check_interval = 5  # 5秒間隔でチェック
        
        while wait_time < max_wait:
            time.sleep(check_interval)
            wait_time += check_interval
            
            # ファイル存在確認
            if session_file.exists():
                file_size = session_file.stat().st_size
                print(f"📄 セッションファイル発見: {file_size} bytes")
                
                # ファイル内容確認
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    # セッションステータス確認
                    metadata = session_data.get("session_metadata", {})
                    status = metadata.get("status", "unknown")
                    current_phase = metadata.get("current_phase", "unknown")
                    
                    print(f"🔍 セッション状態: {status}, フェーズ: {current_phase}")
                    
                    # 完了状態確認
                    if status in ["completed", "failed", "cancelled"]:
                        print(f"✅ セッション完了: {status}")
                        break
                    
                    # 収集結果確認
                    collection_results = session_data.get("collection_results")
                    if collection_results:
                        sources = collection_results.get("information_sources", [])
                        print(f"📊 収集済みソース数: {len(sources)}")
                        
                        # 収集が完了している場合
                        if len(sources) > 0:
                            print(f"📚 データ収集確認完了")
                            break
                    
                except json.JSONDecodeError:
                    print("⚠️ JSONファイルがまだ完成していません")
                except Exception as e:
                    print(f"⚠️ ファイル読み取りエラー: {e}")
            
            print(f"⏰ 待機中... ({wait_time}秒経過)")
        
        # 最終確認
        total_time = time.time() - start_time
        print(f"\n📊 セッション実行結果:")
        print(f"実行時間: {total_time:.1f}秒")
        print(f"ファイル存在: {session_file.exists()}")
        
        if session_file.exists():
            file_size = session_file.stat().st_size
            print(f"ファイルサイズ: {file_size} bytes")
            
            # 最終的なデータ分析
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            print(f"\n📋 最終データ分析:")
            
            # メタデータ分析
            metadata = session_data.get("session_metadata", {})
            print(f"セッションID: {metadata.get('session_id', 'N/A')}")
            print(f"ステータス: {metadata.get('status', 'N/A')}")
            print(f"フェーズ: {metadata.get('current_phase', 'N/A')}")
            print(f"収集アイテム: {metadata.get('collected_items', 0)}")
            print(f"処理アイテム: {metadata.get('processed_items', 0)}")
            print(f"コスト: ${metadata.get('current_cost', 0):.4f}")
            
            # 収集結果分析
            collection_results = session_data.get("collection_results")
            if collection_results:
                sources = collection_results.get("information_sources", [])
                print(f"\n✅ 収集結果: {len(sources)}件")
                
                if sources:
                    print("📋 収集内容サンプル:")
                    for i, source in enumerate(sources[:3], 1):
                        print(f"{i}. {source.get('title', '無題')}")
                        print(f"   URL: {source.get('url', 'N/A')}")
                        print(f"   タイプ: {source.get('source_type', 'N/A')}")
                        print(f"   内容長: {len(source.get('content', ''))} 文字")
                        print()
                
                return True
            else:
                print("❌ 収集結果がありません")
                return False
        else:
            print("❌ セッションファイルが作成されませんでした")
            return False
    
    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メイン実行"""
    print("🔧 セッション完了待機修正テスト")
    print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    result = test_session_completion_wait()
    
    print("=" * 60)
    if result:
        print("🎉 セッション完了待機テスト成功！")
        print("✅ セッション実行からデータ保存まで正常に動作しました")
    else:
        print("❌ セッション完了待機テストで問題を検出")
        print("🔧 スレッド処理の改善が必要です")

if __name__ == "__main__":
    main()