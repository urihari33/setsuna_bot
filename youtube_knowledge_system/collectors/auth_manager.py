"""
YouTube API OAuth認証管理
"""
import os
import pickle
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from ..config.settings import (
    YOUTUBE_CREDENTIALS_PATH, 
    YOUTUBE_TOKEN_PATH,
    YOUTUBE_API_SERVICE_NAME,
    YOUTUBE_API_VERSION,
    YOUTUBE_SCOPES
)


class YouTubeAuthManager:
    """YouTube API認証を管理するクラス"""
    
    def __init__(self):
        self.credentials = None
        self.service = None
    
    def authenticate(self):
        """OAuth認証を実行"""
        print("YouTube API認証を開始します...")
        
        # 既存のトークンファイルがあるかチェック
        if YOUTUBE_TOKEN_PATH.exists():
            print("既存の認証トークンを読み込み中...")
            with open(YOUTUBE_TOKEN_PATH, 'rb') as token_file:
                self.credentials = pickle.load(token_file)
        
        # 認証情報が無効または存在しない場合
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                print("認証トークンを更新中...")
                self.credentials.refresh(Request())
            else:
                print("新しい認証を実行中...")
                if not YOUTUBE_CREDENTIALS_PATH.exists():
                    raise FileNotFoundError(
                        f"認証情報ファイルが見つかりません: {YOUTUBE_CREDENTIALS_PATH}\n"
                        "Google Cloud Consoleからダウンロードしたcredentials.jsonを配置してください。"
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(YOUTUBE_CREDENTIALS_PATH), YOUTUBE_SCOPES
                )
                self.credentials = flow.run_local_server(port=0)
            
            # トークンを保存
            YOUTUBE_TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(YOUTUBE_TOKEN_PATH, 'wb') as token_file:
                pickle.dump(self.credentials, token_file)
            print("認証トークンを保存しました")
        
        print("認証完了！")
        return self.credentials
    
    def get_youtube_service(self):
        """認証済みのYouTube APIサービスオブジェクトを取得"""
        if not self.credentials:
            self.authenticate()
        
        if not self.service:
            self.service = build(
                YOUTUBE_API_SERVICE_NAME, 
                YOUTUBE_API_VERSION, 
                credentials=self.credentials
            )
            print("YouTube APIサービスを初期化しました")
        
        return self.service
    
    def test_connection(self):
        """API接続テスト"""
        try:
            service = self.get_youtube_service()
            
            # チャンネル情報を取得してテスト
            request = service.channels().list(
                part="snippet,statistics",
                mine=True
            )
            response = request.execute()
            
            if response.get('items'):
                channel = response['items'][0]
                channel_title = channel['snippet']['title']
                subscriber_count = channel['statistics'].get('subscriberCount', 'N/A')
                print(f"接続テスト成功！")
                print(f"チャンネル名: {channel_title}")
                print(f"登録者数: {subscriber_count}")
                return True
            else:
                print("チャンネル情報が取得できませんでした")
                return False
                
        except Exception as e:
            print(f"接続テストでエラーが発生しました: {e}")
            return False


if __name__ == "__main__":
    # テスト実行
    auth_manager = YouTubeAuthManager()
    auth_manager.test_connection()