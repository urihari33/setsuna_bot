"""
データベース修正スクリプト

日時フォーマット問題を修正して統一データベースを再構築
"""

import sys
import json
from datetime import datetime
from pathlib import Path

sys.path.append('.')

from storage.unified_storage import UnifiedStorage
from core.data_models import *


def fix_datetime_format(dt_string):
    """日時文字列のフォーマットを修正"""
    if dt_string.endswith('Z'):
        return dt_string.replace('Z', '+00:00')
    return dt_string


def manual_migrate_playlist():
    """手動でプレイリストデータを移行"""
    print("=== 手動プレイリスト移行 ===")
    
    # プレイリストファイルを直接読み込み
    playlist_file = Path(r"D:\setsuna_bot\youtube_knowledge_system\data\playlists\playlist_PL4R2l8ETuvxueMZJo63H8ykV_OY0LuzfX.json")
    
    if not playlist_file.exists():
        print(f"❌ プレイリストファイルが見つかりません: {playlist_file}")
        return False
    
    try:
        with open(playlist_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ プレイリストファイル読み込み成功")
        print(f"動画数: {data['total_videos']}")
        
        # プレイリストメタデータ作成（日時フォーマット修正）
        playlist_info = data['playlist_info']
        
        metadata = PlaylistMetadata(
            id=playlist_info['id'],
            title=playlist_info['title'],
            description=playlist_info['description'],
            channel_title=playlist_info['channel_title'],
            channel_id=playlist_info['channel_id'],
            published_at=datetime.fromisoformat(fix_datetime_format(playlist_info['published_at'])),
            item_count=playlist_info['item_count'],
            collected_at=datetime.fromisoformat(data['last_updated'])
        )
        
        # 動画IDリストを作成
        video_ids = []
        videos_for_db = {}
        
        for video_data in data['videos']:
            video_id = video_data['id']
            video_ids.append(video_id)
            
            # VideoMetadata作成（日時フォーマット修正）
            video_metadata = VideoMetadata(
                id=video_data['id'],
                title=video_data['title'],
                description=video_data['description'],
                published_at=datetime.fromisoformat(fix_datetime_format(video_data['published_at'])),
                channel_title=video_data['channel_title'],
                channel_id=video_data['channel_id'],
                duration=video_data['duration'],
                view_count=int(video_data.get('view_count', 0)),
                like_count=int(video_data.get('like_count', 0)),
                comment_count=int(video_data.get('comment_count', 0)),
                tags=video_data.get('tags', []),
                category_id=video_data.get('category_id', ''),
                collected_at=datetime.fromisoformat(video_data['collected_at'])
            )
            
            # Video作成
            video = Video(
                source=ContentSource.YOUTUBE,
                metadata=video_metadata,
                playlists=[playlist_info['id']],
                playlist_positions={playlist_info['id']: video_data.get('position', 0)},
                analysis_status=AnalysisStatus.PENDING,
                creative_insight=None,
                analysis_error=None,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            videos_for_db[video_id] = video
        
        # Playlist作成
        playlist = Playlist(
            source=ContentSource.YOUTUBE,
            metadata=metadata,
            video_ids=video_ids,
            last_full_sync=datetime.fromisoformat(data['last_updated']),
            last_incremental_sync=None,
            sync_settings={},
            total_videos=data['total_videos'],
            analyzed_videos=0,
            analysis_success_rate=0.0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # 統一データベースに保存
        storage = UnifiedStorage()
        
        # 動画を追加
        for video in videos_for_db.values():
            storage.add_video(video)
        
        # プレイリストを追加
        storage.add_playlist(playlist)
        
        # 保存
        storage.save_database()
        
        print(f"✅ 移行完了")
        print(f"  プレイリスト: {metadata.title}")
        print(f"  動画数: {len(video_ids)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 移行エラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_database():
    """データベースの確認"""
    print("\\n=== データベース確認 ===")
    
    try:
        storage = UnifiedStorage()
        db = storage.load_database()
        
        print(f"総動画数: {db.total_videos}")
        print(f"総プレイリスト数: {db.total_playlists}")
        
        # プレイリスト詳細
        for playlist_id, playlist in db.playlists.items():
            print(f"\\nプレイリスト: {playlist.metadata.title}")
            print(f"  ID: {playlist_id}")
            print(f"  動画数: {len(playlist.video_ids)}")
            print(f"  最新動画: {playlist.video_ids[-3:] if playlist.video_ids else []}")
        
        return True, db
        
    except Exception as e:
        print(f"❌ データベース確認エラー: {e}")
        return False, None


def main():
    """メイン実行"""
    print("🔧 データベース修正開始")
    print("=" * 50)
    
    # 手動移行実行
    if manual_migrate_playlist():
        # 確認
        success, db = verify_database()
        
        if success:
            print("\\n✅ データベース修正完了")
            print("これで test_api_windows.py を再実行できます")
        else:
            print("\\n❌ データベース確認で問題発生")
    else:
        print("\\n❌ データベース移行失敗")


if __name__ == "__main__":
    main()