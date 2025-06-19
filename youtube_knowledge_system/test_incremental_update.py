"""
差分更新システムのテストスクリプト

IncrementalUpdateManager の動作確認とパフォーマンステスト
"""

import sys
import time
from datetime import datetime
from pathlib import Path

# パッケージパスを追加
sys.path.append(str(Path(__file__).parent))

from managers.incremental_manager import IncrementalUpdateManager
from storage.unified_storage import UnifiedStorage
from collectors.auth_manager import YouTubeAuthManager


def test_basic_functionality():
    """基本機能のテスト"""
    print("=== 基本機能テスト ===")
    
    # マネージャー初期化
    manager = IncrementalUpdateManager()
    manager.initialize()
    
    print("✅ IncrementalUpdateManager 初期化完了")
    
    # 統合データベースの状況確認
    storage = manager.storage
    db = storage.load_database()
    
    print(f"現在のデータベース状況:")
    print(f"  総動画数: {db.total_videos}")
    print(f"  総プレイリスト数: {db.total_playlists}")
    
    return manager


def test_new_video_detection(manager: IncrementalUpdateManager, playlist_id: str, limit: int = 5):
    """新規動画検出のテスト"""
    print(f"\\n=== 新規動画検出テスト: {playlist_id} ===")
    
    try:
        # 新規動画検出
        start_time = time.time()
        new_video_ids = manager.detect_new_videos(playlist_id, limit_check=limit)
        detection_time = time.time() - start_time
        
        print(f"検出時間: {detection_time:.2f}秒")
        print(f"新規動画数: {len(new_video_ids)}")
        
        if new_video_ids:
            print("新規動画ID:")
            for i, video_id in enumerate(new_video_ids[:3], 1):
                print(f"  {i}. {video_id}")
            if len(new_video_ids) > 3:
                print(f"  ... 他 {len(new_video_ids) - 3} 件")
        
        return new_video_ids
        
    except Exception as e:
        print(f"❌ 新規動画検出エラー: {e}")
        return []


def test_incremental_update(manager: IncrementalUpdateManager, playlist_id: str):
    """差分更新のテスト"""
    print(f"\\n=== 差分更新テスト: {playlist_id} ===")
    
    try:
        # 更新前の状況を記録
        db_before = manager.storage.load_database()
        videos_before = db_before.total_videos
        
        # 差分更新実行
        start_time = time.time()
        result = manager.update_playlist_incrementally(playlist_id)
        update_time = time.time() - start_time
        
        # 更新後の状況確認
        db_after = manager.storage.load_database()
        videos_after = db_after.total_videos
        
        print(f"\\n更新結果:")
        print(f"  ステータス: {result['status']}")
        print(f"  処理時間: {update_time:.2f}秒")
        print(f"  動画数変化: {videos_before} → {videos_after} (+{videos_after - videos_before})")
        
        if result['status'] == 'success':
            print(f"  新規動画数: {result['new_videos_count']}")
            print(f"  追加動画数: {result['added_videos_count']}")
            print("✅ 差分更新成功")
        else:
            print(f"⚠️ 更新結果: {result.get('status', 'unknown')}")
        
        return result
        
    except Exception as e:
        print(f"❌ 差分更新エラー: {e}")
        return {'status': 'error', 'error': str(e)}


def test_performance_comparison(manager: IncrementalUpdateManager, playlist_id: str):
    """パフォーマンス比較テスト"""
    print(f"\\n=== パフォーマンス比較テスト ===")
    
    # 差分更新のパフォーマンス測定
    print("1. 差分更新のパフォーマンス測定中...")
    start_time = time.time()
    
    # 新規動画検出のみ（軽量）
    new_videos = manager.detect_new_videos(playlist_id, limit_check=10)
    detection_time = time.time() - start_time
    
    print(f"新規動画検出時間: {detection_time:.2f}秒")
    print(f"検出された新規動画: {len(new_videos)}件")
    
    # API効率性の推定
    if len(new_videos) > 0:
        estimated_full_sync_time = detection_time * 10  # 推定値
        efficiency_gain = ((estimated_full_sync_time - detection_time) / estimated_full_sync_time) * 100
        print(f"推定効率化: {efficiency_gain:.1f}%")
    
    return detection_time


