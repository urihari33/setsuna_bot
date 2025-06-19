"""
実際の差分更新テスト（修正版）

プレイリスト順序に依存せず、全件チェックで新規動画を確実に検出
"""

import sys
import pickle
from datetime import datetime

import googleapiclient.discovery
from google.oauth2.credentials import Credentials

sys.path.append('.')

from storage.unified_storage import UnifiedStorage
from core.data_models import (
    Video, Playlist, VideoMetadata, PlaylistMetadata,
    ContentSource, AnalysisStatus
)

# 認証設定
TOKEN_FILE = r"D:\setsuna_bot\config\youtube_token.json"
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'


def load_credentials():
    """認証情報を読み込み"""
    try:
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
        return creds
    except Exception as e:
        print(f"❌ 認証読み込みエラー: {e}")
        return None


def get_all_playlist_video_ids(service, playlist_id):
    """プレイリストの全動画IDを取得"""
    print(f"プレイリスト全動画取得中...")
    
    all_video_ids = []
    next_page_token = None
    page = 1
    
    try:
        while True:
            print(f"  ページ {page} 取得中...")
            
            request = service.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token,
                fields='items/snippet/resourceId/videoId,nextPageToken'
            )
            
            response = request.execute()
            
            page_video_ids = []
            for item in response.get('items', []):
                resource_id = item.get('snippet', {}).get('resourceId', {})
                if resource_id.get('kind') == 'youtube#video':
                    video_id = resource_id['videoId']
                    all_video_ids.append(video_id)
                    page_video_ids.append(video_id)
            
            print(f"    {len(page_video_ids)}件取得")
            
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
            
            page += 1
        
        print(f"✅ 全動画ID取得完了: {len(all_video_ids)}件")
        return all_video_ids
        
    except Exception as e:
        print(f"❌ プレイリスト取得エラー: {e}")
        return []


def test_real_incremental_update():
    """実際の差分更新テスト"""
    print("🚀 実際の差分更新テスト")
    print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 認証・サービス作成
    creds = load_credentials()
    if not creds:
        return False
    
    service = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=creds)
    print("✅ YouTube API接続成功")
    
    # 2. データベース読み込み
    print("\\n=== データベース読み込み ===")
    
    storage = UnifiedStorage()
    db = storage.load_database()
    
    test_playlist_id = 'PL4R2l8ETuvxueMZJo63H8ykV_OY0LuzfX'
    
    if test_playlist_id not in db.playlists:
        print(f"❌ プレイリストがデータベースに見つかりません")
        return False
    
    playlist = db.playlists[test_playlist_id]
    existing_video_ids = set(playlist.video_ids)
    
    print(f"既存動画数: {len(existing_video_ids)}")
    print(f"最新5件: {playlist.video_ids[-5:]}")
    
    # 3. YouTube APIで全動画ID取得
    print("\\n=== YouTube API全動画取得 ===")
    
    api_video_ids = get_all_playlist_video_ids(service, test_playlist_id)
    
    if not api_video_ids:
        print("❌ API動画取得失敗")
        return False
    
    api_video_ids_set = set(api_video_ids)
    
    # 4. 差分計算
    print("\\n=== 差分計算 ===")
    
    # 新規動画（APIにあってDBにない）
    new_videos = [vid for vid in api_video_ids if vid not in existing_video_ids]
    
    # 削除動画（DBにあってAPIにない）
    deleted_videos = [vid for vid in existing_video_ids if vid not in api_video_ids_set]
    
    print(f"API動画数: {len(api_video_ids)}")
    print(f"DB動画数: {len(existing_video_ids)}")
    print(f"新規動画: {len(new_videos)}件")
    print(f"削除動画: {len(deleted_videos)}件")
    
    # 5. 新規動画の詳細取得
    if new_videos:
        print(f"\\n=== 新規動画詳細取得 ===")
        print(f"新規動画ID: {new_videos}")
        
        try:
            # 新規動画の詳細を取得
            details_request = service.videos().list(
                part='snippet,statistics,contentDetails',
                id=','.join(new_videos)
            )
            details_response = details_request.execute()
            
            new_video_details = []
            
            for item in details_response.get('items', []):
                video_info = {
                    'id': item['id'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'published_at': item['snippet']['publishedAt'],
                    'channel_title': item['snippet']['channelTitle'],
                    'channel_id': item['snippet']['channelId'],
                    'duration': item['contentDetails']['duration'],
                    'view_count': item['statistics'].get('viewCount', '0'),
                    'like_count': item['statistics'].get('likeCount', '0'),
                    'comment_count': item['statistics'].get('commentCount', '0'),
                    'tags': item['snippet'].get('tags', []),
                    'category_id': item['snippet'].get('categoryId', ''),
                    'collected_at': datetime.now().isoformat()
                }
                
                new_video_details.append(video_info)
                
                print(f"  ✅ {item['id']}: {item['snippet']['title']}")
                print(f"    公開日: {item['snippet']['publishedAt']}")
                print(f"    再生回数: {item['statistics'].get('viewCount', '0')}")
            
            # 6. 統一データモデルに変換してデータベースに追加
            print(f"\\n=== データベース更新 ===")
            
            added_count = 0
            
            for video_data in new_video_details:
                try:
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
                        collected_at=datetime.fromisoformat(video_data['collected_at'])
                    )
                    
                    # Video作成
                    video = Video(
                        source=ContentSource.YOUTUBE,
                        metadata=metadata,
                        playlists=[test_playlist_id],
                        playlist_positions={test_playlist_id: len(playlist.video_ids) + added_count},
                        analysis_status=AnalysisStatus.PENDING,
                        creative_insight=None,
                        analysis_error=None,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    
                    # データベースに追加
                    storage.add_video(video)
                    added_count += 1
                    
                    print(f"  ✅ {video.metadata.title} をデータベースに追加")
                    
                except Exception as e:
                    print(f"  ❌ {video_data['id']} の追加でエラー: {e}")
            
            # プレイリストの動画リストを更新
            updated_playlist = storage.get_playlist(test_playlist_id)
            if updated_playlist:
                updated_playlist.video_ids.extend(new_videos)
                updated_playlist.total_videos = len(updated_playlist.video_ids)
                updated_playlist.last_incremental_sync = datetime.now()
                updated_playlist.updated_at = datetime.now()
                
                storage.add_playlist(updated_playlist)
            
            # 保存
            storage.save_database()
            
            print(f"\\n✅ データベース更新完了")
            print(f"  追加動画数: {added_count}")
            
        except Exception as e:
            print(f"❌ 新規動画処理エラー: {e}")
            import traceback
            traceback.print_exc()
    
    else:
        print("\\n新規動画はありませんでした")
    
    # 7. 最終確認
    print("\\n=== 最終確認 ===")
    
    final_db = storage.load_database()
    final_playlist = final_db.playlists[test_playlist_id]
    
    print(f"更新後動画数: {len(final_playlist.video_ids)}")
    print(f"最新5件: {final_playlist.video_ids[-5:]}")
    
    # 目標動画が含まれているかチェック
    target_video_id = 'SSjgr_ddMfA'
    if target_video_id in final_playlist.video_ids:
        print(f"✅ 目標動画 {target_video_id} がデータベースに存在")
    else:
        print(f"⚠️ 目標動画 {target_video_id} がデータベースに未存在")
    
    print("\\n" + "=" * 60)
    print(f"🎉 差分更新テスト完了")
    print(f"終了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return True


if __name__ == "__main__":
    test_real_incremental_update()