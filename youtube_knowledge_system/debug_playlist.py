"""
プレイリスト詳細デバッグスクリプト

YouTube APIで実際のプレイリストの状況を詳しく確認
"""

import sys
import pickle
from datetime import datetime

import googleapiclient.discovery
from google.oauth2.credentials import Credentials

sys.path.append('.')

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


def debug_playlist_details():
    """プレイリストの詳細を調査"""
    print("🔍 プレイリスト詳細デバッグ")
    print("=" * 60)
    
    # 認証
    creds = load_credentials()
    if not creds:
        return
    
    service = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=creds)
    
    test_playlist_id = 'PL4R2l8ETuvxueMZJo63H8ykV_OY0LuzfX'
    target_video_id = 'SSjgr_ddMfA'  # 追加した動画ID
    
    # 1. プレイリスト基本情報
    print("1. プレイリスト基本情報")
    try:
        playlist_request = service.playlists().list(
            part='snippet,contentDetails',
            id=test_playlist_id
        )
        playlist_response = playlist_request.execute()
        
        if playlist_response['items']:
            playlist = playlist_response['items'][0]
            print(f"タイトル: {playlist['snippet']['title']}")
            print(f"動画数: {playlist['contentDetails']['itemCount']}")
            print(f"更新日: {playlist['snippet']['publishedAt']}")
        
    except Exception as e:
        print(f"❌ プレイリスト情報取得エラー: {e}")
        return
    
    # 2. 最新10件の動画を取得
    print(f"\\n2. 最新10件の動画ID取得")
    try:
        items_request = service.playlistItems().list(
            part='snippet',
            playlistId=test_playlist_id,
            maxResults=10
        )
        items_response = items_request.execute()
        
        video_ids = []
        print(f"取得件数: {len(items_response.get('items', []))}")
        
        for i, item in enumerate(items_response.get('items', []), 1):
            resource_id = item['snippet']['resourceId']
            if resource_id['kind'] == 'youtube#video':
                video_id = resource_id['videoId']
                video_ids.append(video_id)
                
                # 目標動画かチェック
                marker = " ← 🎯 TARGET" if video_id == target_video_id else ""
                print(f"  {i:2d}. {video_id}{marker}")
        
    except Exception as e:
        print(f"❌ プレイリスト動画取得エラー: {e}")
        return
    
    # 3. 目標動画を直接検索
    print(f"\\n3. 目標動画の直接確認")
    print(f"目標動画ID: {target_video_id}")
    
    try:
        video_request = service.videos().list(
            part='snippet',
            id=target_video_id
        )
        video_response = video_request.execute()
        
        if video_response['items']:
            video = video_response['items'][0]
            print(f"✅ 動画存在確認: {video['snippet']['title']}")
            print(f"公開日: {video['snippet']['publishedAt']}")
            print(f"チャンネル: {video['snippet']['channelTitle']}")
        else:
            print(f"❌ 動画が見つかりません")
        
    except Exception as e:
        print(f"❌ 動画検索エラー: {e}")
    
    # 4. プレイリスト内検索
    print(f"\\n4. プレイリスト内で目標動画を検索")
    
    found = False
    next_page_token = None
    page = 1
    
    try:
        while not found and page <= 5:  # 最大5ページまで
            print(f"ページ {page} 検索中...")
            
            search_request = service.playlistItems().list(
                part='snippet',
                playlistId=test_playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
            search_response = search_request.execute()
            
            for item in search_response.get('items', []):
                resource_id = item['snippet']['resourceId']
                if resource_id['kind'] == 'youtube#video':
                    video_id = resource_id['videoId']
                    if video_id == target_video_id:
                        print(f"✅ 目標動画をプレイリスト内で発見！")
                        print(f"位置: ページ{page}")
                        print(f"タイトル: {item['snippet']['title']}")
                        found = True
                        break
            
            next_page_token = search_response.get('nextPageToken')
            if not next_page_token:
                break
            
            page += 1
        
        if not found:
            print(f"❌ 目標動画がプレイリスト内に見つかりませんでした")
            print(f"可能性:")
            print(f"  1. 動画がプレイリストに実際に追加されていない")
            print(f"  2. プライベート動画のため取得できない")
            print(f"  3. YouTube API側の反映遅延")
        
    except Exception as e:
        print(f"❌ プレイリスト検索エラー: {e}")
    
    # 5. データベース比較
    print(f"\\n5. データベースとの比較")
    
    try:
        from storage.unified_storage import UnifiedStorage
        
        storage = UnifiedStorage()
        db = storage.load_database()
        playlist = db.playlists[test_playlist_id]
        
        print(f"データベース動画数: {len(playlist.video_ids)}")
        print(f"API取得動画数: {len(video_ids)}")
        
        db_ids = set(playlist.video_ids)
        api_ids = set(video_ids)
        
        only_in_db = db_ids - api_ids
        only_in_api = api_ids - db_ids
        
        if only_in_db:
            print(f"データベースのみ: {len(only_in_db)}件")
            print(f"  例: {list(only_in_db)[:3]}")
        
        if only_in_api:
            print(f"APIのみ: {len(only_in_api)}件")
            print(f"  例: {list(only_in_api)[:3]}")
        
        if target_video_id in db_ids:
            print(f"✅ 目標動画はデータベースに存在")
        else:
            print(f"❌ 目標動画はデータベースに未存在")
            
    except Exception as e:
        print(f"❌ データベース比較エラー: {e}")


if __name__ == "__main__":
    debug_playlist_details()