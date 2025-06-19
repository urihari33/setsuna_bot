"""
実際の差分更新テスト（修正版2）

fields指定を修正してプレイリスト全動画を確実に取得
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
    """プレイリストの全動画IDを取得（修正版）"""
    print(f"プレイリスト全動画取得中...")
    
    all_video_ids = []
    next_page_token = None
    page = 1
    
    try:
        while True:
            print(f"  ページ {page} 取得中...")
            
            # fields指定を簡素化
            request = service.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
            
            response = request.execute()
            
            page_video_ids = []
            items = response.get('items', [])
            print(f"    レスポンス項目数: {len(items)}")
            
            for item in items:
                snippet = item.get('snippet', {})
                resource_id = snippet.get('resourceId', {})
                
                if resource_id.get('kind') == 'youtube#video':
                    video_id = resource_id.get('videoId')
                    if video_id:
                        all_video_ids.append(video_id)
                        page_video_ids.append(video_id)
                else:
                    print(f"    非動画アイテム: {resource_id.get('kind', 'unknown')}")
            
            print(f"    動画ID取得: {len(page_video_ids)}件")
            if page_video_ids:
                print(f"    例: {page_video_ids[:3]}")
            
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                print(f"  最終ページに到達")
                break
            
            page += 1
            
            # 安全のため10ページでストップ
            if page > 10:
                print(f"  10ページ制限に到達")
                break
        
        print(f"✅ 全動画ID取得完了: {len(all_video_ids)}件")
        return all_video_ids
        
    except Exception as e:
        print(f"❌ プレイリスト取得エラー: {e}")
        import traceback
        traceback.print_exc()
        return []


def test_simple_api_call(service, playlist_id):
    """シンプルなAPI呼び出しテスト"""
    print("\\n=== シンプルAPI呼び出しテスト ===")
    
    try:
        # 最もシンプルな呼び出し
        request = service.playlistItems().list(
            part='snippet',
            playlistId=playlist_id,
            maxResults=5
        )
        
        response = request.execute()
        
        print(f"レスポンス構造:")
        print(f"  items数: {len(response.get('items', []))}")
        
        if response.get('items'):
            first_item = response['items'][0]
            print(f"  最初のアイテム構造:")
            print(f"    kind: {first_item.get('kind')}")
            print(f"    snippet keys: {list(first_item.get('snippet', {}).keys())}")
            
            resource_id = first_item.get('snippet', {}).get('resourceId', {})
            print(f"    resourceId: {resource_id}")
        
        return len(response.get('items', []))
        
    except Exception as e:
        print(f"❌ シンプルAPI呼び出しエラー: {e}")
        import traceback
        traceback.print_exc()
        return 0


def test_real_incremental_update():
    """実際の差分更新テスト（修正版）"""
    print("🚀 実際の差分更新テスト（修正版）")
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
    
    # 3. シンプルAPI呼び出しテスト
    simple_count = test_simple_api_call(service, test_playlist_id)
    
    if simple_count == 0:
        print("❌ シンプルAPI呼び出しも失敗")
        return False
    
    # 4. 全動画取得
    print("\\n=== YouTube API全動画取得 ===")
    
    api_video_ids = get_all_playlist_video_ids(service, test_playlist_id)
    
    if not api_video_ids:
        print("❌ API動画取得失敗")
        return False
    
    api_video_ids_set = set(api_video_ids)
    
    # 5. 差分計算
    print("\\n=== 差分計算 ===")
    
    new_videos = [vid for vid in api_video_ids if vid not in existing_video_ids]
    deleted_videos = [vid for vid in existing_video_ids if vid not in api_video_ids_set]
    
    print(f"API動画数: {len(api_video_ids)}")
    print(f"DB動画数: {len(existing_video_ids)}")
    print(f"新規動画: {len(new_videos)}件")
    print(f"削除動画: {len(deleted_videos)}件")
    
    if new_videos:
        print(f"新規動画ID: {new_videos}")
        
        # 目標動画が含まれているかチェック
        target_video_id = 'SSjgr_ddMfA'
        if target_video_id in new_videos:
            print(f"✅ 目標動画 {target_video_id} が新規動画に含まれています！")
        else:
            print(f"⚠️ 目標動画 {target_video_id} が新規動画に含まれていません")
            if target_video_id in api_video_ids:
                print(f"  → ただし、API結果には含まれています")
            else:
                print(f"  → API結果にも含まれていません")
    
    # 6. 新規動画の詳細取得と追加
    if new_videos:
        print(f"\\n=== 新規動画詳細取得・追加 ===")
        
        try:
            # 動画詳細取得
            details_request = service.videos().list(
                part='snippet,statistics,contentDetails',
                id=','.join(new_videos)
            )
            details_response = details_request.execute()
            
            added_count = 0
            
            for item in details_response.get('items', []):
                video_id = item['id']
                title = item['snippet']['title']
                
                print(f"  処理中: {video_id} - {title}")
                
                # VideoMetadata作成
                metadata = VideoMetadata(
                    id=video_id,
                    title=title,
                    description=item['snippet']['description'],
                    published_at=datetime.fromisoformat(item['snippet']['publishedAt'].replace('Z', '+00:00')),
                    channel_title=item['snippet']['channelTitle'],
                    channel_id=item['snippet']['channelId'],
                    duration=item['contentDetails']['duration'],
                    view_count=int(item['statistics'].get('viewCount', 0)),
                    like_count=int(item['statistics'].get('likeCount', 0)),
                    comment_count=int(item['statistics'].get('commentCount', 0)),
                    tags=item['snippet'].get('tags', []),
                    category_id=item['snippet'].get('categoryId', ''),
                    collected_at=datetime.now()
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
                
                print(f"    ✅ データベースに追加完了")
            
            # プレイリスト更新
            updated_playlist = storage.get_playlist(test_playlist_id)
            if updated_playlist:
                updated_playlist.video_ids.extend(new_videos)
                updated_playlist.total_videos = len(updated_playlist.video_ids)
                updated_playlist.last_incremental_sync = datetime.now()
                updated_playlist.updated_at = datetime.now()
                storage.add_playlist(updated_playlist)
            
            # 保存
            storage.save_database()
            
            print(f"\\n✅ データベース更新完了: {added_count}件追加")
            
        except Exception as e:
            print(f"❌ 動画追加エラー: {e}")
            import traceback
            traceback.print_exc()
    
    # 7. 最終確認
    print("\\n=== 最終確認 ===")
    
    final_db = storage.load_database()
    final_playlist = final_db.playlists[test_playlist_id]
    
    print(f"更新後動画数: {len(final_playlist.video_ids)}")
    print(f"最新5件: {final_playlist.video_ids[-5:]}")
    
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