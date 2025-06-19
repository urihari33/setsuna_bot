"""
YouTube API接続テスト（Windows環境用）

Windowsパスで認証ファイルにアクセス
"""

import os
import json
import pickle
from datetime import datetime
from pathlib import Path

import googleapiclient.discovery
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials


# YouTube Data API設定
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

# 認証ファイルパス（Windows実パス）
CREDENTIALS_FILE = r"D:\setsuna_bot\config\youtube_credentials.json"
TOKEN_FILE = r"D:\setsuna_bot\config\youtube_token.json"


def load_credentials():
    """認証情報を読み込み"""
    print("=== 認証情報読み込み ===")
    print(f"認証ファイル: {CREDENTIALS_FILE}")
    print(f"トークンファイル: {TOKEN_FILE}")
    
    creds = None
    
    # 既存のトークンファイルを確認
    if os.path.exists(TOKEN_FILE):
        print(f"既存トークンファイル発見")
        try:
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
            print("✅ 既存トークン読み込み成功")
        except Exception as e:
            print(f"⚠️ トークン読み込みエラー: {e}")
            creds = None
    
    # 認証が無効または存在しない場合
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("トークンの更新を試行中...")
            try:
                creds.refresh(Request())
                print("✅ トークン更新成功")
            except Exception as e:
                print(f"❌ トークン更新失敗: {e}")
                creds = None
        
        if not creds:
            print("新規認証が必要です")
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"❌ 認証ファイルが見つかりません: {CREDENTIALS_FILE}")
                return None
            
            print("OAuth認証フローを開始...")
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            print("✅ 新規認証完了")
        
        # トークンを保存
        try:
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
            print(f"✅ トークンを保存")
        except Exception as e:
            print(f"⚠️ トークン保存エラー: {e}")
    
    return creds


def create_youtube_service(credentials):
    """YouTubeサービスを作成"""
    print("\\n=== YouTubeサービス作成 ===")
    
    if not credentials:
        print("❌ 認証情報がありません")
        return None
    
    try:
        service = googleapiclient.discovery.build(
            API_SERVICE_NAME, API_VERSION, credentials=credentials)
        print("✅ YouTubeサービス作成成功")
        return service
    except Exception as e:
        print(f"❌ YouTubeサービス作成エラー: {e}")
        return None


def test_incremental_detection():
    """差分検出テスト（メイン処理）"""
    print("🔗 差分検出テスト開始")
    print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 認証
    credentials = load_credentials()
    if not credentials:
        print("\\n❌ 認証に失敗しました")
        return False
    
    # 2. YouTubeサービス作成
    service = create_youtube_service(credentials)
    if not service:
        print("\\n❌ YouTubeサービスの作成に失敗しました")
        return False
    
    # 3. 既存データベース読み込み
    print("\\n=== 既存データベース確認 ===")
    import sys
    sys.path.append('.')
    
    from storage.unified_storage import UnifiedStorage
    
    storage = UnifiedStorage()
    db = storage.load_database()
    
    test_playlist_id = 'PL4R2l8ETuvxueMZJo63H8ykV_OY0LuzfX'
    
    if test_playlist_id not in db.playlists:
        print(f"❌ プレイリスト {test_playlist_id} がデータベースに見つかりません")
        return False
    
    playlist = db.playlists[test_playlist_id]
    existing_count = len(playlist.video_ids)
    print(f"既存データベース動画数: {existing_count}")
    print(f"最新5件: {playlist.video_ids[-5:]}")
    
    # 4. YouTube APIで最新動画取得
    print("\\n=== YouTube API最新動画取得 ===")
    
    try:
        request = service.playlistItems().list(
            part='snippet',
            playlistId=test_playlist_id,
            maxResults=5,
            fields='items/snippet/resourceId/videoId'
        )
        response = request.execute()
        
        api_video_ids = []
        for item in response.get('items', []):
            resource_id = item.get('snippet', {}).get('resourceId', {})
            if resource_id.get('kind') == 'youtube#video':
                api_video_ids.append(resource_id['videoId'])
        
        print(f"YouTube API最新5件: {api_video_ids}")
        
    except Exception as e:
        print(f"❌ YouTube API呼び出しエラー: {e}")
        return False
    
    # 5. 差分計算
    print("\\n=== 差分計算 ===")
    
    existing_ids = set(playlist.video_ids)
    new_videos = [vid for vid in api_video_ids if vid not in existing_ids]
    
    print(f"新規動画検出: {len(new_videos)}件")
    if new_videos:
        print(f"新規動画ID: {new_videos}")
        
        # 新規動画の詳細取得
        print("\\n=== 新規動画詳細取得 ===")
        
        try:
            details_request = service.videos().list(
                part='snippet,statistics,contentDetails',
                id=','.join(new_videos)
            )
            details_response = details_request.execute()
            
            for item in details_response.get('items', []):
                title = item['snippet']['title']
                published = item['snippet']['publishedAt']
                view_count = item['statistics'].get('viewCount', '0')
                
                print(f"  {item['id']}: {title}")
                print(f"    公開日: {published}")
                print(f"    再生回数: {view_count}")
            
        except Exception as e:
            print(f"❌ 動画詳細取得エラー: {e}")
    
    else:
        print("新規動画はありませんでした")
    
    print("\\n" + "=" * 60)
    print("✅ 差分検出テスト完了")
    print(f"終了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return True


if __name__ == "__main__":
    test_incremental_detection()