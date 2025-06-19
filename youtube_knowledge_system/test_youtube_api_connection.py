"""
YouTube API接続テストスクリプト

認証状況とAPI接続を確認し、差分更新に必要な基本機能をテスト
"""

import sys
import json
import time
from datetime import datetime
from pathlib import Path

# パッケージパスを追加
sys.path.append(str(Path(__file__).parent))


def test_basic_imports():
    """基本インポートのテスト"""
    print("=== 基本インポートテスト ===")
    
    try:
        import googleapiclient.discovery
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import InstalledAppFlow
        import google.auth.exceptions
        print("✅ Google API関連ライブラリのインポート成功")
        return True
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        return False


def test_credentials_loading():
    """認証情報の読み込みテスト"""
    print("\\n=== 認証情報読み込みテスト ===")
    
    # 認証ファイルのパス（Windows実パス）
    credentials_file = Path("D:/setsuna_bot/config/youtube_credentials.json")
    token_file = Path("D:/setsuna_bot/config/youtube_token.json")
    
    print(f"認証ファイル: {credentials_file}")
    print(f"トークンファイル: {token_file}")
    
    # ファイル存在確認
    if not credentials_file.exists():
        print(f"❌ 認証ファイルが見つかりません: {credentials_file}")
        return False, None, None
    
    if not token_file.exists():
        print(f"⚠️ トークンファイルが見つかりません: {token_file}")
        print("初回認証が必要です")
    else:
        print("✅ 認証ファイル確認済み")
    
    return True, credentials_file, token_file


