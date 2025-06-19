#!/usr/bin/env python3
"""
プレイリスト動画収集の詳細デバッグスクリプト

プレイリスト収集プロセスを詳細にログ出力して問題を特定
"""

import sys
import json
import pickle
from pathlib import Path
from datetime import datetime

import googleapiclient.discovery
from google.oauth2.credentials import Credentials

# パス設定
sys.path.append('.')

def debug_playlist_collection():
    """プレイリスト収集プロセスを詳細デバッグ"""
    print("=== プレイリスト収集詳細デバッグ ===")
    
    # 調査対象プレイリスト
    playlist_id = "PLKosfnGdlrBXVS-zL2aeOjkrXjKCL6drp"
    
    print(f"調査対象プレイリスト: {playlist_id}")
    print()
    
    # 1. 認証情報の取得
    print("🔐 認証情報の取得")
    try:
        # まずJSONファイルとして読み込みを試行
        token_path = r"D:\setsuna_bot\config\youtube_token.json"
        
        try:
            # JSONファイルとして読み込み
            with open(token_path, 'r', encoding='utf-8') as token:
                token_data = json.load(token)
            print("   JSONトークンファイルを検出")
            from google.oauth2.credentials import Credentials
            creds = Credentials.from_authorized_user_info(token_data)
        except (json.JSONDecodeError, KeyError):
            # pickleファイルとして読み込み
            print("   pickleトークンファイルとして読み込み試行")
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        service = googleapiclient.discovery.build(
            'youtube', 'v3', credentials=creds
        )
        print("✅ YouTube API接続成功")
    except Exception as e:
        print(f"❌ 認証エラー: {e}")
        print("   トークンファイルの再生成が必要です")
        
        # 認証ファイルからの再認証を試行
        try:
            print("   新規認証を試行中...")
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            
            credentials_file = r"D:\setsuna_bot\config\youtube_credentials.json"
            SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
            
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
            
            # トークンを保存
            with open(token_path, 'w', encoding='utf-8') as token:
                token.write(creds.to_json())
            
            service = googleapiclient.discovery.build(
                'youtube', 'v3', credentials=creds
            )
            print("✅ 新規認証完了")
            
        except Exception as auth_error:
            print(f"❌ 新規認証失敗: {auth_error}")
            return
    
    print()
    
    # 2. プレイリスト基本情報の取得
    print("📋 プレイリスト基本情報の取得")
    try:
        playlist_request = service.playlists().list(
            part='snippet,contentDetails',
            id=playlist_id
        )
        playlist_response = playlist_request.execute()
        
        if not playlist_response.get('items'):
            print("❌ プレイリストが見つかりません")
            return
        
        playlist_info = playlist_response['items'][0]
        
        print(f"   タイトル: {playlist_info['snippet']['title']}")
        print(f"   チャンネル: {playlist_info['snippet']['channelTitle']}")
        print(f"   動画数（メタデータ）: {playlist_info['contentDetails']['itemCount']}")
        print(f"   公開日: {playlist_info['snippet']['publishedAt']}")
        
    except Exception as e:
        print(f"❌ プレイリスト情報取得エラー: {e}")
        return
    
    print()
    
    # 3. 動画リストの詳細収集
    print("📹 動画リスト詳細収集")
    
    all_video_ids = []
    next_page_token = None
    page = 1
    collected_videos = 0
    
    try:
        while True:
            print(f"   ページ {page} 処理中...")
            
            # APIリクエスト
            request = service.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
            
            response = request.execute()
            
            # レスポンス詳細の確認
            total_results = response.get('pageInfo', {}).get('totalResults', 0)
            results_per_page = response.get('pageInfo', {}).get('resultsPerPage', 0)
            items_count = len(response.get('items', []))
            
            print(f"      APIレスポンス:")
            print(f"        総結果数: {total_results}")
            print(f"        ページあたり結果数: {results_per_page}")
            print(f"        実際のアイテム数: {items_count}")
            print(f"        nextPageToken: {response.get('nextPageToken', 'なし')}")
            
            page_video_ids = []
            private_count = 0
            deleted_count = 0
            
            # 各アイテムの詳細処理
            for i, item in enumerate(response.get('items', [])):
                snippet = item.get('snippet', {})
                resource_id = snippet.get('resourceId', {})
                
                title = snippet.get('title', '')
                
                # プライベート・削除済み動画のチェック
                if title == 'Private video':
                    private_count += 1
                    print(f"        {i+1:2d}. [プライベート動画] - スキップ")
                    continue
                elif title == 'Deleted video':
                    deleted_count += 1
                    print(f"        {i+1:2d}. [削除済み動画] - スキップ")
                    continue
                
                # 通常の動画
                if resource_id.get('kind') == 'youtube#video':
                    video_id = resource_id.get('videoId')
                    if video_id:
                        all_video_ids.append(video_id)
                        page_video_ids.append(video_id)
                        collected_videos += 1
                        print(f"        {i+1:2d}. {video_id} - {title[:50]}...")
                else:
                    print(f"        {i+1:2d}. [非動画コンテンツ] {resource_id.get('kind', 'unknown')} - スキップ")
            
            print(f"      ページ {page} 結果:")
            print(f"        取得動画: {len(page_video_ids)}件")
            print(f"        プライベート: {private_count}件")
            print(f"        削除済み: {deleted_count}件")
            print(f"        累計動画: {len(all_video_ids)}件")
            
            # 次ページの確認
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                print(f"      ページネーション終了 - nextPageTokenなし")
                break
            
            page += 1
            
            # 安全制限
            if page > 20:
                print(f"      安全制限到達 - ページ制限20")
                break
        
        print(f"   ✅ 収集完了: {len(all_video_ids)}件")
        
    except Exception as e:
        print(f"   ❌ 動画収集エラー: {e}")
        print(f"      エラー時点での収集数: {len(all_video_ids)}件")
    
    print()
    
    # 4. 結果のサマリー
    print("📊 収集結果サマリー:")
    print(f"   メタデータ上の動画数: {playlist_info['contentDetails']['itemCount']}")
    print(f"   実際に収集した動画数: {len(all_video_ids)}")
    print(f"   差分: {playlist_info['contentDetails']['itemCount'] - len(all_video_ids)}")
    
    # 最初の10件を表示
    if all_video_ids:
        print(f"\n📹 収集した動画ID（最初の10件）:")
        for i, video_id in enumerate(all_video_ids[:10]):
            print(f"   {i+1:2d}. {video_id}")
    
    print()
    
    # 5. データベースとの比較
    print("🗃️ データベース比較:")
    try:
        from storage.unified_storage import UnifiedStorage
        storage = UnifiedStorage()
        db = storage.load_database()
        
        if playlist_id in db.playlists:
            db_playlist = db.playlists[playlist_id]
            db_video_ids = set(db_playlist.video_ids)
            collected_video_ids = set(all_video_ids)
            
            print(f"   データベース内動画数: {len(db_video_ids)}")
            print(f"   今回収集動画数: {len(collected_video_ids)}")
            
            # 差分分析
            only_in_db = db_video_ids - collected_video_ids
            only_in_collection = collected_video_ids - db_video_ids
            common = db_video_ids & collected_video_ids
            
            print(f"   共通動画: {len(common)}件")
            print(f"   DB のみ: {len(only_in_db)}件")
            print(f"   収集のみ: {len(only_in_collection)}件")
            
            if only_in_db:
                print(f"   DBにのみ存在する動画:")
                for vid in list(only_in_db)[:5]:
                    print(f"     {vid}")
            
            if only_in_collection:
                print(f"   今回収集でのみ見つかった動画:")
                for vid in list(only_in_collection)[:5]:
                    print(f"     {vid}")
        else:
            print("   データベースにプレイリスト情報なし")
    
    except Exception as e:
        print(f"   ❌ データベース比較エラー: {e}")

if __name__ == "__main__":
    debug_playlist_collection()