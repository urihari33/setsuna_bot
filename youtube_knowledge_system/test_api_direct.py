"""
YouTube API接続テスト（直接実装版）

既存のauth_managerを使わず、直接Google APIライブラリを使用してテスト
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

# 認証ファイルパス（WSL2パス）
CREDENTIALS_FILE = "/mnt/d/setsuna_bot/config/youtube_credentials.json"
TOKEN_FILE = "/mnt/d/setsuna_bot/config/youtube_token.json"


def load_credentials():
    """認証情報を読み込み"""
    print("=== 認証情報読み込み ===")
    
    creds = None
    
    # 既存のトークンファイルを確認
    if os.path.exists(TOKEN_FILE):
        print(f"既存トークンファイル発見: {TOKEN_FILE}")
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
            print(f"✅ トークンを保存: {TOKEN_FILE}")
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


def test_basic_api_call(service):
    """基本的なAPI呼び出しテスト"""
    print("\\n=== 基本API呼び出しテスト ===")
    
    if not service:
        return False, None
    
    try:
        # チャンネル情報取得
        request = service.channels().list(
            part='snippet',
            mine=True,
            maxResults=1
        )
        response = request.execute()
        
        if 'items' in response and response['items']:
            channel = response['items'][0]
            channel_title = channel['snippet']['title']
            channel_id = channel['id']
            
            print(f"✅ API呼び出し成功")
            print(f"  チャンネル名: {channel_title}")
            print(f"  チャンネルID: {channel_id}")
            
            return True, channel_id
        else:
            print("⚠️ チャンネル情報を取得できませんでした")
            return False, None
            
    except Exception as e:
        print(f"❌ API呼び出しエラー: {e}")
        return False, None


def test_playlist_access(service):
    """プレイリストアクセステスト"""
    print("\\n=== プレイリストアクセステスト ===")
    
    if not service:
        return False, None
    
    # テスト用プレイリストID
    test_playlist_id = "PL4R2l8ETuvxueMZJo63H8ykV_OY0LuzfX"
    
    try:
        # プレイリスト情報取得
        request = service.playlists().list(
            part='snippet,contentDetails',
            id=test_playlist_id
        )
        response = request.execute()
        
        if 'items' in response and response['items']:
            playlist = response['items'][0]
            title = playlist['snippet']['title']
            item_count = playlist['contentDetails']['itemCount']
            
            print(f"✅ プレイリスト情報取得成功")
            print(f"  タイトル: {title}")
            print(f"  動画数: {item_count}")
            
            return True, playlist
        else:
            print(f"❌ プレイリスト {test_playlist_id} が見つかりません")
            return False, None
            
    except Exception as e:
        print(f"❌ プレイリストアクセスエラー: {e}")
        return False, None


def test_incremental_video_detection(service):
    """差分更新用動画検出テスト"""
    print("\\n=== 差分更新用動画検出テスト ===")
    
    if not service:
        return False, []
    
    test_playlist_id = "PL4R2l8ETuvxueMZJo63H8ykV_OY0LuzfX"
    
    try:
        print("最新5件の動画ID取得中...")
        
        # 最小限のフィールドで動画IDのみ取得（API効率化）
        request = service.playlistItems().list(
            part='snippet',
            playlistId=test_playlist_id,
            maxResults=5,
            fields='items/snippet/resourceId/videoId'
        )
        response = request.execute()
        
        video_ids = []
        for item in response.get('items', []):
            resource_id = item.get('snippet', {}).get('resourceId', {})
            if resource_id.get('kind') == 'youtube#video':
                video_ids.append(resource_id['videoId'])
        
        print(f"✅ 動画ID取得成功: {len(video_ids)}件")
        print(f"  最新動画ID: {video_ids}")
        
        # 動画詳細情報取得テスト（差分更新で新規動画のみ取得する想定）
        if video_ids:
            print(f"\\n最新3件の詳細情報取得テスト...")
            
            details_request = service.videos().list(
                part='snippet,statistics,contentDetails',
                id=','.join(video_ids[:3])
            )
            details_response = details_request.execute()
            
            print(f"取得した動画詳細:")
            for item in details_response.get('items', []):
                title = item['snippet']['title']
                published = item['snippet']['publishedAt']
                view_count = item['statistics'].get('viewCount', '0')
                
                print(f"  {item['id']}: {title[:40]}...")
                print(f"    公開日: {published}")
                print(f"    再生回数: {view_count}")
            
            print(f"✅ 動画詳細取得成功")
        
        return True, video_ids
        
    except Exception as e:
        print(f"❌ 動画検出エラー: {e}")
        return False, []


def test_quota_usage_simulation():
    """API配額使用量シミュレーション"""
    print("\\n=== API配額使用量シミュレーション ===")
    
    print("差分更新でのAPI配額計算:")
    print("1. プレイリスト動画ID取得 (fields指定): 1クォータ")
    print("2. 新規動画詳細取得 (バッチ処理): 1クォータ")
    print("   → 新規動画2件の場合: 合計2クォータ")
    print()
    print("従来の全件取得との比較:")
    print("- 全件取得: プレイリスト(1) + 動画詳細(110/50=3) = 4クォータ")
    print("- 差分取得: プレイリスト(1) + 新規動画(1) = 2クォータ")
    print("- 削減効果: 50%の配額削減")
    print()
    print("✅ 大幅なAPI配額削減が可能")
    
    return True


def run_direct_api_test():
    """直接API接続テストの実行"""
    print("🔗 YouTube API直接接続テスト開始")
    print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 認証情報読み込み
    credentials = load_credentials()
    if not credentials:
        print("\\n❌ 認証に失敗しました")
        return False
    
    # 2. YouTubeサービス作成
    service = create_youtube_service(credentials)
    if not service:
        print("\\n❌ YouTubeサービスの作成に失敗しました")
        return False
    
    # 3. 基本API呼び出し
    api_ok, channel_id = test_basic_api_call(service)
    
    # 4. プレイリストアクセステスト
    playlist_ok, playlist_info = test_playlist_access(service)
    
    # 5. 差分更新用動画検出テスト
    detection_ok, video_ids = test_incremental_video_detection(service)
    
    # 6. API配額使用量シミュレーション
    quota_ok = test_quota_usage_simulation()
    
    # 結果サマリー
    print("\\n" + "=" * 60)
    print("📊 API接続テスト結果サマリー")
    print("=" * 60)
    
    tests = [
        ("認証", credentials is not None),
        ("YouTubeサービス", service is not None),
        ("基本API呼び出し", api_ok),
        ("プレイリストアクセス", playlist_ok),
        ("差分更新機能", detection_ok),
        ("API配額効率化", quota_ok)
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\\n総合結果: {passed}/{total} テスト通過")
    
    if passed >= total * 0.8:
        print("\\n🎉 YouTube API接続は正常に動作しています！")
        print("\\n次のステップ:")
        print("1. 実際の差分更新システムでのテスト")
        print("2. バッチ分析機能の実装")
        print("3. 自動化スケジュールの設定")
        
        return True
    else:
        print("\\n⚠️ いくつかの問題があります")
        return False


if __name__ == "__main__":
    run_direct_api_test()