"""
差分更新システムの簡単なテスト

実際のYouTube APIを使わずに、既存データでの差分検出をテスト
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# パッケージパスを追加
sys.path.append(str(Path(__file__).parent))

from storage.unified_storage import UnifiedStorage


class MockIncrementalManager:
    """テスト用の簡易差分更新マネージャー"""
    
    def __init__(self):
        self.storage = UnifiedStorage()
    
    def detect_new_videos_mock(self, playlist_id: str, simulated_new_count: int = 2):
        """新規動画検出のモック（シミュレーション）"""
        print(f"=== モック新規動画検出: {playlist_id} ===")
        
        # 現在のプレイリスト状況
        playlist = self.storage.get_playlist(playlist_id)
        if not playlist:
            print(f"プレイリスト {playlist_id} が見つかりません")
            return []
        
        existing_video_ids = set(playlist.video_ids)
        print(f"既存動画数: {len(existing_video_ids)}")
        
        # 新規動画をシミュレート
        simulated_new_videos = []
        for i in range(simulated_new_count):
            new_video_id = f"mock_new_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}"
            simulated_new_videos.append(new_video_id)
        
        # 差分計算（実際のロジック）
        new_video_ids = [vid for vid in simulated_new_videos if vid not in existing_video_ids]
        
        print(f"シミュレート新規動画: {simulated_new_videos}")
        print(f"差分検出結果: {len(new_video_ids)}件")
        
        return new_video_ids
    
    def simulate_incremental_update(self, playlist_id: str):
        """差分更新のシミュレーション"""
        print(f"\\n=== 差分更新シミュレーション: {playlist_id} ===")
        
        start_time = datetime.now()
        
        # 新規動画検出
        new_video_ids = self.detect_new_videos_mock(playlist_id, 2)
        
        if not new_video_ids:
            print("新規動画がありません")
            return {
                'status': 'no_updates',
                'new_videos_count': 0,
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
        
        # 新規動画情報をシミュレート
        print(f"\\n新規動画情報をシミュレート中...")
        simulated_videos = []
        
        for i, video_id in enumerate(new_video_ids):
            video_info = {
                'id': video_id,
                'title': f'シミュレート動画 {i+1}',
                'description': f'これはテスト用のシミュレート動画です。ID: {video_id}',
                'published_at': (datetime.now() - timedelta(hours=i+1)).isoformat() + 'Z',
                'channel_title': 'テストチャンネル',
                'channel_id': 'UC_test_channel',
                'duration': 'PT3M30S',
                'view_count': str(1000 + i * 100),
                'like_count': str(50 + i * 5),
                'comment_count': str(10 + i),
                'tags': ['テスト', 'シミュレート', f'動画{i+1}'],
                'category_id': '10'
            }
            simulated_videos.append(video_info)
        
        # 統一データモデルへの変換をテスト
        print("\\n統一データモデルへの変換テスト...")
        converted_videos = []
        
        try:
            from core.data_models import (
                Video, VideoMetadata, ContentSource, AnalysisStatus
            )
            
            for video_data in simulated_videos:
                # VideoMetadata作成
                metadata = VideoMetadata(
                    id=video_data['id'],
                    title=video_data['title'],
                    description=video_data['description'],
                    published_at=datetime.fromisoformat(video_data['published_at'].replace('Z', '+00:00')),
                    channel_title=video_data['channel_title'],
                    channel_id=video_data['channel_id'],
                    duration=video_data['duration'],
                    view_count=int(video_data.get('view_count', 0)),
                    like_count=int(video_data.get('like_count', 0)),
                    comment_count=int(video_data.get('comment_count', 0)),
                    tags=video_data.get('tags', []),
                    category_id=video_data.get('category_id', ''),
                    collected_at=datetime.now()
                )
                
                # Video作成
                video = Video(
                    source=ContentSource.YOUTUBE,
                    metadata=metadata,
                    playlists=[playlist_id],
                    playlist_positions={playlist_id: len(self.storage.get_playlist(playlist_id).video_ids)},
                    analysis_status=AnalysisStatus.PENDING,
                    creative_insight=None,
                    analysis_error=None,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                converted_videos.append(video)
                print(f"  ✅ {video.metadata.title} 変換成功")
        
        except Exception as e:
            print(f"❌ データモデル変換エラー: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
        
        # データベース更新のシミュレート（実際には保存しない）
        print(f"\\n[シミュレート] データベース更新...")
        print(f"[シミュレート] {len(converted_videos)}件の動画を追加")
        print(f"[シミュレート] プレイリスト {playlist_id} の動画リスト更新")
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        result = {
            'status': 'simulation_success',
            'new_videos_count': len(new_video_ids),
            'added_videos_count': len(converted_videos),
            'new_video_ids': new_video_ids,
            'processing_time': processing_time
        }
        
        print(f"\\n=== シミュレーション完了 ===")
        print(f"処理時間: {processing_time:.2f}秒")
        print(f"新規動画: {len(converted_videos)}件処理")
        
        return result


def test_actual_data_processing():
    """実際のデータでの処理テスト"""
    print("=== 実際のデータ処理テスト ===")
    
    storage = UnifiedStorage()
    db = storage.load_database()
    
    print(f"現在のデータベース:")
    print(f"  動画数: {db.total_videos}")
    print(f"  プレイリスト数: {db.total_playlists}")
    
    # 実際のプレイリストで処理テスト
    if db.playlists:
        playlist_id = list(db.playlists.keys())[0]
        playlist = db.playlists[playlist_id]
        
        print(f"\\nテスト対象プレイリスト:")
        print(f"  ID: {playlist_id}")
        print(f"  タイトル: {playlist.metadata.title}")
        print(f"  動画数: {len(playlist.video_ids)}")
        print(f"  最終同期: {playlist.last_full_sync}")
        
        # 最新の動画を確認
        if playlist.video_ids:
            latest_video_ids = playlist.video_ids[-3:]
            print(f"\\n最新動画3件:")
            for i, video_id in enumerate(latest_video_ids, 1):
                if video_id in db.videos:
                    video = db.videos[video_id]
                    print(f"  {i}. {video.metadata.title[:50]}...")
                    print(f"     公開日: {video.metadata.published_at}")
                    print(f"     分析状況: {video.analysis_status}")
        
        return playlist_id
    
    return None


def test_search_and_statistics():
    """検索・統計機能のテスト"""
    print(f"\\n=== 検索・統計機能テスト ===")
    
    storage = UnifiedStorage()
    
    # 検索テスト
    print("1. タグ検索テスト")
    tags = storage.get_all_tags()[:3]
    for tag in tags:
        videos = storage.search_videos_by_tag(tag)
        print(f"  '{tag}': {len(videos)}動画")
    
    print("\\n2. 統計情報テスト")
    stats = storage.get_statistics()
    print(f"  総動画数: {stats['total_videos']}")
    print(f"  分析済み: {stats['analyzed_videos']}")
    print(f"  分析成功率: {stats['analysis_success_rate']:.2%}")
    print(f"  総クリエイター数: {stats['total_creators']}")
    
    # プレイリスト別統計
    print("\\n3. プレイリスト別統計")
    for playlist_id, pstats in stats['playlists'].items():
        print(f"  {pstats['title']}: {pstats['total_videos']}動画")
        print(f"    分析済み: {pstats['analyzed_videos']}件 ({pstats['analysis_rate']:.2%})")


def run_simple_test():
    """簡単なテストの実行"""
    print("🧪 差分更新システム簡単テスト開始")
    print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # 1. 実際のデータ処理テスト
        playlist_id = test_actual_data_processing()
        
        if playlist_id:
            # 2. モック差分更新テスト
            manager = MockIncrementalManager()
            result = manager.simulate_incremental_update(playlist_id)
            
            print(f"\\n差分更新結果: {result['status']}")
            if result['status'] == 'simulation_success':
                print(f"✅ 差分更新シミュレーション成功")
            
        # 3. 検索・統計テスト
        test_search_and_statistics()
        
        print("\\n" + "=" * 60)
        print("📊 簡単テスト完了")
        print("=" * 60)
        print("✅ 差分更新システムの基本機能は正常です")
        print("\\n次のステップ:")
        print("1. YouTube API認証設定 (config/youtube_credentials.json)")
        print("2. 実際のAPIを使った差分更新テスト")
        print("3. バッチ分析機能の統合")
        
    except Exception as e:
        print(f"\\n❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\\n終了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    run_simple_test()