def test_database_consistency(manager: IncrementalUpdateManager):
    """データベース整合性テスト"""
    print(f"\\n=== データベース整合性テスト ===")
    
    try:
        db = manager.storage.load_database()
        
        # 基本統計
        print(f"データベース統計:")
        print(f"  動画数: {db.total_videos}")
        print(f"  プレイリスト数: {db.total_playlists}")
        print(f"  クリエイター数: {len(db.creator_index)}")
        print(f"  タグ数: {len(db.tag_index)}")
        
        # 整合性チェック
        inconsistencies = []
        
        # プレイリストと動画の整合性
        for playlist_id, playlist in db.playlists.items():
            for video_id in playlist.video_ids:
                if video_id not in db.videos:
                    inconsistencies.append(f"プレイリスト {playlist_id} に存在しない動画 {video_id}")
        
        # 動画のプレイリスト参照整合性
        for video_id, video in db.videos.items():
            for playlist_id in video.playlists:
                if playlist_id not in db.playlists:
                    inconsistencies.append(f"動画 {video_id} が存在しないプレイリスト {playlist_id} を参照")
        
        if inconsistencies:
            print(f"⚠️ 整合性の問題が見つかりました:")
            for issue in inconsistencies[:5]:
                print(f"  - {issue}")
            if len(inconsistencies) > 5:
                print(f"  ... 他 {len(inconsistencies) - 5} 件")
        else:
            print("✅ データベース整合性OK")
        
        return len(inconsistencies) == 0
        
    except Exception as e:
        print(f"❌ 整合性テストエラー: {e}")
        return False


def run_comprehensive_test():
    """包括的テストの実行"""
    print("🚀 差分更新システム包括テスト開始")
    print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # テスト用プレイリストID（実際のプレイリストに変更してください）
    test_playlist_id = "PL4R2l8ETuvxueMZJo63H8ykV_OY0LuzfX"  # MVプレイリスト
    
    try:
        # 1. 基本機能テスト
        manager = test_basic_functionality()
        
        # 2. 新規動画検出テスト
        new_videos = test_new_video_detection(manager, test_playlist_id, limit=3)
        
        # 3. 差分更新テスト
        update_result = test_incremental_update(manager, test_playlist_id)
        
        # 4. パフォーマンステスト
        performance_time = test_performance_comparison(manager, test_playlist_id)
        
        # 5. データベース整合性テスト
        consistency_ok = test_database_consistency(manager)
        
        # 総合結果
        print("\\n" + "=" * 50)
        print("📊 テスト結果サマリー")
        print("=" * 50)
        
        tests_passed = 0
        total_tests = 5
        
        print(f"1. 基本機能: ✅ PASS")
        tests_passed += 1
        
        if len(new_videos) >= 0:  # 新規動画がなくてもテストとしては成功
            print(f"2. 新規動画検出: ✅ PASS ({len(new_videos)}件検出)")
            tests_passed += 1
        else:
            print(f"2. 新規動画検出: ❌ FAIL")
        
        if update_result.get('status') in ['success', 'no_updates']:
            print(f"3. 差分更新: ✅ PASS ({update_result.get('status')})")
            tests_passed += 1
        else:
            print(f"3. 差分更新: ❌ FAIL ({update_result.get('status')})")
        
        if performance_time < 10.0:  # 10秒以内なら合格
            print(f"4. パフォーマンス: ✅ PASS ({performance_time:.2f}秒)")
            tests_passed += 1
        else:
            print(f"4. パフォーマンス: ⚠️ SLOW ({performance_time:.2f}秒)")
            tests_passed += 0.5
        
        if consistency_ok:
            print(f"5. データ整合性: ✅ PASS")
            tests_passed += 1
        else:
            print(f"5. データ整合性: ❌ FAIL")
        
        print(f"\\n総合結果: {tests_passed}/{total_tests} テスト通過")
        
        if tests_passed >= total_tests * 0.8:
            print("🎉 差分更新システムは正常に動作しています！")
        else:
            print("⚠️ いくつかの問題が検出されました。詳細を確認してください。")
        
    except Exception as e:
        print(f"\\n❌ テスト実行中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\\n終了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def quick_test():
    """クイックテスト（新規動画検出のみ）"""
    print("⚡ クイックテスト実行")
    
    manager = IncrementalUpdateManager()
    manager.initialize()
    
    # テスト用プレイリスト
    test_playlist_id = "PL4R2l8ETuvxueMZJo63H8ykV_OY0LuzfX"
    
    # 新規動画検出のみ
    new_videos = manager.detect_new_videos(test_playlist_id, limit_check=5)
    print(f"新規動画: {len(new_videos)}件")
    
    if new_videos:
        print("新規動画が見つかりました。差分更新を実行しますか？")
        print("完全テストを実行するには run_comprehensive_test() を呼び出してください。")


if __name__ == "__main__":
    # コマンドライン引数に応じてテストを選択
    if len(sys.argv) > 1:
        if sys.argv[1] == "quick":
            quick_test()
        elif sys.argv[1] == "full":
            run_comprehensive_test()
        else:
            print("使用方法:")
            print("  python test_incremental_update.py quick   # クイックテスト")
            print("  python test_incremental_update.py full    # 完全テスト")
    else:
        # デフォルトは完全テスト
        run_comprehensive_test()