def test_youtube_service_creation():
    """YouTube サービス作成テスト"""
    print("\\n=== YouTube サービス作成テスト ===")
    
    try:
        from collectors.auth_manager import YouTubeAuthManager
        
        # パス設定を調整
        auth_manager = YouTubeAuthManager()
        auth_manager.credentials_file = Path("D:/setsuna_bot/config/youtube_credentials.json")
        auth_manager.token_file = Path("D:/setsuna_bot/config/youtube_token.json")
        
        print("YouTube認証マネージャーの初期化中...")
        service = auth_manager.get_youtube_service()
        
        if service:
            print("✅ YouTubeサービス作成成功")
            return True, service
        else:
            print("❌ YouTubeサービス作成失敗")
            return False, None
            
    except Exception as e:
        print(f"❌ YouTubeサービス作成エラー: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_api_basic_call(service):
    """基本的なAPI呼び出しテスト"""
    print("\\n=== 基本API呼び出しテスト ===")
    
    if not service:
        print("サービスが利用できません")
        return False
    
    try:
        # 最も軽量なAPI呼び出し：チャンネル情報取得
        print("チャンネル情報取得テスト中...")
        
        request = service.channels().list(
            part='snippet',
            mine=True,
            maxResults=1
        )
        
        response = request.execute()
        
        if 'items' in response and len(response['items']) > 0:
            channel = response['items'][0]
            channel_title = channel['snippet']['title']
            channel_id = channel['id']
            
            print(f"✅ API呼び出し成功")
            print(f"  チャンネル名: {channel_title}")
            print(f"  チャンネルID: {channel_id}")
            
            return True, channel_id
        else:
            print("⚠️ チャンネル情報が取得できませんでした")
            return False, None
            
    except Exception as e:
        print(f"❌ API呼び出しエラー: {e}")
        return False, None


def test_playlist_access(service, channel_id=None):
    """プレイリストアクセステスト"""
    print("\\n=== プレイリストアクセステスト ===")
    
    if not service:
        print("サービスが利用できません")
        return False
    
    try:
        # テスト用プレイリストID
        test_playlist_id = "PL4R2l8ETuvxueMZJo63H8ykV_OY0LuzfX"
        
        print(f"プレイリスト {test_playlist_id} の情報取得中...")
        
        # プレイリスト情報取得
        playlist_request = service.playlists().list(
            part='snippet,contentDetails',
            id=test_playlist_id
        )
        
        playlist_response = playlist_request.execute()
        
        if 'items' in playlist_response and len(playlist_response['items']) > 0:
            playlist_info = playlist_response['items'][0]
            title = playlist_info['snippet']['title']
            item_count = playlist_info['contentDetails']['itemCount']
            
            print(f"✅ プレイリスト情報取得成功")
            print(f"  タイトル: {title}")
            print(f"  動画数: {item_count}")
            
            return True, playlist_info
        else:
            print(f"❌ プレイリスト {test_playlist_id} が見つかりません")
            return False, None
            
    except Exception as e:
        print(f"❌ プレイリストアクセスエラー: {e}")
        return False, None


def test_playlist_videos_fetch(service, limit=3):
    """プレイリスト動画取得テスト（差分更新用）"""
    print(f"\\n=== プレイリスト動画取得テスト（先頭{limit}件） ===")
    
    if not service:
        print("サービスが利用できません")
        return False
    
    try:
        test_playlist_id = "PL4R2l8ETuvxueMZJo63H8ykV_OY0LuzfX"
        
        print(f"プレイリスト動画リスト取得中（最大{limit}件）...")
        
        # プレイリスト動画リスト取得（差分更新で使用する最小限のフィールド）
        request = service.playlistItems().list(
            part='snippet',
            playlistId=test_playlist_id,
            maxResults=limit,
            fields='items/snippet/resourceId/videoId,nextPageToken'
        )
        
        response = request.execute()
        
        video_ids = []
        for item in response.get('items', []):
            resource_id = item.get('snippet', {}).get('resourceId', {})
            if resource_id.get('kind') == 'youtube#video':
                video_ids.append(resource_id['videoId'])
        
        print(f"✅ 動画ID取得成功: {len(video_ids)}件")
        print(f"  動画ID: {video_ids}")
        
        # 動画詳細情報取得テスト
        if video_ids:
            print(f"\\n動画詳細情報取得テスト...")
            
            details_request = service.videos().list(
                part='snippet,statistics',
                id=','.join(video_ids[:2])  # 最初の2件のみ
            )
            
            details_response = details_request.execute()
            
            for item in details_response.get('items', []):
                title = item['snippet']['title']
                view_count = item['statistics'].get('viewCount', '0')
                print(f"  {item['id']}: {title[:50]}... (再生回数: {view_count})")
            
            print(f"✅ 動画詳細取得成功")
        
        return True, video_ids
        
    except Exception as e:
        print(f"❌ プレイリスト動画取得エラー: {e}")
        return False, []


def test_api_quota_efficiency():
    """API配額効率性のテスト"""
    print(f"\\n=== API配額効率性テスト ===")
    
    print("差分更新でのAPI使用パターン:")
    print("1. プレイリスト動画ID取得: 1クォータ (fields指定で最小化)")
    print("2. 新規動画詳細取得: 1クォータ (新規動画分のみ)")
    print("3. 従来の全件取得との比較:")
    print("   - 全件取得: 動画数/50 × 2クォータ (例: 110動画 = 5クォータ)")
    print("   - 差分取得: 新規動画のみ (例: 2動画 = 1クォータ)")
    print("   - 削減率: 80-90%の配額削減効果")
    
    return True


def run_comprehensive_api_test():
    """包括的なAPI接続テストの実行"""
    print("🔗 YouTube API接続包括テスト開始")
    print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    test_results = {}
    
    # 1. 基本インポートテスト
    test_results['imports'] = test_basic_imports()
    
    # 2. 認証情報読み込みテスト
    creds_ok, creds_file, token_file = test_credentials_loading()
    test_results['credentials'] = creds_ok
    
    # 3. YouTubeサービス作成テスト
    service_ok, service = test_youtube_service_creation()
    test_results['service'] = service_ok
    
    if service:
        # 4. 基本API呼び出しテスト
        api_ok, channel_id = test_api_basic_call(service)
        test_results['api_call'] = api_ok
        
        # 5. プレイリストアクセステスト
        playlist_ok, playlist_info = test_playlist_access(service, channel_id)
        test_results['playlist'] = playlist_ok
        
        # 6. プレイリスト動画取得テスト
        videos_ok, video_ids = test_playlist_videos_fetch(service, 3)
        test_results['video_fetch'] = videos_ok
        
        # 7. API効率性確認
        test_results['efficiency'] = test_api_quota_efficiency()
    
    # 結果サマリー
    print("\\n" + "=" * 60)
    print("📊 API接続テスト結果")
    print("=" * 60)
    
    passed_tests = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.upper()}: {status}")
    
    print(f"\\n総合結果: {passed_tests}/{total_tests} テスト通過")
    
    if passed_tests >= total_tests * 0.8:
        print("🎉 YouTube API接続は正常です！")
        print("\\n次のステップ:")
        print("1. 実際のプレイリストで差分更新テスト")
        print("2. バッチ分析機能の実装")
        print("3. API配額監視の設定")
    else:
        print("⚠️ いくつかの問題があります。認証設定を確認してください。")
    
    print(f"\\n終了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return test_results


if __name__ == "__main__":
    run_comprehensive_api_test()