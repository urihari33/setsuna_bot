#!/usr/bin/env python3
"""
既存プレイリストJSONファイル生成スクリプト

既存のプレイリストに対してもJSONファイルを生成
"""

import sys
import os
from pathlib import Path

# パス設定
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 直接インポートで認証機能を実装
import json
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from collectors.multi_playlist_collector import MultiPlaylistCollector
from storage.unified_storage import UnifiedStorage
from managers.playlist_config_manager import PlaylistConfigManager

def get_youtube_service():
    """YouTube API サービスを取得"""
    # YouTube API設定
    SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
    SERVICE_NAME = 'youtube'
    API_VERSION = 'v3'
    
    # 認証ファイルパス（Windows）
    credentials_file = r"D:\setsuna_bot\config\youtube_credentials.json"
    token_file = r"D:\setsuna_bot\config\youtube_token.json"
    
    creds = None
    
    # トークンファイルが存在する場合は読み込み
    if os.path.exists(token_file):
        try:
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        except Exception as e:
            print(f"   トークンファイル読み込みエラー: {e}")
            creds = None
    
    # 認証が無効または存在しない場合
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"   トークン更新エラー: {e}")
                creds = None
        
        if not creds:
            try:
                # 認証ファイルの存在確認
                if not os.path.exists(credentials_file):
                    raise FileNotFoundError(f"認証ファイルが見つかりません: {credentials_file}")
                
                flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                print(f"   新規認証エラー: {e}")
                raise
        
        # トークンを保存
        try:
            with open(token_file, 'w', encoding='utf-8') as token:
                token.write(creds.to_json())
        except Exception as e:
            print(f"   トークン保存エラー: {e}")
    
    return build(SERVICE_NAME, API_VERSION, credentials=creds)

def generate_existing_playlist_jsons():
    """既存プレイリストのJSONファイルを生成"""
    print("=== 既存プレイリストJSONファイル生成 ===")
    
    # 初期化
    collector = MultiPlaylistCollector()
    storage = UnifiedStorage()
    config_manager = PlaylistConfigManager()
    
    # API初期化
    try:
        collector.service = get_youtube_service()
        if not collector.service:
            print("❌ YouTube API サービス初期化に失敗しました")
            return
        print("✅ YouTube API サービス初期化完了")
    except Exception as e:
        print(f"❌ API初期化エラー: {e}")
        return
    
    # 設定とデータベースを読み込み
    configs = config_manager.list_configs()
    db = storage.load_database()
    
    print(f"設定プレイリスト数: {len(configs)}")
    print(f"データベースプレイリスト数: {len(db.playlists)}")
    
    generated_count = 0
    
    for config in configs:
        playlist_id = config.playlist_id
        print(f"\n処理中: {config.display_name} ({playlist_id})")
        
        # データベースにプレイリストが存在するかチェック
        if playlist_id not in db.playlists:
            print(f"   ⚠️ データベースにプレイリスト {playlist_id} が見つかりません")
            continue
        
        playlist = db.playlists[playlist_id]
        
        # プレイリスト情報の構築
        playlist_info = {
            'title': playlist.metadata.title,
            'description': playlist.metadata.description,
            'channel_title': playlist.metadata.channel_title,
            'channel_id': playlist.metadata.channel_id,
            'item_count': playlist.metadata.item_count,
            'published_at': playlist.metadata.published_at.isoformat()
        }
        
        # JSONファイル生成
        try:
            collector._generate_playlist_json(
                playlist_id, 
                playlist_info, 
                playlist.video_ids, 
                config
            )
            generated_count += 1
            print(f"   ✅ JSONファイル生成完了")
            
        except Exception as e:
            print(f"   ❌ JSON生成エラー: {e}")
    
    print(f"\n=== 生成完了 ===")
    print(f"生成したJSONファイル数: {generated_count}")

if __name__ == "__main__":
    generate_existing_playlist_jsons()