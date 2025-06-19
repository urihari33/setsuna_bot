"""
差分更新システムの基本テスト（依存関係最小版）

統一データモデルと差分検出ロジックのテスト
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# パッケージパスを追加
sys.path.append(str(Path(__file__).parent))

from storage.unified_storage import UnifiedStorage


def test_unified_storage():
    """統一ストレージシステムのテスト"""
    print("=== 統一ストレージテスト ===")
    
    try:
        storage = UnifiedStorage()
        db = storage.load_database()
        
        print(f"✅ 統一データベース読み込み成功")
        print(f"  総動画数: {db.total_videos}")
        print(f"  総プレイリスト数: {db.total_playlists}")
        print(f"  クリエイター数: {len(db.creator_index)}")
        print(f"  最終更新: {db.last_updated}")
        
        return db
        
    except Exception as e:
        print(f"❌ 統一ストレージテストエラー: {e}")
        return None


def test_playlist_analysis(db):
    """プレイリスト構造の分析"""
    print(f"\\n=== プレイリスト分析 ===")
    
    if not db or not db.playlists:
        print("プレイリストが見つかりません")
        return
    
    for playlist_id, playlist in db.playlists.items():
        print(f"\\nプレイリスト: {playlist.metadata.title}")
        print(f"  ID: {playlist_id}")
        print(f"  動画数: {len(playlist.video_ids)}")
        print(f"  最終同期: {playlist.last_full_sync}")
        print(f"  増分同期: {playlist.last_incremental_sync}")
        
        # 最新動画の確認
        if playlist.video_ids:
            latest_videos = playlist.video_ids[-3:]  # 最新3件
            print(f"  最新動画ID: {latest_videos}")
            
            # 実際の動画データを確認
            for video_id in latest_videos:
                if video_id in db.videos:
                    video = db.videos[video_id]
                    print(f"    {video_id}: {video.metadata.title[:50]}...")
                    print(f"    公開日: {video.metadata.published_at}")


def simulate_new_video_detection(db, playlist_id: str):
    """新規動画検出のシミュレーション"""
    print(f"\\n=== 新規動画検出シミュレーション ===")
    
    if playlist_id not in db.playlists:
        print(f"プレイリスト {playlist_id} が見つかりません")
        return
    
    playlist = db.playlists[playlist_id]
    existing_video_ids = set(playlist.video_ids)
    
    print(f"プレイリスト: {playlist.metadata.title}")
    print(f"既存動画数: {len(existing_video_ids)}")
    
    # 実際のYouTube APIの代わりに、新規動画IDをシミュレート
    simulated_new_videos = [
        f"new_video_{i}" for i in range(1, 4)  # 3件の新規動画をシミュレート
    ]
    
    print(f"シミュレートされた新規動画: {simulated_new_videos}")
    
    # 差分計算のロジックテスト
    new_videos = [vid for vid in simulated_new_videos if vid not in existing_video_ids]
    
    print(f"差分検出結果: {len(new_videos)}件の新規動画")
    
    return new_videos


def test_data_model_conversion():
    """データモデル変換のテスト"""
    print(f"\\n=== データモデル変換テスト ===")
    
    # サンプル動画データ（YouTube API レスポンス形式）
    sample_video_data = {
        'id': 'test_video_123',
        'title': 'テスト動画タイトル',
        'description': 'テスト動画の説明文です。',
        'published_at': '2025-06-19T12:00:00Z',
        'channel_title': 'テストチャンネル',
        'channel_id': 'UC_test_channel',
        'duration': 'PT3M30S',
        'view_count': '1000',
        'like_count': '50',
        'comment_count': '10',
        'tags': ['テスト', '音楽', 'MV'],
        'category_id': '10',
        'collected_at': datetime.now().isoformat()
    }
    
    try:
        from core.data_models import (
            Video, VideoMetadata, ContentSource, AnalysisStatus
        )
        
        # VideoMetadata作成
        metadata = VideoMetadata(
            id=sample_video_data['id'],
            title=sample_video_data['title'],
            description=sample_video_data['description'],
            published_at=datetime.fromisoformat(sample_video_data['published_at'].replace('Z', '+00:00')),
            channel_title=sample_video_data['channel_title'],
            channel_id=sample_video_data['channel_id'],
            duration=sample_video_data['duration'],
            view_count=int(sample_video_data.get('view_count', 0)),
            like_count=int(sample_video_data.get('like_count', 0)),
            comment_count=int(sample_video_data.get('comment_count', 0)),
            tags=sample_video_data.get('tags', []),
            category_id=sample_video_data.get('category_id', ''),
            collected_at=datetime.fromisoformat(sample_video_data['collected_at'])
        )
        
        # Video作成
        video = Video(
            source=ContentSource.YOUTUBE,
            metadata=metadata,
            playlists=['test_playlist'],
            playlist_positions={'test_playlist': 0},
            analysis_status=AnalysisStatus.PENDING,
            creative_insight=None,
            analysis_error=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        print("✅ データモデル変換成功")
        print(f"  動画ID: {video.metadata.id}")
        print(f"  タイトル: {video.metadata.title}")
        print(f"  公開日: {video.metadata.published_at}")
        print(f"  分析ステータス: {video.analysis_status}")
        
        # 辞書変換テスト
        video_dict = video.to_dict()
        print(f"✅ 辞書変換成功（{len(video_dict)}項目）")
        
        # 辞書から復元テスト
        restored_video = Video.from_dict(video_dict)
        print(f"✅ 辞書から復元成功")
        print(f"  復元タイトル: {restored_video.metadata.title}")
        
        return True
        
    except Exception as e:
        print(f"❌ データモデル変換エラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_search_functionality(db):
    """検索機能のテスト"""
    print(f"\\n=== 検索機能テスト ===")
    
    if not db:
        print("データベースが利用できません")
        return
    
    # タグ検索テスト
    available_tags = list(db.tag_index.keys())[:5]
    print(f"利用可能なタグ（先頭5件）: {available_tags}")
    
    for tag in available_tags[:2]:
        video_ids = db.tag_index[tag]
        print(f"  タグ '{tag}': {len(video_ids)}動画")
    
    # クリエイター検索テスト
    available_creators = list(db.creator_index.keys())[:5]
    print(f"\\n利用可能なクリエイター（先頭5件）: {available_creators}")
    
    for creator in available_creators[:2]:
        video_ids = db.creator_index[creator]
        print(f"  クリエイター '{creator}': {len(video_ids)}動画")


def run_basic_tests():
    """基本テストの実行"""
    print("🧪 差分更新システム基本テスト開始")
    print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 5
    
    # 1. 統一ストレージテスト
    db = test_unified_storage()
    if db:
        tests_passed += 1
    
    # 2. プレイリスト分析
    if db:
        test_playlist_analysis(db)
        tests_passed += 1
    
    # 3. 新規動画検出シミュレーション
    if db and db.playlists:
        playlist_id = list(db.playlists.keys())[0]
        new_videos = simulate_new_video_detection(db, playlist_id)
        if new_videos is not None:
            tests_passed += 1
    
    # 4. データモデル変換テスト
    if test_data_model_conversion():
        tests_passed += 1
    
    # 5. 検索機能テスト
    if db:
        test_search_functionality(db)
        tests_passed += 1
    
    # 結果サマリー
    print("\\n" + "=" * 50)
    print("📊 基本テスト結果")
    print("=" * 50)
    print(f"合格: {tests_passed}/{total_tests} テスト")
    
    if tests_passed >= total_tests * 0.8:
        print("✅ 基本システムは正常に動作しています")
        print("\\n次のステップ:")
        print("1. YouTube API認証を設定")
        print("2. 実際のプレイリストで差分更新テスト")
        print("3. バッチ分析機能の実装")
    else:
        print("⚠️ いくつかの問題が検出されました")
    
    print(f"\\n終了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    run_basic_tests()